import QtQuick
import QtQuick.Controls

Popup {
    id: popup
    x: parent ? (parent.width - width) / 2 : 0
    y: 40
    modal: false
    focus: false
    closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside

    property color infoColor: "#333333"
    property color successColor: "#2e7d32"
    property color errorColor: "#b00020"

    background: Rectangle {
        id: backgroundRect
        radius: 8
        color: popup.infoColor
        border.color: "#555555"
    }

    contentItem: Label {
        id: messageLabel
        padding: 12
        color: "white"
        wrapMode: Text.Wrap
    }

    function showMessage(msg, color) {
        messageLabel.text = msg
        backgroundRect.color = color
        open()
        hideTimer.restart()
    }

    function show(msg) {
        showMessage(msg, popup.infoColor)
    }

    function showInfo(msg) {
        showMessage(msg, popup.infoColor)
    }

    function showSuccess(msg) {
        showMessage(msg, popup.successColor)
    }

    function showError(msg) {
        showMessage(msg, popup.errorColor)
    }

    Timer {
        id: hideTimer
        interval: 2400
        running: false
        repeat: false
        onTriggered: popup.close()
    }
}
