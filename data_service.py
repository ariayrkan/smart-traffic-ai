from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
import glob

import pandas as pd

REQUIRED_COLUMNS = [
    "step",
    "real_vehicle_count",
    "sensor_vehicle_count",
    "avg_speed",
    "waiting_time",
    "attack_detected",
    "mode",
    "green_light_duration",
]


@dataclass
class Snapshot:
    step: int
    real_count: int
    sensor_count: int
    avg_speed: float
    waiting_time: float
    attack_detected: int
    mode: str
    green_duration: int


class DataService:
    """Streams CSV rows like a live feed and keeps state/history for panels."""

    def __init__(self, csv_path: Path):
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        self.df = pd.read_csv(csv_path)

        # Normalise boolean/string attack_detected
        if self.df["attack_detected"].dtype == object:
            self.df["attack_detected"] = (
                self.df["attack_detected"]
                .str.strip()
                .str.upper()
                .map({"TRUE": 1, "FALSE": 0, "1": 1, "0": 0})
                .fillna(0)
                .astype(int)
            )

        missing = [c for c in REQUIRED_COLUMNS if c not in self.df.columns]
        if missing:
            raise ValueError(f"Missing columns in CSV: {missing}")

        self.index    = 0
        self.history: List[Snapshot] = []
        self.events:  List[str]      = ["[SYSTEM] Dashboard initialised"]
        self.scenario = "normal"

    def has_data(self) -> bool:
        return len(self.df) > 0

    def set_scenario(self, scenario: str):
        self.scenario = scenario
        self.events.append(f"[SYSTEM] Scenario → {scenario.upper()}")

    def next(self) -> Snapshot:
        row = self.df.iloc[self.index]
        self.index = (self.index + 1) % len(self.df)

        real_count      = int(row["real_vehicle_count"])
        sensor_count    = int(row["sensor_vehicle_count"])
        avg_speed       = float(row["avg_speed"])
        waiting_time    = float(row["waiting_time"])
        attack_detected = int(row["attack_detected"])
        mode            = str(row["mode"])

        if self.scenario == "spoofing":
            sensor_count    += 10
            attack_detected  = 1
            mode             = "SAFE_TIMED"
            waiting_time    += 1.2
        elif self.scenario == "heavy":
            real_count      += 8
            sensor_count    += 5
            avg_speed        = max(10.0, avg_speed - 6)
            waiting_time    += 2.2
            attack_detected  = 0
            mode             = "ADAPTIVE_HEAVY"
        elif self.scenario == "recovery":
            sensor_count    = real_count + 1
            avg_speed      += 2
            waiting_time    = max(0.2, waiting_time - 1.1)
            attack_detected = 0
            mode            = "RECOVERY_MONITOR"

        item = Snapshot(
            step            = int(row["step"]),
            real_count      = real_count,
            sensor_count    = sensor_count,
            avg_speed       = avg_speed,
            waiting_time    = waiting_time,
            attack_detected = attack_detected,
            mode            = mode,
            green_duration  = int(row["green_light_duration"]),
        )
        self.history.append(item)
        self.history = self.history[-40:]

        diff = abs(item.real_count - item.sensor_count)
        if item.attack_detected:
            self.events.append(
                f"[ALERT] Step {item.step}: spoofing suspected — gap={diff} | mode={item.mode}"
            )
        elif diff > 7:
            self.events.append(
                f"[WARN]  Step {item.step}: elevated mismatch — gap={diff}"
            )
        else:
            self.events.append(
                f"[INFO]  Step {item.step}: telemetry stable"
            )
        self.events = self.events[-120:]
        return item

    def summary(self) -> Dict[str, float]:
        if not self.history:
            return {"attack_rate": 0.0, "avg_wait": 0.0, "avg_speed": 0.0, "avg_gap": 0.0}
        h = self.history
        return {
            "attack_rate": sum(i.attack_detected for i in h) / len(h),
            "avg_wait":    sum(i.waiting_time    for i in h) / len(h),
            "avg_speed":   sum(i.avg_speed       for i in h) / len(h),
            "avg_gap":     sum(abs(i.real_count - i.sensor_count) for i in h) / len(h),
        }


def resolve_csv() -> Path:
    """Find the traffic CSV regardless of exact filename / spaces / parens."""
    here = Path(__file__).resolve().parent

    # 1) exact names
    for name in [
        "traffic_ai_attack_results (1).csv",
        "traffic_ai_attack_results.csv",
        "traffic_ai_attack_results__1_.csv",
    ]:
        p = here / name
        if p.exists():
            return p

    # 2) any CSV containing "traffic" in this directory
    matches = list(here.glob("*traffic*.csv")) + list(here.parent.glob("*traffic*.csv"))
    if matches:
        return matches[0]

    raise FileNotFoundError(
        "Could not find traffic_ai_attack_results CSV. "
        "Place it in the same folder as app.py."
    )
