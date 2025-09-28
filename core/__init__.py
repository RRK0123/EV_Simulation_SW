"""Core simulation package scaffolding.

This module exposes high-level factories for the simulation orchestrator
and supporting services.  The implementation is intentionally lightweight
and focused on wiring so that the project can evolve without carrying
hard dependencies on numerical solvers at this early stage.
"""

from .orchestrator.orchestrator import SimulationOrchestrator
from .orchestrator.scenario import ScenarioConfig

__all__ = [
    "SimulationOrchestrator",
    "ScenarioConfig",
]

