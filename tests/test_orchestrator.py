"""Unit tests for orchestrator scaffolding."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import ScenarioConfig, SimulationOrchestrator


def test_orchestrator_creates_run(tmp_path: Path) -> None:
    store_root = tmp_path / "store"
    orchestrator = SimulationOrchestrator()
    orchestrator._result_store.root = store_root  # type: ignore[attr-defined]

    scenario = ScenarioConfig(scenario_id="TEST_SCENARIO")
    run_id = orchestrator.run(scenario)

    metadata = orchestrator.result(run_id)
    assert metadata["scenario_id"] == "TEST_SCENARIO"
    artifacts = list(orchestrator._result_store.list_artifacts(run_id))  # type: ignore[attr-defined]
    assert artifacts

