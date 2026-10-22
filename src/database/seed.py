"""Загрузка данных из JSON в общую базу."""

import json
from pathlib import Path

from src.database.schema import create_schema, get_connection, DB_PATH

ROOT = Path(__file__).resolve().parents[2]
HERITAGE_JSON = ROOT / "mock-data" / "heritage_objects.json"
THERMAL_JSON = ROOT / "mock-data" / "thermal_readings.json"


def _load_json(path: Path):
    for enc in ("utf-8-sig", "utf-8", "cp1251"):
        try:
            with open(path, encoding=enc) as f:
                return json.load(f)
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    raise RuntimeError(f"Не удалось прочитать {path}")


def seed(db_path=None):
    conn = get_connection(db_path)
    create_schema(conn)
    try:
        # временно отключаем FK, чтобы спокойно перезалить данные
        conn.execute("PRAGMA foreign_keys = OFF")

        conn.execute("DELETE FROM object_tags")
        conn.execute("DELETE FROM thermal_readings")
        conn.execute("DELETE FROM tags")
        conn.execute("DELETE FROM heritage_objects")
        conn.commit()

        objects = _load_json(HERITAGE_JSON)
        readings = _load_json(THERMAL_JSON)

        print(f"Загружено из JSON: объектов={len(objects)}, показаний={len(readings)}")
        object_ids = set()

        tag_ids = {}
        for obj in objects:
            conn.execute(
                """INSERT INTO heritage_objects
                   (id, title, address, year_built, style, wall_material, protection_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    obj["id"], obj["title"], obj["address"], int(obj["year_built"]),
                    obj["style"], obj["wall_material"], obj["protection_status"]
                )
            )
            object_ids.add(obj["id"])
            for tag_name in obj.get("tags", []):
                if tag_name not in tag_ids:
                    cur = conn.execute("INSERT INTO tags (name) VALUES (?)", (tag_name,))
                    tag_ids[tag_name] = cur.lastrowid
                conn.execute(
                    "INSERT OR IGNORE INTO object_tags (object_id, tag_id) VALUES (?, ?)",
                    (obj["id"], tag_ids[tag_name])
                )

        conn.commit()
        print(f"Объекты в базе: {sorted(object_ids)}")

        skipped = 0
        for r in readings:
            if r["object_id"] not in object_ids:
                print(f"  ПРОПУСК показания {r['id']}: нет объекта {r['object_id']}")
                skipped += 1
                continue
            conn.execute(
                """INSERT INTO thermal_readings
                   (id, object_id, temperature, humidity, timestamp)
                   VALUES (?, ?, ?, ?, ?)""",
                (r["id"], r["object_id"], float(r["temperature"]), float(r["humidity"]), r["timestamp"])
            )

        conn.commit()
        conn.execute("PRAGMA foreign_keys = ON")

        print(f"База создана: {db_path or DB_PATH}")
        print(f"Импортировано объектов: {len(objects)}; показаний: {len(readings) - skipped}; тегов: {len(tag_ids)}")
        if skipped:
            print(f"Пропущено показаний из-за отсутствующих объектов: {skipped}")
    finally:
        conn.close()


if __name__ == "__main__":
    seed()