"""Simulation orchestrator scaffold.

The orchestrator coordinates models, solvers, result storage and plugin
integration.  The implementation below focuses on defining the public
interfaces and wiring mandated by the architecture documents while
keeping the runtime lightweight for early development.
"""

from __future__ import annotations

import logging
import uuid
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable, Iterator, Optional

from core.models.registry import ModelRegistry
from core.plugins.manager import PluginManager
from core.solvers.base import SolverRegistry
from data_io.importers.base import ImporterRegistry
from data_io.exporters.base import ExporterRegistry
from storage.result_store import ResultStore
from .events import RunCompleted, RunFailed, RunProgress, RunStarted
from .scenario import ScenarioConfig

LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class OrchestratorConfig:
    """Configuration hooks that control orchestrator services."""

    enable_plugins: bool = True
    enable_event_stream: bool = True


class SimulationOrchestrator(AbstractContextManager["SimulationOrchestrator"]):
    """Entry point for running EV simulations."""

    def __init__(
        self,
        models: Optional[ModelRegistry] = None,
        solvers: Optional[SolverRegistry] = None,
        result_store: Optional[ResultStore] = None,
        importer_registry: Optional[ImporterRegistry] = None,
        exporter_registry: Optional[ExporterRegistry] = None,
        plugin_manager: Optional[PluginManager] = None,
        config: Optional[OrchestratorConfig] = None,
    ) -> None:
        self._models = models or ModelRegistry()
        self._solvers = solvers or SolverRegistry()
        self._result_store = result_store or ResultStore()
        self._importers = importer_registry or ImporterRegistry()
        self._exporters = exporter_registry or ExporterRegistry()
        self._plugins = plugin_manager or PluginManager()
        self._config = config or OrchestratorConfig()
        self._event_listeners: Dict[str, Iterable] = {}
        self._active_runs: Dict[str, ScenarioConfig] = {}

    # ------------------------------------------------------------------
    # Context manager helpers
    # ------------------------------------------------------------------
    def __enter__(self) -> "SimulationOrchestrator":  # pragma: no cover - trivial
        if self._config.enable_plugins:
            self._plugins.load()
        return self

    def __exit__(self, *exc_info) -> None:  # pragma: no cover - trivial
        self._plugins.unload()

    # ------------------------------------------------------------------
    # Public API inspired by the architecture spec (section 3.12)
    # ------------------------------------------------------------------
    def run(self, scenario: ScenarioConfig) -> str:
        """Start a simulation run and return the generated ``run_id``.

        The default implementation does not perform heavy numerical
        computation; instead, it allocates the result structure, notifies
        listeners, and records metadata to satisfy the architectural
        contracts.  Concrete solver integration can be added incrementally
        by extending :class:`ModelRegistry` and :class:`SolverRegistry`.
        """

        run_id = uuid.uuid4().hex
        LOGGER.info("Starting simulation", extra={"run_id": run_id, "scenario_id": scenario.scenario_id})

        self._active_runs[run_id] = scenario
        self._result_store.initialize_run(run_id=run_id, scenario=scenario)
        self._emit(RunStarted(run_id, scenario.scenario_id, datetime.now(timezone.utc)))

        # The placeholder integration simply produces an empty frame that
        # respects the canonical channel schema.
        canonical_channels = scenario.canonical_channels()
        self._result_store.append_samples(
            run_id=run_id,
            samples=[],
            channels=canonical_channels,
        )

        self._result_store.finalize_run(run_id=run_id)
        self._emit(
            RunCompleted(
                run_id=run_id,
                scenario_id=scenario.scenario_id,
                timestamp=datetime.now(timezone.utc),
                artifacts=self._result_store.list_artifacts(run_id),
            )
        )
        return run_id

    def progress(self, run_id: str) -> Iterator[RunProgress]:
        """Yield progress events for a run.

        In the scaffold this simply exposes the cached events emitted so
        far.  Once real-time stepping is implemented this method should
        stream incremental updates from the solver thread pool.
        """

        yield from self._result_store.iter_progress(run_id)

    def result(self, run_id: str) -> Dict[str, object]:
        """Return a handle to the stored dataset for the supplied run."""

        return self._result_store.get_run_metadata(run_id)

    # ------------------------------------------------------------------
    # Event stream
    # ------------------------------------------------------------------
    def subscribe(self, event: str, listener) -> None:
        listeners = list(self._event_listeners.get(event, []))
        listeners.append(listener)
        self._event_listeners[event] = listeners

    def _emit(self, payload) -> None:
        event_name = payload.__class__.__name__
        for listener in self._event_listeners.get(event_name, []):
            try:
                listener(payload)
            except Exception as exc:  # pragma: no cover - defensive logging
                LOGGER.exception("Listener failed", exc_info=exc)


__all__ = ["SimulationOrchestrator", "OrchestratorConfig"]

