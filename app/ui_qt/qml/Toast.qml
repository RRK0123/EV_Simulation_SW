import QtQuick 2.15
import QtQuick.Controls 2.15

Popup {
    id: popup
    x: parent ? (parent.width - width) / 2 : 0
    y: 40
    modal: false
    focus: false
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    background: Rectangle {
        radius: 8
        color: "#333333"
        border.color: "#555555"
    }

    contentItem: Label {
        id: messageLabel
        padding: 12
        color: "white"
        wrapMode: Text.Wrap
    }

    function show(msg) {
        messageLabel.text = msg
        open()
        hideTimer.restart()
    }

    Timer {
        id: hideTimer
        interval: 2400
        running: false
        repeat: false
        onTriggered: popup.close()
    }
}
