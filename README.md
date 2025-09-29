# EV Simulation Software Scaffold

This repository contains the baseline framework for the EV simulation toolchain described in the
system and software architecture. The focus of this revision is establishing a C++ simulation
kernel, a Qt/Python UI shell, and the integration seams required for data I/O and plugin
development.

## Repository layout

```
├── CMakeLists.txt               # Root build that wires the C++ simulation core and tests
├── src/sim_core                 # C++ simulation kernel and orchestration logic
│   ├── include/evsim            # Public headers for consumers and bindings
│   └── src                      # Concrete model, solver, registry, and C API stubs
├── tests/cpp                    # Minimal smoke test for the orchestrator and solver loop
└── app/ui_qt                    # PySide6/QML desktop shell that exercises the C API
```

## Building the simulation core

The simulation core is implemented in modern C++ (C++20) and built with CMake:

```bash
cmake -S . -B build -DEV_SIM_ENABLE_TESTS=ON
cmake --build build
ctest --test-dir build
```

The build emits a shared library named `libevsim_core` (or `evsim_core.dll` on Windows). The
library exposes a minimal C interface that the Python UI consumes via `ctypes`.

## Running the Qt UI

The Qt desktop shell is implemented in Python using PySide6. Install the runtime dependencies and
launch the shell after building the C++ core so that the shared library is available. The parameter
explorer now introspects the active PyBaMM installation to expose the entire parameter catalogue and
can execute a full PyBaMM simulation with MDF/DAT exports when the optional Python packages are
installed:

```bash
python -m venv .venv
source .venv/bin/activate
pip install PySide6 pybamm asammdf
python app/ui_qt/main.py
```

Click **Run default scenario** to run the PyBaMM DFN model with the current overrides and export the
results as `.dat` and `.mdf` files inside `data/simulations`. If `asammdf` is not available the MDF
export is skipped and the UI reports the missing optional dependency alongside the success message.
The button also retains the legacy link to the C++ orchestrator when the shared library is present.

## WLTP single-cell export

The repository ships with a WLTP Class 3 drive-cycle dataset (`data/wltp/wltp_class3_cycle.csv`) and
a CLI utility that runs the cycle through three representative single-cell models (ohmic, RC, and
thermal). Build and execute the exporter to obtain a `.dat` file that merges the WLTP trace with
each cell's telemetry:

```bash
scripts/generate_wltp_class3_dataset.py  # regenerate the WLTP trace if required
cmake --build build --target wltp_single_cell_cli
build/app/cli/wltp_single_cell_cli \
  --wltp data/wltp/wltp_class3_cycle.csv \
  --output data/wltp/wltp_single_cell_results.dat \
  --ambient 25
```

The output file includes `drive.*` signals (speed, distance, acceleration, phase id) alongside each
cell's voltage, current, SOC, and thermal estimates.

## Next steps

- Flesh out additional subsystem models (BMS, thermal, drivetrain) with validated dynamics.
- Extend the solver abstraction to support more advanced integrators and adaptive time-stepping.
- Implement MDF/MDF4/DAT importers and exporters that populate the canonical timeseries schema.
- Wire structured logging, configuration loading, and plugin discovery.
- Replace the `ctypes` bridge with a dedicated binding layer (pybind11 or SIP) once the C++ API
  stabilises.
