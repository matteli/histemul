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

function FixedSpriteMap(sprite, RQ, province, xAttribute, yAttribute, variable)
{
    this.__spriteProvince = [];
    this.__x0 = [];
    this.__y0 = [];
    this.__isInit = false;
    this.__xAttribute = xAttribute;
    this.__yAttribute = yAttribute;
    this.__variable = variable;
    this.__RQ = RQ;
    this.__province = province;

    this.__init(sprite);
}

FixedSpriteMap.prototype =
{
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
        this.__isInit = true;
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
    __placeSprite: function()
    {
        /*if (this.__isInit)
        {
            model.lock();
            console.log(provinceChanged);
            for (var i in provinceChanged)
            {
                var id = provinceChanged[i];
                var variable = []
                for (var j in this.__variable)
                    variable[j] = model.get("Province", id, this.__variable[j])[1];
                if (!this.__spriteProvince.hasOwnProperty(id))
                {
                    this.__x0[id] = model.get("Province", id, this.__xAttribute)[1];
                    this.__y0[id] = model.get("Province", id, this.__yAttribute)[1];
                    this.__spriteProvince[id] = this.__component.createObject(map, {"x": (this.__x0[id] - map.left), "y":(this.__y0[id] - map.top), "z":(this.__y0[id] - map.top), "province":id, "variable":variable});
                }
                else
                {
                    this.__spriteProvince[id].variable = variable;
                }
            }
            model.unlock();
        }
        else
        {
            console.log("Army sprite not initialized.");
        }*/
        if (this.__isInit)
        {
            for (var i in this.__province)
            {
                if (!this.__spriteProvince.hasOwnProperty(i))
                {
                    var params = {};
                    this.__x0[i] = this.__province[i][this.__xAttribute];
                    this.__y0[i] = this.__province[i][this.__yAttribute];
                    for (var j in this.__variable)
                        params[this.__variable[j]]  = this.__province[i][this.__variable[j]];
                    this.__spriteProvince[i] = this.__component.createObject(map,
                        {'x': this.__x0[i] - map.left, 'y': this.__y0[i] - map.top, 'z': this.__y0[i] - map.top,
                        'variable': params});
                }
                else
                {
                    var params = {};
                    for (var k in this.__variable)
                        params[this.__variable[k]]  = this.__province[i][this.__variable[k]];
                    this.__spriteProvince[i]['variable'] = params;
                }
            }

        }
        else
        {
            console.log("Army sprite not initialized.");
        }
    },
    move: function()
    {
        for (var i in this.__spriteProvince)
        {
            this.__spriteProvince[i].x = this.__x0[i] - map.left;
            this.__spriteProvince[i].y = this.__y0[i] - map.top;
            this.__spriteProvince[i].z = this.__y0[i] - map.top;
        }
    },
    getAll: function()
    {
        return (this.__spriteProvince);
    },
    get: function(id)
    {
        if (this.__spriteProvince.hasOwnProperty(id))
            return (this.__spriteProvince[id]);
        else
            return (-1);
    }
}
