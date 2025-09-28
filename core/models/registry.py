"""Registry for simulation models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, MutableMapping, Optional, Type

from .base import ModelDescriptor, SimulationModel


@dataclass(slots=True)
class ModelRegistry:
    """In-memory registry for available model components."""

    _models: MutableMapping[str, Type[SimulationModel]] = field(default_factory=dict)

    def register(self, name: str, model_cls: Type[SimulationModel]) -> None:
        if name in self._models:
            raise ValueError(f"Model '{name}' already registered")
        self._models[name] = model_cls

    def create(self, name: str, **kwargs) -> SimulationModel:
        try:
            model_cls = self._models[name]
        except KeyError as exc:  # pragma: no cover - simple guard
            raise KeyError(f"Model '{name}' is not registered") from exc
        return model_cls(**kwargs)  # type: ignore[arg-type]

    def registered_models(self) -> Iterable[str]:
        return tuple(self._models.keys())

    def descriptors(self) -> Iterator[ModelDescriptor]:
        for name, model_cls in self._models.items():
            provides = getattr(model_cls, "provides", [])
            depends_on = getattr(model_cls, "depends_on", [])
            yield ModelDescriptor(name=name, provides=provides, depends_on=depends_on, parameters={})


__all__ = ["ModelRegistry"]

