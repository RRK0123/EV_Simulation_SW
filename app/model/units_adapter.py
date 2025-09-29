from __future__ import annotations

from typing import Any, Dict

# Simple unit multipliers to SI (scalars only)
UNIT_TO_SI: dict[str, float] = {
    "μm": 1e-6,
    "um": 1e-6,
    "nm": 1e-9,
    "mm": 1e-3,
    "cm": 1e-2,
    "m": 1.0,
    "A.h": 1.0,
    "Ah": 1.0,
    "A": 1.0,
    "V": 1.0,
    "K": 1.0,
    "s": 1.0,
    "%": 1e-2,
    "S/m": 1.0,
    "W/(m·K)": 1.0,
    "W/(m^2·K)": 1.0,
    "J/K": 1.0,
}

# UI key → canonical PyBaMM parameter key
PYBAMM_KEY_MAP: dict[str, str] = {
    # Geometry
    "geometry.anode.thickness": "Negative electrode thickness [m]",
    "geometry.cathode.thickness": "Positive electrode thickness [m]",
    "geometry.separator.thickness": "Separator thickness [m]",
    "geometry.anode.particle_radius": "Negative particle radius [m]",
    "geometry.cathode.particle_radius": "Positive particle radius [m]",

    # Cell basics
    "cell.nominal_capacity": "Nominal cell capacity [A.h]",
    "cell.rated_voltage": "Rated voltage [V]",

    # Initial conditions
    "initial.soc": "Initial State of Charge",
    "initial.temperature": "Initial temperature [K]",

    # Thermal
    "thermal.heat_capacity": "Cell heat capacity [J.K-1]",
    "thermal.conductivity_axial": "Cell thermal conductivity [W.m-1.K-1]",
    "thermal.conductivity_radial": "Cell thermal conductivity [W.m-1.K-1]",
    "thermal.ambient_temp": "Ambient temperature [K]",
    "thermal.h_coeff": "Heat transfer coefficient [W.m-2.K-1]",

    # Transport (constant overrides)
    "transport.solid.anode_conductivity": "Negative electrode conductivity [S.m-1]",
    "transport.solid.cathode_conductivity": "Positive electrode conductivity [S.m-1]",
    "transport.electrolyte.t_plus": "Electrolyte transference number",

    # Kinetics
    "kinetics.anode.alpha": "Negative electrode charge transfer coefficient",
    "kinetics.cathode.alpha": "Positive electrode charge transfer coefficient",
}

# Keys whose UI unit is "°C" and must be shifted to K
CELSIUS_KEYS = {"initial.temperature", "thermal.ambient_temp"}


def _build_unit_index(categories: list[dict]) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for cat in categories:
        for sec in cat.get("sections", []):
            for field in sec.get("fields", []):
                idx[field["key"]] = {
                    "unit": field.get("unit"),
                    "advanced": field.get("advanced", False),
                }
    return idx


def convert_to_si(values: Dict[str, Any], categories_schema: list[dict]) -> Dict[str, Any]:
    unit_idx = _build_unit_index(categories_schema)
    out: Dict[str, Any] = {}
    for key, value in values.items():
        meta = unit_idx.get(key, {})
        unit = meta.get("unit")
        if isinstance(value, (int, float)):
            if key in CELSIUS_KEYS:
                out[key] = float(value) + 273.15 if unit in ("°C", "C") else float(value)
            elif unit in UNIT_TO_SI:
                out[key] = float(value) * UNIT_TO_SI[unit]
            else:
                out[key] = float(value)
        else:
            out[key] = value
    return out


def values_to_pybamm_keys(values_si: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for key, value in values_si.items():
        out[PYBAMM_KEY_MAP.get(key, key)] = value
    return out
