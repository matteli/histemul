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

import QtQuick 2.7
import QtQuick.Controls 1.0
import "./" as Comp
import QtGraphicalEffects 1.0
//import "constantMsg.js" as Cmsg
//import "text.js" as JSText
import "./js/request.js" as RQ
import Histemul 0.1
import "./js/fixedSpriteMap.js" as JSFixedSpriteMap
import "./js/units.js" as JSUnits



Item {
    id: root

    Map {
        id: map
        objectName: "map"
        fill: "land"
        topLeftBlock: 2355
        //property bool moved: false
        PropertyAnimation on t { to: 100; loops: Animation.Infinite }
        property var province: ({})
        property var armyFile: ({'army_parameters': false, 'army_for_the': false})
        property var army: ({})
        property var city: ({})
        property var armySprite: new JSUnits.ArmySpriteMap("../Units.qml", RQ, province, army)
        property var citySprite: new JSFixedSpriteMap.FixedSpriteMap("../Cities.qml", RQ, province, "city_x", "city_y", ["population", "siege", "morale"])
        signal filesReceived(string code)

        /*Timer {
            id: time_remaining
            interval: 1000000
            running: false
            repeat: false
            onIntervalChanged: restart()
            onTriggered: {
                RQ.getTimeRemaining(time_remaining, 'interval');
                map.nbFilesReceived = 0;
                map.nbFilesAsked = 2;
                map.updateUI();
                map.updateMap();
                console.log('finish');
            }

        }*/
        QtObject {
            id: clock
            property int tick
            onTickChanged:{
                RQ.getUpdate(clock, 'tick', tick+1);
                map.updateMap();
                map.updateUI();
            }
        }

        function updateMap()
        {
            for (var i in armyFile)
                armyFile[i] = false;
            RQ.getAll(army, 'army', 'knights;location;attitude;morale;way;next_province', 'army_parameters');
            RQ.getAll(army, 'army', 'for_the.player', 'army_for_the');
            RQ.getAll(province, 'province', 'population;siege;morale', 'province_others_parameters');
        }

        function updateUI()
        {
            if (root.provinceSelected){
                var p = root.provinceSelected;
                RQ.get(selected_province_name, 'text', 'province',  p, 'name');
                RQ.get(selected_province_domain_of_holder_name, 'text', 'province', p, 'domain_of.holder.name');
                RQ.get(selected_province_domain_of_name, 'text', 'province', p, 'domain_of.name');
                RQ.get(selected_province_domain_of_holder_player_armory, 'division', 'province', p, 'domain_of.holder.player.armory.division');
                RQ.get(selected_province_domain_of_holder_player_armory, 'tinctures', 'province', p, 'domain_of.holder.player.armory.tinctures', true);
                RQ.getStatus(declare_war_button, 'status', 'declare_war', p)
                RQ.getStatus(propose_peace_button, 'status', 'propose_peace', p)
                RQ.getStatus(rally_troops_button, 'status', 'rally_troops', p)
            }
        }

        Component.onCompleted:
        {
            RQ.getAll(province, 'province', 'army_x;army_y;city_x;city_y;land', 'province_fixed_parameters');
        }

        onFilesReceived:
        {
            if (code == 'province_fixed_parameters')
            {
                RQ.getUpdate(clock, 'tick', 0);
                map.updateMap();
                return;
            }
            if (code == 'army_parameters' || code == 'army_for_the')
            {
                armyFile[code] = true;
                var ready = true;
                for (var i in armyFile)
                    if (!armyFile[i])
                        ready = false;
                if (ready)
                    armySprite.update();
                return;
            }
            if (code == 'province_others_parameters')
            {
                citySprite.update();
                return;
            }

            return;
        }

        /*onArmyModelChanged:
        {
            armySprite.manage(armyChanged);
        }

        onProvinceModelChanged:
        {
            citySprite.manage(visibleProvinceChanged);
            //console.log(visibleProvinceChanged);
        }*/

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
                    var armies = map.armySprite.getSelected();
                    for (var i in armies)
                        RQ.postMsg(map.armySprite.get( armies[i]), 'way', 'move_troops', armies[i], parent.hitID(mouse.x,mouse.y));
                }
                else
                {
                    var p = map.selectID(mouse.x,mouse.y);
                    if (p === root.provinceSelected)
                    {
                        map.unSelectID();
                        root.provinceSelected = 0;
                    }
                    else
                    {
                        root.provinceSelected = p;
                        map.updateUI();
                        map.armySprite.unselectAll();
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

    property int provinceSelected: 0
    property int sizeBorder: 15
    property string colorFont: "#ff101010"
    property string colorFontDisabled: "#ff606060"

    /*Connections {
        target: notifications
        onNewMessage:
        {
            var t = JSText.getText(model.getLastMessage());
            var jso = {};
            console.log(t[0]);
            jso["title"] = t[0];
            jso["nbButton"] = t[2].length;
            jso["button"] = [];
            for (var i in t[2])
            {
                jso["button"].push({"button": t[2][i]});
            }
            notifList.insert(0, jso);
        }
    }
    Connections {
        target: notifications
        onModelChanged:
        {
            if (provinceSelected)
            {
                var pro = provinceSelected;
                provinceSelected = 0;
                provinceSelected = pro;
            }
        }
    }

    ListModel
    {
        id: notifList
    }*/

    /*Comp.Window {
        id: topMenu
        anchors.top: parent.top
        anchors.left: parent.left
        width: 300
        style: 1
        height: 200
        ScrollView{
            anchors.margins: sizeBorder
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            width: 100
            ListView {
                id: notifListView
                model: notifList
                anchors.fill: parent

                delegate: Comp.Notification{}
                add: Transition {
                        NumberAnimation { property: "opacity"; from: 0; to: 1.0; duration: 500  }
                    }
                remove: Transition {
                        NumberAnimation { property: "opacity"; to: 0; duration: 500  }
                    }

                displaced: Transition {
                        NumberAnimation { properties: "y"; duration: 500 }
                    }
                function closeEvent(index)
                {
                    console.log(index);
                    notifList.remove(index);
                }
            }
        }
    }*/

    Comp.Window {
        id : leftMenu
        property int countryPeace: 0
        style: 2
        states:
            State {
                when: provinceSelected
                PropertyChanges { target: leftMenu; x: 0}
            }
        transitions:
            Transition {
                NumberAnimation { properties: "x"; easing.type: Easing.OutExpo; duration: 500 }
            }

        //anchors.margins: sizeBorder
        width: 300
        x: -width
        //y: sizeBorder
        //height: parent.height - 2*sizeBorder
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        Column{
            anchors.horizontalCenter: parent.horizontalCenter
            y: 20
            spacing: 0
            id: peaceBar
            visible: false
            Row
            {
                Image {
                    source: "gfx/gui/wood_square.png"
                    /*Image {
                        id: pbTopShieldLeft
                        source: "gfx/shields/shield_" + model.getName("Country", model.controlled()) + "_1.png"
                        anchors.centerIn: parent
                    }*/
                }
                Image {
                    source: "gfx/gui/peace_arrow.png"
                }

                Image {
                    source: "gfx/gui/wood_square.png"
                    Image {
                        id: pbTopShieldRight
                        //source: "gfx/shields/shield_" + model.getName("Country", leftMenu.countryPeace) + "_1.png"
                        anchors.centerIn: parent
                    }
                }

            }
        }

        Column{
            anchors.horizontalCenter: parent.horizontalCenter
            y: 20
            spacing: 0
            id: infoBar
            visible: true
            Image {
                source: "gfx/gui/wood_square.png"
                anchors.horizontalCenter: parent.horizontalCenter
                Comp.Shield{
                    id: selected_province_domain_of_holder_player_armory
                    tinctures: ["blue", "red"]
                    division: "plain"
                }
            }
            Text
            {
                id: selected_province_domain_of_holder_name
                text: "Holder"
                renderType: Text.NativeRendering
                wrapMode: Text.Wrap
                width: leftMenu.width
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 24
                font.family: "Linux Biolinum"
                font.bold: true
                color: colorFont
            }
            Text
            {
                id: selected_province_domain_of_name
                text: "Title"
                renderType: Text.NativeRendering
                wrapMode: Text.Wrap
                width: leftMenu.width
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 16
                font.family: "Linux Biolinum"
                font.bold: true
                color: colorFont
            }

            Row{
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                spacing: 5
                Comp.IconButton{
                    id: declare_war_button
                    z: 10
                    toolTip: 'Declare War'
                    sourceImage: 'gfx/gui/war.png'
                    onClicked:{
                        if (status === 'normal')
                            RQ.postMsg(declare_war_button, 'status', 'declare_war', root.provinceSelected);
                    }
                }
                Comp.IconButton{
                    id: propose_peace_button
                    z: 5
                    toolTip: "Propose peace"
                    sourceImage: "gfx/gui/peace.png"
                    onClicked:{
                        if (status === 'normal')
                        {
                            infoBar.visible = false;
                            peaceBar.visible = true;
                        }
                    }
                }
            }

            BorderImage {
                border { left: 9; top: 0; right: 9; bottom: 0 }
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 20
                horizontalTileMode: BorderImage.Repeat
                source: "gfx/gui/line.png"
            }
            Text
            {
                id: selected_province_name
                text: "Province"
                renderType: Text.NativeRendering
                wrapMode: Text.Wrap
                width: leftMenu.width
                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 24
                font.family: "Linux Biolinum"
                font.bold: true
                color: colorFont
            }

            Row{
                anchors.left: parent.left
                anchors.right: parent.left
                anchors.leftMargin: 20
                anchors.rightMargin: 20
                spacing: 5
                Comp.IconButton
                {
                    id: rally_troops_button
                    toolTip: "Rally troops"
                    sourceImage: "gfx/gui/aban.png"
                    onClicked:{
                        if (status == "normal")
                            RQ.postMsg(rally_troops_button, 'status', 'rally_troops', root.provinceSelected);
                    }

                }
            }
        }

    }
}
