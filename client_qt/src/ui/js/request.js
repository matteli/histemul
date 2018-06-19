var cache = {};

function getUpdate(item, prop, num){
    var http_params = JSON.stringify({'type': 'get_update', 'player': player, 'prop': prop, 'num': num});
    send(item, prop, http_params);
}

function postMsg(item, prop, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : '{}';
    console.log(option)
    var http_params = JSON.stringify({'type': 'post_msg', 'player': player, 'prop': prop, 'msg': msg, 'id': idd, 'opt': option});
    send(item, prop, http_params);
    console.log("post " + msg)

}

function getStatus(item, prop, msg, idd, opt)
{
    var option = (typeof opt !== 'undefined') ? opt : '{}';
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
                if (!(Object.keys(res).length === 0))
                {
                    if (!Array.isArray(props))
                        item[props] = res[props];
                    else
                    {
                        for (var p in props)
                        {
                            item[props[p]] = res[props[p]];
                        }
                    }
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

function getInFunction(item, props, func, opts)
{
    var http_params = JSON.stringify({'type': 'get_in_function', 'player': player, 'props': props, 'func': func, 'opts': opts});
    send(item, props, http_params);
}

function get(item, props, cls, id, atts, tabs, cache)
{

    /*if (cache && (cls in cache) && (id in  cache[cls]) && (props in cache[cls][id])) {
        console.info('in cache');
        item[props] = cache[cls][id][atts];
    }
    else {*/
        var http_params = JSON.stringify({'type': 'get', 'player': player, 'cls': cls, 'id': id, 'atts': atts});
        var http = new XMLHttpRequest();
        http.open("POST", url, true);
        http.setRequestHeader("Content-type", "application/json");
        http.onreadystatechange = function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                for (var i in atts)
                {
                    var tab_bool = false;
                    for (var j in tabs)
                    {
                        if (tabs[j] == atts[i])
                        {
                            item[props[i]] = res[atts[i]];
                            tab_bool = true;
                            break;
                        }
                    }
                    if (!tab_bool)
                    {
                        if (res[atts[i]][0])
                            item[props[i]] = res[atts[i]][0];
                        else
                            item[props[i]] = 'Undefined';
                    }
                }

                /*
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

function getAll(item, cls, atts, id, sig, reset)
{

    /*if ((cls in cache) && (id in  cache[cls]) && (prop in cache[cls][id])) {
        console.info('in cache');
        idLocal[prop] = cache[cls][id][prop];
    }
    else {*/
        var http_params = JSON.stringify({'type': 'get_all', 'player': player, 'cls': cls, 'id': id, 'atts': atts});
        var http = new XMLHttpRequest();
        //console.info(url);
        http.open("POST", url, true);
        http.setRequestHeader("Content-type", "application/json");
        http.onreadystatechange = function() {
            if(http.readyState == 4 && http.status == 200) {
                //console.info(http.responseText);
                var res = JSON.parse(http.responseText);
                if (reset)
                    for (var member in item) delete item[member];
                for (var r in res) {
                    var idd;
                    if (typeof res[r]['_id'] == 'object')
                        idd = res[r]['_id']['$oid'];
                    else
                        idd = res[r]['_id'];
                    delete res[r]['_id'];
                    if (!(idd in item)) item[idd] = {};
                    for (var att in res[r])
                    {
                        item[idd][att] = res[r][att];
                    }
                }
                map.filesReceived(sig);
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
