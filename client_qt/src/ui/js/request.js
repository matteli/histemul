var cache = {};

function serialize (obj) {
  var str = [];
  for(var p in obj)
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  return str.join("&");
}

function getUpdate(item, prop, num){
    //var http_params = serialize({'type': 'get_update', 'player': player, 'prop': prop, 'num': num});
    var http_params = JSON.stringify({'type': 'get_update', 'player': player, 'prop': prop, 'num': num});
    send(item, prop, http_params);
}

function postMsg(item, prop, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : ';';
    //var http_params = serialize({'type': 'post_msg', 'player': player, 'prop': prop, 'msg': msg, 'id': idd, 'opt': option});
    var http_params = JSON.stringify({'type': 'post_msg', 'player': player, 'prop': prop, 'msg': msg, 'id': idd, 'opt': option});
    send(item, prop, http_params);
    console.log("post " + msg)

}

function getStatus(item, prop, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : ';';
    //var http_params = serialize({'type': 'get_status', 'player': player, 'prop': prop, 'msg': msg, 'id': idd, 'opt': option});
    var http_params = JSON.stringify({'type': 'get_status', 'player': player, 'prop': prop, 'msg': msg, 'id': idd, 'opt': option});
    send(item, prop, http_params);
}

function getTimeRemaining(item, prop)
{
    var http_params = serialize({'type': 'get_time_remaining', 'player': player});
    send(item, prop, http_params);
}

function send(item, props, http_params)
{
    function callBack(item, props)
    {
        return function() {
            if(http.readyState == 4 && http.status == 200) {
                console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                var prop = props.split(';');
                for (var p in prop)
                {
                    item[prop[p]] = res[prop[p]];
                }
            }
        }
    }

    var http = new XMLHttpRequest();
    http.open("POST", url, true);
    http.setRequestHeader("Content-Type", "application/json");
    http.onreadystatechange = callBack(item, props);
    http.send(http_params);
}

function getInFunction(item, props, func, arg)
{
    //var http_params = serialize({'type': 'get_in_function', 'player': player, 'props': props, 'func': func, 'arg': arg});
    var http_params = JSON.stringify({'type': 'get_in_function', 'player': player, 'props': props, 'func': func, 'arg': arg});
    send(item, props, http_params);
}

function get(item, props, cls, id, atts, tabs, cache)
{

    /*if (cache && (cls in cache) && (id in  cache[cls]) && (props in cache[cls][id])) {
        console.info('in cache');
        item[props] = cache[cls][id][atts];
    }
    else {*/
        var http_params = serialize({'type': 'get', 'player': player, 'cls': cls, 'id': id, 'atts': atts});
        var http = new XMLHttpRequest();
        //console.info("dd");
        http.open("POST", url, true);
        http.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        http.onreadystatechange = function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var prop = props.split(';');
                var att = atts.split(';');
                if (tabs)
                    var tab = tabs.split(';');
                var res = JSON.parse(http.responseText);
                for (var i in att)
                {
                    var tab_bool = false;
                    for (var j in tab)
                    {
                        if (tab[j] == att[i])
                        {
                            item[prop[i]] = res[att[i]];
                            tab_bool = true;
                            break;
                        }
                    }
                    if (!tab_bool)
                    {
                        if (res[att[i]][0])
                            item[prop[i]] = res[att[i]][0];
                        else
                            item[prop[i]] = 'Undefined';
                    }
                }

                /*if (tab)
                    item[props] = res[atts];
                else
                    if (res[atts][0])
                        item[props] = res[atts][0];
                    else
                        item[props] = 'Undefined';

                if (cache)
                {
                    if (!(cls in cache)) cache[cls] = {};
                    if (!(id in cache[cls])) cache[cls][id] = {};
                    cache[cls][id][atts] = item[props];
                }*/

            }
        }
        http.send(http_params);
    //}
}

function getAll(item, cls, atts, id, iden)
{

    /*if ((cls in cache) && (id in  cache[cls]) && (prop in cache[cls][id])) {
        console.info('in cache');
        idLocal[prop] = cache[cls][id][prop];
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
                    if (!(idd in item)) item[idd] = {};
                    //for (var p in ps)
                        //item[idd][ps[p]] = res[r][ps[p]];
                    for (var att in res[r])
                    {
                        item[idd][att] = res[r][att];
                    }

                    //item[idd] = res[r];
                }
                map.filesReceived(iden);
                //console.info(item);

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

