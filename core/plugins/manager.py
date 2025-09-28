"""Plugin discovery and lifecycle management."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from importlib import metadata
from typing import Dict, Iterable, MutableMapping


LOGGER = logging.getLogger(__name__)

ENTRY_POINT_GROUP = "ev_simulation.plugins"


@dataclass(slots=True)
class PluginSpec:
    name: str
    version: str
    module: str
    obj: str


@dataclass(slots=True)
class PluginManager:
    """Python entry-point based plugin loader."""

    _loaded_plugins: MutableMapping[str, object] = field(default_factory=dict)

    def discover(self) -> Iterable[PluginSpec]:
        for entry_point in metadata.entry_points(group=ENTRY_POINT_GROUP):
            name = entry_point.name
            module, _, obj = entry_point.value.partition(":")
            version = metadata.version(entry_point.module)
            yield PluginSpec(name=name, version=version, module=module, obj=obj)

    def load(self) -> None:
        for spec in self.discover():
            try:
                module = importlib.import_module(spec.module)
                plugin = getattr(module, spec.obj) if spec.obj else module
                self._loaded_plugins[spec.name] = plugin
                LOGGER.info("Loaded plugin %s (%s)", spec.name, spec.version)
            except Exception as exc:  # pragma: no cover - defensive log
                LOGGER.exception("Failed to load plugin %s", spec.name, exc_info=exc)

    def unload(self) -> None:
        self._loaded_plugins.clear()

    def get(self, name: str) -> object:
        return self._loaded_plugins[name]


__all__ = ["PluginManager", "PluginSpec", "ENTRY_POINT_GROUP"]

