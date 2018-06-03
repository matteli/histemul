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

    def stop(self):
        self.next_province = None
        self.time_walking = 0
        self.way = []
        self.save()

    def retreat(self):
        province = self.location.get_random_walkable_adjacent()
        if province:
          self.battle = None
          self.attitude = 'retreat'
          self.next_province = province
          self.way.append(province)
          self.time_walking = 0
          self.save()
          return True
        else:
          return False