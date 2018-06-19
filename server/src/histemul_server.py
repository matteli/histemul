#!/usr/bin/python3
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

import datetime
from flask import Flask, request, Response
from bson.objectid import ObjectId
from engine import Engine

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError


class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def jsonify(*args):
    """ jsonify with support for MongoDB ObjectId
    """
    return Response(json.dumps(*args, cls=MongoJsonEncoder), mimetype='application/json')

app = Flask(__name__)
engine = Engine(True, True)
#engine = Engine()
engine.start()

@app.route('/', methods=['GET', 'POST'])
def requesting():
    """
        request from client arrive here.
    """
    if request.method == 'POST':
        if request.is_json:
            requestjs = request.get_json()
            player = requestjs['player']
            typerq = requestjs['type']
        print(requestjs)

        if typerq == 'get' or typerq == 'get_all':
            cls = requestjs['cls']
            atts = requestjs['atts']
            idd = requestjs['id']
            return jsonify(engine.model.get_in_model(typerq, player, cls, atts, idd))

        elif typerq == 'get_status' or typerq == 'post_msg':
            response = {}
            prop = requestjs['prop']
            if not engine.update_flag_global.is_set():
                if typerq == 'get_status':
                    response[prop] = 'disabled'
                else:
                    response[prop] = 'rejected'

            msg = requestjs['msg']
            opt = requestjs['opt']
            print(opt)
            idd = requestjs['id']
            '''if player in engine.model.orders and engine.model.orders[player] and (msg, idd) in engine.model.orders[player][0]:
                if type == 'get_status':
                    response[prop] = 'accepted'
                else:
                    response[prop] = 'rejected'
            else:
                if type == 'get_status':
                    result = engine.model.make_orders(player, msg, idd, opt, 'test')
                else:
                    result = engine.model.make_orders(player, msg, idd, opt, 'order')
                response[prop] = result'''
            return jsonify(engine.model.post_in_model(prop, typerq, player, msg, opt, idd))

        elif typerq == 'get_update':
            response = {}
            prop = requestjs['prop']
            num = requestjs['num']
            if num == 0:
                engine.update_flag_global.wait()
            else:
                engine.update_flag_tick[num%2].wait()

            response[prop] = engine.tick
            return jsonify(response)

        elif typerq == 'get_in_function':
            response = {}
            func = requestjs['func']
            opts = requestjs['opts']
            if func == 'player_person_title':
                response = engine.model.get_player_person_title(player, opts)
            return jsonify(response)

    return jsonify({})
