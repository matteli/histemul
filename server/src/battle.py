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
from army import Army
from functions import *


class Battle(Document):

    war = ReferenceField('War')
    location = ReferenceField('Province')
    active = BooleanField()

    @property
    def aggressors(self):
        #from army import Army
        return Army.objects(Q(battle=self) & Q(attitude='aggressor'))

    @property
    def defenders(self):
        #from army import Army
        return Army.objects(Q(battle=self) & Q(attitude='defender'))

    def add_aggressor(self, army):
        army.battle = self
        army.attitude = 'aggressor'

    def add_defender(self, army):
        army.battle = self
        army.attitude = 'defender'

    def remove_army(self, army):
        army.battle = None
        army.attitude = 'normal'

    def end(self):
        self.active = False
        for army in merge_qsets(self.defenders, self.aggressors):
            self.remove_army(army)
