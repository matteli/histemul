import QtQuick 2.9

AnimatedSprite {
    function isCurrent(num, w)
    {
        if (direction === num)
        {
            wSize = w;
            return true;
        }
        else return false;
    }

    interpolate: false
    antialiasing : false
    visible: isCurrent(num, width)
    running: visible

    Rectangle{
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        id: rec
        width: wRec
        color: "transparent"
        border.color: "#ff580000"
        border.width: 3
        radius: 5
        Behavior on width {
             NumberAnimation {duration: 100}
        }
    }

    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        //onEntered: map.armySprite.spread(units.iden);
        //onExited: map.armySprite.gather(units.iden);
        onClicked: {
            if (for_the_player === player)
            {
                selected = !selected;
                map.unSelectID();
                root.provinceSelected = 0;
            }
        }
    }

}
