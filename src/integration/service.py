"""Интеграционный сервис: объединение данных и оценка риска."""

from typing import Any, Optional, List, Dict

from src.heritage_store.adapter import load_objects
from src.thermal_store.adapter import load_readings
from src.common.models import calc_risk


def get_latest_reading(object_id: str, readings: List[dict]) -> Optional[dict]:
    """Возвращает последнее показание для объекта."""
    obj_readings = [r for r in readings if r["object_id"] == object_id]
    if not obj_readings:
        return None
    return max(obj_readings, key=lambda r: r["timestamp"])


def build_passport(obj: dict, reading: Optional[dict]) -> Dict[str, Any]:
    """Формирует паспорт объекта с оценкой риска."""
    passport = {
        "object": obj,
        "latest_reading": reading,
        "risk_level": "нет данных",
        "recommendation": "Недостаточно тепловых данных",
    }

    if reading is None:
        return passport

    risk = calc_risk(reading["temperature"], reading["humidity"])
    passport["risk_level"] = risk

    if risk == "высокий":
        passport["recommendation"] = (
            "Критический режим: риск промерзания/конденсата. "
            "Требуется корректировка отопления и проверка вентиляции."
        )
    elif risk == "средний":
        passport["recommendation"] = (
            "Повышенный риск. Рекомендуется мониторинг и "
            "поддержание стабильного температурно-влажностного режима."
        )
    else:
        passport["recommendation"] = "Режим в норме. Продолжать плановый мониторинг."

    return passport


def get_all_passports() -> List[Dict[str, Any]]:
    """Строит паспорта для всех объектов."""
    objects = load_objects()
    readings = load_readings()
    return [build_passport(obj, get_latest_reading(obj["id"], readings)) for obj in objects]


def find_high_risk() -> List[Dict[str, Any]]:
    """Возвращает объекты с высоким риском."""
    return [p for p in get_all_passports() if p["risk_level"] == "высокий"]


def search_objects(query: str = "", style: str = "", status: str = "") -> List[dict]:
    """Простой поиск/фильтрация объектов."""
    objects = load_objects()
    result = objects

    if query:
        q = query.lower()
        result = [
            o for o in result
            if q in o["title"].lower() or q in o["address"].lower()
        ]
    if style:
        result = [o for o in result if o["style"].lower() == style.lower()]
    if status:
        result = [o for o in result if o["protection_status"].lower() == status.lower()]

    return result


if __name__ == "__main__":
    print("=== Паспорта объектов ===")
    for p in get_all_passports():
        obj = p["object"]
        print(f"\n{obj['title']} ({obj['id']})")
        print(f"  Риск: {p['risk_level']}")
        print(f"  Рекомендация: {p['recommendation']}")

    print("\n=== Объекты с высоким риском ===")
    high = find_high_risk()
    print(f"Найдено: {len(high)}")
    for p in high:
        print(f"  - {p['object']['title']}")