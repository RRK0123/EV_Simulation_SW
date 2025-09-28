"""Placeholder battery pack model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .base import ModelContext, SimulationModel


@dataclass(slots=True)
class BatteryPackModel(SimulationModel):
    """Simplified battery pack representation for scaffolding purposes."""

    name: str = "battery_pack"
    provides = ("pack.V", "pack.I", "soc")
    depends_on = tuple()
    _params: Dict[str, float] = field(default_factory=dict)

    def configure(self, parameters: Dict[str, float]) -> None:
        self._params.update(parameters)

    def initial_state(self) -> Dict[str, float]:
        return {"soc": self._params.get("soc_init", 1.0)}

    def evaluate(self, context: ModelContext, state: Dict[str, float]) -> Dict[str, float]:
        soc = max(0.0, state.get("soc", 1.0) - 1e-4 * context.timestep_s)
        voltage = self._params.get("voltage_nominal", 350.0) * soc
        current = self._params.get("current_nominal", 0.0)
        return {"soc": soc, "pack.V": voltage, "pack.I": current}


__all__ = ["BatteryPackModel"]

