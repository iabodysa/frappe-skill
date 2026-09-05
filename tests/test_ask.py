#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("frappe_ask", ROOT / "tools" / "ask.py")
ask = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ask)


def scored(needles: list[str], hay: str, path: str = "knowledge/x/y.md") -> int:
    patterns = [ask.edged(n) for n in needles]
    phrases = [p.strip() for p in hay.split(",")]
    return ask.rank(needles, patterns, " ".join(needles), hay, phrases, ask.address(path))


class Ask(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.log = pathlib.Path(tmp.name) / "ask.log"
        previous = ask.LOG
        ask.LOG = self.log
        self.addCleanup(setattr, ask, "LOG", previous)

    def entries(self) -> list[dict]:
        return [json.loads(line)
                for line in self.log.read_text(encoding="utf-8").splitlines() if line]

    def run_main(self, argv: list[str]) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = ask.main(argv)
        return code, out.getvalue()

    def test_a_hit_returns_the_path_and_not_the_whole_row(self):
        hits = ask.match(["autoname"])
        self.assertTrue(hits, "the index carries an autoname leaf; a zero here is a broken matcher")
        self.assertTrue(all("\t" in row for row in hits))
        self.assertLess(max(len(row) for row in hits), 200)

    def test_every_needle_must_appear(self):
        self.assertEqual(ask.match(["autoname", "zzzznotathing"]), [])

    def test_a_hit_is_logged_as_a_hit(self):
        self.assertEqual(self.run_main(["autoname"])[0], 0)
        entries = self.entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["outcome"], "hit")
        self.assertGreater(entries[0]["hits"], 0)
        self.assertGreater(entries[0]["bytes"], 0)

    def test_a_miss_is_logged_as_a_miss_and_exits_one(self):
        code, out = self.run_main(["zzzznotathing"])
        self.assertEqual(code, 1)
        self.assertEqual(self.entries()[0]["outcome"], "miss")
        self.assertEqual(self.entries()[0]["hits"], 0)
        self.assertLess(len(out), 400)

    def test_a_lookup_survives_an_unwritable_log(self):
        ask.LOG = self.log.parent / "no" / "such" / "dir" / "ask.log"
        with mock.patch.object(pathlib.Path, "mkdir", side_effect=OSError):
            self.assertEqual(self.run_main(["autoname"])[0], 0)

    def test_the_cap_bounds_what_is_printed(self):
        code, out = self.run_main(["--cap", "1", "a"])
        self.assertIn(code, (0, 1))
        self.assertLessEqual(out.count("\n"), 3)

    def test_an_exact_symbol_query_still_returns_its_leaf_first(self):
        hits = ask.match(["make_app_page"])
        self.assertTrue(hits, "the symbol lookup is a working exact match; a zero is a regression")
        self.assertEqual(hits[0].split("\t")[0], "knowledge/desk/app-page.md")

    def test_a_natural_sentence_returns_at_least_one_leaf(self):
        hits = ask.match("the button i added does not appear on the form".split())
        self.assertTrue(hits, "a plain-English symptom sentence must find at least one leaf")

    def test_a_query_of_pure_stopwords_returns_nothing_and_exits_one(self):
        words = ["the", "a", "is", "of", "to", "and"]
        self.assertEqual(ask.match(words), [])
        self.assertEqual(self.run_main(words)[0], 1)

    def test_a_nonsense_query_returns_nothing_and_exits_one(self):
        words = ["zzqxx", "wibbleflorp", "notarealword"]
        self.assertEqual(ask.match(words), [])
        self.assertEqual(self.run_main(words)[0], 1)

    def test_one_trigger_naming_the_failure_outranks_the_same_words_scattered(self):
        needles = ["button", "added", "appear"]
        focused = "the button i added does not appear, an unrelated trigger"
        scattered = "button, a note about added rows, appear in a chart"
        self.assertGreater(scored(needles, focused), scored(needles, scattered))

    def test_the_whole_query_as_one_phrase_outranks_every_other_signal(self):
        needles = ["install", "fails", "partway"]
        verbatim = "install fails partway"
        spread = "install, fails, partway, install_site, install fails"
        self.assertGreater(scored(needles, verbatim), scored(needles, spread))

    def test_a_symbol_needle_outranks_a_plain_word_needle(self):
        self.assertGreater(scored(["get_list"], "get_list"), scored(["getlist"], "getlist"))

    def test_the_leaf_named_for_the_query_word_breaks_a_tie(self):
        needles = ["install", "fails"]
        hay = "install fails on this site"
        self.assertGreater(
            scored(needles, hay, "knowledge/bench/install-app.md"),
            scored(needles, hay, "knowledge/api/credential-storage.md"))

    def test_the_named_leaf_never_outranks_a_trigger_that_carries_one_more_word(self):
        needles = ["install", "fails", "partway"]
        named_but_thin = "install fails, something else entirely"
        unnamed_but_full = "install fails partway through, another trigger"
        self.assertGreater(
            scored(needles, unnamed_but_full, "knowledge/api/credential-storage.md"),
            scored(needles, named_but_thin, "knowledge/bench/install-app.md"))


if __name__ == "__main__":
    unittest.main()
