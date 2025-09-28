#!/usr/bin/env python3
"""Generate a JSON schema describing PyBaMM parameters for a model."""
from __future__ import annotations

import argparse
import json
import math
import numbers
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence

try:
    import yaml  # type: ignore
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit("PyYAML is required to run this script") from exc

try:
    import pybamm  # type: ignore
except ImportError as exc:  # pragma: no cover - optional dependency
    raise SystemExit("PyBaMM must be installed to introspect models") from exc


@dataclass
class ParameterRow:
    identifier: str
    name: str
    label: str
    type: str
    default: Any
    unit: str
    category: str
    advanced: bool
    description: str = ""
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    step: Optional[float] = None
    choices: Sequence[Dict[str, Any]] = field(default_factory=tuple)
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "id": self.identifier,
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "default": self.default,
            "unit": self.unit,
            "category": self.category,
            "advanced": self.advanced,
        }
        if self.description:
            data["description"] = self.description
        if self.minimum is not None:
            data["min"] = self.minimum
        if self.maximum is not None:
            data["max"] = self.maximum
        if self.step is not None:
            data["step"] = self.step
        if self.choices:
            data["choices"] = list(self.choices)
        if self.source:
            data["source"] = self.source
        return data


def slugify(name: str) -> str:
    """Turn a human-readable parameter name into a slug identifier."""
    cleaned = []
    for char in name:
        if char.isalnum():
            cleaned.append(char.lower())
        elif cleaned and cleaned[-1] != "_":
            cleaned.append("_")
    result = "".join(cleaned)
    return result.strip("_") or "parameter"


def serialise_default(value: Any) -> Any:
    """Convert PyBaMM values into JSON-friendly values."""
    if hasattr(value, "_scalar"):  # PyBaMM Scalar
        value = value.value
    if hasattr(value, "value") and isinstance(value.value, numbers.Number):
        value = value.value
    if isinstance(value, (numbers.Integral, numbers.Real)) and not isinstance(value, bool):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            return None
        return float(value) if isinstance(value, float) else int(value)
    if isinstance(value, bool):
        return bool(value)
    if isinstance(value, str):
        return value
    return value


def collect_parameters(model: pybamm.BaseModel) -> Iterable[pybamm.Symbol]:  # type: ignore[name-defined]
    """Walk a PyBaMM model graph to find parameter symbols."""
    seen: Dict[int, pybamm.Symbol] = {}

    def walk(symbol: pybamm.Symbol) -> None:  # type: ignore[name-defined]
        if id(symbol) in seen:
            return
        seen[id(symbol)] = symbol
        if isinstance(symbol, (pybamm.Parameter, pybamm.InputParameter)):
            return
        for child in getattr(symbol, "children", []) or []:
            walk(child)

    for collection in (model.rhs, model.algebraic, model.initial_conditions, model.events):
        for symbol in collection.values():
            walk(symbol)
    for symbol in model.variables.values():
        walk(symbol)

    for symbol in seen.values():
        if isinstance(symbol, (pybamm.Parameter, pybamm.InputParameter)):
            yield symbol


def load_curation(overrides_path: pathlib.Path) -> Dict[str, Any]:
    if overrides_path.exists():
        with overrides_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    return {}


def apply_curation(row: ParameterRow, curation: Dict[str, Any]) -> ParameterRow:
    defaults = curation.get("metadata_defaults", {})
    params = curation.get("parameters", {})
    overrides = params.get(row.identifier, {})
    row.category = overrides.get("category", row.category or defaults.get("category", ""))
    row.advanced = overrides.get("advanced", row.advanced if row.advanced is not None else defaults.get("advanced", False))
    if "label" in overrides:
        row.label = overrides["label"]
    if "min" in overrides:
        row.minimum = overrides["min"]
    if "max" in overrides:
        row.maximum = overrides["max"]
    if "step" in overrides:
        row.step = overrides["step"]
    return row


def determine_type(default: Any) -> str:
    if isinstance(default, bool):
        return "bool"
    if isinstance(default, numbers.Integral):
        return "integer"
    if isinstance(default, numbers.Real):
        return "number"
    return "text"


def build_rows(
    model: pybamm.BaseModel,  # type: ignore[name-defined]
    parameter_values: "pybamm.ParameterValues",  # type: ignore[name-defined]
    curation: Dict[str, Any],
) -> List[ParameterRow]:
    rows: Dict[str, ParameterRow] = {}
    for param in collect_parameters(model):
        name = getattr(param, "name", getattr(param, "id", "parameter"))
        identifier = slugify(name)
        default_value = serialise_default(parameter_values.get(name, getattr(param, "default", None)))
        unit = str(getattr(param, "units", ""))
        defaults = curation.get("metadata_defaults", {})
        default_category = defaults.get("category", "")
        default_advanced = bool(defaults.get("advanced", False))
        row = ParameterRow(
            identifier=identifier,
            name=name,
            label=name,
            type=determine_type(default_value),
            default=default_value,
            unit=unit,
            category=default_category,
            advanced=default_advanced,
            description=getattr(param, "description", ""),
            source=getattr(param, "domain", None),
        )
        if isinstance(param, pybamm.InputParameter) and getattr(param, "allowed_values", None):
            row.type = "enum"
            row.choices = tuple({"value": value, "label": str(value)} for value in param.allowed_values)
        apply_curation(row, curation)
        rows[identifier] = row
    return sorted(rows.values(), key=lambda r: r.label.lower())


def parse_arguments(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chemistry", help="PyBaMM chemistry module (e.g. lithium_ion)")
    parser.add_argument("model", help="PyBaMM model class (e.g. DFN)")
    parser.add_argument("parameter_set", help="Parameter set name (e.g. Chen2020)")
    parser.add_argument("output", type=pathlib.Path, help="Path to the JSON schema to write")
    parser.add_argument(
        "--curation",
        type=pathlib.Path,
        default=pathlib.Path("configs/schemas/pybamm/ranges_overrides.yaml"),
        help="Optional YAML file providing metadata overrides",
    )
    return parser.parse_args(argv)


def resolve_model(chemistry: str, model_name: str) -> pybamm.BaseModel:  # type: ignore[name-defined]
    try:
        chemistry_module = getattr(pybamm, chemistry)
    except AttributeError as exc:  # pragma: no cover - invalid input
        raise SystemExit(f"Unknown PyBaMM chemistry module: {chemistry}") from exc
    try:
        model_factory = getattr(chemistry_module, model_name)
    except AttributeError as exc:  # pragma: no cover - invalid input
        raise SystemExit(f"Unknown model '{model_name}' in pybamm.{chemistry}") from exc
    model = model_factory()
    return model


def resolve_parameter_values(parameter_set: str) -> "pybamm.ParameterValues":  # type: ignore[name-defined]
    try:
        preset = getattr(pybamm.parameter_sets, parameter_set)
    except AttributeError as exc:  # pragma: no cover - invalid input
        raise SystemExit(f"Unknown parameter set '{parameter_set}'") from exc
    return pybamm.ParameterValues(chemistry=preset)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_arguments(argv or sys.argv[1:])
    model = resolve_model(args.chemistry, args.model)
    parameter_values = resolve_parameter_values(args.parameter_set)
    parameter_values.process_model(model)
    curation = load_curation(args.curation)
    rows = build_rows(model, parameter_values, curation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump([row.to_dict() for row in rows], handle, indent=2, sort_keys=False)
        handle.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
