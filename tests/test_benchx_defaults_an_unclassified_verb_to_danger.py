# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
benchx = importlib.import_module("benchx")


class UnclassifiedVerbIsDanger(unittest.TestCase):
    def test_an_unknown_verb_is_danger_and_a_listed_one_keeps_its_tier(self) -> None:
        population = len(benchx.READ) + len(benchx.KNOWN_WRITE) + len(benchx.DANGEROUS)
        self.assertGreater(population, 0)

        self.assertEqual(benchx.tier("no-such-bench-verb"), "danger")
        self.assertEqual(benchx.tier(""), "danger")
        self.assertEqual(benchx.tier("drop-site"), "danger")
        self.assertEqual(benchx.tier("build"), "write")

        self.assertEqual(benchx.verb_of(["--site", "one.local", "migrate"]), "migrate")
        self.assertEqual(benchx.verb_of(["--verbose", "drop-site", "one.local"]), "drop-site")

        classified = {verb for verb in benchx.KNOWN_WRITE if benchx.tier(verb) == "write"}
        self.assertEqual(
            len(classified), len(benchx.KNOWN_WRITE),
            f"read={population} classified verbs; every KNOWN_WRITE name must tier as write",
        )
