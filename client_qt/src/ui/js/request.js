var cache = {};

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
    send(clsLocal, propLocal, http_params);
}

function postMsg(clsLocal, propLocal, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : ';';
    var http_params = serialize({'type': 'post_msg', 'player': player, 'msg': msg, 'id': idd, 'opt': option});
    send(clsLocal, propLocal, http_params);
    console.log("post " + msg)

}

function getStatus(clsLocal, propLocal, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : ';';
    var http_params = serialize({'type': 'get_status', 'player': player, 'msg': msg, 'id': idd, 'opt': option});
    send(clsLocal, propLocal, http_params);

}

function getTimeRemaining(clsLocal, propLocal)
{
    var http_params = serialize({'type': 'get_time_remaining', 'player': player});
    send(clsLocal, propLocal, http_params);
}

function send(clsLocal, propLocal, http_params)
{
    function callBack(clsLocal, propLocal)
    {
        return function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                clsLocal[propLocal] = res['res'];
            }
        }
    }

    var http = new XMLHttpRequest();
    http.open("POST", url, true);
    http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    http.onreadystatechange = callBack(clsLocal, propLocal);
    http.send(http_params);
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

function getAll(clsLocal, cls, atts, id, iden)
{

    /*if ((cls in cache) && (id in  cache[cls]) && (prop in cache[cls][id])) {
        console.info('in cache');
        idLocal[propLocal] = cache[cls][id][prop];
    }
    else {*/
        var http_params = serialize({'type': 'get_all', 'player': player, 'cls': cls, 'id': id, 'atts': atts});
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

