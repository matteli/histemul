/*Copyright 2012-2013 Matthieu Nué
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
*/

function ArmySpriteMap(sprite, RQ, province, army)
{
    this.__army = army;
    this.__armySprite = {};
    this.__x0 = {};
    this.__y0 = {};
    this.__isInit = false;
    this.__RQ = RQ;
    this.__province = province;

    this.__init(sprite);
}

ArmySpriteMap.prototype =
{
    move: function()
    {
        for (var i in this.__armySprite)
        {
            var d = this.__delta(this.__armySprite[i].attitude)
            this.__armySprite[i].x = this.__x0[i] - map.left + d[0];
            this.__armySprite[i].y = this.__y0[i] - map.top + d[1];
            this.__armySprite[i].z = this.__y0[i] - map.top + d[1];
        }
    },

    gather: function(id)
    {
        /*var army = model.get("Province", (model.get("Army", id, "province")[1]), "army");
        for (var i = 1; i < army.length; i++)
        {
            var ida = army[i]
            var d = this.__delta(this.__armySprite[ida].attitude)
            this.__armySprite[ida].x = this.__x0[ida] - map.left + d[0];
            this.__armySprite[ida].y = this.__y0[ida] - map.top + d[1];
            this.__armySprite[ida].z = this.__y0[ida] - map.top + d[1];
        }
        this.__armySprite[army[1]].wRec = 0;*/
    },

    spread: function(id)
    {
        /*var army = model.get("Province", (model.get("Army", id, "province")[1]), "army");
        var dx = 0;

        if (army.length > 2)
        {
            for (var i = 1; i < army.length; i++)
            {
                this.__armySprite[army[i]].x = this.__x0[army[i]] - map.left + dx;
                this.__armySprite[army[i]].y = this.__y0[army[i]] - map.top;
                this.__armySprite[army[i]].z = this.__y0[army[i]] - map.top;
                dx += this.__armySprite[army[i]].wSize;
            }
            this.__armySprite[army[1]].wRec = dx;
        }*/
    },

    isArmyVisible: function(idProvince, idArmy)
    {
        //return (model.get("Province", idProvince,"army")[1] == iden);
    },

    getSelected: function()
    {
        var s = [];
        for (var id in this.__armySprite)
        {
            if (this.__armySprite[id]["selected"])
                s.push(id);
        }
        return s;
    },

    getAll: function()
    {
        return (this.__armySprite);
    },

    get: function(id)
    {
        if (this.__armySprite.hasOwnProperty(id))
            return (this.__armySprite[id]);
        else
            return (-1);
    },

    unselectAll: function()
    {
        for (var id in this.__armySprite)
        {
            this.__armySprite[id]["selected"] = false;
        }
    },
    update: function()
    {
        if (this.__isInit)
        {
            this.__placeSprite();
        }
        else
        {
            console.log("Army sprite not initialized.");
        }
    },
    __init: function(sp)
    {
        this.__component = Qt.createComponent(sp);
        if (this.__component.status == Component.Ready){
            this.__finish();
            return true
        }
        else if (this.__component.status == Component.Error) {
            console.info("Error for loading units qml");
            return false
        }
        else {
            this.__component.statusChanged.connect(this.__finish);
            return true
        }
    },

    __finish: function()
    {
        //console.info("finish init sprite");
        this.__isInit = true;
    },

    __calculateDirection: function(origin, destination, attitude)
    {
        if (attitude == 'aggressor')
            return (9);
        if (attitude == 'defender')
            return (10);
        if (destination == undefined || destination == 0 || destination == origin)
            return (0);
        var dx = this.__province[destination]['army_x'] - this.__province[origin]['army_x'];
        var dy = this.__province[destination]['army_y'] - this.__province[origin]['army_y'];
        var rap = Math.abs(dx/dy);
        if(dx > 0)
        {
            if (dy < 0)
            {
                if (rap > 2.414)
                    return(3);
                else if (rap < 0.414)
                    return(1);
                else
                    return(2);
            }
            else
            {
                if (rap > 2.414)
                    return(3);
                else if (rap < 0.414)
                    return(5);
                else
                    return(4);
            }
        }
        else
        {
            if (dy < 0)
            {
                if (rap > 2.414)
                    return(7);
                else if (rap < 0.414)
                    return(1);
                else
                    return(8);
            }
            else
            {
                if (rap > 2.414)
                    return(7);
                else if (rap < 0.414)
                    return(5);
                else
                    return(6);
            }
        }
    },
    __placeSprite: function()
    {
        //console.info("place sprites");
        for (var id in this.__armySprite)
        {
            if (!this.__army.hasOwnProperty(id))
            {
                this.__armySprite[id].destroy();
                delete this.__armySprite[id];
                delete this.__x0[id];
                delete this.__y0[id];
            }
        }

        for (id in this.__army)
        {
            this.__x0[id] = this.__province[this.__army[id]['location']]['army_x'];
            this.__y0[id] = this.__province[this.__army[id]['location']]['army_y'];
            var attitude = this.__army[id]['attitude'];
            var d = this.__delta(attitude)
            var direction = this.__calculateDirection(this.__army[id]['location'], this.__army[id]['next_province'], attitude);
            var knights = this.__army[id]['knights'];
            var morale = this.__army[id]['morale'];
            var for_the_player = this.__army[id]['for_the']['player'];
            var way = this.__army[id]['way'];

            if (!this.__armySprite.hasOwnProperty(id))
            {
                this.__armySprite[id] = this.__component.createObject(map, {
                    "x": (this.__x0[id] - map.left + d[0]),
                    "y":(this.__y0[id] - map.top + d[1]),
                    "z":(this.__y0[id] - map.top + d[1]),
                    //"iden":id,
                    "selected": false,
                    "direction":  direction,
                    "knights": knights,
                    "morale": morale,
                    "attitude": attitude,
                    "for_the_player": for_the_player,
                    'way': way
                });
            }
            else
            {
                //console.info("place sprite");
                this.__armySprite[id].x = this.__x0[id] - map.left + d[0];
                this.__armySprite[id].y = this.__y0[id] - map.top + d[1];
                this.__armySprite[id].z = this.__y0[id] - map.top + d[1];
                //this.__armySprite[id].iden = id;
                this.__armySprite[id].direction = direction;
                this.__armySprite[id].knights = knights;
                this.__armySprite[id].morale = morale;
                this.__armySprite[id].attitude = attitude;
                this.__armySprite[id].for_the_player = for_the_player;
                this.__armySprite[id].way = way;
            }
        }
    },
    __delta: function(attitude)
    {
        var deltaX = 0;
        var deltaY = 0;
        if (attitude == 'aggressor')
        {
            deltaX = -30;
            deltaY = 30;
        }
        else if (attitude == 'defender')
        {
            deltaX = 30;
            deltaY = -30;
        }
        return ([deltaX, deltaY])
    },
}
