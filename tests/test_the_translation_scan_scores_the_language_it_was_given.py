# Copyright (c) 2026, iabodysa

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCAN = Path(__file__).resolve().parent.parent / "tools" / "check_translations.py"

DOCTYPE = {
    "doctype": "DocType",
    "name": "Leave Slip",
    "fields": [{"fieldname": "reason", "fieldtype": "Data", "label": "Reason For Leave"}],
}

SHIPPED = ("Leave Slip", "Reason For Leave")


def _app(root: Path, csvs: dict[str, tuple[str, ...]]) -> Path:
    package = root / "demoapp"
    doctype = package / "leave" / "doctype" / "leave_slip"
    doctype.mkdir(parents=True)
    (doctype / "leave_slip.json").write_text(json.dumps(DOCTYPE), encoding="utf-8")
    translations = package / "translations"
    translations.mkdir()
    for lang, sources in csvs.items():
        rows = "".join(f"{source},{lang.upper()}-{index}\n" for index, source in enumerate(sources))
        (translations / f"{lang}.csv").write_text(rows, encoding="utf-8")
    return package


def _run(package: Path, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCAN), "--package", str(package), *argv],
        capture_output=True, text=True, check=False,
    )


class TheTranslationScanScoresTheLanguageItWasGiven(unittest.TestCase):

    def test_the_runner_names_the_language_and_the_scan_scores_that_one_alone(self):
        with tempfile.TemporaryDirectory() as raw:
            package = _app(Path(raw), {"fr": SHIPPED, "ar": SHIPPED[:1]})

            unnamed = _run(package)
            self.assertEqual(unnamed.returncode, 2,
                             "the scan ran without being told which language to score")
            self.assertIn("--lang", unnamed.stderr)
            self.assertIn("required", unnamed.stderr)

            covered = _run(package, "--lang", "fr")
            self.assertEqual(covered.returncode, 0, covered.stdout + covered.stderr)
            self.assertIn("PASS", covered.stdout)
            self.assertIn("translations (fr)", covered.stdout)

            short = _run(package, "--lang", "ar")
            self.assertEqual(short.returncode, 1,
                             "a shipped string with no row in the named language passed")
            self.assertIn("Reason For Leave", short.stdout)
            self.assertIn("add a row in ar", short.stdout)
            self.assertNotIn("Leave Slip\n", short.stdout.split("MISSING")[-1])

            payload = json.loads(_run(package, "--lang", "ar", "--json").stdout)
            self.assertEqual(payload["lang"], "ar")
            self.assertEqual(payload["missing_count"], 1,
                             "the scan consumed the app but scored nothing from it")
            self.assertFalse(payload["passed"])

            absent = _run(package, "--lang", "de", "--json")
            self.assertEqual(absent.returncode, 2,
                             "a language the app ships no CSV for was scored instead of refused")
            refusal = json.loads(absent.stdout)
            self.assertEqual(refusal["lang"], "de")
            self.assertTrue(refusal["refused"])
            self.assertFalse(refusal["passed"])


if __name__ == "__main__":
    unittest.main()
