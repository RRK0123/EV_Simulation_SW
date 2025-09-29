"""Utilities for executing PyBaMM simulations and exporting their results.

This module centralises the glue that the Qt layer relies on so that it can
be reused by command-line tooling or automated tests without having to reach
into the ``ParameterBridge`` implementation details. The helpers purposely
avoid importing PySide to keep their dependency surface minimal.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence


# A curated set of variables that provide a representative snapshot of the
# single-cell behaviour. Additional variables can be requested by callers via
# ``extra_variables`` when executing a simulation.
DEFAULT_EXPORT_VARIABLES: Sequence[str] = (
    "Terminal voltage [V]",
    "Voltage [V]",
    "Current [A]",
    "Discharge capacity [A.h]",
    "Cell temperature [K]",
    "X-averaged cell temperature [K]",
)


@dataclass
class ExportResult:
    """Metadata about the artefacts written by :func:`export_simulation_results`."""

    dat_path: pathlib.Path
    mdf_path: Optional[pathlib.Path]
    warnings: List[str] = field(default_factory=list)


def run_pybamm_simulation(
    *,
    chemistry: str,
    model: str,
    parameter_set: str,
    overrides: Mapping[str, object],
    t_eval: Optional[Iterable[float]] = None,
    extra_variables: Optional[Iterable[str]] = None,
) -> Dict[str, List[float]]:
    """Execute a PyBaMM simulation and return the requested result channels.

    Parameters
    ----------
    chemistry:
        Name of the chemistry module to load from :mod:`pybamm` (e.g.
        ``"lithium_ion"``).
    model:
        Model factory exposed by the chosen chemistry (e.g. ``"DFN"``).
    parameter_set:
        Identifier of the parameter set defined in :mod:`pybamm.parameter_sets`.
    overrides:
        Mapping of PyBaMM parameter names to override values.
    t_eval:
        Optional iterable of timestamps (in seconds) to evaluate during the
        solve. When omitted a one hour discharge sampled every second is used.
    extra_variables:
        Additional solution variables to extract from the simulation.
    """

    try:
        import pybamm  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional runtime dependency
        raise RuntimeError("PyBaMM is not available in the runtime environment") from exc

    try:
        chemistry_module = getattr(pybamm, chemistry)
        model_factory = getattr(chemistry_module, model)
    except AttributeError as exc:  # pragma: no cover - invalid configuration
        raise RuntimeError(f"Unknown PyBaMM model '{chemistry}.{model}'") from exc

    if not parameter_set:
        raise ValueError("No PyBaMM parameter set selected")

    try:
        parameter_values_source = getattr(pybamm.parameter_sets, parameter_set)
    except AttributeError as exc:
        raise RuntimeError(f"Unknown PyBaMM parameter set '{parameter_set}'") from exc

    parameter_values = pybamm.ParameterValues(chemistry=parameter_values_source)
    if overrides:
        parameter_values.update(dict(overrides))

    if t_eval is None:
        t_eval = pybamm.linspace(0, 3600, 361)
    else:
        t_eval = [float(value) for value in t_eval]

    model_instance = model_factory()
    simulation = pybamm.Simulation(model_instance, parameter_values=parameter_values)
    solution = simulation.solve(t_eval=t_eval)

    results: Dict[str, List[float]] = {
        "Time [s]": solution.t.tolist(),
    }

    variables = list(DEFAULT_EXPORT_VARIABLES)
    if extra_variables:
        for variable in extra_variables:
            if variable not in variables:
                variables.append(variable)

    for variable in variables:
        try:
            channel = solution[variable]
        except KeyError:  # pragma: no cover - variable not produced by model
            continue
        results[variable] = channel.entries.tolist()

    return results


def export_simulation_results(
    export_dir: pathlib.Path,
    prefix: str,
    results: Mapping[str, Sequence[float]],
    *,
    include_mdf: bool = True,
) -> ExportResult:
    """Persist simulation results as ``.dat`` (and optionally ``.mdf``) files."""

    export_dir.mkdir(parents=True, exist_ok=True)

    if "Time [s]" not in results:
        raise ValueError("Simulation results missing 'Time [s]' channel")
    time = [float(value) for value in results["Time [s]"]]
    columns = [key for key in results.keys() if key != "Time [s]"]
    expected_length = len(time)

    column_data: Dict[str, List[float]] = {"Time [s]": time}
    for column in columns:
        values = [float(value) for value in results[column]]
        if len(values) != expected_length:
            raise ValueError(f"Result channel '{column}' length mismatch")
        column_data[column] = values

    dat_path = export_dir / f"{prefix}.dat"
    header = "\t".join(["Time [s]"] + columns)
    with dat_path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(f"{header}\n")
        for row_index in range(expected_length):
            row_values = [column_data["Time [s]"][row_index]]
            row_values.extend(column_data[column][row_index] for column in columns)
            formatted = "\t".join(_format_float(value) for value in row_values)
            handle.write(f"{formatted}\n")

    mdf_path: Optional[pathlib.Path] = None
    warnings: List[str] = []

    if include_mdf:
        try:
            from asammdf import MDF, Signal  # type: ignore
        except ImportError:  # pragma: no cover - optional dependency
            warnings.append("asammdf is not installed; MDF export skipped")
        else:
            signals = []
            for column in columns:
                samples = [float(value) for value in results[column]]
                signals.append(Signal(samples=samples, timestamps=time, name=column))

            mdf = MDF()
            mdf.append(signals)
            mdf_path = export_dir / f"{prefix}.mdf"
            mdf.save(mdf_path, overwrite=True)

    return ExportResult(dat_path=dat_path, mdf_path=mdf_path, warnings=warnings)


def _format_float(value: float) -> str:
    if value == 0:
        return "0"
    magnitude = abs(value)
    if magnitude != 0 and (magnitude >= 1e4 or magnitude <= 1e-3):
        return f"{value:.6e}"
    return f"{value:.12g}"


__all__ = [
    "DEFAULT_EXPORT_VARIABLES",
    "ExportResult",
    "export_simulation_results",
    "run_pybamm_simulation",
]

