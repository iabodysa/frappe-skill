# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
repo_guards = importlib.import_module("repo_guards")


def _git(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *argv],
        capture_output=True, text=True, check=True)


class ATrackedHookNothingReachesIsNamed(unittest.TestCase):
    def test_an_unwired_tracked_hook_is_reported_then_wired(self) -> None:
        with TemporaryDirectory() as raw:
            root = Path(raw)
            _git(root, "init", "-q")
            hooks = root / ".githooks"
            hooks.mkdir()
            (hooks / "pre-commit").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (root / "README.md").write_text("demo\n", encoding="utf-8")

            self.assertEqual(repo_guards.unwired_hooks(root), [],
                             "read=0 tracked hooks before the commit, so nothing is unwired")

            _git(root, "add", "-A")
            _git(root, "commit", "-qm", "tracked hook")

            self.assertEqual(repo_guards.unwired_hooks(root), ["pre-commit"])

            self.assertEqual(repo_guards.wire_hooks(root), ["pre-commit"])
            self.assertEqual(repo_guards.unwired_hooks(root), [])

            bare = Path(raw) / "bare"
            bare.mkdir()
            _git(bare, "init", "-q")
            self.assertEqual(repo_guards.unwired_hooks(bare), [])
