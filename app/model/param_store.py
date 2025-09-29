from __future__ import annotations

from typing import Any, Dict

from PySide6.QtCore import QObject, Property, Signal, Slot


class ParamStore(QObject):
    """Mutable storage of parameter values exposed to QML."""

    changed = Signal(str, "QVariant")

    def __init__(self, catalog, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._catalog = catalog
        self._values: Dict[str, Any] = {}
        self._load_defaults()

    def _load_defaults(self) -> None:
        for category in self._catalog.categories():
            for section in category.get("sections", []):
                for field in section.get("fields", []):
                    if "default" in field:
                        self._values[field["key"]] = field["default"]

    @Slot(str, "QVariant")
    def setValue(self, key: str, value: Any) -> None:  # noqa: N802 - Qt slot naming
        if value is None and key in self._values:
            del self._values[key]
        else:
            self._values[key] = value
        self.changed.emit(key, value)

    @Slot(str, result="QVariant")
    def getValue(self, key: str) -> Any:  # noqa: N802 - Qt slot naming
        return self._values.get(key)

    @Property("QVariant", constant=True)
    def values(self) -> Dict[str, Any]:  # noqa: D401
        return self._values.copy()

    @Slot(result="QVariant")
    def defaults(self) -> Dict[str, Any]:
        defaults: Dict[str, Any] = {}
        for category in self._catalog.categories():
            for section in category.get("sections", []):
                for field in section.get("fields", []):
                    if "default" in field:
                        defaults[field["key"]] = field["default"]
        return defaults
