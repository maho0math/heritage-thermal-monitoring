"""Единый формат данных и простая валидация."""

from typing import Any, Dict, List, Set

REQUIRED_OBJECT_FIELDS: Set[str] = {
    "id", "title", "address", "year_built", "style",
    "wall_material", "protection_status", "tags"
}

REQUIRED_READING_FIELDS: Set[str] = {
    "id", "object_id", "temperature", "humidity", "timestamp"
}


def normalize_object(raw: dict[str, Any]) -> dict[str, Any]:
    """Приводит запись объекта наследия к единому формату."""
    missing = REQUIRED_OBJECT_FIELDS - raw.keys()
    if missing:
        raise ValueError(f"Объект {raw.get('id', '?')}: нет полей {missing}")

    return {
        "id": str(raw["id"]),
        "title": str(raw["title"]),
        "address": str(raw["address"]),
        "year_built": int(raw["year_built"]),
        "style": str(raw["style"]),
        "wall_material": str(raw["wall_material"]),
        "protection_status": str(raw["protection_status"]),
        "tags": list(raw["tags"]),
        "source": "heritage_store",
        "item_type": "heritage_object",
    }


def normalize_reading(raw: dict[str, Any]) -> dict[str, Any]:
    """Приводит тепловое показание к единому формату."""
    missing = REQUIRED_READING_FIELDS - raw.keys()
    if missing:
        raise ValueError(f"Показание {raw.get('id', '?')}: нет полей {missing}")

    return {
        "id": str(raw["id"]),
        "object_id": str(raw["object_id"]),
        "temperature": float(raw["temperature"]),
        "humidity": float(raw["humidity"]),
        "timestamp": str(raw["timestamp"]),
        "source": "thermal_store",
        "item_type": "thermal_reading",
    }


def calc_risk(temperature: float, humidity: float) -> str:
    """Простая оценка риска по температуре и влажности."""
    if temperature < 12.0 or humidity > 75.0:
        return "высокий"
    if temperature < 15.0 or humidity > 65.0:
        return "средний"
    return "низкий"