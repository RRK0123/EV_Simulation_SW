"""Integration tests for the Qt Quick parameter UI."""

import os

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QCoreApplication, QObject, QUrl  # noqa: E402  (import after skip)
from PySide6.QtGui import QGuiApplication  # noqa: E402
from PySide6.QtQml import QQmlApplicationEngine  # noqa: E402

from app.main import Bridge, resource_path  # noqa: E402
from app.model.param_catalog import ParamCatalog  # noqa: E402
from app.model.param_store import ParamStore  # noqa: E402


@pytest.fixture(scope="module")
def qapp():
    """Provide a shared QApplication instance for Qt tests."""

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication.instance()
    if app is None:
        app = QGuiApplication([])
    return app


@pytest.fixture()
def loaded_main(qapp):
    """Load the main QML scene with the production context objects."""

    engine = QQmlApplicationEngine()
    catalog = ParamCatalog.from_json(
        resource_path("params/params_schema.json"), parent=engine
    )
    store = ParamStore(catalog, parent=engine)
    bridge = Bridge(store, catalog)
    bridge.setParent(engine)
    context = engine.rootContext()
    context.setContextProperty("ParamCatalog", catalog)
    context.setContextProperty("ParamStore", store)
    context.setContextProperty("Bridge", bridge)

    engine.load(QUrl.fromLocalFile(resource_path("ui_qt/qml/Main.qml")))
    assert engine.rootObjects(), "Main QML failed to load"

    QCoreApplication.processEvents()
    root = engine.rootObjects()[0]

    yield {
        "root": root,
        "engine": engine,
        "catalog": catalog,
        "store": store,
        "bridge": bridge,
    }

    engine.deleteLater()


def test_sidebar_lists_categories(loaded_main):
    """The sidebar should expose at least one category in the list view."""

    root = loaded_main["root"]
    sidebar = root.findChild(QObject, "sidebar")
    assert sidebar is not None, "Sidebar component should be discoverable"

    category_list = sidebar.findChild(QObject, "categoryList")
    assert category_list is not None, "Sidebar should expose the category list view"
    assert category_list.property("count") > 0


def test_param_form_populates_fields(loaded_main):
    """The parameter form should instantiate editors for the active section."""

    root = loaded_main["root"]
    param_form = root.findChild(QObject, "paramForm")
    assert param_form is not None, "Parameter form should be discoverable"

    repeater = param_form.findChild(QObject, "fieldRepeater")
    assert repeater is not None, "Field repeater should exist in the parameter form"

    QCoreApplication.processEvents()
    assert repeater.property("count") > 0
