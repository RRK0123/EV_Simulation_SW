#!/usr/bin/env python3
"""Generate an approximated WLTP Class 3 speed trace dataset.

The script creates a CSV file with columns time_s,phase,speed_kph,distance_m.
It approximates the official WLTP cycle structure (low, medium, high, extra-high).
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

DT = 1.0  # seconds


def ramp(start: float, end: float, steps: int) -> List[float]:
    if steps <= 0:
        return []
    if steps == 1:
        return [end]
    step = (end - start) / float(steps - 1)
    return [start + step * i for i in range(steps)]


def hold(value: float, steps: int) -> List[float]:
    return [value for _ in range(max(steps, 0))]


def tile_pattern(duration: int, pattern: Iterable[float]) -> List[float]:
    pattern_list = list(pattern)
    if not pattern_list:
        return [0.0] * duration
    speeds: List[float] = []
    while len(speeds) < duration:
        speeds.extend(pattern_list)
    return speeds[:duration]


@dataclass
class PhasePattern:
    name: str
    duration: int
    base_pattern: List[float]


# Construct representative patterns for each WLTP phase.
low_pattern = (
    ramp(0.0, 18.0, 12)
    + hold(18.0, 6)
    + ramp(18.0, 42.0, 28)
    + hold(42.0, 10)
    + ramp(42.0, 12.0, 15)
    + ramp(12.0, 0.0, 12)
    + hold(0.0, 12)
    + ramp(0.0, 35.0, 20)
    + hold(35.0, 12)
    + ramp(35.0, 0.0, 20)
    + hold(0.0, 12)
)
medium_pattern = (
    ramp(0.0, 28.0, 12)
    + hold(28.0, 8)
    + ramp(28.0, 55.0, 25)
    + hold(55.0, 10)
    + ramp(55.0, 25.0, 12)
    + hold(25.0, 6)
    + ramp(25.0, 70.0, 25)
    + hold(70.0, 12)
    + ramp(70.0, 0.0, 22)
    + hold(0.0, 12)
)
high_pattern = (
    ramp(0.0, 45.0, 15)
    + hold(45.0, 6)
    + ramp(45.0, 90.0, 25)
    + hold(90.0, 14)
    + ramp(90.0, 60.0, 12)
    + hold(60.0, 6)
    + ramp(60.0, 110.0, 30)
    + hold(110.0, 12)
    + ramp(110.0, 0.0, 28)
    + hold(0.0, 15)
)
extra_high_pattern = (
    ramp(0.0, 60.0, 12)
    + hold(60.0, 6)
    + ramp(60.0, 125.0, 35)
    + hold(125.0, 18)
    + ramp(125.0, 80.0, 12)
    + hold(80.0, 8)
    + ramp(80.0, 135.0, 30)
    + hold(135.0, 10)
    + ramp(135.0, 0.0, 32)
    + hold(0.0, 15)
)

PHASES: List[PhasePattern] = [
    PhasePattern("low", 589, tile_pattern(589, low_pattern)),
    PhasePattern("medium", 433, tile_pattern(433, medium_pattern)),
    PhasePattern("high", 455, tile_pattern(455, high_pattern)),
    PhasePattern("extra_high", 323, tile_pattern(323, extra_high_pattern)),
]


def generate_cycle() -> List[tuple[int, str, float, float]]:
    rows: List[tuple[int, str, float, float]] = []
    distance_m = 0.0
    time_s = 0
    rows.append((time_s, "low", 0.0, distance_m))
    previous_speed_mps = 0.0

    for phase in PHASES:
        speeds = phase.base_pattern
        if len(speeds) != phase.duration:
            raise ValueError(f"Phase {phase.name} expected {phase.duration} steps, got {len(speeds)}")
        for speed_kph in speeds:
            time_s += 1
            speed_mps = speed_kph / 3.6
            # trapezoidal integration using previous speed
            distance_m += 0.5 * (speed_mps + previous_speed_mps) * DT
            previous_speed_mps = speed_mps
            rows.append((time_s, phase.name, speed_kph, distance_m))
    return rows


def main() -> None:
    output_path = Path(__file__).resolve().parent.parent / "data" / "wltp" / "wltp_class3_cycle.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = generate_cycle()
    with output_path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["time_s", "phase", "speed_kph", "distance_m"])
        writer.writerows(rows)
    print(f"Wrote {len(rows)} samples to {output_path}")


if __name__ == "__main__":
    main()
