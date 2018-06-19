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
from bson import ObjectId
from pymongo import MongoClient


class Model():
    """Here is the model of the game"""
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
            db.command('aggregate', 'province_vo', pipeline=[{'$match':{}}, {'$out': "province"}], allowDiskUse=True, cursor={})
            if preset:
                Matthieu = self.new_player('Matthieu', division='fess', tinctures=['green', 'orange'])
                Pierre = self.new_player('Pierre', division='pale', tinctures=['blue', 'red'])
                Robert = self.new_person('Robert', True, datetime.date(975, 1, 1), Matthieu, 1)
                Jean = self.new_person('Jean', True, datetime.date(981, 1, 1), Pierre, 14)
                Philippe = self.new_person('Philippe', True, datetime.date(965, 1, 1), Pierre, 39)
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
            War.new(aggressor, defender)
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
            Army.new(province)
            return 'done'
        return self.end_order(status)

    def move_troops(self, player, army, to_province, status):
        if army.for_the.player != player:
            return 'hidden'
        way = army.location.a_star(to_province)
        if not way:
            return 'disabled'
        if status == 'execute':
            army.move(way)
            return 'done'
        return self.end_order(status)
        #return self.list_list_att(way, 'id_map')

    def new_person(self, name, male, born, player, location, father=None, mother=None):
        return Person.new(name=name, male=male, born=born, player=player, location=location, father=father, mother=mother)

    def new_player(self, name, leader=None, shape='triangle', division='plain', tinctures=['blue', 'red']):
        return Player.new(name=name, leader=leader, shape=shape, division=division, tinctures=tinctures)

    def update(self, date):
        for player, orders in self.orders.items():
            if orders:
                order = orders.pop()
                self.make_orders(player, order[0][0], order[0][1], order[1], 'execute')
        print("Start update army")
        for army in Army.objects.select_related(3):
            army.update(date)

        print("Start update province")
        for province in Province.objects.select_related(3):
            province.update(date)

        print("Start update battle")
        for battle in Battle.objects.select_related(3):
            battle.update(date)
        
        print('Start update person')
        for person in Person.objects.select_related(2):
            person.update(date)

    def post_in_model(self, prop, typerq, player, msg, opt, idd):
        response = {}
        if player in self.orders and self.orders[player] and (msg, idd) in self.orders[player][0]:
            if typerq == 'get_status':
                response[prop] = 'accepted'
            else:
                response[prop] = 'rejected'
        else:
            if typerq == 'get_status':
                response[prop] = self.make_orders(player, msg, idd, opt, 'test')
            else:
                response[prop] = self.make_orders(player, msg, idd, opt, 'order')
        return response

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

        if result == 'accepted' and status == 'order':
            if player not in self.orders:
                self.orders[player] = []
            self.orders[player].append(((msg, idd), opt))

        return result

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

    def get_in_model(self, typerq, player, cls, atts, idd):
        if typerq == 'get':
            response = {}
            for att in atts:
                response[att] = []
                att_tab = att.split('.')
                try:
                    instance = self.model[cls].objects.filter(pk=idd).first()
                    self.get_instances(instance, att_tab, 0, response[att])

                    '''for p in pro_tab:
                        instance = getattr(instance, p)
                    response[pro] = instance'''

                except AttributeError:
                    break
            return response

        elif typerq == 'get_all':
            if idd == 'all':
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
