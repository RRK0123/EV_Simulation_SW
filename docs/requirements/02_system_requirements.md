# 02 — System Requirements (Black-Box)

> IDs: `SYS-###`

## Scope
System-level behaviors and constraints visible to users/integrations (not internal design).

### Functional
- **SYS-001 (MUST)** The system SHALL run simulations for configured scenarios and produce timeseries outputs and metadata artifacts.
- **SYS-002 (MUST)** The system SHALL import measurement files in **.mdf**, **.mdf4**, and **.dat** and map channels into the canonical schema.
- **SYS-003 (MUST)** The system SHALL export simulation results in **.mdf4**, **.mdf**, **.dat**, **CSV**, and **Parquet**.
- **SYS-004 (SHOULD)** The system SHOULD optionally sync artifacts to a configured cloud bucket.
- **SYS-005 (MUST)** The system SHALL provide a desktop UI for scenario setup, run control, and result visualization.
- **SYS-006 (SHOULD)** The system SHOULD support HIL/bench data sources when enabled.

### Non-Functional
- **SYS-101 (Performance / MUST)** Simulate **10 Hz × 3600 s** drive cycle in **< 5 min** on a laptop-class CPU/GPU.
- **SYS-102 (Interop / MUST)** MDF4 import/export SHALL preserve channel names, units, and sampling precision.
- **SYS-103 (Reliability / MUST)** A deterministic re-run with fixed seed/config SHALL yield bitwise-identical outputs (excluding timestamps/githash).
- **SYS-104 (Usability / SHOULD)** UI SHALL show progress and ETA for simulations and I/O operations.
- **SYS-105 (Security / SHOULD)** Local-only by default; any network features MUST be opt-in.
