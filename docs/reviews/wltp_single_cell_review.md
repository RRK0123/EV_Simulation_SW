# WLTP Single-Cell Capability Review

## Scope
Assessment of the current simulation core against the requirement to run a **WLTP drive-cycle simulation for a single battery cell with advanced parameters exposed to users**.

## Summary
The present implementation cannot execute a WLTP single-cell simulation with advanced parameter control. Fundamental gaps exist in scenario modelling, component coverage, and solver configurability, so the requirement is **not met**.

## Detailed Findings

### Scenario definition is too limited
The software requirements mandate that scenarios expose seed, ambient conditions, pack definition, drive cycle, and solver options.【F:docs/requirements/03_software_requirements_spec.md†L10-L18】 However, the in-memory `Scenario` model only tracks an identifier, time-step, step count, and a flat list of numeric parameters, with no structure for ambient conditions, drive-cycle profiles, or solver settings.【F:src/sim_core/include/evsim/core/Scenario.hpp†L9-L22】 Likewise, the JSON schema permits only scalar name/value overrides, preventing users from supplying complex WLTP inputs such as speed traces or temperature breakpoints.【F:configs/schemas/scenario.schema.json†L7-L45】 This prevents configuring the advanced parameters required for a WLTP run.

### Missing component models for WLTP physics
The requirements call for baseline models covering the battery pack, BMS, inverter/motor, thermal system, and auxiliary loads.【F:docs/requirements/03_software_requirements_spec.md†L15-L18】 The current codebase only provides a simplistic battery-pack model; other subsystems are absent from the public headers, so a WLTP drive train cannot be simulated.【F:src/sim_core/include/evsim/models/BatteryPackModel.hpp†L1-L72】 Even within the battery model, behaviour is limited to a fixed current draw with no dependency on vehicle speed or WLTP phases.【F:src/sim_core/src/BatteryPackModel.cpp†L9-L38】

### Solver lacks advanced configuration
To support WLTP tuning, users must control solver tolerances and step size, as specified in the solver requirements.【F:docs/requirements/03_software_requirements_spec.md†L16-L18】 The only available solver is a fixed-step explicit Euler integrator that ignores tolerance settings and advanced controls.【F:src/sim_core/src/EulerSolver.cpp†L5-L26】 Consequently, advanced solver parameters cannot be exposed to users.

### Orchestration limits model composition
The orchestrator should build a DAG of models per scenario to capture coupled subsystems.【F:docs/requirements/03_software_requirements_spec.md†L11-L13】 Instead, it simply invokes the first registered model and solver, offering no means to compose multiple components required for a WLTP cycle (vehicle dynamics, thermal management, etc.).【F:src/sim_core/src/SimulationOrchestrator.cpp†L33-L54】

## Conclusion
Significant development is required before a WLTP single-cell simulation with advanced parameter exposure can be supported. Enhancements are needed to the scenario schema, subsystem modelling, solver stack, and orchestration pipeline.
