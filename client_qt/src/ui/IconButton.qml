import QtQuick 2.7
import QtGraphicalEffects 1.0

MouseArea {
    width: mask.width + 2
    height: mask.height + 2
    property string toolTip: ''
    property string sourceImage: ''
    property string status: 'hidden'
    visible: (status != 'hidden')
    //property bool active: true
    hoverEnabled: status=="normal"?true:false
    onEntered: timerToolTip.start()
    onExited: {
        timerToolTip.stop()
        rectToolTip.visible = false
    }
    onPositionChanged: {
        timerToolTip.restart()
        rectToolTip.visible = false
    }

    Rectangle {
        color: "#d0bd8300"
        visible: parent.pressed && parent.status=="normal"
        anchors.fill: parent
    }

    Rectangle {
        border.color: "#ff000000"
        border.width: 2
        radius: 4
        color: "#00000000"
        visible: parent.containsMouse && parent.status=="normal"
        anchors.fill: parent
    }

    Image {
        id: mask
        visible: false
        source: sourceImage
        anchors.centerIn: parent
    }
    Rectangle {
        id: colorRect
        visible: false
        height: parent.height
        width: parent.width
        color: { switch (parent.status){
                case "normal": return "black";
                case "disabled": return "#56410f";
                case "accepted": return "green";
                case "rejected": return "red";
                default: return "orange";
            }
        }
        anchors.fill: parent
    }

    OpacityMask {
            anchors.fill: parent
            source: colorRect
            maskSource: mask
    }


    Timer {
        id: timerToolTip
        interval: 800
        running: false
        repeat: false
        onTriggered: toolTip ? rectToolTip.visible = true : rectToolTip.visible = false
    }

    Rectangle{
        id: rectToolTip
        visible: false
        x: parent.mouseX
        y: parent.mouseY - 14
        border.color: "#ff000000"
        border.width: 1
        color: "#ffffffff"
        width: textToolTip.width + 4
        height: textToolTip.height
        Text {
            id: textToolTip
            text: toolTip
            anchors.horizontalCenter: parent.horizontalCenter
            horizontalAlignment: Text.AlignHCenter
            font.pointSize: 10
            font.family: "Liberation Serif"
        }
    }

}
