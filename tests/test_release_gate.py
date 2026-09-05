# Copyright (c) 2026, iabodysa


import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import release_gate

ROOT = Path("/nonexistent")


def _stamp(hours_ago):
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self._real = release_gate.release_timestamp

    def tearDown(self):
        release_gate.release_timestamp = self._real

    def _pretend_last_release_was(self, hours_ago):
        release_gate.release_timestamp = lambda root, ref: _stamp(hours_ago)


    def test_batched_inside_the_window_is_refused_and_names_the_previous_release(self):
        self._pretend_last_release_was(1.5)
        text = release_gate.refusal(ROOT, "v2.9.3", "batched", "")
        self.assertIn("Refusing to bump", text)
        self.assertIn("v2.9.3", text, "the refusal must name the previous release")
        self.assertIn("1.5 hours ago", text, "and say how long ago it was cut")
        self.assertIn(str(release_gate.BATCHED_MIN_HOURS), text)


if __name__ == "__main__":
    unittest.main()
