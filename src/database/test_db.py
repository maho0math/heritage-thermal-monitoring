"""Автоматические тесты общей базы данных."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.database.schema import get_connection
from src.database.seed import seed
from src.database import queries


class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False)
        cls.tmp.close()
        cls.db_path = Path(cls.tmp.name)
        seed(db_path=cls.db_path)

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink(cls.db_path)
        except OSError:
            pass

    def test_objects_count(self):
        conn = get_connection(self.db_path)
        cnt = conn.execute("SELECT COUNT(*) FROM heritage_objects").fetchone()[0]
        conn.close()
        self.assertEqual(cnt, 4)

    def test_readings_count(self):
        conn = get_connection(self.db_path)
        cnt = conn.execute("SELECT COUNT(*) FROM thermal_readings").fetchone()[0]
        conn.close()
        self.assertEqual(cnt, 6)

    def test_tags_exist(self):
        conn = get_connection(self.db_path)
        cnt = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        conn.close()
        self.assertGreaterEqual(cnt, 5)

    def test_high_risk(self):
        conn = get_connection(self.db_path)
        rows = queries.high_risk_objects(conn)
        conn.close()
        self.assertGreaterEqual(len(rows), 1)

    def test_search_sobor(self):
        conn = get_connection(self.db_path)
        rows = queries.search_by_title("собор", conn)
        conn.close()
        self.assertTrue(any("собор" in r["title"].lower() for r in rows))

    def test_stats(self):
        conn = get_connection(self.db_path)
        rows = queries.stats_by_status(conn)
        conn.close()
        self.assertGreaterEqual(len(rows), 1)


if __name__ == "__main__":
    unittest.main()