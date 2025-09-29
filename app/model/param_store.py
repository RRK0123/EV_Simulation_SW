from __future__ import annotations

from typing import Any, Dict, Iterator, Tuple


from PySide6.QtCore import QObject, Property, Signal, Slot


class ParamStore(QObject):
    """Mutable storage of parameter values exposed to QML."""

    changed = Signal(str, "QVariant")


    def __init__(self, catalog, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._catalog = catalog

        self._values: Dict[str, Any] = dict(self._iter_default_items())

    def _iter_default_items(self) -> Iterator[Tuple[str, Any]]:
        for field in self._catalog.iter_fields():
            if getattr(field, "has_default", False):
                yield field.key, field.default


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

    @Slot("QVariantMap")
    def setValues(self, values: Dict[str, Any]) -> None:
        for key, value in values.items():
            self.setValue(key, value)

    @Property("QVariant", constant=True)
    def values(self) -> Dict[str, Any]:  # noqa: D401

        return dict(self._values)

    @Slot(result="QVariant")
    def defaults(self) -> Dict[str, Any]:
        return dict(self._iter_default_items())
