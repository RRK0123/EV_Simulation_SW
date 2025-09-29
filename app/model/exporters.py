from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict


class ExportError(RuntimeError):
    """Raised when an export operation fails."""


def export_json(values: Dict[str, Any], destination: str | Path) -> None:
    import json

    path = Path(destination)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(values, handle, indent=2, sort_keys=True)


def export_csv(values: Dict[str, Any], destination: str | Path) -> None:
    path = Path(destination)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        for key, value in values.items():
            writer.writerow([key, value])


def export_dat(values: Dict[str, Any], destination: str | Path) -> None:
    path = Path(destination)
    with path.open("w", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key} = {value}\n")


def export_mdf(values: Dict[str, Any], destination: str | Path) -> None:
    path = Path(destination)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("; MDF4 export is not yet implemented.\n")
        for key, value in values.items():
            handle.write(f"; {key} = {value}\n")


EXPORTERS = {
    ".json": export_json,
    ".csv": export_csv,
    ".dat": export_dat,
    ".mdf": export_mdf,
    ".mdf4": export_mdf,
}
