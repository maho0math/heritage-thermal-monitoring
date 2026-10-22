"""Базовые тесты прототипа."""

import unittest
import sys
from pathlib import Path

# Чтобы импорты работали при запуске из корня проекта
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.heritage_store.adapter import load_objects
from src.thermal_store.adapter import load_readings
from src.integration.service import get_all_passports, find_high_risk, search_objects
from src.common.models import calc_risk


class TestPrototype(unittest.TestCase):

    def test_load_objects(self):
        objects = load_objects()
        self.assertGreaterEqual(len(objects), 3)
        self.assertEqual(objects[0]["source"], "heritage_store")
        self.assertIn("title", objects[0])

    def test_load_readings(self):
        readings = load_readings()
        self.assertGreaterEqual(len(readings), 4)
        self.assertEqual(readings[0]["source"], "thermal_store")

    def test_passports_created(self):
        passports = get_all_passports()
        self.assertEqual(len(passports), len(load_objects()))
        for p in passports:
            self.assertIn(p["risk_level"], ["низкий", "средний", "высокий", "нет данных"])

    def test_high_risk_found(self):
        high = find_high_risk()
        # В тестовых данных есть объекты с T < 12 или H > 75
        self.assertGreaterEqual(len(high), 1)

    def test_search(self):
        result = search_objects(query="собор")
        self.assertTrue(any("собор" in o["title"].lower() for o in result))

    def test_calc_risk(self):
        self.assertEqual(calc_risk(10.0, 50.0), "высокий")
        self.assertEqual(calc_risk(18.0, 80.0), "высокий")
        self.assertEqual(calc_risk(13.0, 70.0), "средний")
        self.assertEqual(calc_risk(20.0, 50.0), "низкий")


if __name__ == "__main__":
    unittest.main()