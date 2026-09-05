# Copyright (c) 2026, iabodysa


import sys
import unittest
import unittest.mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from ctlkit import release


def wave(surface: int = 0, behavior: int = 0, breaking: int = 0, module: int = 0) -> dict:
    return {"docs_i18n": 0, "new_surface": surface, "behavior": behavior,
            "breaking": breaking, "new_module": module}


class TheMiddleDigit(unittest.TestCase):


    def test_both_floors_cleared_earns_the_minor(self):
        kind, why = release._decide_bump(wave(surface=6), since_minor=12)
        self.assertEqual(kind, "minor")
        self.assertIn("both floors cleared", why.lower())


if __name__ == "__main__":
    unittest.main()
