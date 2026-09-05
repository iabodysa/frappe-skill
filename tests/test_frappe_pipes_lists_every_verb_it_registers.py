# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import subprocess
import sys
import unittest
from pathlib import Path

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
frappe_pipes = importlib.import_module("frappe_pipes")


class VerbsAreDeclaredInOnePlace(unittest.TestCase):
    def test_the_verbs_listing_is_the_registered_subcommands_and_names_its_count(self) -> None:
        parser, verbs = frappe_pipes.build_parser()
        self.assertIn("verbs", verbs)

        registered = {
            name
            for action in parser._actions
            for name in (action.choices or {})
            if isinstance(action.choices, dict)
        }
        self.assertEqual(set(verbs), registered)

        run = subprocess.run(
            [sys.executable, str(SUITE / "tools" / "frappe-pipes"), "verbs"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(f"read={len(verbs)} verbs registered", run.stdout)
        for name in verbs:
            self.assertIn(name, run.stdout)

        thinned = dict(verbs)
        thinned.pop("schema")
        self.assertNotIn(f"read={len(verbs)} ", frappe_pipes.render_verbs(thinned))
