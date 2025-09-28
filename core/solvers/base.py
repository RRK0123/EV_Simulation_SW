"""Solver interfaces and registry."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Iterator, MutableMapping, Protocol


class SolverBackend(Protocol):
    """Protocol describing a solver backend."""

    name: str

    def configure(self, **options) -> None:
        ...

    def solve(self, step_fn: Callable[[float, Dict[str, float]], Dict[str, float]]) -> Iterable[Dict[str, float]]:
        ...


@dataclass(slots=True)
class SolverRegistry:
    """Registry that holds solver backend factories."""

    _solvers: MutableMapping[str, Callable[[], SolverBackend]] = field(default_factory=dict)

    def register(self, name: str, factory: Callable[[], SolverBackend]) -> None:
        if name in self._solvers:
            raise ValueError(f"Solver '{name}' already registered")
        self._solvers[name] = factory

    def create(self, name: str) -> SolverBackend:
        try:
            factory = self._solvers[name]
        except KeyError as exc:  # pragma: no cover - guard clause
            raise KeyError(f"Solver '{name}' is not registered") from exc
        return factory()

    def registered_solvers(self) -> Iterator[str]:
        return iter(self._solvers.keys())


__all__ = ["SolverRegistry", "SolverBackend"]

