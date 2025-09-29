import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: root
    property var currentSection: ({ category: 0, section: 0 })
    property var categories: ParamCatalog.categories()

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
                    model: {
                        const section = safeSection(root.currentSection.category, root.currentSection.section)
                        return section ? section.fields || [] : []
                    }
                    delegate: ParamField {
                        field: modelData
                    }
                }
            }
        }
    }
}
