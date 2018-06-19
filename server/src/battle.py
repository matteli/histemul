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

from mongoengine import Document, ReferenceField, BooleanField
from mongoengine.queryset.visitor import Q
from functions import *


class Battle(Document):

    war = ReferenceField('War')
    active = BooleanField()

    @property
    def aggressors(self):
        from army import Army
        return Army.objects(Q(battle=self) & Q(attitude='aggressor'))

    @property
    def defenders(self):
        from army import Army
        return Army.objects(Q(battle=self) & Q(attitude='defender'))

    @property
    def armies(self):
        from army import Army
        return Army.objects(battle=self)

    @property
    def location(self):
        from province import Province
        return Province.objects(location=self).first()

    
    @classmethod
    def new(cls, war, location, aggressors, defenders):
        battle = cls.objects.create(war=war, active=True)
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

    def add_aggressor(self, army):
        army.battle = self
        army.attitude = 'aggressor'
        army.save()

    def add_defender(self, army):
        army.battle = self
        army.attitude = 'defender'
        army.save()

    def remove_army(self, army):
        army.battle = None
        army.attitude = 'normal'
        army.save()
    
    def counting_knights(self, armies = None):
        aggressors = 0
        defenders = 0
        if not armies:
            armies = self.armies
        for army in armies:
            if army.attitude == 'defender':
                defenders += army.knights
            elif army.attitude == 'aggressor':
                aggressors += army.knights
        return {'aggressors': aggressors, 'defenders': defenders}

    def determine_winner(self, armies = None):
        if not armies:
            armies = self.armies
        nb_knights = self.counting_knights(armies)

        if nb_knights['aggressors'] == 0 and nb_knights['defenders'] == 0:
            self.end(winner='tie')
            return True
        elif nb_knights['aggressors'] == 0:
            self.end(winner='defenders')
            return True
        elif nb_knights['defenders'] == 0:
            self.end(winner='aggressors')
            return True
        return False

    def end(self, winner):
        self.active = False
        self.save()
        for army in self.armies:
            self.remove_army(army)
    
    def update(self, date):
        if self.active:
            battle_dice_defenders = ((random.randrange(10) + 1)**2) / 2
            battle_dice_aggressors = ((random.randrange(10) + 1)**2) / 2

            armies = self.armies
            nb_knights = self.counting_knights(armies)

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
                    
            armies = self.armies
            if not self.determine_winner(armies):
                for army in armies:
                    if army.morale == 0:
                        army.retreat()
                        army.save()

            self.determine_winner(armies)

