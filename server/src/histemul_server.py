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

from engine import Engine
from flask import Flask, request

try:
    import simplejson as json
except ImportError:
    try:
        import json
    except ImportError:
        raise ImportError
import datetime
from bson.objectid import ObjectId
from flask import Response

class MongoJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

def jsonify(*args, **kwargs):
    """ jsonify with support for MongoDB ObjectId
    """
    print (*args)
    print (**kwargs)
    return Response(json.dumps(*args, cls=MongoJsonEncoder), mimetype='application/json')

app = Flask(__name__)


engine = Engine()
engine.start()

@app.route('/', methods=['GET', 'POST'])
def requesting():
    if request.method == 'POST':
        player = request.form['player']
        type = request.form['type']

        if type == 'get' or type == 'get_all':
            cls = request.form['cls']
            atts = request.form['atts'].split(';')
            idd = request.form['id']

            try:
                idd = int(idd)
            except:
                pass
            return jsonify(engine.model.get_in_model(cls, atts, idd))

        elif type == 'get_status' or type == 'post_msg':
            response = {}
            if not engine.update_flag_global.is_set():
                if type == 'get_status':
                    response['res'] = 'disabled'
                else:
                    response['res'] = 'rejected'

            msg = request.form['msg']
            try:
                idd = [int(i) for i in (request.form['id'].split(';'))]
            except ValueError:
                idd = request.form['id'].split(';')
            opt = request.form['opt'].split(';')
            for i in idd:
                if player in engine.model.orders and engine.model.orders[player] and (msg, i) in engine.model.orders[player][0]:
                    if type == 'get_status':
                        response['res'] = 'accepted'
                    else:
                        response['res'] = 'rejected'
                else:
                    if type == 'get_status':
                        result = engine.model.make_orders(player, msg, i, opt, 'test')
                    else:
                        result = engine.model.make_orders(player, msg, i, opt, 'order')
                    response['res'] = result
            return jsonify(response)

        elif type == 'get_update':
            response = {}
            num = int(request.form['num'])
            if num == 0:
                engine.update_flag_global.wait()
            else:
                engine.update_flag_tick[num%2].wait()

            response['res'] = engine.tick
            return jsonify(response)
