# EV_Simulation_SW

Prototype implementation scaffolding for the EV simulation desktop suite.

## Documentation
- [System & Software Architecture (Markdown)](system_software_architecture.md)
- [Requirements Overview](docs/requirements/README.md)

## Building the Qt UI

```bash
cmake -S . -B build
cmake --build build
```

The Qt project depends on Qt 6.5 or newer.  When Qt is not available the
build system configuration step will fail; this is expected on bare
environments.

## Python Core

The Python packages located under ``core/``, ``data_io/``, and ``storage/``
provide the scaffolding for the simulation orchestrator, models, solver
registry, and data I/O subsystems.  Run the unit tests with ``pytest``:

```bash
pytest
```
