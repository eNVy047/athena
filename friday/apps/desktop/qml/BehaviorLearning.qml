import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: behaviorPage

    // ── Header ──────────────────────────────────────────────────────────────
    Column {
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: 16
        spacing: 12

        // Title row
        Row {
            width: parent.width
            spacing: 12

            Text {
                text: "🧠"
                font.pixelSize: 24
                verticalAlignment: Text.AlignVCenter
            }

            Column {
                spacing: 2
                Text {
                    text: "Behavior Learning"
                    color: themeManager.textColor
                    font.pixelSize: 16
                    font.bold: true
                }
                Text {
                    text: "What Friday has learned from your real usage"
                    color: Qt.rgba(255, 255, 255, 0.45)
                    font.pixelSize: 11
                }
            }

            Item { width: 1; Layout.fillWidth: true }

            // Reset all button
            Rectangle {
                width: resetLabel.implicitWidth + 20
                height: 28
                radius: 6
                color: resetMouse.pressed ? Qt.rgba(239, 68, 68, 0.3) : Qt.rgba(239, 68, 68, 0.12)
                border.color: Qt.rgba(239, 68, 68, 0.4)
                border.width: 1
                Behavior on color { ColorAnimation { duration: 120 } }

                Text {
                    id: resetLabel
                    text: "Reset All"
                    color: "#ef4444"
                    font.pixelSize: 11
                    anchors.centerIn: parent
                }

                MouseArea {
                    id: resetMouse
                    anchors.fill: parent
                    onClicked: {
                        bridge.resetAllBehaviors()
                        bridge.refreshBehaviors()
                    }
                }
            }
        }

        // Confidence legend
        Row {
            spacing: 16
            Repeater {
                model: [
                    { label: "High (≥75%)",   color: "#22c55e" },
                    { label: "Medium (40-75%)", color: "#f59e0b" },
                    { label: "Low (<40%)",      color: "#6b7280" },
                ]
                Row {
                    spacing: 5
                    Rectangle {
                        width: 10; height: 10; radius: 5
                        color: modelData.color
                        anchors.verticalCenter: parent.verticalCenter
                    }
                    Text {
                        text: modelData.label
                        color: Qt.rgba(255, 255, 255, 0.5)
                        font.pixelSize: 10
                        anchors.verticalCenter: parent.verticalCenter
                    }
                }
            }
        }

        // Separator
        Rectangle {
            width: parent.width
            height: 1
            color: Qt.rgba(255, 255, 255, 0.08)
        }
    }

    // ── Behavior list ────────────────────────────────────────────────────────
    ListView {
        id: behaviorList
        anchors.top: parent.top
        anchors.topMargin: 130
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 12
        spacing: 6
        clip: true
        model: ListModel { id: behaviorModel }

        delegate: Rectangle {
            width: behaviorList.width
            height: 64
            radius: 8
            color: Qt.rgba(255, 255, 255, 0.04)
            border.color: Qt.rgba(255, 255, 255, 0.07)
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 12

                // Confidence color dot
                Rectangle {
                    width: 10; height: 10; radius: 5
                    anchors.verticalCenter: parent.verticalCenter
                    color: {
                        if (model.confidence_level === "high") return "#22c55e"
                        if (model.confidence_level === "medium") return "#f59e0b"
                        return "#6b7280"
                    }
                }

                // Pattern + Choice
                Column {
                    width: 150
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 2
                    Text {
                        text: model.choice || "?"
                        color: themeManager.textColor
                        font.pixelSize: 13
                        font.bold: true
                        elide: Text.ElideRight
                        width: parent.width
                    }
                    Text {
                        text: (model.pattern || "").replace(/_/g, " ")
                        color: Qt.rgba(255, 255, 255, 0.45)
                        font.pixelSize: 10
                        elide: Text.ElideRight
                        width: parent.width
                    }
                }

                // Confidence bar + percentage
                Column {
                    width: 130
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 4

                    Row {
                        spacing: 6
                        // Bar background
                        Rectangle {
                            width: 90
                            height: 6
                            radius: 3
                            color: Qt.rgba(255, 255, 255, 0.1)
                            anchors.verticalCenter: parent.verticalCenter

                            // Fill
                            Rectangle {
                                width: Math.max(4, parent.width * (model.confidence / 100))
                                height: parent.height
                                radius: parent.radius
                                color: {
                                    if (model.confidence_level === "high") return "#22c55e"
                                    if (model.confidence_level === "medium") return "#f59e0b"
                                    return "#6b7280"
                                }
                                Behavior on width { NumberAnimation { duration: 400; easing.type: Easing.OutCubic } }
                            }
                        }

                        Text {
                            text: (model.confidence || 0).toFixed(1) + "%"
                            color: {
                                if (model.confidence_level === "high") return "#22c55e"
                                if (model.confidence_level === "medium") return "#f59e0b"
                                return "#6b7280"
                            }
                            font.pixelSize: 11
                            font.bold: true
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }

                    Text {
                        text: (model.frequency || 0) + " uses · " + (model.days_ago || 0) + "d ago"
                        color: Qt.rgba(255, 255, 255, 0.3)
                        font.pixelSize: 9
                    }
                }

                Item { width: 1; Layout.fillWidth: true }

                // Forget button
                Rectangle {
                    width: 54
                    height: 24
                    radius: 5
                    color: forgetMouse.pressed ? Qt.rgba(239, 68, 68, 0.3) : Qt.rgba(255, 255, 255, 0.05)
                    border.color: Qt.rgba(255, 255, 255, 0.1)
                    border.width: 1
                    anchors.verticalCenter: parent.verticalCenter
                    Behavior on color { ColorAnimation { duration: 100 } }

                    Text {
                        text: "Forget"
                        color: "#ef4444"
                        font.pixelSize: 10
                        anchors.centerIn: parent
                    }

                    MouseArea {
                        id: forgetMouse
                        anchors.fill: parent
                        onClicked: {
                            bridge.forgetBehavior(model.pattern, model.choice)
                            bridge.refreshBehaviors()
                        }
                    }
                }
            }
        }

        // Empty state
        Text {
            anchors.centerIn: parent
            visible: behaviorModel.count === 0
            text: "No behaviors learned yet.\nStart interacting with Friday and\nI'll learn your preferences over time."
            color: Qt.rgba(255, 255, 255, 0.3)
            font.pixelSize: 13
            horizontalAlignment: Text.AlignHCenter
            lineHeight: 1.6
        }
    }

    // ── Bridge connections ────────────────────────────────────────────────────
    Connections {
        target: bridge

        function onBehaviorsReady(behaviors) {
            behaviorModel.clear()
            for (var i = 0; i < behaviors.length; i++) {
                behaviorModel.append(behaviors[i])
            }
        }
    }

    // Load on appear
    Component.onCompleted: bridge.refreshBehaviors()
}
