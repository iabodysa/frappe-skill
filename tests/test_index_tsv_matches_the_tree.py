# Copyright (c) 2026, iabodysa

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_index as K

SUITE = Path(__file__).resolve().parent.parent


class TheShippedIndexIsBuiltFromTheTree(unittest.TestCase):


    def test_the_file_on_disk_is_what_the_generator_produces(self):
        found = (SUITE / K.INDEX_NAME).read_text(encoding="utf-8")
        self.assertEqual(K.index_text(SUITE), found)


if __name__ == "__main__":
    unittest.main()
