#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

"""Runs the known symptom-lookup probes in symptom_probes.tsv through tools/ask.py and
asserts each non-expected-fail probe resolves its expected leaf as the top hit.

symptom_probes.tsv columns: probe, expected_leaf, status (control|ok|expected-fail), cause.
The 'control' row is a trivially unambiguous probe that must always pass; a mass failure
elsewhere while the control still passes reads as a real regression, not a broken harness.
An 'expected-fail' row is recorded, not asserted, with its one-line cause.
"""

from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "tests" / "symptom_probes.tsv"

spec = importlib.util.spec_from_file_location("frappe_ask_probes", ROOT / "tools" / "ask.py")
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)


def load_probes() -> list[dict[str, str]]:
    lines = DATA.read_text(encoding="utf-8").splitlines()
    rows = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        parts += [""] * (4 - len(parts))
        probe, expected_leaf, status, cause = parts[:4]
        rows.append({
            "probe": probe,
            "expected_leaf": expected_leaf,
            "status": status,
            "cause": cause,
        })
    return rows


class SymptomProbes(unittest.TestCase):
    def test_the_population_carries_a_positive_control(self) -> None:
        rows = load_probes()
        controls = [r for r in rows if r["status"] == "control"]
        self.assertEqual(len(controls), 1, "exactly one control row proves the harness is alive")

    def test_every_asserted_probe_resolves_its_expected_leaf(self) -> None:
        rows = load_probes()
        asserted = [r for r in rows if r["status"] != "expected-fail"]
        skipped = [r for r in rows if r["status"] == "expected-fail"]

        control_hit = False
        failures = []
        for row in asserted:
            hits = ask.match(row["probe"].split())
            top = hits[0].split("\t")[0] if hits else None
            if row["status"] == "control":
                control_hit = top == row["expected_leaf"]
            if top != row["expected_leaf"]:
                failures.append(f"{row['probe']!r} -> {top!r}, expected {row['expected_leaf']!r}")

        print(
            f"symptom_probes: consumed={len(rows)} asserted={len(asserted)} "
            f"expected_fail={len(skipped)} passed={len(asserted) - len(failures)} "
            f"control_fired={control_hit}"
        )

        self.assertTrue(control_hit, "the positive control itself failed — the harness is broken")
        self.assertFalse(failures, "; ".join(failures))


if __name__ == "__main__":
    unittest.main()
