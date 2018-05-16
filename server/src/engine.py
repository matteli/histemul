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
from model2 import Model
import threading
import time
import datetime


class Engine(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        random.seed()
        self.terminated = False
        self.model = Model()
        self.speed = 20.0 #update rate in seconds
        self.update_flag_tick = [threading.Event(), threading.Event()]
        self.update_flag_global = threading.Event()
        self.tick = 1
        self.time0 = time.time()
        self.update_flag_global.set()
        self.update_flag_tick[1].set()
        self.date = datetime.date(1000,1,1)
        self.day = datetime.timedelta(days=1)

    def run(self):
        print('Engine started.')
        while not self.terminated:
            #update rate
            if (time.time() - self.time0) < self.speed:
                time.sleep(self.speed - (time.time() - self.time0))
            print("Start Update")
            self.time0 = time.time()
            #Update clock
            #Update model
            if self.tick%2:
                self.update_flag_tick[1].clear()
            else:
                self.update_flag_tick[0].clear()
            
            self.update_flag_global.clear()

            self.model.update(self.date)
            self.tick += 1
            self.date += self.day
            print("Finish Update")
            self.update_flag_global.set()
            if self.tick%2:
                self.update_flag_tick[1].set()
            else:
                self.update_flag_tick[0].set()