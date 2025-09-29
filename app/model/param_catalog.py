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


class ParamCatalog:
    """Lightweight wrapper around the parameter schema for QML."""

    def __init__(self, categories: Sequence[dict[str, Any]]):
        self._categories = list(categories)

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
                    yield Field(**field)
