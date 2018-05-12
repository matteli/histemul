'''
Copyright (c) 2012-2015, Matthieu Nué
All rights reserved.

Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, 
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice, 
  this list of conditions and the following disclaimer in the documentation 
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT 
OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF 
THE POSSIBILITY OF SUCH DAMAGE.
'''

from itemsclass import ItemsClass
from army import Army
from battle import Battle
from culture import Culture
from land import Land
from person import Person
from player import Player
from province import Province
from title import Title
from war import War
from config import Config
import random
import struct
from enumeration import *

class Model(dict):
    def __init__(self):
        random.seed()
        self['Config'] = ItemsClass('config.yaml')
        self['Army'] = ItemsClass('army.yaml')
        self['Battle'] = ItemsClass('battle.yaml')
        self['Culture'] = ItemsClass('culture.yaml')
        self['Land'] = ItemsClass('land.yaml')
        self['Person'] = ItemsClass('person.yaml')
        self['Player'] = ItemsClass('player.yaml')
        self['Province'] = ItemsClass('province.yaml')
        self['Title'] = ItemsClass('title.yaml')
        self['War'] = ItemsClass('war.yaml')

        for items_class in self.values():
            if items_class:
                cls = items_class[list(items_class.keys())[0]].__class__
                #for att,handler in cls.relations.items():
                for att, cls_handler in cls.relations.items():
                    #cls_handler, delimiter, attribute_handler = handler.partition('.')
                    #if not(len(delimiter)):
                    for v in items_class.values():
                        attr = ''
                        if hasattr(v, att + '_'):
                            attr = att
                        else:
                            print (str(att) + " attribute in " + str(cls) + " class is not present!")
                            break

                        if isinstance(getattr(v, attr + '_'), list):
                            li = []
                            for val in getattr(v, attr + '_'):
                                li.append(self[cls_handler][val])
                            try:
                                setattr(v, attr, li)
                            except:
                                pass #define a warning message
                        elif isinstance(getattr(v, attr + '_'), set):
                            s = set()
                            for val in getattr(v, attr + '_'):
                                s.add(self[cls_handler][val])
                            try:
                                setattr(v, attr, s)
                            except:
                                pass #define a warning message
                        else:
                            try:
                                setattr(v, attr, self[cls_handler][getattr(v, attr + '_')])
                            except:
                                pass #define a warning message

        for items_class in self.values():
            items_class.init()

    def update(self, tick):
        #army walk
        for key, army in self['Army'].items():
            if army.knights:
                if army.new_destination:
                    army.way = self.a_star(army.locating, army.new_destination)
                    army.new_destination = None
                    army.way_pc_done = 0
                    army.set_next_province()
                if army.way_pc_done >= 100:
                    province = army.nextprovince
                    army.move_to(province)
                    army.set_next_province()

                    #when enter a new province, look if there is ennemy or already a battle
                    person = army.for_the
                    if not province.battle:
                        enemy = set()
                        for war in person.wars_aggressor | person.wars_defender:
                            for enemy_person in war.get_enemies(person):
                                for other_army in province.army:
                                    if enemy_person == other_army.for_the:
                                        enemy.add(other_army)
                            if enemy:
                                self.new_battle({army}, enemy, war, province)
                                army.stop()
                                break

                    else:
                        war = province.battle.war
                        person_defender = next(iter(province.battle.defenders)).for_the
                        if person_defender in war.get_allies(person): #allies
                            province.battle.add_defender(army)
                            army.stop()
                        elif person_defender in war.get_enemies(person): #enemy
                            province.battle.add_aggressor(army)
                            army.stop()

                    army.way_pc_done -= 100

                if army.next_province:
                    army.way_pc_done += 50
                else:
                    army.way_pc_done = 0

                #morale
                if army.morale < 100:
                    if army.attitude == Attitude.NORMAL:
                        army.morale += 5
                        if army.morale > 100:
                            army.morale = 100

        for key, province in self['Province'].items():
            if key != 'TI':
                if province.armies:
                    if province.battle:
                        province.set_war_siege(None)
                    elif province.controller:
                        province.aggressor = 0
                        province_controller = province.controller
                        if province.war_siege:
                            war = province.war_siege
                            for enemy in war.get_enemies(province_controller):
                                for army in province.armies:
                                    if army.for_the == enemy:
                                        province.aggressor += army.knights
                            if province.aggressor == 0:
                                #import pdb; pdb.set_trace()
                                province.set_war_siege(None)
                        else:
                            for war in province_controller.wars_aggressor | province_controller.wars_defender:
                                for enemy_country in war.get_enemies(province_controller):
                                    for army in province.armies:
                                        if army.for_the == enemy_country and army.attitude == Attitude.NORMAL:
                                            province.aggressor += army.knights
                                            province.war_siege = war
                    else:
                        province.set_war_siege(None)

                if not tick%10:
                    war = province.war_siege
                    if war:
                        dice = int(((random.randrange(10) + 1)**2) / 4)
                        if dice >= province.morale:
                            province.change_controller(war.get_enemies(province.owner)[0])
                            province.set_war_siege(None)
                            province.morale = 100
                        else:
                            province.morale -= int(dice)
                    else:
                        if province.morale < 100:
                            if province.morale < 90:
                                province.morale += 10
                            else:
                                province.morale = 100

        for key, battle in self['Battle'].items():
            if key != 'TI':
                if battle.active:
                    if not battle.tick%4:
                        battle.dice_defenders = ((random.randrange(10) + 1)**2) / 4
                        battle.dice_aggressors = ((random.randrange(10) + 1)**2) / 4

                    defenders = list(battle.defenders)
                    for army in defenders:
                        army_loose = int(army.knights * battle.nb_knights_aggressors * battle.dice_aggressors / (500 * battle.nb_knights_defenders))
                        if army_loose >= army.knights:
                            battle.nb_knights_defenders -= army.knights
                            army.knights = 0
                            army.dismiss()
                        else:
                            army.knights -= army_loose
                            battle.nb_knights_defenders -= army_loose

                            if int(battle.dice_aggressors) >= army.morale:
                                army.morale = 0
                                army.retreat()
                            else:
                                army.morale -= int(battle.dice_aggressors)

                    if battle.nb_knights_defenders <= 0:
                        battle.end()
                        break

                    aggressors = list(battle.aggressors)
                    for army in aggressors:
                        army_loose = int(army.knights * battle.nb_knights_defenders * battle.dice_defenders / (500 * battle.nb_knights_aggressors))
                        if army_loose >= army.knights:
                            battle.nb_knights_aggressors -= army.knights
                            army.knights = 0
                            army.dismiss()
                        else:
                            army.knights -= army_loose
                            battle.nb_knights_aggressors -= army_loose

                            if int(battle.dice_defenders) >= army.morale:
                                army.morale = 0
                                army.retreat()
                            else:
                                army.morale -= int(battle.dice_defenders)


                    if battle.nb_knights_aggressors <= 0:
                        battle.end()

                    battle.tick += 1

    def new_army(self, province, knights = 0, name = ''):
        #TODO : fix same name for multiple army from the same province
        if province.manpower > 0:
            if name == '':
                name = self.get_name_by_id('province', province.idd) + ' army'
            #import pdb; pdb.set_trace()
            if knights == 0:
                knights = province.manpower
            province.manpower -= knights
            self['army'][name] = Army(self['army'].first_free_id(), knights, province, province, province.owner)
            self['army'][name].init()

    #def delete_army(self, value):
    #    if not isinstance(value, str):
    #        value = self.get_name('army', value)
    #    self['army'][value].delete()
    #    del self['army'][value]

    def new_battle(self, defenders, aggressors, war, province, name = ''):
        if name == '':
            name = self.get_name_by_id('province', province.idd) + ' battle'
        if name in self['battle'] :
            i = 2
            while (name + " " + str(i) in self['battle']):
                i += 1
            name += ' ' + str(i)
        self['battle'][name] = Battle(war, province, aggressors, defenders)
        self['battle'][name].init()
        print('Start of the ' + name)

    def new_war(self, aggressors, defenders, name = ''):
        for war in aggressors[0].wars_aggressor | aggressors[0].wars_defender:
            if defenders[0] in war.get_enemies(aggressors[0]):
                return False
        if name == '':
            name = self.get_name('country', aggressors[0]) + ' against ' + self.get_name('country', defenders[0]) + ' war'
        if name in self['war'] :
            i = 2
            while (name + ' ' + str(i) in self['war']):
                i += 1
            name += ' ' + str(i)
        self['war'][name] = War(aggressors, defenders)
        self['war'][name].init()
        return True

    def a_star(self, current, end):
        if current == end:
            return []
        open_list = set()
        closed_list = set()
        start = current

        def retracePath(c):
            path = []
            path.append(c)
            while c.parent is not start:
                c = c.parent
                path.append(c)
            return path

        open_list.add(current)
        while open_list:
            current = sorted(open_list, key=lambda inst:inst.f)[0]
            if current == end:
                return retracePath(current)
            open_list.remove(current)
            closed_list.add(current)
            for adja in current.adjacent:
                if adja.land.walkable > 0 and adja not in closed_list:
                    temp_g = current.g + current.size/(2*current.land.walkable) + adja.size/(2*current.land.walkable)
                    if adja not in open_list:
                        open_list.add(adja)
                        adja.parent = current
                        adja.g = temp_g
                        adja.f = adja.g + (abs(end.armyXPos-adja.armyXPos)+abs(end.armyYPos-adja.armyYPos))/100
                    else:
                        if temp_g < adja.g :
                            adja.parent = current
                            adja.g = temp_g
                            adja.f = adja.g + (abs(end.armyXPos-adja.armyXPos)+abs(end.armyYPos-adja.armyYPos))/100
        return []


    def get_name(self, item, instance):
        for k, v in self[item].items():
            if v == instance:
                return (k)
        return ("")

    def get_name_by_id(self, item, idd):
        for k, v in self[item].items():
            if v.idd == idd:
                return (k)
        return ("")

    def pack_all_data(self, player):
        data_bytes = b''
        for v in self.values():
            data_bytes += v.pack_all_data(player)
        return (struct.pack('>I', 0) + data_bytes) #data

    def pack_modified_data(self, player):
        data_bytes = b''
        for v in self.values():
            data_bytes += v.pack_modified_data(player)
        return (struct.pack('>I', 0) + data_bytes) #data