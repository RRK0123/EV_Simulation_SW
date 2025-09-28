"""Placeholder SciPy-like solver backend."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Iterable

from .base import SolverBackend


@dataclass(slots=True)
class DummySciPySolver(SolverBackend):
    """Emulates a SciPy solver for scaffold purposes."""

    name: str = "scipy"
    max_steps: int = 1

    def configure(self, **options) -> None:
        self.max_steps = int(options.get("max_steps", self.max_steps))

    def solve(self, step_fn: Callable[[float, Dict[str, float]], Dict[str, float]]) -> Iterable[Dict[str, float]]:
        state: Dict[str, float] = {}
        time_s = 0.0
        timestep = 0.1
        for _ in range(self.max_steps):
            state = step_fn(time_s, state)
            time_s += timestep
            yield {"time_s": time_s, **state}


__all__ = ["DummySciPySolver"]

