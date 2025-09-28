# WLTP Single-Cell Simulation How-To

This guide explains how to build the EV Simulation software locally and what is currently required to attempt a WLTP-style simulation for a single battery cell. Because the WLTP workflow is not yet implemented end-to-end (see the companion capability review), the final section highlights the missing pieces you would need to implement before a true WLTP run is possible.

## 1. Prerequisites
- C++20-compatible toolchain (e.g., GCC 11+ or Clang 13+).
- CMake 3.20 or newer.
- Python 3.10+ (for the optional Qt UI shell).
- Ninja (optional but recommended for faster builds).

Ensure your compiler and CMake are available on the `PATH`.

## 2. Clone and configure the project
```bash
git clone <url-to-EV_Simulation_SW-repository>
cd EV_Simulation_SW
```

Generate the build directory and configure the project (enable tests if you plan to run them):
```bash
cmake -S . -B build -DEV_SIM_ENABLE_TESTS=ON
```

## 3. Build and test the simulation core
Compile the C++ core and, optionally, run the unit tests:
```bash
cmake --build build
ctest --test-dir build
```
This produces the `libevsim_core` shared library in `build/src/sim_core`.

## 4. Launch the optional Qt UI shell
If you wish to experiment with the Python/QML shell:
```bash
python -m venv .venv
source .venv/bin/activate
pip install PySide6
python app/ui_qt/main.py
```
The UI can invoke the default constant-current discharge scenario that ships with the C++ core.

## 5. Crafting a single-cell WLTP scenario (work-in-progress)
As of this revision, scenarios accept only a simple identifier, fixed time-step, total step count, and a flat list of numeric parameters. WLTP-specific inputs (speed trace, ambient temperature profile, gear-shift schedule, etc.) cannot yet be expressed. To experiment with the available hooks:

1. Create a JSON document that matches `configs/schemas/scenario.schema.json`, for example:
    ```json
    {
      "id": "mock_wltp_single_cell",
      "time_step": 1.0,
      "step_count": 3600,
      "parameters": [
        { "name": "nominal_voltage", "value": 3.7 },
        { "name": "capacity_kwh", "value": 0.25 },
        { "name": "internal_resistance", "value": 0.01 },
        { "name": "current_draw", "value": 5.0 }
      ]
    }
    ```
2. Extend or script against the C API (see `src/sim_core/src/core_c_api.cpp`) to load your scenario structure and execute `SimulationOrchestrator::run`.
3. Inspect the generated timeseries samples from the in-memory result store.

This replicates a constant-current discharge for a single cell rather than a WLTP drive cycle but exercises the available plumbing.

## 6. Gaps before a true WLTP single-cell run
To achieve a standards-compliant WLTP simulation, additional work is required:
- Extend the `Scenario` model and JSON schema to include ambient conditions, a drive-cycle speed trace, and solver tolerances.
- Implement WLTP-aware component models (cell electrochemistry, vehicle longitudinal dynamics, thermal management, auxiliaries).
- Provide configurable solver backends with tolerance controls and event handling.
- Wire the orchestrator to compose multiple models and propagate structured WLTP parameters to each subsystem.

Once these features exist, you will be able to place a WLTP speed trace in the scenario, configure solver tolerances, and run the orchestrator to generate WLTP results for a single cell.
