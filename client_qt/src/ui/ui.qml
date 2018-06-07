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

import QtQuick 2.9
import QtQuick.Controls 2.2

import "./" as Comp
import QtGraphicalEffects 1.0
//import "constantMsg.js" as Cmsg
//import "text.js" as JSText
import "./js/request.js" as RQ
import Histemul 0.1
import "./js/fixedSpriteMap.js" as JSFixedSpriteMap
import "./js/units.js" as JSUnits
import "./js/func.js" as FC


Item {
    id: root
    Map {
        id: map
        objectName: "map"
        stripe1: "controller.player.tinctures"
        stripe0: "domain_of.holder.player.tinctures"
        topLeftBlock: 2355
        //property bool moved: false
        //PropertyAnimation on t { to: 100; loops: Animation.Infinite }
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
                map.updateInfoBar();
                map.updateMap();
                console.log('finish');
            }

        }*/

        function updateMap()
        {
            for (var i in armyFile)
                armyFile[i] = false;
            RQ.getAll(army, 'army', ['for_the.player', 'knights', 'location', 'attitude', 'morale', 'way', 'next_province'], 'all', 'army_parameters', true);
            //RQ.getAll(army, 'army', ['for_the.player'], 'all', 'army_for_the');
            RQ.getAll(province, 'province', ['population', 'siege', 'morale'], 'all', 'province_others_parameters', false);
            map.updateLightMap();
        }


        Component.onCompleted:
        {
            RQ.getAll(province, 'province', ['army_x', 'army_y', 'city_x', 'city_y', 'land'], 'all', 'province_fixed_parameters', false);
            RQ.getInFunction(selectedPerson, ['name', 'number', 'title', 'treasure', 'level', 'shape', 'division', 'tinctures', 'id'], 'player_person_title', {'type': 'leader'})
        }

        onFilesReceived:
        {
            if (code == 'province_fixed_parameters')
            {
                RQ.getUpdate(clock, 'tick', 0);
                map.updateMap();
                return;
            }
            /*if (code == 'army_parameters' || code == 'army_for_the')
            {
                armyFile[code] = true;
                var ready = true;
                for (var i in armyFile)
                    if (!armyFile[i])
                        ready = false;
                if (ready)
                    armySprite.update();
                return;
            }*/
            if (code == 'army_parameters')
            {
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
                if (!peaceBar.visible)
                {
                    if (mouse.button === Qt.RightButton)
                    {
                        var armies = map.armySprite.getSelected();
                        for (var i in armies)
                            RQ.postMsg(map.armySprite.get(armies[i]), 'way', 'move_troops', armies[i], {'to': parent.hitID(mouse.x,mouse.y)});
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
                            root.updateInfoBar();
                            map.armySprite.unselectAll();
                        }
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
    property int personSelected: 0
    property int sizeBorder: 15
    property string colorFont: "#ff101010"
    property string colorFontDisabled: "#ff606060"

    QtObject {
        id: selectedPerson
        property string name: ""
        property int number: 1
        property string title: ""
        property int level: 1
        property int treasure: 0
        property string shape: ""
        property string division: ""
        property var tinctures: ["white", "white"]
        property string id: ""
        onNameChanged: update();
        onNumberChanged: update();
        onTitleChanged: update();
        onLevelChanged: update();
        onShapeChanged: updateArmory();
        onDivisionChanged: updateArmory();
        onTincturesChanged: updateArmory();
        function update()
        {
            selectedPersonText.text = name + ' ' + FC.a2r(number) + ' of ' + title
        }
        function updateArmory()
        {
            //selectedPersonShield.shape = shape;
            selectedPersonShield.division = division;
            selectedPersonShield.tinctures = tinctures;
        }
    }

    QtObject {
        id: selectedProvincePerson
        property string name: ""
        property int number: 1
        property string title: ""
        property int level: 1
        property string shape: ""
        property string division: ""
        property var tinctures: ["white", "white"]
        property string id: ""
        onNameChanged: update();
        onNumberChanged: update();
        onTitleChanged: update();
        onLevelChanged: update();
        onShapeChanged: updateArmory();
        onDivisionChanged: updateArmory();
        onTincturesChanged: updateArmory();
        function update()
        {
            selectedProvincePersonText.text = name + ' ' + FC.a2r(number) + ' of ' + title
            rowTopMenu.level = level
        }
        function updateArmory()
        {
            //selectedPersonShield.shape = shape;
            selectedProvincePersonShield.division = division;
            selectedProvincePersonShield.tinctures = tinctures;
            selectedProvincePersonShieldPeace.division = division;
            selectedProvincePersonShieldPeace.tinctures = tinctures;
        }

    }

    QtObject {
        id: clock
        property int tick
        onTickChanged:{
            RQ.getUpdate(clock, 'tick', tick+1);
            map.updateMap();
            root.updateInfoBar();
        }
    }

    function updateInfoBar()
    {
        if (root.provinceSelected){
            var p = root.provinceSelected;
            RQ.getInFunction(selectedProvincePerson, ['name', 'number', 'title', 'level', 'shape', 'division', 'tinctures', 'id'], 'player_person_title', {'type': 'province', 'province': p});
            RQ.get(selectedProvinceName, ['text'], 'province',  p, ['name']);
            RQ.getStatus(declareWarButton, 'status', 'declare_war', p, {'from': selectedPerson.id})
            RQ.getStatus(proposePeaceButton, 'status', 'propose_peace', p, {'from': selectedPerson.id})
            RQ.getStatus(rallyTroopsButton, 'status', 'rally_troops', p)
        }
    }

    function updateTopBar()
    {

    }

    function updatePeaceBar()
    {
        if (root.leftMenu.peaceBar.visible)
        {
            //RQ.get(selectedProvinceDomainOfHolderPlayer2, ['division', 'tinctures'], 'province', p, ['domain_of.holder.player.division', 'domain_of.holder.player.tinctures'], ['domain_of.holder.player.tinctures']);
        }
    }


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

    /*Comp.Background {
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
    Comp.Background {
        id: topMenu
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 50
        style: 1
        Row{
            id: rowTopMenu
            y: 10
            x: 15
            spacing: 5
            property int level: 1
            Image{
                source: "gfx/gui/crown_" + parent.level + ".png"
                anchors.verticalCenter: parent.verticalCenter
            }

            Text
            {
                id: selectedPersonText
                text: ""
                renderType: Text.NativeRendering
                wrapMode: Text.Wrap
                font.pointSize: 16
                font.family: "Linux Biolinum"
                font.bold: true
                color: colorFont
                anchors.verticalCenter: parent.verticalCenter

            }
            Image{
                source: "gfx/gui/coin.png"
                anchors.verticalCenter: parent.verticalCenter

            }

            Text
            {
                id: selectedPersonTreasury
                text: "0"
                renderType: Text.NativeRendering
                wrapMode: Text.Wrap
                font.pointSize: 18
                font.family: "Linux Biolinum"
                font.bold: true
                color: colorFont
                anchors.verticalCenter: parent.verticalCenter

            }

        }

    }

    Comp.Background {
        id: leftMenu
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

        width: 300
        x: -width
        anchors.top: topMenu.bottom
        anchors.bottom: parent.bottom

        Column{
            anchors.horizontalCenter: parent.horizontalCenter
            y: 20
            spacing: 0
            id: peaceBar
            visible: false
            Row
            {
                Comp.IconButton{
                    toolTip: 'Cancel'
                    sourceImage: 'gfx/gui/arrow.png'
                    status: 'normal'
                    onClicked:{
                        peaceBar.visible = false;
                        infoBar.visible = true;
                    }
                }
                Comp.IconButton{
                    toolTip: 'Offer peace'
                    sourceImage: 'gfx/gui/peace.png'
                    status: 'normal'
                    onClicked:{
                        peaceBar.visible = false;
                        infoBar.visible = true;
                    }
                }

            }
            Row
            {
                Image {
                    source: "gfx/gui/wood_square.png"
                    Comp.Shield {
                        id: selectedPersonShield
                    }
                }

                Image {
                    source: "gfx/gui/peace_arrow.png"
                }

                Image {
                    source: "gfx/gui/wood_square.png"
                    Comp.Shield {
                        id: selectedProvincePersonShieldPeace
                    }
                }

            }
            Row
            {
                SpinBox {

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
                    id: selectedProvincePersonShield
                    MouseArea{
                        anchors.fill: parent
                        onClicked: RQ.getInFunction(selectedPerson, ['name', 'number', 'title', 'treasure', 'level', 'shape', 'division', 'tinctures', 'id'], 'player_person_title', {'type': 'home_province', 'province': provinceSelected})
                    }
                }

            }

            Text
            {
                id: selectedProvincePersonText
                text: ""
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
                    id: declareWarButton
                    z: 10
                    toolTip: 'Declare War'
                    sourceImage: 'gfx/gui/war.png'
                    onClicked:{
                        if (status === 'normal')
                            RQ.postMsg(declareWarButton, 'status', 'declare_war', root.provinceSelected, {'from': selectedPerson.id});
                    }
                }
                Comp.IconButton{
                    id: proposePeaceButton
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
                id: selectedProvinceName
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
                    id: rallyTroopsButton
                    toolTip: "Rally troops"
                    sourceImage: "gfx/gui/aban.png"
                    onClicked:{
                        if (status == "normal")
                            RQ.postMsg(rallyTroopsButton, 'status', 'rally_troops', root.provinceSelected);
                    }
                }
            }
        }
    }

}

