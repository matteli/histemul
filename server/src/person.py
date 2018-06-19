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

from mongoengine import Document, IntField, StringField, DateTimeField, ReferenceField, ListField, BooleanField
from mongoengine.queryset.visitor import Q
from army import Army


class Person(Document):

    name = StringField()
    born = DateTimeField()
    die = DateTimeField()
    father = ReferenceField('self')
    mother = ReferenceField('self')
    male = BooleanField()
    pregnant = BooleanField()
    fertility = BooleanField()
    spouse = ReferenceField('self')
    player = ReferenceField('Player')
    location = ReferenceField('Province')
    treasure = IntField(default=0)

    @property
    def wars(self):
        from war import War
        return War.objects(Q(aggressors=self) | Q(defenders=self))

    @property
    def children(self):
        return Person.objects(Q(father=self) | Q(mother=self))

    @property
    def titles(self):
        from title import Title
        return Title.objects(holder=self)

    @property
    def controlled(self):
        from province import Province
        return Province.objects(controller=self)

    @property
    def armies(self):
        #from army import Army
        return Army.objects(for_the=self)

    @classmethod
    def new(cls, name, male, born, player, location, father=None, mother=None):
        return cls.objects.create(name=name, male=male, born=born, player=player, location=location, father=father, mother=mother)

    def is_married_with(self, spouse):
        if not (self.male==spouse.male):
            self.spouse = spouse
            spouse = self
            return True
        return False

    def in_war_against(self, person):
        for war in self.wars:
            if self in war.aggressors:
                if person in war.defenders:
                    return {'war': war, 'attitude': 'aggressor'}
            if self in war.defenders:
                if person in war.aggressors:
                    return {'war': war, 'attitude': 'defender'}
        return None

    def age(self, date):
        return date.year - self.born.year - ((date.month, date.day) < (self.born.month, self.born.day))

    def dead(self, date):
        if self.spouse:
            self.spouse.spouse = None
            self.spouse.save()
            self.spouse = None
        self.die = date
        self.save()

    def update(self, date):
        if not self.male and not self.pregnant and self.spouse and self.location==self.spouse.location:
            if bool_random(self.fertility*self.spouce.fertility*0.1):
                male = bool_random(0.5)
                if male:
                    list_name = self.location.culture.male_name
                else:
                    list_name = self.location.culture.female_name
                name = random.choice(list_name)
                Person.new(name, male, date, self.player, self.location, self.spouse, self)
