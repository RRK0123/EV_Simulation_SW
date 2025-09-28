# PyBaMM UI Exposure Review

## Scope

Review the user interfaces provided in this repository to verify whether they expose PyBaMM
parameters, offer a WLTP simulation control, and export the resulting data in `.dat` format.

## Findings

### UI technology baseline
- The only interactive user interface in the tree is the Qt/QML shell under `app/ui_qt`. The
  controller simply triggers the legacy C++ orchestrator's "default scenario"; there is no
  integration with PyBaMM or its parameter sets.
- `Main.qml` declares a single button labelled "Run default scenario" and no additional form
  controls, parameter editors, or WLTP-specific affordances.

### Parameter exposure
- The Qt shell does not import or depend on the PyBaMM Python package. There is no runtime code that
  enumerates PyBaMM models, parameter sets, or exposes parameter overrides to the user.
- Consequently, the application cannot provide end users with access to "all PyBaMM parameters" as
  requested. The simulation still delegates to the C++ orchestrator rather than a PyBaMM-based
  stack.

### WLTP simulation control
- No UI element, signal, or slot references a WLTP simulation. The only available action remains the
  generic default scenario invocation.
- The WLTP tooling that exists today is a standalone C++ CLI located under `app/cli`. It is
  decoupled from the Qt UI and therefore unavailable to UI users.

### Data export sanity check
- Building the C++ tools and executing `wltp_single_cell_cli` against
  `data/wltp/wltp_class3_cycle.csv` successfully generates a `.dat` export containing an LFP cell
  run, confirming the backend capability exists even though the UI does not surface it.

## Recommendations

1. Replace or augment the Qt shell with a UI that binds to PyBaMM, dynamically enumerates its
   parameter sets, and allows users to inspect/override parameter values.
2. Introduce WLTP-specific controls (e.g., a "Run WLTP" button) that call into either a PyBaMM-based
   simulation pipeline or the existing C++ CLI.
3. Surface status feedback and download links for the generated `.dat` files within the UI so that
   the export workflow is transparent to end users.
