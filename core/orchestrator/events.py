"""Event and telemetry primitives emitted by the orchestrator."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable


@dataclass(slots=True)
class RunStarted:
    run_id: str
    scenario_id: str
    timestamp: datetime


@dataclass(slots=True)
class RunProgress:
    run_id: str
    scenario_id: str
    timestamp: datetime
    progress_pct: float
    sim_time_s: float


@dataclass(slots=True)
class RunCompleted:
    run_id: str
    scenario_id: str
    timestamp: datetime
    artifacts: Iterable[str]


@dataclass(slots=True)
class RunFailed:
    run_id: str
    scenario_id: str
    timestamp: datetime
    error_code: str
    message: str
    diagnostics: Dict[str, str]

