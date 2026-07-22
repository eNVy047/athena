import QtQuick

Rectangle {
    id: core
    color: "transparent"
    
    property string status: "idle"
    
    Connections {
        target: bridge
        function onStatusChanged(newStatus) {
            core.status = newStatus
        }
    }
    
    Rectangle {
        id: outerRing
        anchors.centerIn: parent
        width: parent.width * 0.9
        height: parent.height * 0.9
        radius: width / 2
        color: "transparent"
        border.color: themeManager.primaryColor
        border.width: 2
        opacity: 0.6
        
        RotationAnimation on rotation {
            loops: Animation.Infinite
            from: 0
            to: 360
            duration: core.status == "Thinking..." ? 1500 : 5000
        }
    }
    
    Rectangle {
        id: innerOrb
        anchors.centerIn: parent
        width: parent.width * 0.4
        height: parent.height * 0.4
        radius: width / 2
        color: themeManager.primaryColor
        
        SequentialAnimation on scale {
            loops: Animation.Infinite
            NumberAnimation { to: core.status == "Thinking..." ? 1.2 : 1.05; duration: 1000; easing.type: Easing.InOutQuad }
            NumberAnimation { to: 1.0; duration: 1000; easing.type: Easing.InOutQuad }
        }
    }
}
