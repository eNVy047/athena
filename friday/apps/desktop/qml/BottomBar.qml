import QtQuick
import QtQuick.Controls

Item {
    id: bottomBar

    Rectangle {
        anchors.fill: parent
        color: Qt.rgba(0, 0, 0, 0.6)
        border.color: themeManager.primaryColor
        border.width: 0
    }

    // Push-to-Talk Button
    Rectangle {
        id: voiceButton
        anchors.centerIn: parent
        width: 180
        height: 40
        radius: 20
        color: voiceArea.pressed
               ? Qt.rgba(14, 165, 233, 0.5)
               : Qt.rgba(14, 165, 233, 0.15)

        border.color: themeManager.primaryColor
        border.width: 1.5

        Behavior on color {
            ColorAnimation { duration: 150 }
        }

        Row {
            anchors.centerIn: parent
            spacing: 8

            Rectangle {
                id: voiceDot
                width: 10
                height: 10
                radius: 5
                color: voiceStatusText.text === "Listening..." ||
                       voiceStatusText.text === "Recording..."
                       ? "#22c55e"   // green when active
                       : themeManager.primaryColor

                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    running: voiceStatusText.text === "Listening..." ||
                             voiceStatusText.text === "Recording..."
                    NumberAnimation { to: 0.2; duration: 600 }
                    NumberAnimation { to: 1.0; duration: 600 }
                }
            }

            Text {
                id: voiceStatusText
                text: "Hold to Talk"
                color: themeManager.textColor
                font.pixelSize: 13
                anchors.verticalCenter: parent.verticalCenter
            }
        }

        MouseArea {
            id: voiceArea
            anchors.fill: parent
            onPressed: {
                voiceStatusText.text = "Listening..."
                bridge.startVoice()
            }
            onReleased: {
                voiceStatusText.text = "Processing..."
                bridge.stopVoice()
            }
        }
    }

    // Voice status feedback from backend
    Connections {
        target: bridge
        function onVoiceStatusChanged(status) {
            voiceStatusText.text = status === "Ready" || status === "" ? "Hold to Talk" : status
        }
    }
}
