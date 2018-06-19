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
import "./" as Comp


Rectangle{
    //property int iden: 0
    property int direction: 0
    property bool selected: false
    property int morale: 0
    property int knights: 0
    property int wSize: 0
    property string flags: ''
    property string attitude: 'normal'
    property int wRec: 0
    property string for_the_player: ''
    property var way

    id: units

    Image {
        id: circle
        visible: selected
        source: "./gfx/circle.png"
        x: -40
        y: -30
    }

    /*Behavior on x{
        NumberAnimation {duration: 100}
        enabled: !map.moved
    }
    Behavior on y{
        NumberAnimation {duration: 100}
        enabled: !map.moved
    }*/

    Comp.AnimatedUnits{
        id: standUp
        property int num: 0
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_ST.png"
        frameCount: 20
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkN
        property int num: 1
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RN.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkNE
        property int num: 2
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RNE.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkE
        property int num: 3
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RE.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkSE
        property int num: 4
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RSE.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkS
        property int num: 5
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RS.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkSW
        property int num: 6
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RSW.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkW
        property int num: 7
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RW.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: walkNW
        property int num: 8
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_RNW.png"
        frameCount: 10
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: attackNE
        property int num: 9
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_ANE.png"
        frameCount: 20
        frameRate: 10
    }

    Comp.AnimatedUnits{
        id: attackSW
        property int num: 10
        x: -60
        y: -90
        width: 120
        height: 140
        source: "./gfx/units/french/FK_ASW.png"
        frameCount: 20
        frameRate: 10
    }
    AnimatedSprite{
        x:0
        y: -80
        width: 36
        height: 27
        frameCount: 25
        frameRate: 10
        //source: "gfx/flags/flag_" + model.getName("Country", model.get("Army", iden,"country")[1]) + ".png"
    }

    Rectangle{
        x: -20
        y: 6
        id: power
        height: 10
        border.width: 1
        border.color: "black"
        color: Qt.hsla(morale/300,1,0.5,1)
        width: 0.03*knights
    }

    Text{
        visible: selected
        id: dismiss
        font.family: "Liberation Serif"
        font.pointSize: 15
        renderType: Text.NativeRendering
        text: "X"
        color: "Red"
        font.bold: true
        x: -40
        y: 0
        MouseArea {
            anchors.fill: parent
            onClicked: {
                /*if (model.get("Army", iden,"country")[1] == model.controlled())
                {
                    var message = [10003, iden];
                    //console.log(message);
                    model.sendMessage(message);
                }*/
            }
        }
    }
}


