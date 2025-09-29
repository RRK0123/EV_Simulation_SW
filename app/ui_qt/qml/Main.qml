import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3

ApplicationWindow {
    id: win
    width: 1200
    height: 800
    visible: true
    title: qsTr("PyBaMM Parameter Explorer")

    function storedParameterSet() {
        var value = ParamStore.getValue("parameter_set")
        if (value !== undefined && value !== null && value !== "")
            return value

        var fallback = ParamCatalog.field_default("parameter_set")
        if (fallback !== undefined && fallback !== null && fallback !== "")
            return fallback

        var options = ParamCatalog.field_options("parameter_set")
        return options.length > 0 ? options[0] : ""
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
                property var presetOptions: ParamCatalog.field_options("parameter_set")
                model: presetOptions
                editable: false
                currentIndex: presetOptions.length > 0 ? Math.max(0, presetOptions.indexOf(storedParameterSet())) : -1
                onActivated: function(index) {
                    if (index >= 0 && index < presetOptions.length)
                        ParamStore.setValue("parameter_set", presetOptions[index])
                }

                Connections {
                    target: ParamStore
                    function onChanged(key, value) {
                        if (key === "parameter_set") {
                            var candidate = value
                            if (candidate === undefined || candidate === null || candidate === "")
                                candidate = storedParameterSet()
                            var idx = presetOptions.indexOf(candidate)
                            if (idx >= 0)
                                presetBox.currentIndex = idx
                        }
                    }
                }
            }

            Button {
                text: qsTr("Import")
                onClicked: importDialog.open()
            }

            Button {
                text: qsTr("Export")
                onClicked: exportDialog.open()
            }

            Button {
                text: qsTr("Run Simulation")
                onClicked: toast.show(qsTr("Launching PyBaMM with current parameters…"))
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
        title: qsTr("Import parameters (.json)")
        nameFilters: [qsTr("JSON (*.json)")]
    }

    FileDialog {
        id: exportDialog
        title: qsTr("Export parameters (.json/.csv/.dat/.mdf4)")
        nameFilters: [
            qsTr("JSON (*.json)"),
            qsTr("CSV (*.csv)"),
            qsTr("DAT (*.dat)"),
            qsTr("MDF (*.mdf *.mdf4)")
        ]
    }
}
