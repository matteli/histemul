import QtQuick 2.1
//import QtQuick.Controls 1.0
//import QtQuick.Controls.Styles 1.0


Item {
    //color: "transparent"
    //border.color: "black"
    //border.width: 1
    width: 100
    height: textNotification.height// + buttonRow.height
    id: rectNotification
    function close()
    {
        notifListView.closeEvent(index);
    }
    Row {
        Text{
            id: closeText
            font.pointSize: 12
            font.family: "Liberation Serif"
            text: "x  "
            color: maTextNotification.containsMouse ? "red" : "black"
            //anchors.left: parent.right
            MouseArea {
                id: maTextNotification
                hoverEnabled: true
                anchors.fill: closeText
                onClicked: {
                    close();
                }
            }
        }

        Text{
            id: textNotification
            wrapMode: Text.Wrap
            color: "black"
            font.pointSize: 12
            font.family: "Liberation Serif"
            text: title
        }
    }


    /*Row {
        id: buttonRow
        anchors.top: textNotification.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.margins: 5
        Repeater {
            model: button
            Button {
                id: buttonNotification
                //width: 190/nbAnswer; height: 20
                style: ButtonStyle {
                        background: Rectangle {
                            //width: 190/nbButton
                            //height: 20
                            border.width: 3
                            border.color: "#ff580000"
                            radius: 5
                            color: control.pressed ? "#ff580000" : "#a0180000"
                        }
                        label: Text {
                            color: colorFont
                            text: modelData
                            horizontalAlignment: Text.AlignHCenter
                        }
                }
                onClicked:
                {
                    if (nbButton > 1)
                    {

                    }
                    close();
                }
            }
       }
    }*/
}
