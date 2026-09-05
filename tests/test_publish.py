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
publish = importlib.import_module("publish")


def _git(root: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.email=t@t", "-c", "user.name=t", *argv],
        capture_output=True, text=True, check=True)


def _commit(root: Path, subject: str) -> None:
    _git(root, "add", "-A")
    _git(root, "commit", "-qm", subject)


class PublishFixture(unittest.TestCase):
    """A bare repo standing in for the public remote, and a repo with a skill tree inside it."""

    def setUp(self) -> None:
        self.scratch = TemporaryDirectory()
        tmp = Path(self.scratch.name).resolve()
        self.remote = tmp / "remote.git"
        subprocess.run(["git", "init", "-q", "--bare", "--initial-branch=main", str(self.remote)],
                       check=True, capture_output=True)

        seed = tmp / "seed"
        seed.mkdir()
        subprocess.run(["git", "init", "-q", "--initial-branch=main", str(seed)],
                       check=True, capture_output=True)
        (seed / "SKILL.md").write_text("the published tree\n", encoding="utf-8")
        (seed / "README.md").write_text("old text\n", encoding="utf-8")
        _commit(seed, "seed")
        _git(seed, "remote", "add", "origin", str(self.remote))
        _git(seed, "push", "-q", "origin", "main")

        self.repo = tmp / "config"
        self.source = self.repo / "skills" / "frappe"
        self.source.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", "--initial-branch=main", str(self.repo)],
                       check=True, capture_output=True)
        (self.source / "SKILL.md").write_text("the published tree\n", encoding="utf-8")
        (self.source / "README.md").write_text("new text\n", encoding="utf-8")
        (self.source / "INDEX.tsv").write_text("triggers\tpath\n", encoding="utf-8")
        _commit(self.repo, "seed")

    def tearDown(self) -> None:
        self.scratch.cleanup()


class TheScanSparesTheOneLineThatOnlyLooksLikeACredential(unittest.TestCase):


    def test_the_scanners_own_controls_all_fire_the_way_they_are_meant_to(self):
        passed, total, _ = publish.controls()
        self.assertEqual(passed, total)


if __name__ == "__main__":
    unittest.main()
