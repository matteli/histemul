'''
Copyright (c) 2012-2017, Matthieu Nué
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

from army import Army
from battle import Battle
from culture import Culture
from land import Land
from person import Person
from player import Player
from province import Province
from title import Title
from war import War
from mongoengine import connect, QuerySet
import random
import time
from functions import *
import datetime
from pymongo import MongoClient


class Model():
    def __init__(self, reset=False, preset=False):
        self.model = {
            'army': Army,
            'battle': Battle,
            'culture': Culture,
            'land': Land,
            'person': Person,
            'player': Player,
            'province': Province,
            'title': Title,
            'war': War,
        }
        connect('histemul')
        self.orders = {}
        
        if reset:
            client = MongoClient()
            db = client.histemul
            Player.drop_collection()
            Person.drop_collection()
            Army.drop_collection()
            Battle.drop_collection()
            War.drop_collection()

            Province.drop_collection()
            #collection = db.province_vo
            db.command('aggregate', 'province_vo', pipeline= [ { '$match': {} }, { '$out': "province" } ], allowDiskUse=True, cursor={})
            if preset:
                Matthieu = self.new_player('Matthieu', division='fess', tinctures=['green','orange'])
                Pierre = self.new_player('Pierre', division='pale', tinctures=['blue','red'])
                Robert = self.new_person('Robert', True, datetime.date(975,1,1), Matthieu, 1)
                Jean = self.new_person('Jean', True, datetime.date(981,1,1), Pierre, 14)
                Philippe = self.new_person('Philippe', True, datetime.date(965,1,1), Pierre, 39)
                Matthieu.leader = Robert
                Matthieu.save()
                Pierre.leader = Jean
                Pierre.save()

                Berquinais = Title.objects.get(pk='Berquinais')
                Berquinais.holder = Robert
                Berquinais.name_number = {'Robert': 1}
                Berquinais.save()

                Orvence = Title.objects.get(pk='Orvence')
                Orvence.holder = Jean
                Orvence.name_number = {'Jean': 1}
                Orvence.save()

                Bourquige = Title.objects.get(pk='Bourquige')
                Bourquige.holder = Philippe
                Bourquige.name_number = {'Philippe': 1}
                Bourquige.save()

                Berquinais_province = Province.objects.get(name='Berquinais')
                Berquinais_province.controller = Robert
                Berquinais_province.save()

                Orvence_province = Province.objects.get(name='Orvence')
                Orvence_province.controller = Jean
                Orvence_province.save()

                Bourquige_province = Province.objects.get(name='Bourquige')
                Bourquige_province.controller = Philippe
                Bourquige_province.save()

                Army_Orvence = self.rally_troops(Pierre, Orvence_province, 'execute')

    def end_order(self, status):
        if status == 'order':
            return 'accepted'
        return 'normal'
        
    def declare_war(self, aggressor, defender, status):
        if aggressor.player == defender.player:
            return 'hidden'
        if set(aggressor.wars).intersection(defender.wars):
            return 'disabled'
        if status == 'execute':
            War.objects.create(aggressors=[aggressor], defenders=[defender], active=True)
            return 'done'
        return self.end_order(status)
        
    def propose_peace(self, aggressor, defender, opt, status):
        if aggressor.player == defender.player:
            return 'hidden'
        if not set(aggressor.wars).intersection(defender.wars):
            return 'disabled'
        return self.end_order(status)

    def rally_troops(self, player, province, status):
        if province.domain_of.holder.player != player:
            return 'hidden'
        if province.manpower == 0:
            return 'disabled'
        if status == 'execute':
            Army.objects.create(for_the=province.domain_of.holder, attitude='normal', location=province, origin=province, knights = province.manpower, morale=100, time_walking=0)
            province.manpower = 0
            province.save()
            return 'done'
        return self.end_order(status)
    
    def move_troops(self, player, army, to_province, status):
        if army.for_the.player != player:
            return 'hidden'
        way = self.a_star(army.location, to_province)
        if not way:
            return 'disabled'
        if status == 'execute':
            army.way = way
            army.save()
            return 'done'
        return self.end_order(status)
        #return self.list_list_att(way, 'id_map')

    def new_person(self, name, male, born, player, location, father=None, mother=None):
        return Person.objects.create(name=name, male=male, born=born, player=player, location=location, father=father, mother=mother)

    def new_player(self, name, leader=None, shape='triangle', division='plain', tinctures=['blue', 'red']):
        return Player.objects.create(name=name, leader=leader, shape=shape, division=division, tinctures=tinctures)

    def new_battle(self, war, location, aggressors, defenders):
        battle = Battle.objects.create(war=war, active=True)
        location.battle = battle
        location.save()
        for aggressor in aggressors:
            aggressor.battle = battle
            aggressor.attitude = 'aggressor'
            aggressor.save()
        for defender in defenders:
            defender.battle = battle
            defender.attitude = 'defender'
            defender.save()
        return battle
    
    def dismiss_army(self, army):
        army.origin.manpower += army.knights
        army.knights = 0
        army.save()
        army.delete()

    def make_orders(self, player, msg, idd, opt, status):

        result = 'rejected'

        if msg == 'rally_troops':
            result = self.rally_troops(Player.objects.get(pk=player), Province.objects.get(pk=idd), status)

        elif msg == 'move_troops':
            result = self.move_troops(Player.objects.get(pk=player), Army.objects.get(pk=idd), Province.objects.get(pk=opt['to']), status)

        elif msg == 'declare_war':
            result = self.declare_war(Person.objects.get(pk=opt['from']), Province.objects.get(pk=idd).domain_of.holder, status)

        elif msg == 'propose_peace':
            result = self.propose_peace(Person.objects.get(pk=opt['from']), Province.objects.get(pk=idd).domain_of.holder, opt, status)

        if result == 'accepted' and status=='order':
            if player not in self.orders:
                self.orders[player] = []
            self.orders[player].append(((msg, idd), opt))

        return result

    def update(self, date):
        for player, orders in self.orders.items():
            if orders:
                order = orders.pop()
                self.make_orders(player, order[0][0], order[0][1], order[1], 'execute')
        print("Start update army")
        for army in Army.objects.select_related(3):
            if army.way and army.next_province != army.way[-1]: #change way since last update
                army.next_province = army.way[-1]
                army.time_walking = 0

            if army.time_walking >= army.location.size: #enter a new province
                army.time_walking -= army.location.size
                province = army.next_province
                army.location = province
                army.way.pop()
                if army.way:
                    army.next_province = army.way[-1]
                else:
                    army.next_province = None
                    army.attitude = 'normal'

                #when enter a new province, look if there is enemy or already a battle
                person = army.for_the
                battle = province.battle

                if not battle:
                    war = None
                    enemies = []
                    for army_in_province in province.armies:
                        if not war:
                            war = person.in_war_against(army_in_province.for_the)['war']
                            enemies.append(army_in_province)
                        else:
                            w = person.in_war_against(army_in_province.for_the)[0]['war']
                            if w == war:
                                enemies.append(army_in_province)
                    if enemies: #enemy so battle
                        army.stop()
                        self.new_battle(war, province, [army], enemies)

                else:
                    war = battle.war
                    if person in war.aggressors:
                        army.stop()
                        battle.add_aggressor(army)
                    if person in war.defenders:
                        army.stop()
                        battle.add_defender(army)

            if army.next_province:
                army.time_walking += 500 * army.location.land.walkable
            else:
                army.time_walking = 0

            #morale
            if army.attitude == 'normal':
                if army.morale < 95:
                    army.morale += 5
                else:
                    army.morale = 100
            
            army.save()

        print("Start update province")
        for province in Province.objects.select_related(3):
            if province.domain_of:
                province.domain_of.treasure += 10
                province.domain_of.save()
            province_war_siege_knights = 0            
            if province.battle and province.battle.active:
                province.war_siege = None
            elif province.controller:
                if province.war_siege:
                    war = province.war_siege
                    for enemy in war.get_enemies(province.controller):
                        for army in province.armies:
                            if army.for_the == enemy:
                                province_war_siege_knights += army.knights
                    if province_war_siege_knights == 0:
                        province.war_siege = None
                        province.siege = 0
                else:
                    for war in province.controller.wars:
                        for enemy_country in war.get_enemies(province.controller):
                            for army in province.armies:
                                if army.for_the == enemy_country and army.attitude == 'normal':
                                    province_war_siege_knights += army.knights
                                    province.war_siege = war
                                    province.siege = 1
            else:
                province.war_siege = None
                province.siege = 0

            if province.land.is_walkable():
                war = province.war_siege
                if war:
                    dice = int(((random.randrange(10) + 1)**2) / 4)
                    if dice >= province.morale:
                        province.controller = war.get_enemies(province.controller)[0]
                        province.war_siege = None
                        province.siege = 0
                        province.morale = 100
                    else:
                        province.morale -= int(dice)
                else:
                    if province.morale < 100:
                        if province.morale < 90:
                            province.morale += 10
                        else:
                            province.morale = 100

            province.save()

        print("Start update battle")
        for battle in Battle.objects.select_related(3):
            if battle.active:
                battle_dice_defenders = ((random.randrange(10) + 1)**2) / 2
                battle_dice_aggressors = ((random.randrange(10) + 1)**2) / 2

                armies = battle.armies
                nb_knights = battle.counting_knights(armies)

                for army in armies:
                    if army.attitude == 'aggressor':
                        army.knights -= int(army.knights * nb_knights['defenders'] * battle_dice_defenders / (400 * nb_knights['aggressors']))
                        army.morale -= int(battle_dice_defenders)
                    elif army.attitude == 'defender':
                        army.knights -= int(army.knights * nb_knights['aggressors'] * battle_dice_aggressors / (100 * nb_knights['defenders']))
                        army.morale -= int(battle_dice_aggressors)
                    if army.morale < 0:
                        army.morale = 0
                    army.save()
                    if army.knights <= 0:
                        army.delete()
                        
                armies = battle.armies
                if not battle.determine_winner(armies):
                    for army in armies:
                        if army.morale == 0:
                            army.retreat()
                            army.save()

                battle.determine_winner(armies)
        
        print('Start update person')
        for person in Person.objects.select_related(2):
            if not person.male and not person.pregnant and person.spouse and person.location==person.spouse.location:
                if bool_random(person.fertility*person.spouce.fertility*0.1):
                    male = bool_random(0.5)
                    if male:
                        list_name = person.location.culture.male_name
                    else:
                        list_name = person.location.culture.female_name
                    name = random.choice(list_name)
                    self.new_person(name, male, date, person.player, player.location, player.spouse, player)

    
    def a_star(self, current, end):
        if current == end:
            return []
        open_list = set()
        closed_list = set()
        start = current

        def retrace_path(c):
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
                return retrace_path(current)
            open_list.remove(current)
            closed_list.add(current)
            for adja in current.adjacency:
                if adja.land.walkable > 0 and adja not in closed_list:
                    temp_g = current.g + current.size/(2*current.land.walkable) + adja.size/(2*current.land.walkable)
                    if adja not in open_list:
                        open_list.add(adja)
                        adja.parent = current
                        adja.g = temp_g
                        adja.f = adja.g + (abs(end.army_x-adja.army_x)+abs(end.army_y-adja.army_y))/100
                    else:
                        if temp_g < adja.g :
                            adja.parent = current
                            adja.g = temp_g
                            adja.f = adja.g + (abs(end.army_x-adja.army_x)+abs(end.army_y-adja.army_y))/100
        return []

    def get_instances(self, instance, pro_tab, i_pro_tab, response):
        try:
            ins = getattr(instance, pro_tab[i_pro_tab])
        except AttributeError:
            #response.append('AttributeError')
            return

        if isinstance(ins, QuerySet) or isinstance(ins, list):
            for i in ins:
                if i_pro_tab + 1 < len(pro_tab):
                    return self.get_instances(i, pro_tab, i_pro_tab + 1, response)
                else:
                    response.append(i)
        else:
            if i_pro_tab + 1 < len(pro_tab):
                return self.get_instances(ins, pro_tab, i_pro_tab + 1, response)
            else:
                response.append(ins)

    def get_in_model(self, type, player, cls, atts, idd):
        if type == 'get':
            response = {}
            for att in atts:
                response[att] = []
                att_tab = att.split('.')
                try:
                    #instance = self.get_cls(cls).objects.filter(pk=idd).first()
                    instance = self.model[cls].objects.filter(pk=idd).first()
                    self.get_instances(instance, att_tab, 0, response[att])

                    '''for p in pro_tab:
                        instance = getattr(instance, p)
                    response[pro] = instance'''

                except AttributeError:
                    break
            return response
            
        elif type == 'get_all':
            if (idd == 'all'):
                #qset = self.get_cls(cls).objects
                qset = self.model[cls].objects

            att_no_join = []
            att_join = []
            for att in atts:
                if att.count('.'):
                    att_join.append(att)
                else:
                    att_no_join.append(att)

            result_non_join = []
            result_join = []
            if att_no_join:
                result_non_join = self.list_qset_atts(qset, att_no_join)
            if att_join:
                result_join = self.list_qset_atts_2(qset, att_join)

            #print(result_join)
            return result_non_join + result_join
       
    def list_list_att(self, lis, att):
        result = []
        for l in lis:
            result.append(getattr(l, att))
        return result
    
    def list_qset_atts(self, qset, atts):
        af = {}
        pj = {}

        for att in atts:
            af[att] = '$' + att
            pj[att] = True

        pipeline = [
            {
                '$addFields':
                    af
            },

            {
                '$project':
                    pj
            }
        ]

        #t0 = time.perf_counter()
        res = list(qset.aggregate(*pipeline))
        #t1 = time.perf_counter()
        #print (t1-t0)
        return res

    def list_qset_atts_2(self, qset, atts):
        #t0 = time.perf_counter()
        if not qset:
            return []
        af = {}
        pj = {}
        pipeline = []
        for att in atts:
            attributs = att.split('.')
            final_property = attributs.pop()
            cls = []
            q = qset[0]._cls.lower()
            
            for a in attributs:
                q = getattr(self.model[q], a).document_type._class_name.lower()
                cls.append(q)

            c = ''
            for index, a in enumerate(attributs):
                if c:
                    c = c + '.' + a
                else:
                    c = a
                pipeline.append(
                    {
                        '$lookup':
                        {
                            'from': cls[index],
                            'localField': c,
                            'foreignField': '_id',
                            'as': c
                        }
                    }                
                )
                pipeline.append(
                    {
                        '$unwind': '$'+ c
                    }
                )

            af[att] = '$' + c + '.' + final_property
            pj[att] = True
        

        pipeline.append(
            {
                '$addFields': af
            }
        )
        pipeline.append(
            {
                '$project':  pj
            }
        )
        #print (pipeline)

        res = list(qset.aggregate(*pipeline))
        #t1 = time.perf_counter()
        #print (t1-t0)
        return res

    def get_player_person_title(self, player, opts):
        response = {}
        try:
            player = Player.objects.get(pk=player)
        except:
            return {}
        
        if opts['type'] == 'leader':
            person = player.leader
            response['treasure'] = person.treasure
            player2 = player
        
        elif opts['type'] == 'home_province':
            try:
                province = Province.objects.get(pk=opts['province']).select_related(3)
            except:
                return {}
            if player != province.domain_of.holder.player:
                return {}
            response['treasure'] = person.treasure
            person = province.domain_of.holder
            player2 = player
            
        elif opts['type'] == 'province':
            try:
                province = Province.objects.get(pk=opts['province']).select_related(3)
            except:
                return {}
            person = province.domain_of.holder
            player2 = person.player

        elif opts['type'] == 'person':
            try:
                person = Person.objects.get(pk=opts['person'])
            except:
                return {}
            response['treasure'] = person.treasure
            player2 = person.player
        else:
            return {}

        response['name'] = person.name
        titles = Title.objects.filter(holder=person)
        level = 0
        title = None
        for t in titles:
            if t.level > level:
                title = t
                level = t.level
        
        response['title'] = title.name
        response['level'] = title.level
        response['number'] = title.name_number[person.name]
        response['id'] = person.id
        response['shape'] = player2.shape
        response['division'] = player2.division
        response['tinctures'] = player2.tinctures

        return response
