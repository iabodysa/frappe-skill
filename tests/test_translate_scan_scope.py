# Copyright (c) 2026, iabodysa

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

from ctlkit import translate


class WalkFilesScope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def _write(self, rel: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('__("Building");\n', encoding="utf-8")
        return path

    def _walked(self) -> set[str]:
        return {p.relative_to(self.root).as_posix() for p in translate.walk_files(self.root)}


    def test_built_output_under_public_stays_skipped(self):
        self._write("public/dist/js/demoapp.bundle.ABCD1234.js")
        self._write("public/worker_portal/assets/index-9f1.js")
        self._write("public/vendor/leaflet.js")
        self.assertEqual(self._walked(), set())


if __name__ == "__main__":
    unittest.main()
