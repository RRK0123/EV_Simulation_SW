import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    id: window
    width: 480
    height: 320
    visible: true
    title: qsTr("EV Simulation")

    Column {
        anchors.centerIn: parent
        spacing: 12

        Text {
            text: qsTr("EV Simulation Framework")
            font.pointSize: 18
            horizontalAlignment: Text.AlignHCenter
            width: parent.width
        }

        Button {
            text: qsTr("Run default scenario")
            onClicked: simulationController.run_scenario()
        }

        Label {
            id: statusLabel
            width: parent.width
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.Wrap
        }
    }

    Connections {
        target: simulationController
        onRunCompleted: statusLabel.text = message
        onRunFailed: statusLabel.text = message
    }
}
