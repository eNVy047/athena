import QtQuick
import QtQuick.Controls

Rectangle {
    id: glassPanel
    color: Qt.rgba(255, 255, 255, 0.05)
    radius: 12
    border.color: Qt.rgba(255, 255, 255, 0.1)
    border.width: 1
    
    // Simple drop shadow simulation
    Rectangle {
        anchors.fill: parent
        anchors.margins: -2
        color: "transparent"
        border.color: Qt.rgba(0,0,0,0.3)
        radius: 14
        z: -1
    }
}
