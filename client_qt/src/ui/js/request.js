var cache = {};
var http2 = []
var i=0;

function serialize (obj) {
  var str = [];
  for(var p in obj)
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}

function getUpdate(clsLocal, propLocal, num){
    var http_params = serialize({'type': 'get_update', 'player': player, 'num': num});
    function callBack(clsLocal, propLocal)
    {
        return function() {
            if(http3.readyState == 4 && http3.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http3.responseText);
                clsLocal[propLocal] = res['res'];
            }
        }
    }

    var http3 = new XMLHttpRequest();
    http3.open("POST", url, true);
    http3.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http3.onreadystatechange = callBack(clsLocal, propLocal);
    console.log("getUpdate")
    http3.send(http_params);

    //send(clsLocal, propLocal, http_params);
    /*var m = new XHR(clsLocal, propLocal, http_params)
    m.send()*/
}

function postMsg(clsLocal, propLocal, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : ';';
    var http_params = serialize({'type': 'post_msg', 'player': player, 'msg': msg, 'id': idd, 'opt': option});
    send(clsLocal, propLocal, http_params);
    console.log("post " + msg)
    /*var m = new XHR(clsLocal, propLocal, http_params)
    m.send()*/

}

function getStatus(clsLocal, propLocal, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : ';';
    var http_params = serialize({'type': 'get_status', 'player': player, 'msg': msg, 'id': idd, 'opt': option});
    send(clsLocal, propLocal, http_params);
    /*var m = new XHR(clsLocal, propLocal, http_params)
    m.send()*/

}

function getTimeRemaining(clsLocal, propLocal)
{
    var http_params = serialize({'type': 'get_time_remaining', 'player': player});
    //send(clsLocal, propLocal, http_params);
    var m = new XHR(clsLocal, propLocal, http_params)
    m.send()

}

function XHR(clsLocal, propLocal, http_params)
{
    this.__http = new XMLHttpRequest();
    this.__clsLocal = clsLocal;
    this.__propLocal = propLocal;
    this.__http_params = http_params;
}

XHR.prototype = {
    __cBack: function()
    {
        return function() {
            if(this.__http.readyState == 4 && this.__http.status == 200) {
                var res = JSON.parse(this.__http.responseText);
                this.__clsLocal[this.__propLocal] = res['res'];
            }
        }
    },

    send: function()
    {
        function cBack()
        {
            return function() {
                if(this.__http.readyState == 4 && this.__http.status == 200) {
                    var res = JSON.parse(this.__http.responseText);
                    this.__clsLocal[this.__propLocal] = res['res'];
                }
            }
        }
        this.__http.open("POST", url, true);
        this.__http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        /*http.onreadystatechange = function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                clsLocal[propLocal] = res['res'];
            }
        }*/
        this.__http.onreadystatechange = cBack();
        this.__http.send(this.__http_params);
    }
}


function send(clsLocal, propLocal, http_params)
{
    function callBack(i, clsLocal, propLocal)
    {
        return function() {
            if(http2[i].readyState == 4 && http2[i].status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http2[i].responseText);
                clsLocal[propLocal] = res['res'];
            }
        }
    }

    http2[i] = new XMLHttpRequest();
    http2[i].open("POST", url, true);
    http2[i].setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http2[i].onreadystatechange = callBack(i, clsLocal, propLocal);
    http2[i].send(http_params);
    i = i+1;
}

function get(clsLocal, propLocal, cls, id, atts, tab, cache)
{

    if (cache && (cls in cache) && (id in  cache[cls]) && (prop in cache[cls][id])) {
        console.info('in cache');
        clsLocal[propLocal] = cache[cls][id][atts];
    }
    else {
        var http_params = serialize({'type': 'get', 'player': player, 'cls': cls, 'id': id, 'atts': atts});
        var http = new XMLHttpRequest();
        //console.info("dd");
        http.open("POST", url, true);
        http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        http.onreadystatechange = function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                if (tab)
                    clsLocal[propLocal] = res[atts];
                else
                    if (res[atts][0])
                        clsLocal[propLocal] = res[atts][0];
                    else
                        clsLocal[propLocal] = 'Undefined';

                if (cache)
                {
                    if (!(cls in cache)) cache[cls] = {};
                    if (!(id in cache[cls])) cache[cls][id] = {};
                    cache[cls][id][atts] = clsLocal[propLocal];
                }

            }
        }
        http.send(http_params);
    }
}

function getAll(clsLocal, cls, atts, iden)
{

    /*if ((cls in cache) && (id in  cache[cls]) && (prop in cache[cls][id])) {
        console.info('in cache');
        idLocal[propLocal] = cache[cls][id][prop];
    }
    else {*/
        var http_params = serialize({'type': 'get_all', 'player': player, 'cls': cls, 'id': -1, 'atts': atts});
        var http = new XMLHttpRequest();
        //console.info(url);
        http.open("POST", url, true);
        http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        http.onreadystatechange = function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                var ps = atts.split(";");
                for (var r in res) {
                    var idd;
                    if (typeof res[r]['_id'] == 'object')
                        idd = res[r]['_id']['$oid'];
                    else
                        idd = res[r]['_id'];
                    delete res[r]['_id'];
                    if (!(idd in clsLocal)) clsLocal[idd] = {};
                    //for (var p in ps)
                        //clsLocal[idd][ps[p]] = res[r][ps[p]];
                    for (var att in res[r])
                    {
                        clsLocal[idd][att] = res[r][att];
                    }

                    //clsLocal[idd] = res[r];
                }
                map.filesReceived(iden);
                //console.info(clsLocal);

                /*if (!(cls in cache)) cache[cls] = {};
                if (!(id in cache[cls])) cache[cls][id] = {};
                cache[cls][id][prop] = res["val"];*/
            }
        }
        http.send(http_params);
        console.log("getall " + cls)
    //});
    //}
}

