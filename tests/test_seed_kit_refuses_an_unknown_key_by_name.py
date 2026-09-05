# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
seed_kit = importlib.import_module("seed_kit")

GOOD = """
[seed]
title = "demo"

[[record]]
doctype = "Item"
ref = "one"
values = { item_code = "A" }
"""

UNKNOWN_KEY = GOOD.replace('values = { item_code = "A" }',
                           'valeus = { item_code = "A" }')


class AnUnknownKeyIsRefusedByName(unittest.TestCase):
    def test_a_good_file_parses_and_a_misspelled_key_names_itself(self) -> None:
        with TemporaryDirectory() as raw:
            root = Path(raw)
            good = root / "good.toml"
            good.write_text(GOOD, encoding="utf-8")
            title, specs = seed_kit.parse_seed_file(good)
            self.assertEqual(len(specs), 1)
            self.assertEqual(specs[0].doctype, "Item")

            bad = root / "bad.toml"
            bad.write_text(UNKNOWN_KEY, encoding="utf-8")
            with self.assertRaises(seed_kit.SeedError) as caught:
                seed_kit.parse_seed_file(bad)
            message = str(caught.exception)
            self.assertIn("valeus", message)
            self.assertIn("Known keys are", message)

            missing = root / "missing.toml"
            with self.assertRaises(seed_kit.SeedError):
                seed_kit.parse_seed_file(missing)
