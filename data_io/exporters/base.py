"""Exporter interfaces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, MutableMapping, Protocol


class Exporter(Protocol):
    """Exporter protocol for persisting datasets to artifacts."""

    format: str

    def export(self, dataset_ref: Dict[str, object], options: Dict[str, object]) -> str:
        ...


@dataclass(slots=True)
class ExporterRegistry:
    """Registry of exporter factories keyed by format."""

    _exporters: MutableMapping[str, Callable[[], Exporter]] = field(default_factory=dict)

    def register(self, fmt: str, factory: Callable[[], Exporter]) -> None:
        if fmt in self._exporters:
            raise ValueError(f"Exporter for '{fmt}' already registered")
        self._exporters[fmt] = factory

    def create(self, fmt: str) -> Exporter:
        try:
            factory = self._exporters[fmt]
        except KeyError as exc:  # pragma: no cover
            raise KeyError(f"No exporter registered for format '{fmt}'") from exc
        return factory()


__all__ = ["Exporter", "ExporterRegistry"]

