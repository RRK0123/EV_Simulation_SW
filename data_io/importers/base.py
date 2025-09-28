"""Importer interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, MutableMapping, Protocol, Tuple


class Importer(Protocol):
    """Importer protocol for data ingestion."""

    format: str

    def import_file(self, path: str, mapping: Dict[str, str]) -> Tuple[Iterable[Dict[str, float]], Dict[str, str]]:
        ...


@dataclass(slots=True)
class ImporterRegistry:
    """Registry of importer factories keyed by format."""

    _importers: MutableMapping[str, Callable[[], Importer]] = field(default_factory=dict)

    def register(self, fmt: str, factory: Callable[[], Importer]) -> None:
        if fmt in self._importers:
            raise ValueError(f"Importer for '{fmt}' already registered")
        self._importers[fmt] = factory

    def create(self, fmt: str) -> Importer:
        try:
            factory = self._importers[fmt]
        except KeyError as exc:  # pragma: no cover
            raise KeyError(f"No importer registered for format '{fmt}'") from exc
        return factory()


__all__ = ["Importer", "ImporterRegistry"]

