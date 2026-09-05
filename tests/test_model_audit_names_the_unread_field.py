# Copyright (c) 2026, iabodysa

import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import model_audit


def _package(fields: list[dict], controller: str) -> Path:
    package = Path(tempfile.mkdtemp()) / "someapp"
    doctype_dir = package / "somemodule" / "doctype" / "thing"
    doctype_dir.mkdir(parents=True)
    (doctype_dir / "thing.json").write_text(
        json.dumps({"doctype": "DocType", "name": "Thing", "module": "Somemodule", "fields": fields}),
        encoding="utf-8",
    )
    (doctype_dir / "thing.py").write_text(controller, encoding="utf-8")
    return package


class ADeadFieldIsTheOneNoSourceFileOutsideTheDoctypeJsonNames(unittest.TestCase):

    def test_the_audit_names_the_unread_field_and_leaves_the_read_one_alone(self):
        package = _package(
            [
                {"fieldname": "live_field", "fieldtype": "Data", "hidden": 1},
                {"fieldname": "dead_field", "fieldtype": "Data", "hidden": 1},
            ],
            "def run(doc):\n    return doc.live_field\n",
        )
        result = model_audit.audit(package)
        self.assertEqual(result["doctypes"], 1)
        dead = [(f["doctype"], f["field"]) for f in result["findings"] if f["kind"] == "dead-field"]
        self.assertEqual(dead, [("Thing", "dead_field")])


if __name__ == "__main__":
    unittest.main()
