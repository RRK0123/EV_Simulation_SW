from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, Tuple

from .units_adapter import convert_to_si, values_to_pybamm_keys

if TYPE_CHECKING:  # pragma: no cover
    import pybamm as pb


def _lazy_import_pybamm():
    try:
        import pybamm as pb  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError(
            "PyBaMM is required to run simulations. Install it with `pip install pybamm`."
        ) from exc
    return pb


def build_experiment(ui_values: Dict[str, Any], pb=None):
    if pb is None:
        pb = _lazy_import_pybamm()
    current = float(ui_values.get("operating.cc_current", 1.0))
    cv_voltage = float(ui_values.get("operating.cv_voltage", 4.2))
    v_min = float(ui_values.get("operating.v_min", 2.8))
    v_max = float(ui_values.get("operating.v_max", 4.2))
    steps = [
        (f"Charge at {current} A until {v_max} V",),
        (f"Hold at {cv_voltage} V until 50 mA",),
        ("Rest for 600 seconds",),
        (f"Discharge at {current} A until {v_min} V",),
        ("Rest for 600 seconds",),
    ]
    return pb.Experiment(steps)


def select_model(kind: str | None, pb=None):
    if pb is None:
        pb = _lazy_import_pybamm()
    kind_upper = (kind or "DFN").upper()
    if kind_upper == "SPM":
        return pb.lithium_ion.SPM()
    if kind_upper == "SPME":
        return pb.lithium_ion.SPMe()
    return pb.lithium_ion.DFN()


def run(ui_values: Dict[str, Any], categories_schema: list[dict]):
    pb = _lazy_import_pybamm()
    model = select_model(ui_values.get("model.type"), pb=pb)
    values_si = convert_to_si(ui_values, categories_schema)
    parameters = pb.ParameterValues(values_to_pybamm_keys(values_si))
    experiment = build_experiment(ui_values, pb=pb)
    simulation = pb.Simulation(model, parameter_values=parameters, experiment=experiment)
    solution = simulation.solve()
    context = {
        "model": model.__class__.__name__,
        "experiment_summary": str(experiment.operating_conditions_strings),
    }
    return solution, context


def extract_series(solution):
    _lazy_import_pybamm()  # ensure dependency present
    series: Dict[str, list] = {"time [s]": solution.t.tolist()}

    def try_get(name: str) -> list | None:
        try:
            return solution[name](solution.t).full().flatten().tolist()
        except Exception:  # noqa: BLE001 - PyBaMM raises many custom exceptions
            return None

    for variable in [
        "Voltage [V]",
        "Current [A]",
        "Cell temperature [K]",
        "Discharge capacity [A.h]",
        "State of Charge",
    ]:
        values = try_get(variable)
        if values is not None:
            series[variable] = values
    return series
