"""Scenario configuration models used by the simulation orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass(slots=True)
class AmbientConfig:
    """Ambient and environmental parameters for a scenario."""

    temperature_c: float = 25.0
    wind_speed_mps: float = 0.0
    humidity_pct: float = 45.0


@dataclass(slots=True)
class PackConfig:
    """High-level representation of a battery pack configuration."""

    topology: str = "96s10p"
    capacity_ah: float = 100.0
    nominal_voltage_v: float = 350.0
    max_discharge_current_a: float = 250.0
    max_charge_current_a: float = 150.0


@dataclass(slots=True)
class DriveCycleConfig:
    """Drive cycle settings referencing a stored profile."""

    profile_name: str
    source_path: Optional[Path] = None
    sample_rate_hz: float = 10.0


@dataclass(slots=True)
class SolverConfig:
    """Simulation solver options that map to registered solver backends."""

    backend: str = "scipy"
    step_size_s: float = 0.1
    rtol: float = 1e-6
    atol: float = 1e-8
    max_steps: Optional[int] = None


@dataclass(slots=True)
class OutputChannel:
    """Channels requested for persistence or export after a run."""

    name: str
    unit: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass(slots=True)
class ScenarioConfig:
    """Aggregate configuration for a single simulation run."""

    scenario_id: str
    seed: int = 42
    ambient: AmbientConfig = field(default_factory=AmbientConfig)
    pack: PackConfig = field(default_factory=PackConfig)
    drive_cycle: Optional[DriveCycleConfig] = None
    solver: SolverConfig = field(default_factory=SolverConfig)
    output_channels: List[OutputChannel] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def canonical_channels(self) -> List[str]:
        """Return canonical channel identifiers requested for the run."""

        if self.output_channels:
            return [channel.name for channel in self.output_channels]
        # Default channels sourced from the architecture specification
        return [
            "pack.V",
            "pack.I",
            "pack.T_mean",
            "soc",
            "soh",
            "pwr_elec_loss",
            "veh_speed",
            "ambient.T",
        ]

