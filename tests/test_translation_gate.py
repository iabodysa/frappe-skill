# Copyright (c) 2026, iabodysa

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))

import translation_gate as tg


def _project(root: Path, scanner_body: str | None) -> Path:
    (root / "demoapp" / "translations").mkdir(parents=True, exist_ok=True)
    if scanner_body is not None:
        scripts = root / "scripts"
        scripts.mkdir(exist_ok=True)
        (scripts / "check_translations.py").write_text(scanner_body, encoding="utf-8")
    return root


def _scanner(missing: int, stale: int, passed: bool, exit_code: int = 0) -> str:
    payload = json.dumps({"missing_count": missing, "stale_count": stale,
                          "label_warning_count": 0, "passed": passed})
    return (
        "#!/usr/bin/env python3\n"
        "import sys\n"
        f"print({payload!r})\n"
        f"sys.exit({exit_code})\n"
    )


class DelegationTests(unittest.TestCase):


    def test_a_scanner_that_exits_nonzero_fails_even_when_it_claims_to_pass(self):
        with tempfile.TemporaryDirectory() as raw:
            root = _project(Path(raw), _scanner(missing=0, stale=0, passed=True, exit_code=1))
            self.assertFalse(tg.verdict(root, "demoapp", "ar", 0, 0, lambda: (0, 0))["ok"])


if __name__ == "__main__":
    unittest.main()
