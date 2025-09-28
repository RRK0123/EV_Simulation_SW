# 03 — Software Requirements Specification (SRS)

> IDs: `SW-###` (functional), `Q-###` (quality)

## 3.1 Context
This SRS refines `SYS-*` into implementable software requirements.

## 3.2 Functional Requirements

### Scenario & Orchestration
- **SW-001 (MUST)** Provide a `Scenario` model with seed, ambient, pack, drive cycle, and solver options.
- **SW-002 (MUST)** Orchestrator SHALL create a directed acyclic graph (DAG) of model components per scenario.
- **SW-003 (MUST)** Orchestrator SHALL stream results via a ring buffer to the result store.

### Models & Solvers
- **SW-010 (MUST)** Provide baseline models: **battery pack**, **BMS**, **inverter/motor**, **thermal**, **aux loads**.
- **SW-011 (MUST)** Solver interface SHALL support SciPy integrators and PyBaMM; tolerance and step control configurable.
- **SW-012 (SHOULD)** Support event detection (e.g., overtemp, current limits) and checkpointing.

### Data Layer
- **SW-020 (MUST)** Result store SHALL index by `run_id`, `scenario_id`, and timestamp; support chunked append and lazy load.
- **SW-021 (MUST)** Importers SHALL map MDF/MDF4/DAT channels to canonical names with units; unmapped go to a staging table.
- **SW-022 (MUST)** Exporters SHALL generate MDF4/MDF/DAT with correct channel metadata and compression as configured.

### Plugin System
- **SW-030 (MUST)** Plugin host SHALL discover Python entry points; version gating via semver.
- **SW-031 (SHOULD)** Support C++ shared library plugins (ABI-stable boundary TBD).

### Telemetry & Errors
- **SW-040 (MUST)** Structured logs with `run_id`, `scenario_id`, phase timings, and error codes.
- **SW-041 (MUST)** Standard error codes: `SIM_INIT_FAIL`, `IMPORT_MAP_ERR`, `EXPORT_UNIT_MISMATCH`, `SOLVER_DIVERGED`.
- **SW-042 (SHOULD)** Emit `Run.*` events for UI.

## 3.3 Non-Functional Requirements
- **Q-001 (Performance)** Import **1 GB MDF4** in **< 60 s**; export **500 MB MDF4** in **< 45 s**.
- **Q-002 (Reliability)** Crash-safe writes via atomic moves or WAL; resume from last checkpoint.
- **Q-003 (Usability)** Keyboard-first navigation; high-contrast theme.
- **Q-004 (Portability)** Windows & Linux parity; Mac best-effort.
- **Q-005 (Security)** No external network calls unless explicitly enabled; file hash on exports (SHA-256).

## 3.4 Acceptance Criteria (Samples)
- **SW-021.AC1** Importer maps `BATT_Pack_V` → `pack.V` (V), `BATT_Pack_I` → `pack.I` (A), `BATT_SOC` → `soc` (%).
- **SW-022.AC1** Exported MDF4 opens in asammdf with correct units and sample count within ±1 sample.
- **SW-011.AC1** Changing `rtol`/`atol` changes solver behavior and is reflected in metadata.
