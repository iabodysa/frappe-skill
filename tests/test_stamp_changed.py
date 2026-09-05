# Copyright (c) 2026, iabodysa


import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import stamp


class StampTimestampTests(unittest.TestCase):

    def test_it_rounds_up_so_the_stamp_is_never_behind_a_row_saved_this_minute(self):
        saved = datetime(2026, 8, 1, 4, 24, 30)
        value = datetime.strptime(stamp.stamp_timestamp(saved), "%Y-%m-%d %H:%M:%S.%f")
        self.assertGreater(value, saved)


if __name__ == "__main__":
    unittest.main()
