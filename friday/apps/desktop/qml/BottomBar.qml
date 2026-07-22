import QtQuick
import QtQuick.Controls

Item {
    id: bottomBar
    
    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.5)
    }
    
    Text {
        text: "Voice Interface Ready (Push to Talk)"
        color: themeManager.primaryColor
        anchors.centerIn: parent
    }
}
