import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: window
    width: 1200
    height: 720
    visible: true
    title: qsTr("EV Simulation Parameter Explorer")

    property var previewData: ({})
    property string statusMessage: ""
    property real progressValue: 0

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: 12

            Label {
                text: qsTr("PyBaMM parameter orchestration")
                font.bold: true
                font.pointSize: 16
                Layout.alignment: Qt.AlignVCenter
            }

            Item { Layout.fillWidth: true }

            Button {
                text: qsTr("Run default scenario")
                onClicked: simulationController.run_scenario()
            }
        }
    }

    footer: ToolBar {
        RowLayout {
            anchors.fill: parent
            spacing: 12

            ProgressBar {
                id: progressBar
                Layout.preferredWidth: 240
                from: 0
                to: 1
                value: window.progressValue
            }

            Label {
                text: window.statusMessage
                Layout.fillWidth: true
                horizontalAlignment: Text.AlignLeft
                elide: Text.ElideRight
            }

            Label {
                text: qsTr("%1 overrides").arg(parameterBridge.dirtyCount)
                Layout.alignment: Qt.AlignRight | Qt.AlignVCenter
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 16

        GroupBox {
            title: qsTr("Presets and filters")
            Layout.fillWidth: true

            GridLayout {
                columns: 6
                columnSpacing: 12
                rowSpacing: 8
                anchors.fill: parent

                Label { text: qsTr("Preset"); Layout.alignment: Qt.AlignVCenter }
                ComboBox {
                    id: presetCombo
                    model: parameterBridge.presets
                    textRole: "label"
                    valueRole: "id"
                    Layout.fillWidth: true
                    onActivated: function(idx) {
                        const value = currentValue !== undefined ? currentValue : parameterBridge.presets[idx].id
                        parameterBridge.applyPreset(value)
                    }
                    Component.onCompleted: {
                        let idx = find(parameterBridge.currentPreset, valueRole)
                        if (idx >= 0) currentIndex = idx
                    }
                }

                Label { text: qsTr("Search"); Layout.alignment: Qt.AlignVCenter }
                TextField {
                    id: searchField
                    placeholderText: qsTr("Filter parameters...")
                    Layout.fillWidth: true
                    onTextChanged: parameterBridge.setSearchQuery(text)
                }

                Label { text: qsTr("Category"); Layout.alignment: Qt.AlignVCenter }
                ComboBox {
                    id: categoryCombo
                    model: parameterBridge.categories
                    Layout.fillWidth: true
                    onActivated: parameterBridge.setCategoryFilter(currentText)
                    Component.onCompleted: {
                        if (model.length > 0) {
                            currentIndex = 0
                            parameterBridge.setCategoryFilter(currentText)
                        }
                    }
                }

                Label { text: qsTr("Advanced") }
                Switch {
                    id: advancedSwitch
                    checked: true
                    onToggled: parameterBridge.setShowAdvanced(checked)
                    Component.onCompleted: parameterBridge.setShowAdvanced(checked)
                }

                Label { text: qsTr("Export name") }
                RowLayout {
                    Layout.columnSpan: 3
                    Layout.fillWidth: true
                    spacing: 8

                    TextField {
                        id: exportNameField
                        Layout.fillWidth: true
                        placeholderText: qsTr("override snapshot name")
                    }

                    Button {
                        text: qsTr("Export")
                        enabled: exportNameField.text.length > 0
                        onClicked: parameterBridge.exportOverrides(exportNameField.text)
                    }

                    Button {
                        text: qsTr("Import")
                        enabled: exportNameField.text.length > 0
                        onClicked: parameterBridge.importOverrides(exportNameField.text)
                    }
                }

                Item { Layout.columnSpan: 2; Layout.fillWidth: true }

                Button {
                    text: qsTr("Reset all overrides")
                    Layout.alignment: Qt.AlignRight
                    onClicked: parameterBridge.resetOverrides()
                }
            }
        }

        SplitView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            orientation: Qt.Horizontal

            Frame {
                id: parameterPane
                SplitView.preferredWidth: 700
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8

                    Label {
                        text: qsTr("Parameters")
                        font.bold: true
                        font.pointSize: 14
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        ListView {
                            id: parameterList
                            model: parameterBridge.model
                            clip: true
                            spacing: 12
                            delegate: parameterDelegate
                        }
                    }
                }
            }

            Frame {
                id: diffPane
                SplitView.preferredWidth: 320
                ColumnLayout {
                    anchors.fill: parent
                    spacing: 8

                    Label {
                        text: qsTr("Overrides diff")
                        font.bold: true
                        font.pointSize: 14
                    }

                    ScrollView {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200

                        ListView {
                            id: diffList
                            model: parameterBridge.diffModel
                            clip: true
                            spacing: 8
                            delegate: diffDelegate
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        radius: 6
                        color: Qt.rgba(0.95, 0.95, 0.97, 1)

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 6

                            Label {
                                text: qsTr("Preview")
                                font.bold: true
                                font.pointSize: 14
                            }

                            Repeater {
                                model: Object.keys(window.previewData)
                                delegate: RowLayout {
                                    Label { text: modelData + ":"; Layout.preferredWidth: 160 }
                                    Label { text: String(window.previewData[modelData]); Layout.fillWidth: true }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    Component {
        id: parameterDelegate

        ColumnLayout {
            width: parent ? parent.width : implicitWidth
            spacing: 4

            Label {
                text: label + (unit.length > 0 ? " [" + unit + "]" : "")
                font.bold: true
            }

            Label {
                visible: description.length > 0
                text: description
                color: "#555"
                wrapMode: Text.WordWrap
            }

            Loader {
                Layout.fillWidth: true
                sourceComponent: {
                    switch (type) {
                    case "bool": return boolEditor;
                    case "enum": return enumEditor;
                    default: return numberEditor;
                    }
                }
            }

            Label {
                visible: category !== ""
                text: qsTr("Category: %1").arg(category)
                font.pixelSize: 12
                color: "#888"
            }

            Rectangle {
                visible: dirty
                color: Qt.rgba(1, 0.9, 0.8, 1)
                radius: 4
                Layout.fillWidth: true
                height: 24

                Label {
                    anchors.centerIn: parent
                    text: qsTr("Override: %1 (default %2)").arg(value).arg(defaultValue)
                    font.pixelSize: 11
                }
            }

            Rectangle { height: 1; width: parent.width; color: Qt.rgba(0,0,0,0.1) }
        }
    }

    Component {
        id: boolEditor
        RowLayout {
            Switch {
                checked: !!value
                onToggled: model.value = checked
            }
        }
    }

    Component {
        id: enumEditor
        RowLayout {
            ComboBox {
                Layout.fillWidth: true
                model: choices
                textRole: "label"
                valueRole: "value"
                onActivated: model.value = currentValue
                Component.onCompleted: {
                    let idx = find(value)
                    if (idx >= 0) currentIndex = idx
                }
            }
        }
    }

    Component {
        id: numberEditor
        ColumnLayout {
            spacing: 4

            RowLayout {
                spacing: 8
                TextField {
                    id: numericField
                    text: String(value)
                    Layout.fillWidth: true
                    inputMethodHints: Qt.ImhFormattedNumbersOnly
                    onEditingFinished: {
                        const trimmed = text.trim()
                        const parsed = Number(trimmed)

                        if (!Number.isFinite(parsed)) {
                            text = String(value)
                            return
                        }

                        model.value = parsed
                        text = String(parsed)
                    }
                }
                Label { text: qsTr("default %1").arg(defaultValue) }
            }

            Slider {
                visible: minimum !== undefined && maximum !== undefined
                Layout.fillWidth: true
                from: minimum !== undefined ? minimum : 0
                to: maximum !== undefined ? maximum : 1
                stepSize: step !== undefined ? step : 0
                value: value
                onMoved: {
                    model.value = value
                    numericField.text = value.toFixed(6)
                }
            }
        }
    }

    Component {
        id: diffDelegate
        RowLayout {
            width: parent ? parent.width : implicitWidth
            spacing: 6

            Label {
                text: label
                font.bold: true
                Layout.fillWidth: true
            }

            Label {
                text: String(value)
            }

            Label {
                text: qsTr("default %1").arg(defaultValue)
                color: "#777"
            }
        }
    }

    Connections {
        target: simulationController
        onRunCompleted: window.statusMessage = message
        onRunFailed: window.statusMessage = message
    }

    Connections {
        target: parameterBridge
        onPreviewReady: window.previewData = data
        onProgressUpdated: function(label, pct) {
            window.statusMessage = label
            window.progressValue = pct
        }
        onErrorOccurred: function(message) {
            window.statusMessage = message
        }
    }
}
