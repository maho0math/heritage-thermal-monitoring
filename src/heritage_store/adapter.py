"""Адаптер реестра объектов культурного наследия."""

import json
from pathlib import Path
from typing import Any

from src.common.models import normalize_object

DATA_PATH = Path(__file__).resolve().parents[2] / "mock-data" / "heritage_objects.json"


def load_objects() -> list[dict[str, Any]]:
    """Загружает и нормализует каталог объектов наследия."""
    with open(DATA_PATH, encoding="utf-8-sig") as f:
        raw_list = json.load(f)

    return [normalize_object(item) for item in raw_list]


if __name__ == "__main__":
    objects = load_objects()
    print(f"Загружено объектов: {len(objects)}")
    for obj in objects:
        print(f"  {obj['id']}: {obj['title']} ({obj['year_built']})")