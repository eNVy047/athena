import QtQuick
import QtQuick.Controls

Item {
    id: topBar
    
    // Allows dragging the frameless window
    MouseArea {
        anchors.fill: parent
        property variant clickPos: "1,1"
        onPressed: (mouse) => clickPos = Qt.point(mouse.x, mouse.y)
        onPositionChanged: (mouse) => {
            var delta = Qt.point(mouse.x - clickPos.x, mouse.y - clickPos.y)
            root.x += delta.x;
            root.y += delta.y;
        }
    }
    
    Text {
        text: "F.R.I.D.A.Y. Core Active"
        color: Qt.rgba(255, 255, 255, 0.5)
        anchors.centerIn: parent
        font.pixelSize: 12
        font.letterSpacing: 2
    }
}
