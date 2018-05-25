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
from army import Army


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
    def battle(self):
        #from battle import Battle
        return Battle.objects(location=self).first()

    @property
    def armies(self, select_related=1):
        #from army import Army
        return Army.objects(location=self).select_related(select_related)

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
                    print (province.idd)
                    return province
                else:
                    i += 1