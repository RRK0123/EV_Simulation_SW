import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: root
    property var currentSection: ({ category: 0, section: 0 })
    property var categories: ParamCatalog.categories
    property string query: ""
    property bool showAdvanced: false

    function safeCategory(index) {
        const cats = root.categories
        if (!cats || index < 0 || index >= cats.length)
            return null
        return cats[index]
    }

    function safeSection(catIndex, sectionIndex) {
        const category = safeCategory(catIndex)
        if (!category)
            return null
        const sections = category.sections || []
        if (sectionIndex < 0 || sectionIndex >= sections.length)
            return null
        return sections[sectionIndex]
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 10

        Label {
            id: header
            text: {
                const category = safeCategory(root.currentSection.category)
                const section = safeSection(root.currentSection.category, root.currentSection.section)
                if (!category || !section)
                    return "Select a section"
                return category.label + " · " + section.label
            }
            font.pixelSize: 18
        }

        ScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ColumnLayout {
                id: fieldColumn
                spacing: 12
                width: parent.width

                Repeater {
                    id: fieldRepeater
                    objectName: "fieldRepeater"
                    model: {
                        const section = safeSection(root.currentSection.category, root.currentSection.section)
                        return section ? section.fields || [] : []
                    }
                    delegate: ParamField {
                        field: modelData
                        visible: {
                            const isAdvanced = !!field.advanced
                            const matchesAdvanced = root.showAdvanced || !isAdvanced
                            const q = (root.query || "").toLowerCase()
                            const label = String(field.label || "").toLowerCase()
                            const key = String(field.key || "").toLowerCase()
                            const matchesQuery = !q || label.indexOf(q) !== -1 || key.indexOf(q) !== -1
                            return matchesAdvanced && matchesQuery
                        }
                    }
                }
            }
        }
    }
}
