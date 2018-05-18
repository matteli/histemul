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
from armory import Armory
from mongoengine import connect, QuerySet
import random


class Model():
    def __init__(self):
        connect('histemul')
        self.orders = {}

    def end_order(self, status):
        if status == 'order':
            return 'accepted'
        return 'normal'
        
    def declare_war(self, aggressor, defender, status):
        if aggressor == defender:
            return 'hidden'
        if set(aggressor.wars_aggressor).intersection(defender.wars_defender):
            return 'disabled'
        if set(aggressor.wars_defender).intersection(defender.wars_aggressor):
            return 'disabled'
        if status == 'execute':
            War.objects.create(aggressors=[aggressor], defenders=[defender], active=True)
            return 'done'
        return self.end_order(status)
        
    def propose_peace(self, aggressor, defender, opt, status):
        if aggressor == defender:
            return 'hidden'
        if not set(aggressor.wars_aggressor).intersection(defender.wars_defender) and not set(aggressor.wars_defender).intersection(defender.wars_aggressor):
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

    def new_battle(self, war, location, aggressors, defenders):
        battle = Battle.objects.create(war=war, location=location, active=True)
        for aggressor in aggressors:
            aggressor.battle = battle
        for defender in defenders:
            defender.battle = battle
        return battle
    
    def merge_qsets(self, *args):
        qset = []
        for a in args:
            if a:
                try:
                    qset += a
                except:
                    qset = a
        return qset

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
        print("Start Update Army")
        #army
        for army in Army.objects:
            if army.knights:
                if army.way and army.next_province != army.way[-1]:
                    army.next_province = army.way[-1]
                    army.time_walking = 0

                if army.time_walking >= army.location.size: #enter a new province
                    province = army.next_province
                    army.location = province
                    army.way.pop()
                    if army.way:
                        army.next_province = army.way[-1]
                    else:
                        army.next_province = None
                    army.time_walking -= army.location.size
                    #when enter a new province, look if there is enemy or already a battle
                    person = army.for_the
                    if not province.battle:
                        enemy = []
                        for war in self.merge_qsets(person.wars_aggressor, person.wars_defender):
                            for enemy_person in war.get_enemies(person):
                                for other_army in province.armies:
                                    if enemy_person == other_army.for_the:
                                        enemy.append(other_army)
                            if enemy: #enemy so battle
                                self.new_battle(war, province, [army], enemy)
                                army.stop()
                                break

                    else:
                        war = province.battle.war
                        person_defender = province.battle.defenders[0].for_the
                        if person_defender in war.get_allies(person): #allies
                            province.battle.add_defender(army)
                            army.stop()
                        elif person_defender in war.get_enemies(person): #enemy
                            province.battle.add_aggressor(army)
                            army.stop()

                    

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

        print("Start Update Province")
        for province in Province.objects.select_related(3):
            province_war_siege_knights = 0            
            if province.armies:
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
                        for war in self.merge_qsets(province.controller.wars_aggressor, province.controller.wars_defender):
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

        print("Start Update Battle")
        for battle in Battle.objects:
            if battle.active:
                battle_dice_defenders = ((random.randrange(10) + 1)**2) / 4
                battle_dice_aggressors = ((random.randrange(10) + 1)**2) / 4

                nb_knights_aggressors = 0
                for aggressor in battle.aggressors:
                    nb_knights_aggressors += aggressor.knights

                nb_knights_defenders = 0
                for defender in battle.defenders:
                    nb_knights_defenders += defender.knights


                defenders = battle.defenders
                for army in defenders:
                    army_loose = int(army.knights * nb_knights_aggressors * battle_dice_aggressors / (500 * nb_knights_defenders))
                    if army_loose >= army.knights:
                        nb_knights_defenders -= army.knights
                        army.knights = 0
                    else:
                        army.knights -= army_loose
                        nb_knights_defenders -= army_loose

                        if int(battle_dice_aggressors) >= army.morale:
                            army.morale = 0
                            army.retreat()
                            army.save()
                        else:
                            army.morale -= int(battle_dice_aggressors)

                if nb_knights_defenders <= 0:
                    battle.end()
                    break

                aggressors = battle.aggressors
                for army in aggressors:
                    army_loose = int(army.knights * nb_knights_defenders * battle_dice_defenders / (500 * nb_knights_aggressors))
                    if army_loose >= army.knights:
                        nb_knights_aggressors -= army.knights
                        army.knights = 0
                    else:
                        army.knights -= army_loose
                        nb_knights_aggressors -= army_loose

                        if int(battle_dice_defenders) >= army.morale:
                            army.morale = 0
                            army.retreat()
                            army.save()
                        else:
                            army.morale -= int(battle_dice_defenders)


                if nb_knights_aggressors <= 0:
                    battle.end()
                
                battle.save()
                
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

    def get_cls(self, cls):
        if cls == 'army':
            return Army
        if cls == 'battle':
            return Battle
        if cls == 'culture':
            return Culture
        if cls == 'land':
            return Land
        if cls == 'person':
            return Person
        if cls == 'player':
            return Player
        if cls == 'province':
            return Province
        if cls == 'title':
            return Title
        if cls == 'war':
            return War
        if cls == 'armory':
            return Armory
        return None

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
                    instance = self.get_cls(cls).objects.filter(pk=idd).first()
                    self.get_instances(instance, att_tab, 0, response[att])

                    '''for p in pro_tab:
                        instance = getattr(instance, p)
                    response[pro] = instance'''

                except AttributeError:
                    break
            return response
            
        elif type == 'get_all':
            if (idd == 'all'):
                qset = self.get_cls(cls).objects

            att_no_union = []
            att_union = []
            for att in atts:
                if att.count('.'):
                    att_union.append(att)
                else:
                    att_no_union.append(att)

            result_non_union = []
            result_union = []
            if att_no_union:
                result_non_union = self.list_qset_atts(qset, att_no_union)
            if att_union:
                result_union = self.list_qset_atts_2(qset, att_union)

            print(result_union)
            return result_non_union + result_union
       
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
        #att = atts[0].split('.')

        print(atts)
        attributs = atts[0].split('.')
        final_property = attributs.pop()
        cls = []
        for q in qset:
            ok = True
            for a in attributs:
                q = getattr(q, a)
                if q:
                    cls.append(q._cls.lower())
                else:
                    ok = False
                    break
            if ok: 
                break

        pipeline = []
        b = ''
        for index, a in enumerate(attributs):
            pipeline.append(
                {
                    '$lookup':
                    {
                        'from': cls[index],
                        'localField': b + a,
                        'foreignField': '_id',
                        'as': a
                    }
                }                
            )
            b = a + '.'
            pipeline.append(
                {
                    '$unwind': '$'+a
                }
            )
        pipeline.append(
            {
                '$addFields': 
                {
                    atts[0]: '$'+a+'.'+final_property
                }
            }
        )
        pipeline.append(
            {
                '$project': 
                {
                    atts[0]: True
                }
            }
        )
        print (pipeline)

        #t0 = time.perf_counter()
        res = list(qset.aggregate(*pipeline))
        #t1 = time.perf_counter()
        #print (t1-t0)
        return res

    def get_player_person_title(self, player, opts):
        try:
            player = Player.objects.get(pk=player)
        except:
            return {}
        
        if opts['type'] == 'leader':
            person = player.leader
        elif opts['type'] == 'province':
            try:
                province = Province.objects.get(pk=opts['province']).select_related(3)
            except:
                return {}
            '''if province.domain_of.holder.player != player:
                return {}'''
            person = province.domain_of.holder
        else:
            return {}

        response = {}
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
        return response
