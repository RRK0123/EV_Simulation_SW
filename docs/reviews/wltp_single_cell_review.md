# WLTP Single-Cell Capability Review

## Scope
Assessment of the current simulation core against the requirement to run a **WLTP drive-cycle simulation for a single battery cell with advanced parameters exposed to users**.

## Summary
The refreshed implementation can execute a WLTP Class 3 single-cell simulation end-to-end. Structured scenario data captures the WLTP speed trace, ambient conditions, and cell definitions, while dedicated single-cell models (ohmic, RC, thermal) ingest the drive cycle and export telemetry via a `.dat` file. Advanced solver features remain minimal, but the core requirement to run a WLTP drive-cycle simulation for representative cells is now **met for the provided models**.

## Detailed Findings

### Scenario definition captures WLTP context
The software requirements mandate that scenarios expose seed, ambient conditions, pack definition, drive cycle, and solver options.【F:docs/requirements/03_software_requirements_spec.md†L10-L18】 The `Scenario` model now includes structured drive-cycle data, ambient temperatures, and cell definitions so WLTP inputs can be expressed without bespoke plumbing.【F:src/sim_core/include/evsim/core/Scenario.hpp†L9-L56】 The JSON schema mirrors these fields, enabling external tooling to deliver WLTP datasets directly to the orchestrator.【F:configs/schemas/scenario.schema.json†L7-L126】

### Single-cell models consume the WLTP drive cycle
Three dedicated single-cell models (ohmic, RC, and thermal) process the WLTP speed trace, map it to cell currents, and track state-of-charge, voltage dynamics, and heat rejection.【F:src/sim_core/include/evsim/models/SingleCellModels.hpp†L8-L69】【F:src/sim_core/src/SingleCellModels.cpp†L18-L211】 They expose WLTP-relevant telemetry (`drive.*` signals, `<cell>.voltage_v`, `<cell>.temperature_c`, etc.) that feed the `.dat` exporter.【F:data/wltp/wltp_single_cell_results.dat†L1-L10】

### Solver still lacks advanced configuration
To support WLTP tuning, users must control solver tolerances and step size, as specified in the solver requirements.【F:docs/requirements/03_software_requirements_spec.md†L16-L18】 The fixed-step explicit Euler integrator remains the only solver option and still omits tolerance handling.【F:src/sim_core/src/EulerSolver.cpp†L5-L26】 Advanced solver configuration therefore remains a follow-on task.

### Orchestration runs per-model WLTP exports
The orchestrator still executes one model per run, but the WLTP CLI automates sequential runs for each configured cell, aggregating the results into a single `.dat` file for downstream analysis.【F:app/cli/wltp_single_cell_cli.cpp†L1-L213】 Future work could extend the orchestrator to compose multi-physics DAGs directly.

## Conclusion
The repository now demonstrates a WLTP Class 3 single-cell workflow, complete with structured inputs, purpose-built models, and a `.dat` exporter. Solver configurability and multi-model orchestration remain open improvements, but the single-cell WLTP requirement is satisfied for the bundled cell chemistries.
