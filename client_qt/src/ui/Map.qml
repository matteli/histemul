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

import QtQuick 2.1
import Histemul 0.1
import "./js/fixedSpriteMap.js" as JSFixedSpriteMap
import "./js/units.js" as JSUnits
import "./js/request.js" as RQ



Map {
    id: map
    objectName: "map"
    fill: "controller"
    topLeftBlock: 20
    //property bool moved: false
    PropertyAnimation on t { to: 100; loops: Animation.Infinite }
    property var armySprite: new JSUnits.ArmySpriteMap("armyXPos", "armyYPos", "Units.qml")
    property var citySprite: new JSFixedSpriteMap.FixedSpriteMap(["population", "siege", "morale"], "cityXPos", "cityYPos", "Cities.qml")

    onArmyModelChanged:
    {
        armySprite.manage(armyChanged);
    }

    Component.onCompleted:
    {
        armySprite.init();
    }

    onProvinceModelChanged:
    {
        citySprite.manage(visibleProvinceChanged);
        //console.log(visibleProvinceChanged);
    }

    onMoved:
    {
        armySprite.move();
        citySprite.move();
    }

    MouseArea {
        x: 0
        y: 0
        height: root.height
        width: root.width
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        onClicked: {
            if (mouse.button === Qt.RightButton)
            {
                for (var i in armySprite.getAll())
                {
                    if (armySprite.get(i).selected)
                    {
                        var message = [10001, i, parent.hitID(mouse.x,mouse.y)];
                        //console.log("Move army " + i + " in " + parent.hitID(mouse.x,mouse.y))
                        //console.log(message);
                        model.sendMessage(message);
                    }
                }
            }
            else
            {
                //map.selectID(mouse.x,mouse.y);
                var p = map.selectID(mouse.x,mouse.y);
                if (p === root.provinceSelected)
                {
                    map.unSelectID();
                    root.provinceSelected = 0;
                }
                else
                {
                    root.provinceSelected = p;
                    RQ.get(selected_province_name, 'text', 'province',  p, 'name')
                    RQ.get(selected_province_domain_of_holder_name, 'text', 'province', p, 'domain_of.holder.name')
                    RQ.get(selected_province_domain_of_name, 'text', 'province', p, 'domain_of.name')
                    RQ.get(selected_province_domain_of_holder_armory, 'division', 'province', p, 'domain_of.holder.player.armory.division')
                    RQ.get(selected_province_domain_of_holder_armory, 'tinctures', 'province', p, 'domain_of.holder.player.armory.tinctures')

                    //root.showProvincePanel();
                    for (i in armySprite.getAll())
                        armySprite.get(i).selected = false;
                }
            }
        }
    }

    MouseArea {
        id: maTopLeft
        z: 100000
        hoverEnabled: true
        x: 0
        y: 0
        height: root.sizeBorder
        width: root.sizeBorder
    }

    MouseArea {
        id: maBottomLeft
        z: 100000
        hoverEnabled: true
        x: 0
        y: root.height-root.sizeBorder
        height: root.sizeBorder
        width: root.sizeBorder
    }

    MouseArea {
        id: maTopRight
        z: 100000
        hoverEnabled: true
        x: root.width-root.sizeBorder
        y: 0
        height: root.sizeBorder
        width: root.sizeBorder
    }

    MouseArea {
        id: maBottomRight
        z: 100000
        hoverEnabled: true
        x: root.width-root.sizeBorder
        y: root.height-root.sizeBorder
        height: root.sizeBorder
        width: root.sizeBorder
    }

    MouseArea {
        id: maLeft
        z: 100000
        hoverEnabled: true
        x: 0
        y: root.sizeBorder
        height: root.height-2*root.sizeBorder
        width: root.sizeBorder
    }

    MouseArea {
        id: maRight
        z: 100000
        hoverEnabled: true
        x: root.width-root.sizeBorder
        y: root.sizeBorder
        width: root.sizeBorder
        height:root.height-2*root.sizeBorder
    }

    MouseArea {
        id: maTop
        z: 100000
        hoverEnabled: true
        x: root.sizeBorder
        y: 0
        width: root.width-2*root.sizeBorder
        height: root.sizeBorder
    }

    MouseArea {
        id: maBottom
        z: 100000
        hoverEnabled: true
        x: root.sizeBorder
        y: root.height-root.sizeBorder
        width: root.width-2*root.sizeBorder
        height: root.sizeBorder
    }

    Timer {
        interval: 50; running: true; repeat: true
        onTriggered: {
            if (maLeft.containsMouse)
            {
                parent.move(Map.OnLeft)
                //moved = true
            }
            else if (maRight.containsMouse)
            {
                parent.move(Map.OnRight)
                //moved = true
            }
            else if (maTop.containsMouse)
            {
                parent.move(Map.OnTop)
                //moved = true
            }
            else if (maBottom.containsMouse)
            {
                parent.move(Map.OnBottom)
                //moved = true
            }
            else if (maTopLeft.containsMouse)
            {
                parent.move(Map.OnTopLeft)
                //moved = true
            }
            else if (maBottomLeft.containsMouse)
            {
                parent.move(Map.OnBottomLeft)
                //moved = true
            }
            else if (maTopRight.containsMouse)
            {
                parent.move(Map.OnTopRight)
                //moved = true
            }
            else if (maBottomRight.containsMouse)
            {
                parent.move(Map.OnBottomRight)
                //moved = true
            }
            //else
                //moved = false
        }
   }
}
