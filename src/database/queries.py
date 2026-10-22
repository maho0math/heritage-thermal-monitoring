"""Запросы к общей базе данных."""

from src.database.schema import get_connection


def objects_with_latest_reading(conn=None):
    own = conn is None
    if own:
        conn = get_connection()
    sql = """
    SELECT o.id, o.title, o.style, o.protection_status,
           r.temperature, r.humidity, r.timestamp
    FROM heritage_objects o
    LEFT JOIN thermal_readings r ON r.id = (
        SELECT id FROM thermal_readings
        WHERE object_id = o.id
        ORDER BY timestamp DESC
        LIMIT 1
    )
    ORDER BY o.title
    """
    rows = conn.execute(sql).fetchall()
    if own:
        conn.close()
    return rows


def high_risk_objects(conn=None):
    own = conn is None
    if own:
        conn = get_connection()
    sql = """
    SELECT o.id, o.title, r.temperature, r.humidity, r.timestamp
    FROM heritage_objects o
    JOIN thermal_readings r ON r.id = (
        SELECT id FROM thermal_readings
        WHERE object_id = o.id
        ORDER BY timestamp DESC
        LIMIT 1
    )
    WHERE r.temperature < 12.0 OR r.humidity > 75.0
    ORDER BY r.temperature
    """
    rows = conn.execute(sql).fetchall()
    if own:
        conn.close()
    return rows


def search_by_title(query, conn=None):
    own = conn is None
    if own:
        conn = get_connection()
    rows = conn.execute(
        "SELECT id, title, address, year_built, style FROM heritage_objects WHERE title LIKE ?",
        (f"%{query}%",)
    ).fetchall()
    if own:
        conn.close()
    return rows


def stats_by_status(conn=None):
    own = conn is None
    if own:
        conn = get_connection()
    rows = conn.execute(
        """SELECT protection_status, COUNT(*) AS cnt
           FROM heritage_objects
           GROUP BY protection_status
           ORDER BY cnt DESC"""
    ).fetchall()
    if own:
        conn.close()
    return rows


def readings_count_per_object(conn=None):
    own = conn is None
    if own:
        conn = get_connection()
    rows = conn.execute(
        """SELECT o.title, COUNT(r.id) AS readings_cnt
           FROM heritage_objects o
           LEFT JOIN thermal_readings r ON r.object_id = o.id
           GROUP BY o.id
           ORDER BY readings_cnt DESC"""
    ).fetchall()
    if own:
        conn.close()
    return rows


if __name__ == "__main__":
    print("=== Объекты с последним показанием ===")
    for row in objects_with_latest_reading():
        t = row["temperature"] if row["temperature"] is not None else "—"
        h = row["humidity"] if row["humidity"] is not None else "—"
        print(f"  {row['title']}: T={t}°C  H={h}%  [{row['protection_status']}]")

    print("\n=== Объекты с высоким риском ===")
    high = high_risk_objects()
    print(f"Найдено: {len(high)}")
    for row in high:
        print(f"  - {row['title']}: T={row['temperature']}°C  H={row['humidity']}%")

    print("\n=== Поиск «собор» ===")
    for row in search_by_title("собор"):
        print(f"  {row['title']} ({row['year_built']})")

    print("\n=== Статистика по охранному статусу ===")
    for row in stats_by_status():
        print(f"  {row['protection_status']}: {row['cnt']}")

    print("\n=== Количество показаний ===")
    for row in readings_count_per_object():
        print(f"  {row['title']}: {row['readings_cnt']}")