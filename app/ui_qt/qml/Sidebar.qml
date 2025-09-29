import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    width: 320

    signal sectionSelected(int categoryIndex, int sectionIndex)

    property string query: ""
    property bool showAdvanced: false
    property var categories: ParamCatalog.categories()

    Rectangle {
        anchors.fill: parent
        color: "#111111"
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 12
        spacing: 8

        TextField {
            id: search
            placeholderText: "Search parameters…"
            text: root.query
            onTextChanged: root.query = text
        }

        Switch {
            id: advancedSwitch
            text: "Show Advanced"
            checked: root.showAdvanced
            onToggled: root.showAdvanced = checked
        }

        ListView {
            id: catList
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            spacing: 4
            model: root.categories
            delegate: Item {
                width: ListView.view.width
                implicitHeight: categoryColumn.implicitHeight + 12
                property bool isAdvanced: (modelData.id || "") === "advanced"
                property bool visibleSections: false
                property int categoryIndex: index

                function sectionMatches(section) {
                    const query = root.query.trim()
                    if (!query)
                        return true
                    const q = query.toLowerCase()
                    if ((section.label || "").toLowerCase().indexOf(q) !== -1)
                        return true
                    const fields = section.fields || []
                    for (let i = 0; i < fields.length; ++i) {
                        const field = fields[i]
                        if ((field.label || "").toLowerCase().indexOf(q) !== -1)
                            return true
                        if ((field.key || "").toLowerCase().indexOf(q) !== -1)
                            return true
                    }
                    return false
                }

                visible: (root.showAdvanced || !isAdvanced) && visibleSections
                height: visible ? implicitHeight : 0

                function updateVisibility() {
                    visibleSections = false
                    const sections = modelData.sections || []
                    for (let i = 0; i < sections.length; ++i) {
                        if (sectionMatches(sections[i])) {
                            visibleSections = true
                            break
                        }
                    }
                }

                Component.onCompleted: updateVisibility()

                Connections {
                    target: root
                    function onQueryChanged() { updateVisibility() }
                    function onShowAdvancedChanged() { updateVisibility() }
                }


                ColumnLayout {
                    id: categoryColumn
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
                        id: sectionRepeater
                        model: modelData.sections || []
                        delegate: Button {
                            text: modelData.label
                            visible: sectionMatches(modelData)
                            onClicked: root.sectionSelected(categoryIndex, index)
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            onModelChanged: forceLayout()
        }
    }
}
