import QtQuick
import QtQuick.Controls

ApplicationWindow {
    id: root
    visible: true
    width: 1280
    height: 720
    title: "F.R.I.D.A.Y."
    
    // Frameless window flags for custom styling
    flags: Qt.Window | Qt.FramelessWindowHint
    
    color: themeManager.backgroundColor
    
    // Background
    ParticleBackground {
        anchors.fill: parent
    }
    
    // Top Bar (Status, Drag area)
    TopBar {
        id: topBar
        width: parent.width
        height: 40
        anchors.top: parent.top
    }
    
    // Main Content Row
    Row {
        anchors.top: topBar.bottom
        anchors.bottom: bottomBar.top
        anchors.left: parent.left
        anchors.right: parent.right
        
        // Left - History
        GlassPanel {
            width: 250
            height: parent.height
            anchors.margins: 10
            Text {
                text: "History"
                color: themeManager.textColor
                anchors.centerIn: parent
            }
        }
        
        // Center - AI Core & Chat
        Item {
            width: parent.width - 500
            height: parent.height
            
            AnimatedCore {
                id: aiCore
                anchors.top: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                width: 200
                height: 200
                anchors.margins: 20
            }
            
            Chat {
                anchors.top: aiCore.bottom
                anchors.bottom: parent.bottom
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 20
            }
        }
        
        // Right - Context (Memory, Browser, Agents)
        GlassPanel {
            width: 250
            height: parent.height
            anchors.margins: 10
            Text {
                text: "Context / Agents"
                color: themeManager.textColor
                anchors.centerIn: parent
            }
        }
    }
    
    // Bottom Bar (Voice)
    BottomBar {
        id: bottomBar
        width: parent.width
        height: 60
        anchors.bottom: parent.bottom
    }
}
