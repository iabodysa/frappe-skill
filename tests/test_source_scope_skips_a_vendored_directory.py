# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
source_scope = importlib.import_module("source_scope")


class VendoredPathsAreNotSource(unittest.TestCase):
    def test_a_vendored_file_is_skipped_and_an_app_file_is_read(self) -> None:
        self.assertTrue(source_scope.is_source_path("demoapp/doctype/thing/thing.py"))
        self.assertFalse(source_scope.is_source_path("demoapp/node_modules/pkg/index.js"))
        self.assertFalse(source_scope.is_source_path("demoapp/translations/ar.csv"))

        with TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "demoapp").mkdir()
            (root / "demoapp" / "thing.py").write_text("x = 1\n", encoding="utf-8")
            (root / "node_modules" / "pkg").mkdir(parents=True)
            (root / "node_modules" / "pkg" / "index.py").write_text("y = 2\n", encoding="utf-8")

            found = source_scope.iter_source_files(root, {".py"})
            names = [path.relative_to(root).as_posix() for path in found]

            self.assertEqual(
                names, ["demoapp/thing.py"],
                f"read=2 python files on disk, {len(names)} counted as source",
            )
