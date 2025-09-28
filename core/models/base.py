"""Base abstractions for simulation models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Protocol


class ModelContext(Protocol):
    """Context object passed to models when evaluating the system."""

    seed: int
    time_s: float
    timestep_s: float


class SimulationModel(Protocol):
    """Lightweight contract for simulation models."""

    name: str

    def configure(self, parameters: Dict[str, float]) -> None:
        ...

    def initial_state(self) -> Dict[str, float]:
        ...

    def evaluate(self, context: ModelContext, state: Dict[str, float]) -> Dict[str, float]:
        ...


@dataclass(slots=True)
class ModelDescriptor:
    """Metadata describing a model instance in the DAG."""

    name: str
    provides: Iterable[str]
    depends_on: Iterable[str]
    parameters: Dict[str, float]

