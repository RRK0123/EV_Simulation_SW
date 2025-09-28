"""Filesystem-backed result store scaffold."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, MutableMapping

from core.orchestrator.events import RunProgress
from core.orchestrator.scenario import ScenarioConfig


@dataclass(slots=True)
class ResultStore:
    """Persist simulation outputs using a canonical layout."""

    root: Path = Path("storage/runtime")
    _progress_events: MutableMapping[str, List[RunProgress]] = field(default_factory=dict)

    def initialize_run(self, run_id: str, scenario: ScenarioConfig) -> None:
        run_dir = self.root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = run_dir / "metadata.json"
        metadata = {
            "run_id": run_id,
            "scenario_id": scenario.scenario_id,
            "seed": scenario.seed,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "requested_channels": scenario.canonical_channels(),
            "metadata": scenario.metadata,
        }
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        self._progress_events[run_id] = []

    def append_samples(self, run_id: str, samples: Iterable[Dict[str, float]], channels: Iterable[str]) -> None:
        run_dir = self.root / run_id
        timeseries_path = run_dir / "timeseries.jsonl"
        timeseries_path.parent.mkdir(parents=True, exist_ok=True)
        with timeseries_path.open("a", encoding="utf-8") as fp:
            for sample in samples:
                fp.write(json.dumps(sample) + "\n")
        # Update progress to 0% when no samples provided (scaffold behaviour).
        progress = RunProgress(
            run_id=run_id,
            scenario_id=self.get_run_metadata(run_id)["scenario_id"],
            timestamp=datetime.now(timezone.utc),
            progress_pct=0.0,
            sim_time_s=0.0,
        )
        self._progress_events[run_id].append(progress)

    def finalize_run(self, run_id: str) -> None:
        progress = RunProgress(
            run_id=run_id,
            scenario_id=self.get_run_metadata(run_id)["scenario_id"],
            timestamp=datetime.now(timezone.utc),
            progress_pct=100.0,
            sim_time_s=0.0,
        )
        self._progress_events[run_id].append(progress)

    def iter_progress(self, run_id: str) -> Iterator[RunProgress]:
        yield from self._progress_events.get(run_id, [])

    def get_run_metadata(self, run_id: str) -> Dict[str, object]:
        metadata_path = self.root / run_id / "metadata.json"
        if not metadata_path.exists():  # pragma: no cover - defensive guard
            raise KeyError(f"Run '{run_id}' metadata missing")
        return json.loads(metadata_path.read_text(encoding="utf-8"))

    def list_artifacts(self, run_id: str) -> Iterable[str]:
        run_dir = self.root / run_id
        if not run_dir.exists():
            return []
        return [str(path) for path in sorted(run_dir.glob("**/*")) if path.is_file()]


__all__ = ["ResultStore"]

