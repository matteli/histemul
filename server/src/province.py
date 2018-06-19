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

import random
from mongoengine import Document, StringField, IntField, BooleanField, ReferenceField, ListField
from mongoengine.queryset.visitor import Q
from culture import Culture
from land import Land
from person import Person
from title import Title
from war import War
from battle import Battle


class Province(Document):

    name = StringField()
    id_map = IntField(primary_key=True)
    active = BooleanField()
    domain_of = ReferenceField('Title')
    land = ReferenceField('Land')
    city_x = IntField()
    city_y = IntField()
    army_x = IntField()
    army_y = IntField()
    culture = ReferenceField('Culture')
    adjacency = ListField(ReferenceField('self'), default=list)
    #river = ListField(IntField())
    sea_adjacency = ReferenceField('self')
    manpower = IntField(default=0)
    population = IntField(default=0)
    size = IntField(default=1000)
    controller = ReferenceField('Person')
    war_siege = ReferenceField('War')
    battle = ReferenceField('Battle')
    defence = IntField(default=0)
    siege = IntField(default=0)
    morale = IntField(default=100)
    f = IntField(default=0)
    g = IntField(default=0)

    @property
    def inhabitants(self):
        #from person import Person
        return Person.objects(location=self)

    @property
    def armies(self, armies=None, select_related=1):
        if not armies:
            from army import Army
            return Army.objects(location=self).select_related(select_related)
        return armies.filter(location=self)

    @property
    def army(self):
        #from army import Army
        return Army.objects(origin=self).first()

    def get_random_walkable_adjacent(self):
        nb_walkable = 0
        for province in self.adjacency:
            if province.land.is_walkable():
                nb_walkable += 1
        r = random.randrange(nb_walkable)
        i = 0
        for province in self.adjacency:
            if province.land.is_walkable():
                if i == r:
                    return province
                else:
                    i += 1

    def a_star(self, end):
        if self == end:
            return []
        open_list = set()
        closed_list = set()
        start = self

        def retrace_path(c):
            path = []
            path.append(c)
            while c.parent is not start:
                c = c.parent
                path.append(c)
            return path
        open_list.add(self)
        while open_list:
            self = sorted(open_list, key=lambda inst:inst.f)[0]
            if self == end:
                return retrace_path(self)
            open_list.remove(self)
            closed_list.add(self)
            for adja in self.adjacency:
                if adja.land.walkable > 0 and adja not in closed_list:
                    temp_g = self.g + self.size/(2*self.land.walkable) + adja.size/(2*self.land.walkable)
                    if adja not in open_list:
                        open_list.add(adja)
                        adja.parent = self
                        adja.g = temp_g
                        adja.f = adja.g + (abs(end.army_x-adja.army_x)+abs(end.army_y-adja.army_y))/100
                    else:
                        if temp_g < adja.g :
                            adja.parent = self
                            adja.g = temp_g
                            adja.f = adja.g + (abs(end.army_x-adja.army_x)+abs(end.army_y-adja.army_y))/100
        return []

    def update(self, date):
        if self.domain_of and self.domain_of.holder:
            self.domain_of.holder.treasure += 10
            self.domain_of.holder.save()

        province_war_siege_knights = 0            
        if self.battle and self.battle.active:
            self.war_siege = None
        elif self.controller:
            if self.war_siege:
                war = self.war_siege
                for enemy in war.get_enemies(self.controller):
                    for army in self.armies:
                        if army.for_the == enemy:
                            province_war_siege_knights += army.knights
                if province_war_siege_knights == 0:
                    self.war_siege = None
                    self.siege = 0
            else:
                for war in self.controller.wars:
                    for enemy_country in war.get_enemies(self.controller):
                        for army in self.armies:
                            if army.for_the == enemy_country and army.attitude == 'normal':
                                province_war_siege_knights += army.knights
                                self.war_siege = war
                                self.siege = 1
        else:
            self.war_siege = None
            self.siege = 0

        if self.land.is_walkable():
            war = self.war_siege
            if war:
                dice = int(((random.randrange(10) + 1)**2) / 4)
                if dice >= self.morale:
                    self.controller = war.get_enemies(self.controller)[0]
                    self.war_siege = None
                    self.siege = 0
                    self.morale = 100
                else:
                    self.morale -= int(dice)
            else:
                if self.morale < 100:
                    if self.morale < 90:
                        self.morale += 10
                    else:
                        self.morale = 100

        self.save()
