import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    width: 320

    signal sectionSelected(int categoryIndex, int sectionIndex)

    property alias query: search.text
    property alias showAdvancedChecked: showAdvanced.checked
    readonly property var paramCatalog: (typeof ParamCatalog !== "undefined" && ParamCatalog !== null) ? ParamCatalog : null

    Rectangle {
        anchors.fill: parent
        color: "#111111"
    }

    function visibleFields(section) {
        const q = (search.text || "").toLowerCase()
        const advanced = showAdvanced.checked
        const fields = section.fields || []
        const matches = []
        for (let i = 0; i < fields.length; ++i) {
            const field = fields[i]
            const isAdvanced = !!field.advanced
            const label = String(field.label || "").toLowerCase()
            const key = String(field.key || "").toLowerCase()
            const matchQuery = !q || label.indexOf(q) !== -1 || key.indexOf(q) !== -1
            const matchAdvanced = advanced || !isAdvanced
            if (matchQuery && matchAdvanced)
                matches.push(field)
        }
        return matches
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        TextField {
            id: search
            placeholderText: qsTr("Search parameters…")
        }

        CheckBox {
            id: showAdvanced
            text: qsTr("Show Advanced")
        }

        ListView {
            id: catList
            objectName: "categoryList"
            Layout.fillWidth: true
            Layout.fillHeight: true
            model: root.paramCatalog ? root.paramCatalog.categories : []
            clip: true
            delegate: Frame {
                width: ListView.view.width
                property int categoryIndex: index

                readonly property bool hasVisibleSections: {
                    const sections = modelData.sections || []
                    if (!search.text)
                        return true
                    for (let i = 0; i < sections.length; ++i) {
                        if (visibleFields(sections[i]).length > 0)
                            return true
                    }
                    return false
                }

                visible: hasVisibleSections
                height: visible ? implicitHeight : 0

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 6
                    spacing: 6

                    Label {
                        text: modelData.label
                        font.bold: true
                        color: "#eeeeee"
                        wrapMode: Text.Wrap
                    }

                    Repeater {
                        model: modelData.sections || []
                        delegate: Button {
                            Layout.fillWidth: true
                            text: modelData.label
                            visible: visibleFields(modelData).length > 0 || search.text.length === 0
                            onClicked: root.sectionSelected(categoryIndex, index)
                        }
                    }
                }
            }
        }
    }
}
