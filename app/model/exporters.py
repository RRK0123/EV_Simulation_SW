from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict

try:  # pragma: no cover - optional dependency
    from asammdf import MDF, Signal  # type: ignore

    HAS_ASAMMDF = True
except Exception:  # noqa: BLE001
    HAS_ASAMMDF = False


def export_params_json(path: str | Path, params: Dict[str, Any]) -> None:
    destination = Path(path)
    with destination.open("w", encoding="utf-8") as handle:
        json.dump(params, handle, indent=2, ensure_ascii=False)


def export_params_csv(path: str | Path, params: Dict[str, Any]) -> None:
    destination = Path(path)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["key", "value"])
        for key, value in params.items():
            writer.writerow([key, value])


def export_params_dat(path: str | Path, params: Dict[str, Any]) -> None:
    destination = Path(path)
    with destination.open("w", encoding="utf-8") as handle:
        handle.write("# PyBaMM Parameters (SI)\n")
        for key, value in params.items():
            handle.write(f"{key}={value}\n")


def export_timeseries_csv(path: str | Path, series: Dict[str, list | tuple]) -> None:
    destination = Path(path)
    keys = list(series.keys())
    rows = zip(*[series[k] for k in keys]) if keys else []
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(keys)
        for row in rows:
            writer.writerow(row)


def export_timeseries_mdf4(path: str | Path, series: Dict[str, list | tuple], rate_hz: float | None = None) -> None:
    if not HAS_ASAMMDF:
        raise RuntimeError("asammdf not installed. Install `asammdf` to enable MDF4 export.")
    import numpy as np

    destination = Path(path)
    mdf = MDF()
    keys = list(series.keys())
    if not keys:
        mdf.save(destination)
        return
    length = len(series[keys[0]])
    timestamps = np.arange(length) / (rate_hz or 1.0)
    for key in keys:
        data = np.asarray(series[key])
        signal = Signal(data=data, timestamps=timestamps, name=key)
        mdf.append(signal)
    mdf.save(destination)


def read_params_json(path: str | Path) -> Dict[str, Any]:
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_params_dat(path: str | Path) -> Dict[str, Any]:
    source = Path(path)
    params: Dict[str, Any] = {}
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            try:
                params[key] = float(value)
            except ValueError:
                params[key] = value
    return params


def read_timeseries_mdf4(path: str | Path) -> Dict[str, list]:
    if not HAS_ASAMMDF:
        raise RuntimeError("asammdf not installed. Install `asammdf` to enable MDF4 read.")
    source = Path(path)
    mdf = MDF(source)
    data: Dict[str, list] = {}
    for channel in mdf.channels_db:  # type: ignore[attr-defined]
        signal = mdf.get(channel)
        data[channel] = signal.samples.tolist()
    return data
