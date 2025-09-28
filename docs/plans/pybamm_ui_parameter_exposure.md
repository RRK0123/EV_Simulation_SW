# PyBaMM Parameter Exposure Plan

## Goal
Expose all PyBaMM parameter values that affect the default EV simulation scenarios through the Qt/QML front end so that engineers can inspect and override them before executing a run.

## Current state recap
- The Qt UI (app/ui_qt) only offers a single "Run default scenario" button and defers all logic to the C++ orchestrator wrapper.
- There is no Python-side bridge to PyBaMM, so parameter sets (e.g., `pybamm.ParameterValues`) are not available to the UI layer.
- Scenario definitions in C++ contain battery attributes, but they are static and not synchronised with PyBaMM's extensive parameter library.

## High-level approach
1. **Introduce a Python PyBaMM adapter** that loads parameter metadata and exposes it in a UI-friendly shape.
   - Import PyBaMM in `app/ui_qt` (new dependency for the UI environment).
   - Instantiate the desired PyBaMM models (e.g., DFN or SPM) and acquire their `ParameterValues`.
   - Normalise parameters into a list of objects containing name, category, default value, units, and value bounds (if known).

2. **Bridge parameters to QML via Qt models.**
   - Implement a `QtCore.QAbstractListModel` subclass (e.g., `PybammParameterModel`) that stores the parameter descriptors and current value.
   - Provide invokable slots for resetting to defaults and applying user edits.
   - Expose this model to QML through the `SimulationController` context property.

3. **Render dynamic parameter editors in QML.**
   - Replace the single-button layout with a `ScrollView` containing grouped controls.
   - Use `Repeater`+`DelegateChooser` to present editors (text fields, spin boxes, drop-downs) based on each parameter's type/metadata.
   - Add search/filter and reset buttons to improve usability when hundreds of parameters are available.

4. **Synchronise overrides with the simulation run.**
   - Collect the modified values from the model when `runScenario()` is triggered.
   - Pass the overrides to PyBaMM prior to solving (e.g., `parameter_values.update(overrides)`), then execute the model.
   - Persist overrides to disk (JSON/YAML) so sessions are reproducible.

5. **Backward compatibility with the C++ orchestrator.**
   - Provide a fallback path that continues to call `OrchestratorClient` when PyBaMM is unavailable (feature flag or dependency check).
   - Translate edited parameters into the C++ scenario structure if both pipelines need to be supported concurrently.

## Incremental delivery steps
1. Scaffold the adapter module with unit tests that verify metadata extraction from a small PyBaMM parameter set.
2. Add the `PybammParameterModel` and expose it to QML; prototype the dynamic form with a handful of parameters.
3. Implement persistence (save/load overrides) and validation feedback in the UI.
4. Wire the run action to apply overrides to the simulation backend (PyBaMM first, C++ orchestration later if required).
5. Expand coverage to all required PyBaMM parameter sets (chemistry-specific, thermal, drive cycle, etc.) and update documentation.

## Risks and mitigations
- **PyBaMM startup cost:** Cache parameter metadata to avoid recomputation on every UI launch.
- **Volume of parameters:** Provide search, grouping, and sensible defaults to keep the UI manageable.
- **Dependency footprint:** Document how to install PyBaMM alongside PySide6 and gate the UI feature behind an availability check for developer ergonomics.

## Deliverables
- Updated Qt UI with dynamic parameter editors.
- Python adapter module with tests.
- Documentation covering setup instructions and user workflow for editing PyBaMM parameters.
