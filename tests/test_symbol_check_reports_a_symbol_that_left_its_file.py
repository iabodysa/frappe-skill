# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
symbol_check = importlib.import_module("symbol_check")

LEAF = """---
name: control
product: "frappe"
---

## paths

frappe/model/naming.py — set_new_name, no_such_symbol_at_all
frappe/model/no_such_file.py — anything
"""


class ASymbolThatLeftItsFileIsNamed(unittest.TestCase):
    def test_the_three_verdicts_come_out_of_one_leaf(self) -> None:
        with TemporaryDirectory() as raw:
            root = Path(raw)
            product = root / "frappe" / "model"
            product.mkdir(parents=True)
            (product / "naming.py").write_text("def set_new_name(doc):\n    return doc\n",
                                               encoding="utf-8")

            leaf = root / "leaf.md"
            leaf.write_text(LEAF, encoding="utf-8")

            def fake_resolve(bench_root, name, version, path):
                target = root / path
                return target if target.is_file() else None

            original = symbol_check.resolve
            symbol_check.resolve = fake_resolve
            try:
                found, seen = symbol_check.check(leaf, root, root)
            finally:
                symbol_check.resolve = original

            self.assertEqual(seen, 2, f"read={seen} path lines, expected 2")
            verdicts = sorted(one.verdict for one in found)
            self.assertEqual(verdicts, ["FILE GONE", "SYMBOL GONE"])
            self.assertTrue(any("no_such_symbol_at_all" in one.detail for one in found))
            self.assertTrue(any("no_such_file.py" in one.detail for one in found))
