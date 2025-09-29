import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var field
    implicitWidth: 640
    implicitHeight: 60

    function currentValue() {
        var value = ParamStore.getValue(field.key)
        if (value === undefined || value === null) {
            if (field.default !== undefined)
                return field.default
            if (field.type === "text")
                return ""
            if (field.type === "bool")
                return false
            if (field.type === "enum" && field.options && field.options.length > 0)
                return field.options[0]
            return 0
        }
        return value
    }

    function clamp(value) {
        if (field.min !== undefined && value < field.min)
            return field.min
        if (field.max !== undefined && value > field.max)
            return field.max
        return value
    }

    RowLayout {
        anchors.fill: parent
        spacing: 12

        ColumnLayout {
            Layout.preferredWidth: 220
            Layout.alignment: Qt.AlignVCenter
            spacing: 2

            Label {
                text: field.label
                wrapMode: Text.Wrap
            }

            Label {
                visible: field.key !== undefined
                text: field.key
                color: "#888888"
                font.pixelSize: 11
                wrapMode: Text.Wrap
            }
        }

        Loader {
            id: editorLoader
            Layout.fillWidth: true
            sourceComponent: (field.type === "number") ? numberEditor
                             : (field.type === "enum") ? enumEditor
                             : (field.type === "bool") ? boolEditor
                             : textEditor
        }

        Label {
            text: field.unit ? field.unit : ""
            color: "#aaaaaa"
            visible: field.unit !== undefined && field.unit !== ""
            Layout.preferredWidth: 64
            horizontalAlignment: Text.AlignRight
        }

        Button {
            text: "↺"
            ToolTip.text: "Reset to default"
            enabled: field.default !== undefined
            onClicked: {
                if (field.default !== undefined)
                    ParamStore.setValue(field.key, field.default)
            }
        }
    }

    Component {
        id: numberEditor

        RowLayout {
            spacing: 8
            Layout.fillWidth: true

            SpinBox {
                id: spin
                Layout.preferredWidth: 150
                from: field.min !== undefined ? field.min : Number.NEGATIVE_INFINITY
                to: field.max !== undefined ? field.max : Number.POSITIVE_INFINITY
                stepSize: field.step !== undefined ? field.step : 0.01
                value: clamp(currentValue())
                editable: true
                validator: DoubleValidator {
                    bottom: field.min !== undefined ? field.min : Number.NEGATIVE_INFINITY
                    top: field.max !== undefined ? field.max : Number.POSITIVE_INFINITY
                }
                onValueModified: ParamStore.setValue(field.key, clamp(value))
            }

            Slider {
                id: slider
                visible: field.min !== undefined && field.max !== undefined
                from: field.min
                to: field.max
                value: spin.value
                stepSize: field.step !== undefined ? field.step : 0
                Layout.fillWidth: true
                onMoved: {
                    spin.value = value
                    ParamStore.setValue(field.key, clamp(value))
                }
            }

            Connections {
                target: ParamStore
                function onChanged(key, value) {
                    if (key === root.field.key) {
                        var newValue = value
                        if (newValue === undefined || newValue === null)
                            newValue = root.field.default
                        spin.value = root.clamp(newValue)
                        if (slider.visible)
                            slider.value = spin.value
                    }
                }
            }
        }
    }

    Component {
        id: enumEditor

        ComboBox {
            id: enumBox
            model: field.options || []
            Layout.fillWidth: true
            currentIndex: Math.max(0, model.indexOf(currentValue()))
            onActivated: ParamStore.setValue(field.key, model[index])

            Connections {
                target: ParamStore
                function onChanged(key, value) {
                    if (key === root.field.key) {
                        var candidate = value
                        if (candidate === undefined || candidate === null)
                            candidate = root.field.default
                        if (candidate === undefined && model.length > 0)
                            candidate = model[0]
                        var idx = model.indexOf(candidate)
                        if (idx >= 0)
                            enumBox.currentIndex = idx
                    }
                }
            }
        }
    }

    Component {
        id: boolEditor

        Switch {
            id: toggle
            checked: !!currentValue()
            onToggled: ParamStore.setValue(field.key, checked)

            Connections {
                target: ParamStore
                function onChanged(key, value) {
                    if (key === root.field.key) {
                        var state = value
                        if (state === undefined || state === null)
                            state = root.field.default
                        toggle.checked = !!state
                    }
                }
            }
        }
    }

    Component {
        id: textEditor

        TextField {
            id: textField
            Layout.fillWidth: true
            text: String(currentValue())
            onEditingFinished: ParamStore.setValue(field.key, text)

            Connections {
                target: ParamStore
                function onChanged(key, value) {
                    if (key === root.field.key) {
                        var textValue = value
                        if (textValue === undefined || textValue === null)
                            textValue = root.field.default !== undefined ? root.field.default : ""
                        textField.text = String(textValue)
                    }
                }
            }
        }
    }
}
