from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Sequence


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    type: str
    unit: str | None = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    default: Any | None = None
    options: Sequence[str] | None = None

    has_default: bool = False





class ParamCatalog:
    """Lightweight wrapper around the parameter schema for QML."""

    def __init__(self, categories: Sequence[dict[str, Any]]):
        self._categories = list(categories)

        self._fields_by_key: dict[str, dict[str, Any]] = {}
        for category in self._categories:
            for section in category.get("sections", []):
                for field in section.get("fields", []):
                    key = field.get("key")
                    if key:
                        self._fields_by_key[key] = field


    @classmethod
    def from_json(cls, path: str | Path) -> "ParamCatalog":
        schema_path = Path(path)
        with schema_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        categories = data.get("categories", [])
        return cls(categories)

    def categories(self) -> list[dict[str, Any]]:
        return list(self._categories)

    def iter_fields(self) -> Iterator[Field]:
        for category in self._categories:
            for section in category.get("sections", []):
                for field in section.get("fields", []):

                    yield Field(**field, has_default="default" in field)

    def _field_by_key(self, key: str) -> dict[str, Any] | None:
        return self._fields_by_key.get(key)


 

    def field_options(self, key: str) -> list[Any]:
        """Return the option list for an enum field or an empty list."""

        field = self._field_by_key(key)
        if not field:
            return []
        options = field.get("options")
        if options is None:
            return []
        return list(options)

    def field_default(self, key: str) -> Any | None:
        """Return the default value for a field if specified."""

        field = self._field_by_key(key)
        if not field:
            return None
        return field.get("default")
