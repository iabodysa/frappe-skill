# Copyright (c) 2026, iabodysa

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import schema_peek as sp


def _project(body: str) -> Path:
    root = Path(tempfile.mkdtemp())
    (root / ".ctl.toml").write_text(body, encoding="utf-8")
    (root / "bench-here").mkdir()
    return root


class ProjectTableTests(unittest.TestCase):
    def test_site_comes_from_the_project_table(self):
        root = _project('[project]\napp = "demoapp"\nsite = "ci.localhost"\n')
        cfg = sp.resolve_config(str(root))
        self.assertEqual(cfg["site"], "ci.localhost")


if __name__ == "__main__":
    unittest.main()
