import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: chatView

    // ── Shared send action ───────────────────────────────────────────────────
    function sendMessage() {
        var text = inputField.text.trim()
        if (text === "") return
        chatModel.append({"sender": "You", "message": text})
        bridge.sendMessage(text)
        inputField.text = ""
        inputField.forceActiveFocus()
    }

    // ── Helper functions for real-time bubble updates ────────────────────────
    function updateLastMessage(newText) {
        if (chatModel.count > 0) {
            chatModel.setProperty(chatModel.count - 1, "message", newText)
        }
    }

    function appendToLastMessage(textChunk) {
        if (chatModel.count > 0) {
            var currentText = chatModel.get(chatModel.count - 1).message
            if (currentText === "Generating...") {
                chatModel.setProperty(chatModel.count - 1, "message", textChunk)
            } else {
                chatModel.setProperty(chatModel.count - 1, "message", currentText + textChunk)
            }
        }
    }

    // ── Thinking/status banner ────────────────────────────────────────────
    Rectangle {
        id: statusBanner
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: visible ? 32 : 0
        color: Qt.rgba(14, 165, 233, 0.12)
        radius: 6
        visible: thinkingLabel.text !== "" && thinkingLabel.text !== "Ready"
                 && thinkingLabel.text !== "Cancelled"

        Behavior on height { NumberAnimation { duration: 160 } }

        Row {
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 12
            spacing: 8

            // Animated thinking dots
            Row {
                spacing: 4
                Repeater {
                    model: 3
                    Rectangle {
                        width: 6; height: 6; radius: 3
                        color: themeManager.primaryColor
                        opacity: 0.4
                        SequentialAnimation on opacity {
                            loops: Animation.Infinite
                            running: statusBanner.visible
                            NumberAnimation { to: 1.0; duration: 400 }
                            NumberAnimation { to: 0.4; duration: 400 }
                            PauseAnimation { duration: index * 180 }
                        }
                    }
                }
            }

            Text {
                id: thinkingLabel
                text: ""
                color: themeManager.primaryColor
                font.pixelSize: 12
                font.italic: true
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    // ── Message list ──────────────────────────────────────────────────────
    ListView {
        id: messageList
        anchors.top: statusBanner.bottom
        anchors.topMargin: 6
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: inputRow.top
        anchors.bottomMargin: 10
        model: ListModel { id: chatModel }
        clip: true
        spacing: 6

        delegate: Item {
            width: messageList.width
            height: bubble.height + 4

            property bool isFriday: model.sender === "Friday"
            property bool isSystem: model.sender === "System"

            // Message bubble
            Rectangle {
                id: bubble
                width: Math.min(messageText.implicitWidth + 24, messageList.width * 0.85)
                height: messageText.height + 16
                radius: 10
                color: {
                    if (isSystem) return Qt.rgba(239, 68, 68, 0.15)
                    if (isFriday) return Qt.rgba(14, 165, 233, 0.13)
                    return Qt.rgba(255, 255, 255, 0.07)
                }
                border.color: {
                    if (isSystem) return Qt.rgba(239, 68, 68, 0.3)
                    if (isFriday) return Qt.rgba(14, 165, 233, 0.2)
                    return Qt.rgba(255, 255, 255, 0.1)
                }
                border.width: 1

                anchors.right: isFriday ? undefined : parent.right
                anchors.left: isFriday ? parent.left : undefined
                anchors.rightMargin: isFriday ? 0 : 4
                anchors.leftMargin: isFriday ? 4 : 0

                // Sender label
                Text {
                    id: senderLabel
                    text: model.sender
                    anchors.top: parent.top
                    anchors.left: parent.left
                    anchors.topMargin: 5
                    anchors.leftMargin: 10
                    font.pixelSize: 10
                    font.bold: true
                    color: {
                        if (isSystem) return "#ef4444"
                        if (isFriday) return themeManager.primaryColor
                        return Qt.rgba(255, 255, 255, 0.5)
                    }
                }

                // Message text
                Text {
                    id: messageText
                    text: model.message
                    anchors.top: senderLabel.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.leftMargin: 10
                    anchors.rightMargin: 10
                    anchors.topMargin: 2
                    anchors.bottomMargin: 8
                    color: themeManager.textColor
                    wrapMode: Text.WordWrap
                    font.pixelSize: 13
                    lineHeight: 1.4
                }
            }
        }

        // Auto-scroll to bottom
        onCountChanged: Qt.callLater(positionViewAtEnd)
    }

    // ── Input row ─────────────────────────────────────────────────────────
    Row {
        id: inputRow
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 8

        TextField {
            id: inputField
            width: parent.width - sendButton.width - parent.spacing
            height: 42
            placeholderText: "Ask Friday anything..."
            color: themeManager.textColor
            background: Rectangle {
                implicitWidth: 200
                implicitHeight: 42
                color: Qt.rgba(255, 255, 255, 0.07)
                radius: 8
                border.color: inputField.activeFocus ? themeManager.primaryColor : Qt.rgba(255, 255, 255, 0.15)
                border.width: inputField.activeFocus ? 2 : 1
                Behavior on border.color { ColorAnimation { duration: 150 } }
            }

            onAccepted: chatView.sendMessage()
        }

        Rectangle {
            id: sendButton
            width: 42
            height: 42
            radius: 8
            color: sendMouseArea.pressed
                   ? Qt.darker(themeManager.primaryColor, 1.2)
                   : sendMouseArea.containsMouse
                     ? Qt.lighter(themeManager.primaryColor, 1.1)
                     : themeManager.primaryColor

            Behavior on color { ColorAnimation { duration: 120 } }

            Text {
                anchors.centerIn: parent
                text: "↑"
                color: "white"
                font.pixelSize: 18
                font.bold: true
            }

            MouseArea {
                id: sendMouseArea
                anchors.fill: parent
                hoverEnabled: true
                onClicked: chatView.sendMessage()
            }
        }
    }

    // ── Bridge connections ─────────────────────────────────────────────────
    Connections {
        target: bridge

        function onResponseReady(sender, message) {
            chatModel.append({"sender": sender, "message": message})
        }

        function onVoiceTranscriptUpdate(status, transcript) {
            if (status === "Listening") {
                chatModel.append({"sender": "You (voice)", "message": "Listening..."})
            } else if (status === "Recognizing") {
                chatView.updateLastMessage("Recognizing...")
            } else if (status === "Final") {
                chatView.updateLastMessage(transcript)
            }
        }

        function onLiveResponseStart(sender) {
            chatModel.append({"sender": sender, "message": "Thinking..."})
        }

        function onTokenReady(token) {
            if (chatModel.count > 0) {
                var currentText = chatModel.get(chatModel.count - 1).message
                if (currentText === "Thinking...") {
                    chatView.updateLastMessage("Generating...")
                }
                chatView.appendToLastMessage(token)
            }
        }

        function onThinkingUpdate(status) {
            thinkingLabel.text = status
        }

        function onStatusChanged(status) {
            if (status === "Ready" || status === "Cancelled") {
                // Brief delay before hiding the status banner
                statusHideTimer.restart()
            }
        }
    }

    Timer {
        id: statusHideTimer
        interval: 1200
        onTriggered: thinkingLabel.text = ""
    }
}
