import QtQuick 2.7
import QtGraphicalEffects 1.0

Item {
    width: 38
    height: 49
    anchors.centerIn: parent
    property var tinctures: ["white", "white", "white", "white"]
    property string division: "plain"
    Rectangle {
        id: colorTopShieldPlain
        color: tinctures[0]
        anchors.fill: parent
        visible: false
    }
    Item {
        id: colorTopShieldFess
        anchors.fill: parent
        visible: false
        Rectangle {
            color: tinctures[0]
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.right: parent.right
            height: parent.height/2
        }
        Rectangle {
            color: tinctures[1]
            anchors.left: parent.left
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            height: parent.height/2
        }
    }
    Item {
        id: colorTopShieldPale
        anchors.fill: parent
        visible: false
        Rectangle {
            color: tinctures[0]
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: parent.width/2
        }
        Rectangle {
            color: tinctures[1]
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.right: parent.right
            width: parent.width/2
        }
    }
    Image {
        id: baseTopShield
        source: "gfx/shields/shield_base.png"
        anchors.centerIn: parent
        visible: false
    }
    OpacityMask {
            anchors.fill: parent
            source: { switch (division) {
                case "plain": return colorTopShieldPlain;
                case "fess": return colorTopShieldFess;
                case "pale": return colorTopShieldPale;
                default: return colorTopShieldPlain;
                }
            }
            maskSource: baseTopShield
    }
    Image {
        id: maskTopShield
        source: "gfx/shields/shield_mask.png"
        anchors.centerIn: parent
    }
    /*MouseArea {
        anchors.fill: parent
        onClicked: {
            //provinceToolsBar.visible = true
            //countryToolsBar.visible = false
        }
    }*/

}
