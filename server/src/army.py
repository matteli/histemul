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

from mongoengine import Document, ReferenceField, IntField, ListField, BooleanField, StringField
from battle import Battle

#TODO: make origin the pk


class Army(Document):

    for_the = ReferenceField('Person')
    battle = ReferenceField('Battle')
    attitude = StringField()
    location = ReferenceField('Province')
    origin = ReferenceField('Province')
    way = ListField(ReferenceField('Province'))
    next_province = ReferenceField('Province')
    knights = IntField()
    morale = IntField()
    time_walking = IntField()

    @classmethod
    def new(cls, province):
        army = cls.objects.create(for_the=province.domain_of.holder, attitude='normal', location=province, origin=province, knights = province.manpower, morale=100, time_walking=0)
        province.manpower = 0
        province.save()
        return army

    def move(self, way):
        self.way = way
        self.save()
        return

    def dismiss(self):
        self.origin.manpower += self.knights
        self.origin.save()
        #army.knights = 0
        #army.save()
        self.delete()
        return

    def stop(self):
        self.next_province = None
        self.time_walking = 0
        self.way = []
        #self.save()
        return

    def retreat(self):
        province = self.location.get_random_walkable_adjacent()
        if province:
            self.battle = None
            self.attitude = 'retreat'
            self.next_province = province
            self.way.append(province)
            self.time_walking = 0
            #self.save()
            return True
        else:
            return False
    
    def update(self, date):
        if self.way and self.next_province != self.way[-1]: #change way since last update
            self.next_province = self.way[-1]
            self.time_walking = 0

        if self.time_walking >= self.location.size: #enter a new province
            self.time_walking -= self.location.size
            province = self.next_province
            self.location = province
            self.way.pop()
            if self.way:
                self.next_province = self.way[-1]
            else:
                self.next_province = None
                self.attitude = 'normal'

            #when enter a new province, look if there is enemy or already a battle
            person = self.for_the
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
                    self.stop()
                    Battle.new(war, province, [self], enemies)

            else:
                war = battle.war
                if person in war.aggressors:
                    self.stop()
                    battle.add_aggressor(self)
                if person in war.defenders:
                    self.stop()
                    battle.add_defender(self)

        if self.next_province:
            self.time_walking += 500 * self.location.land.walkable
        else:
            self.time_walking = 0

        #morale
        if self.attitude == 'normal':
            if self.morale < 95:
                self.morale += 5
            else:
                self.morale = 100
        
        self.save()
