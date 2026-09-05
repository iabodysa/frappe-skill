# Copyright (c) 2026, iabodysa

import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import bench_source as K


def _bench(parent: Path, name: str, version: str, sites: bool = True) -> Path:
    root = parent / name
    app = root / "apps" / "frappe" / "frappe"
    app.mkdir(parents=True)
    (app / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")
    if sites:
        (root / "sites" / "one.localhost").mkdir(parents=True)
        (root / "sites" / "one.localhost" / "site_config.json").write_text(
            "{}", encoding="utf-8"
        )
    return root


class TheBenchRootRefusesRatherThanGuesses(unittest.TestCase):

    def test_two_checkouts_refuse_by_name_and_one_resolves(self):
        parent = Path(tempfile.mkdtemp()).resolve()
        neutral = Path(tempfile.mkdtemp()).resolve()
        os.chdir(neutral)
        os.environ.pop("FRAPPE_BENCH_ROOT", None)
        os.environ["XDG_CONFIG_HOME"] = str(neutral)
        search = (str(parent),)

        alone = _bench(parent, "frappe-bench", "15.109.0")
        self.assertEqual(K._default_bench_root(search), alone)

        _bench(parent, "frappe-v16", "16.32.0", sites=False)
        self.assertEqual(K.bench_roots(search), [alone])
        self.assertEqual(K._default_bench_root(search), alone)

        second = _bench(parent, "frappe-next", "16.32.0")
        with self.assertRaises(ValueError) as refusal:
            K._default_bench_root(search)
        message = str(refusal.exception)
        self.assertIn(str(alone), message)
        self.assertIn(str(second), message)


if __name__ == "__main__":
    unittest.main()
