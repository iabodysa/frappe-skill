# Copyright (c) 2026, iabodysa

import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import create_kit


def fake_bench(root: Path) -> Path:
    package = root / "apps" / "frappe" / "frappe"
    (package / "core" / "doctype" / "user").mkdir(parents=True)
    (package / "core" / "doctype" / "user" / "user.json").write_text(json.dumps({
        "doctype": "DocType", "name": "User", "module": "Core", "fields": [],
        "permissions": [{"role": "System Manager"}],
    }), encoding="utf-8")
    (package / "core" / "doctype" / "sales_invoice").mkdir(parents=True)
    (package / "core" / "doctype" / "sales_invoice" / "sales_invoice.json").write_text(json.dumps({
        "doctype": "DocType", "name": "Sales Invoice", "module": "Core",
        "fields": [{"fieldname": "naming_series", "fieldtype": "Select", "options": "ACC-SINV-.YYYY.-"}],
        "permissions": [],
    }), encoding="utf-8")
    (package / "core" / "role" / "auditor").mkdir(parents=True)
    (package / "core" / "role" / "auditor" / "auditor.json").write_text(
        json.dumps({"doctype": "Role", "name": "Auditor"}), encoding="utf-8")
    (package / "hooks.py").write_text(
        'app_name = "frappe"\ndoc_events = {}\nscheduler_events = {}\n', encoding="utf-8")
    (package / "boot.py").write_text(
        'frappe.get_hooks("permission_query_conditions")\n', encoding="utf-8")
    return root


PLAN_HEAD = """roles = ["Ledger Clerk"]

[app]
name = "ledger"
title = "Ledger"
modules = ["Ledger"]

[hooks]
"""


FIRST_RUN = """
[first_run]
workspace = "Ledger"
module = "Ledger"
onboarding = "none"
"""


def plan_text(*, doctypes: str, hooks: str = "", roles: str = '["Ledger Clerk"]',
              first_run: str = FIRST_RUN) -> str:
    head = PLAN_HEAD.replace('roles = ["Ledger Clerk"]', f"roles = {roles}")
    return head + hooks + doctypes + first_run


ONE_DOCTYPE = """
[[doctype]]
name = "Ledger Entry"
module = "Ledger"
kind = "ordinary"
submittable = "no"
posts_ledger_entries = "no"
naming = "hash"

[[doctype.field]]
fieldname = "{fieldname}"
fieldtype = "Data"

[[doctype.permission]]
role = "Ledger Clerk"
read = true
"""


class CheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bench = fake_bench(self.root / "bench")
        self.addCleanup(self.tmp.cleanup)

    def write(self, text: str) -> Path:
        path = self.root / "plan.toml"
        path.write_text(text, encoding="utf-8")
        return path

    def keys(self, path: Path) -> list[str]:
        return [one.key for one in create_kit.run_check(path, self.bench).refusals]


    def test_an_unanswered_irreversible_key_is_refused(self):
        body = ONE_DOCTYPE.format(fieldname="posting_date").replace(
            'naming = "hash"', 'naming = "ANSWER-ME"')
        path = self.write(plan_text(doctypes=body))
        self.assertIn("doctype[Ledger Entry].naming", self.keys(path))


if __name__ == "__main__":
    unittest.main()
