# Copyright (c) 2026, iabodysa

from __future__ import annotations

import importlib
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

SUITE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SUITE / "tools"))
benchx = importlib.import_module("benchx")


def make_target(bench: Path, site: str = "", log_dir: Path | None = None) -> "benchx.Target":
    config = {
        "target": {"kind": "local", "env": "dev", "bench": str(bench), "site": site},
        "output": {"log_dir": str(log_dir or (bench / "logs"))},
        "safety": {"allow_destructive": True},
    }
    return benchx.Target(config, None)


class FakeDone:
    """Stands in for `subprocess.CompletedProcess` — no real bench call in this file."""

    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


class LaneGuardRefusesEveryNonLaneSite(unittest.TestCase):
    def test_apex_and_ci_are_refused_without_ever_touching_bench(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bench = Path(tmp)
            for forbidden in ("apex.localhost", "ci.localhost"):
                target = make_target(bench, site=forbidden)
                with mock.patch.object(
                    benchx, "execute", side_effect=AssertionError("must not reach bench")
                ) as fake:
                    code = benchx.lane_drop(target, [])
                self.assertNotEqual(code, 0, f"{forbidden} must be refused, exit 0 would mean it dropped")
                fake.assert_not_called()

    def test_a_bare_name_that_is_not_lane_shaped_is_refused_by_the_guard(self) -> None:
        self.assertFalse(benchx.is_lane_site("myname"))
        self.assertFalse(benchx.is_lane_site("apex.localhost"))
        self.assertFalse(benchx.is_lane_site("ci.localhost"))
        self.assertFalse(benchx.is_lane_site(""))
        self.assertTrue(benchx.is_lane_site("lane-my-agent.localhost"))


class LaneNewRefusesAnExistingSite(unittest.TestCase):
    def test_new_refuses_when_the_stubbed_bench_reports_the_site_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bench = Path(tmp)
            target = make_target(bench)
            calls: list[list[str]] = []

            def fake_execute(_target: "benchx.Target", argv: list[str]) -> FakeDone:
                calls.append(argv)
                return FakeDone(returncode=0)  # list-apps succeeding means the site is there

            with mock.patch.object(benchx, "execute", side_effect=fake_execute):
                code = benchx.lane_new(target, ["--name", "worker-1"])

            self.assertEqual(code, benchx.EXIT_REFUSED)
            self.assertEqual(len(calls), 1, "must refuse before ever calling new-site")
            self.assertIn("list-apps", calls[0])
            self.assertNotIn("new-site", calls[0])


class LaneNameDerivation(unittest.TestCase):
    def test_a_worktree_basename_becomes_a_valid_lane_site(self) -> None:
        slug = benchx.slugify("My Worktree_02!!")
        self.assertEqual(slug, "my-worktree-02")
        site = benchx.lane_site(slug)
        self.assertEqual(site, "lane-my-worktree-02.localhost")
        self.assertTrue(benchx.is_lane_site(site))

    def test_a_symbol_only_name_still_derives_a_valid_site(self) -> None:
        self.assertTrue(benchx.is_lane_site(benchx.lane_site(benchx.slugify("!!!"))))


class LaneDropMovesToTrashAndNeverUnlinks(unittest.TestCase):
    def test_drop_relocates_the_site_dir_and_writes_the_four_sidecar_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bench = root / "bench"
            trash = root / "trash"
            site = "lane-test-agent.localhost"
            site_dir = bench / "sites" / site
            site_dir.mkdir(parents=True)
            marker = site_dir / "site_config.json"
            marker.write_text('{"db_name": "x"}', encoding="utf-8")

            target = make_target(bench, site=site, log_dir=root / "logs")
            calls: list[list[str]] = []

            def fake_execute(_target: "benchx.Target", argv: list[str]) -> FakeDone:
                calls.append(argv)
                return FakeDone(returncode=0, stdout="dropped\n")

            with mock.patch.object(benchx, "execute", side_effect=fake_execute), \
                 mock.patch.object(benchx, "trash_home", return_value=trash), \
                 mock.patch.object(benchx, "load", return_value=({}, None)):
                code = benchx.lane_drop(target, [])

            self.assertEqual(code, 0)
            self.assertEqual(calls[0][:2], ["drop-site", site], "the stubbed bench call, not a real one")
            self.assertFalse(site_dir.exists(), "the original path must be empty — moved, not copied")

            dest = trash / time.strftime("%Y-%m-%d") / site
            self.assertTrue(dest.is_dir(), "the site directory must reappear under trash")
            self.assertTrue(
                (dest / "site_config.json").is_file(),
                "the moved directory keeps its content — proof this was shutil.move, not an unlink",
            )

            sidecar = dest.parent / f"{site}.trash.txt"
            self.assertTrue(sidecar.is_file())
            body = sidecar.read_text(encoding="utf-8")
            for key in ("source:", "removed_in:", "reason:", "restore:"):
                self.assertIn(key, body, f"sidecar must carry the {key} key")


if __name__ == "__main__":
    unittest.main()
