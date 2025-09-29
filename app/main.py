from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from model.param_catalog import ParamCatalog
from model.param_store import ParamStore


def resource_path(relative: str) -> str:
    base_path = Path(__file__).resolve().parent
    return str((base_path / relative).resolve())


def main() -> int:
    app = QGuiApplication(sys.argv)

    schema_path = resource_path("params/params_schema.json")
    catalog = ParamCatalog.from_json(schema_path)
    store = ParamStore(catalog)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("ParamStore", store)
    engine.rootContext().setContextProperty("ParamCatalog", catalog)

    qml_path = resource_path("ui_qt/qml/Main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    if not engine.rootObjects():
        print("QQmlApplicationEngine failed to load component", file=sys.stderr)
        return 1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
