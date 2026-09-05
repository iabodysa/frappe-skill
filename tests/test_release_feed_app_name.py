# Copyright (c) 2026, iabodysa

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from ctlkit.changelog import run_changelog

FEED = "_RELEASES = [\n]\n"
SUMMARY = "The release feed names the configured app"


def build_checkout(base: Path, app: str, depth: tuple[str, ...]) -> Path:
    (base / ".ctl.toml").write_text(f'[project]\napp = "{app}"\n', encoding="utf-8")
    package = base / app
    (package / "translations").mkdir(parents=True)
    (package / "modules.txt").write_text(f"{app.capitalize()}\n", encoding="utf-8")
    feed_dir = package.joinpath(*depth)
    feed_dir.mkdir(parents=True, exist_ok=True)
    feed = feed_dir / "changelog.py"
    feed.write_text(FEED, encoding="utf-8")
    return feed


def feed_app_name(feed: Path) -> str:
    for line in feed.read_text(encoding="utf-8").splitlines():
        if '"app_name"' in line:
            return json.loads("{" + line.rstrip(",") + "}")["app_name"]
    raise AssertionError(f"no app_name written into {feed}")


class TheReleaseFeedNamesTheApp(unittest.TestCase):

    def build(self, depth: tuple[str, ...]) -> str:
        with tempfile.TemporaryDirectory() as scratch:
            checkout = Path(scratch) / "release-feed-checkout"
            checkout.mkdir()
            subprocess.run(["git", "init", "-q", "."], cwd=checkout, capture_output=True)
            feed = build_checkout(checkout, "demoapp", depth)
            run_changelog(root=checkout, version="1.2.3", summary=SUMMARY, bullets=[])
            return feed_app_name(feed)

    def test_the_feed_names_the_configured_app_not_the_checkout_directory(self):
        self.assertEqual(self.build(("www",)), "demoapp")


if __name__ == "__main__":
    unittest.main()
