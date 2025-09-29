import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

ApplicationWindow {
    id: win
    width: 1200
    height: 800
    visible: true
    title: "PyBaMM Parameter Explorer"

    function storedParameterSet() {
        var value = ParamStore.getValue("parameter_set")
        return (value === undefined || value === null) ? "Chen2020" : value
    }

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: 12

            Label {
                text: win.title
                font.pixelSize: 18
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            ComboBox {
                id: presetBox
                Layout.preferredWidth: 220
                model: ["Chen2020", "Marquis2019", "Ecker2015", "Ai2020", "OKane2022", "Custom"]
                editable: false
                currentIndex: Math.max(0, model.indexOf(storedParameterSet()))
                onActivated: function(index) { ParamStore.setValue("parameter_set", model[index]) }

                Connections {
                    target: ParamStore
                    function onChanged(key, value) {
                        if (key === "parameter_set") {
                            var candidate = value
                            if (candidate === undefined || candidate === null)
                                candidate = "Chen2020"
                            var idx = model.indexOf(candidate)
                            if (idx >= 0)
                                presetBox.currentIndex = idx
                        }
                    }
                }
            }

            Button {
                text: "Import"
                onClicked: importDialog.open()
            }

            Button {
                text: "Export"
                onClicked: exportDialog.open()
            }

            Button {
                text: "Run Simulation"
                onClicked: toast.show("Launching PyBaMM with current parameters…")
            }
        }
    }

    SplitView {
        anchors.fill: parent
        handle: Rectangle {
            implicitWidth: 1
            color: "#303030"
        }

        Sidebar {
            id: sidebar
            width: 320
            onSectionSelected: function(catIndex, sectionIndex) { paramForm.currentSection = { category: catIndex, section: sectionIndex } }
        }

        ParamForm {
            id: paramForm
            Layout.fillWidth: true
        }
    }

    Toast { id: toast }

    FileDialog {
        id: importDialog
        title: "Import parameters (.json)"
        nameFilters: ["JSON (*.json)"]
    }

    FileDialog {
        id: exportDialog
        title: "Export parameters (.json/.csv/.dat/.mdf4)"
        nameFilters: ["JSON (*.json)", "CSV (*.csv)", "DAT (*.dat)", "MDF (*.mdf *.mdf4)"]
    }
}
