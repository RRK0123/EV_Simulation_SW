from __future__ import annotations

import sys
from pathlib import Path
from json import JSONDecodeError

import logging

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from model.param_catalog import ParamCatalog
from model.param_store import ParamStore
from model.exporters import (
    export_params_csv,
    export_params_dat,
    export_params_json,
    read_params_dat,
    read_params_json,
)
from model.units_adapter import convert_to_si
from model.runner import extract_series, run as run_sim
from model.exporters import export_timeseries_csv, export_timeseries_mdf4


def resource_path(relative: str) -> str:
    base_path = Path(__file__).resolve().parent
    return str((base_path / relative).resolve())


logger = logging.getLogger(__name__)


class Bridge(QObject):
    errorOccurred = Signal(str)
    infoOccurred = Signal(str)

    def __init__(self, store: ParamStore, catalog: ParamCatalog) -> None:
        super().__init__()
        self._store = store
        self._catalog = catalog

    @staticmethod
    def _normalize_path(path: str) -> str:
        url = QUrl(path)
        if url.isLocalFile():
            return url.toLocalFile()
        return path

    def _emit_error(self, message: str, *, exc: Exception | None = None) -> None:
        if exc is not None:
            logger.error("%s", message, exc_info=exc)
        else:
            logger.error("%s", message)
        self.errorOccurred.emit(message)

    def _emit_info(self, message: str) -> None:
        logger.info("%s", message)
        self.infoOccurred.emit(message)

    @Slot(str)
    def importParams(self, path: str) -> None:  # noqa: N802 - Qt slot naming
        normalized = self._normalize_path(path)
        try:
            lower = normalized.lower()
            if lower.endswith(".json"):
                values = read_params_json(normalized)
            elif lower.endswith(".dat"):
                values = read_params_dat(normalized)
            else:
                self._emit_error("Unsupported parameter file type: expected .json or .dat")
                return
            self._store.setValues(values)
            self._emit_info("Parameters imported successfully")
        except (FileNotFoundError, JSONDecodeError, OSError, ValueError) as exc:
            self._emit_error(f"Import failed: {exc}", exc=exc)

    @Slot(str, str)
    def exportParams(self, path: str, fmt: str) -> None:  # noqa: N802
        normalized = self._normalize_path(path)
        target = Path(normalized)
        if target.parent:
            target.parent.mkdir(parents=True, exist_ok=True)
        values = self._store.values
        schema = self._catalog.categories_schema()
        values_si = convert_to_si(values, schema)
        try:
            if fmt == "csv":
                export_params_csv(target, values_si)
            elif fmt == "dat":
                export_params_dat(target, values_si)
            else:
                export_params_json(target, values_si)
            self._emit_info(f"Parameters exported to {target}")
        except (FileNotFoundError, PermissionError) as exc:
            self._emit_error(f"Export failed: {exc}", exc=exc)
        except OSError as exc:
            self._emit_error(f"Export failed: {exc}", exc=exc)

    @Slot(str, str)
    def runSimulation(self, path: str, fmt: str) -> None:  # noqa: N802
        normalized = self._normalize_path(path)
        target = Path(normalized)
        if target.parent:
            target.parent.mkdir(parents=True, exist_ok=True)
        try:
            solution, _context = run_sim(self._store.values, self._catalog.categories_schema())
            series = extract_series(solution)
            if fmt.lower() == "mdf4":
                export_timeseries_mdf4(target, series)
            else:
                export_timeseries_csv(target, series)
            self._emit_info(f"Simulation completed. Results saved to {target}")
        except RuntimeError as exc:
            self._emit_error(f"Simulation failed: {exc}", exc=exc)
        except (FileNotFoundError, PermissionError) as exc:
            self._emit_error(f"Simulation failed: {exc}", exc=exc)
        except OSError as exc:
            self._emit_error(f"Simulation failed: {exc}", exc=exc)


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    app = QGuiApplication(sys.argv)

    schema_path = resource_path("params/params_schema.json")
    catalog = ParamCatalog.from_json(schema_path)
    store = ParamStore(catalog)
    bridge = Bridge(store, catalog)

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("ParamStore", store)
    engine.rootContext().setContextProperty("ParamCatalog", catalog)
    engine.rootContext().setContextProperty("Bridge", bridge)

    qml_path = resource_path("ui_qt/qml/Main.qml")
    engine.load(QUrl.fromLocalFile(qml_path))

    root_objects = engine.rootObjects()
    if not root_objects:
        print("QQmlApplicationEngine failed to load component", file=sys.stderr)
        return 1

    root = root_objects[0]
    root.exportRequested.connect(bridge.exportParams)
    root.importRequested.connect(bridge.importParams)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
