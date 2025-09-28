import QtQuick
import QtQuick.Controls
import EVSim 1.0

ApplicationWindow {
    id: root
    width: 960
    height: 600
    visible: true
    title: qsTr("EV Simulation Studio")

    property string currentRunId: ""

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        GroupBox {
            title: qsTr("Scenario Setup")
            Layout.fillWidth: true

            ColumnLayout {
                anchors.fill: parent
                Layout.margins: 12

                TextField {
                    id: scenarioIdField
                    Layout.fillWidth: true
                    placeholderText: qsTr("Scenario ID")
                    text: "WLTP_25C"
                }

                Button {
                    text: qsTr("Run Simulation")
                    onClicked: {
                        const scenario = {
                            scenario_id: scenarioIdField.text,
                            seed: 42,
                            solver: { backend: "scipy", step_size_s: 0.1 }
                        }
                        root.currentRunId = Orchestrator.runScenario(scenario)
                    }
                }
            }
        }

        GroupBox {
            title: qsTr("Run Metadata")
            Layout.fillWidth: true
            Layout.fillHeight: true

            ScrollView {
                anchors.fill: parent

                TextArea {
                    anchors.fill: parent
                    readOnly: true
                    text: JSON.stringify(Orchestrator.fetchRunMetadata(root.currentRunId), null, 2)
                }
            }
        }
    }
}

