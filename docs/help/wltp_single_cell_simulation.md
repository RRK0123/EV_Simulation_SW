# WLTP Single-Cell Simulation How-To

This guide explains how to build the EV Simulation software locally and how to run the built-in **WLTP single-cell** workflow. The tooling now ships with a WLTP Class 3 drive-cycle trace, purpose-built single-cell models (ohmic, RC, and thermal variants), and a CLI utility that exports combined results as a `.dat` file.

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

## 5. Run the WLTP single-cell export

1. Generate (or refresh) the WLTP dataset. The repository includes a helper script that produces a representative WLTP Class 3 cycle and stores it under `data/wltp/wltp_class3_cycle.csv`:
    ```bash
    scripts/generate_wltp_class3_dataset.py
    ```
2. Build the CLI utility:
    ```bash
    cmake -S . -B build -DEV_SIM_ENABLE_TESTS=OFF
    cmake --build build --target wltp_single_cell_cli
    ```
3. Run the simulation and export the `.dat` file (adjust the output path as desired):
    ```bash
    build/app/cli/wltp_single_cell_cli \
      --wltp data/wltp/wltp_class3_cycle.csv \
      --output data/wltp/wltp_single_cell_results.dat \
      --ambient 25
    ```

The CLI orchestrates the WLTP drive cycle through three single-cell models:

- `NMC811` uses the **ohmic** equivalent-circuit model.
- `LFP` exercises the **RC network** variant with transient voltage dynamics.
- `NCA` activates the **thermal-aware** model that estimates self-heating and convective rejection.

The exported `.dat` file combines WLTP trace data (`drive.*` signals) with each cell's electrical and thermal telemetry (`<cell>.voltage_v`, `<cell>.current_a`, `<cell>.soc`, `<cell>.temperature_c`, etc.).

## 6. Advanced configuration

The scenario schema (`configs/schemas/scenario.schema.json`) now accepts structured drive-cycle information, ambient conditions, and cell definitions. This enables programmatic construction of WLTP scenarios in JSON when integrating with external tooling. Refer to `src/sim_core/include/evsim/core/Scenario.hpp` for the available fields.
