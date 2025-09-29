import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    id: win
    width: 1200
    height: 800
    visible: true

    title: qsTr("PyBaMM Parameter Explorer")

    signal exportRequested(string path, string fmt)
    signal importRequested(string path)

    readonly property var paramCatalog: (typeof ParamCatalog !== "undefined" && ParamCatalog !== null) ? ParamCatalog : null
    readonly property var paramStore: (typeof ParamStore !== "undefined" && ParamStore !== null) ? ParamStore : null
    readonly property var bridge: (typeof Bridge !== "undefined" && Bridge !== null) ? Bridge : null

    function storedParameterSet() {
        if (!paramStore)
            return ""

        var value = paramStore.getValue("parameter_set")
        if (value !== undefined && value !== null && value !== "")
            return value

        if (!paramCatalog)
            return value !== undefined ? value : ""

        var fallback = paramCatalog.field_default("parameter_set")
        if (fallback !== undefined && fallback !== null && fallback !== "")
            return fallback

        var options = paramCatalog.field_options("parameter_set")
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
                property var presetOptions: paramCatalog ? paramCatalog.field_options("parameter_set") : []
                model: presetOptions
                editable: false
                currentIndex: presetOptions.length > 0 ? Math.max(0, presetOptions.indexOf(storedParameterSet())) : -1
                onActivated: function(index) {
                    if (!paramStore)
                        return
                    if (index >= 0 && index < presetOptions.length)
                        paramStore.setValue("parameter_set", presetOptions[index])
                }

                Connections {
                    target: paramStore
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
                onClicked: resultsDialog.open()
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
            objectName: "sidebar"
            width: 320
            onSectionSelected: function(catIndex, sectionIndex) {
                paramForm.currentSection = { category: catIndex, section: sectionIndex }
            }
        }

        ParamForm {
            id: paramForm
            objectName: "paramForm"
            Layout.fillWidth: true
            query: sidebar.query
            showAdvanced: sidebar.showAdvancedChecked
        }
    }

    Toast { id: toast }

    FileDialog {
        id: importDialog
        title: qsTr("Import parameters (.json/.dat)")
        nameFilters: [qsTr("JSON (*.json)"), qsTr("DAT (*.dat)")]
        onAccepted: win.importRequested(selectedFile)
    }

    FileDialog {
        id: exportDialog
        title: qsTr("Export parameters")
        nameFilters: [
            qsTr("JSON (*.json)"),
            qsTr("CSV (*.csv)"),
            qsTr("DAT (*.dat)")
        ]
        onAccepted: {
            const path = selectedFile
            let fmt = "json"
            if (path.endsWith(".csv")) fmt = "csv"
            else if (path.endsWith(".dat")) fmt = "dat"
            win.exportRequested(path, fmt)
            toast.show(qsTr("Parameters exported"))
        }
    }

    FileDialog {
        id: resultsDialog
        title: qsTr("Save results (CSV or MDF4)")
        nameFilters: [qsTr("CSV (*.csv)"), qsTr("MDF4 (*.mf4)")]
        onAccepted: {
            const path = selectedFile
            let fmt = path.endsWith(".mf4") ? "mdf4" : "csv"
            if (bridge)
                bridge.runSimulation(path, fmt)
            toast.show(qsTr("Simulation started… results will be saved to: ") + path)
        }
    }
}
