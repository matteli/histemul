import QtQuick 2.9

Image {
    source: "gfx/gui/background.png"
    fillMode: Image.Tile
    property int style: 0
    BorderImage {
        border { left: 20; top: 20; right: 20; bottom: 20 }
        anchors.fill: parent
        horizontalTileMode: BorderImage.Repeat
        verticalTileMode: BorderImage.Repeat
        source: style==1 ? "gfx/gui/windows_slim.png" : "gfx/gui/windows.png"
        visible: style==0 ? false : true
    }
}
