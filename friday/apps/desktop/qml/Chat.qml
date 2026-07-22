import QtQuick
import QtQuick.Controls

Item {
    id: chatView
    
    ListView {
        id: messageList
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: inputField.top
        anchors.bottomMargin: 10
        model: ListModel { id: chatModel }
        
        delegate: Rectangle {
            width: messageList.width
            height: messageText.height + 20
            color: model.sender === "Friday" ? Qt.rgba(14, 165, 233, 0.1) : "transparent"
            radius: 8
            
            Text {
                id: messageText
                text: model.message
                color: themeManager.textColor
                anchors.fill: parent
                anchors.margins: 10
                wrapMode: Text.WordWrap
            }
        }
    }
    
    Connections {
        target: bridge
        function onResponseReady(sender, message) {
            chatModel.append({"sender": sender, "message": message})
            messageList.positionViewAtEnd()
        }
    }
    
    TextField {
        id: inputField
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right
        height: 40
        placeholderText: "Type a message to Friday..."
        color: themeManager.textColor
        background: Rectangle {
            color: Qt.rgba(255, 255, 255, 0.1)
            radius: 4
        }
        
        onAccepted: {
            if (text.length > 0) {
                chatModel.append({"sender": "You", "message": text})
                bridge.sendMessage(text)
                text = ""
                messageList.positionViewAtEnd()
            }
        }
    }
}
