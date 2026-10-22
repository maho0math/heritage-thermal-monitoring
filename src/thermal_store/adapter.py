"""Адаптер теплового контура."""

import json
from pathlib import Path
from typing import Any

from src.common.models import normalize_reading

DATA_PATH = Path(__file__).resolve().parents[2] / "mock-data" / "thermal_readings.json"


def load_readings() -> list[dict[str, Any]]:
    """Загружает и нормализует тепловые показания."""
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        raw_list = json.load(f)

    return [normalize_reading(item) for item in raw_list]


if __name__ == "__main__":
    readings = load_readings()
    print(f"Загружено показаний: {len(readings)}")
    for r in readings:
        print(f"  {r['id']}: obj={r['object_id']} T={r['temperature']}°C H={r['humidity']}%")