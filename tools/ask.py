#!/usr/bin/env python3
# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "INDEX.tsv"
LOG = pathlib.Path(
    os.environ.get("FRAPPE_ASK_LOG", pathlib.Path.home() / ".claude" / "state" / "frappe-ask.log")
)

STOPWORDS = {
    "a", "an", "the", "i", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "on", "at", "for", "and", "or", "but", "not", "no", "nor",
    "do", "does", "did", "doing", "it", "its", "this", "that", "these", "those",
    "my", "me", "we", "you", "your", "he", "she", "they", "them", "with", "as",
    "by", "from", "if", "when", "then", "so", "just", "still", "after", "before",
    "there", "here", "which", "what", "who", "whom", "am", "will", "would",
    "can", "could", "should", "than", "into", "up", "out", "any", "all",
}

_TOKEN_RE = re.compile(r"[a-z0-9_]+")
_NAME_RE = re.compile(r"[a-z0-9]+")

MAX_HITS = 5
WHOLE_QUERY_WEIGHT = 1000
SYMBOL_WEIGHT = 300
NAME_WEIGHT = 9
ONE_TRIGGER_WEIGHT = 100
WHOLE_WORD_WEIGHT = 10


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def rows() -> list[tuple[str, str]]:
    lines = INDEX.read_text(encoding="utf-8").splitlines()
    out = []
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        out.append((parts[0], parts[1]))
    return out


def edged(needle: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![a-z0-9_]){re.escape(needle)}(?![a-z0-9_])")


def address(path: str) -> set[str]:
    stem = pathlib.PurePosixPath(path)
    return set(_NAME_RE.findall(f"{stem.parent.name} {stem.stem}".lower()))


def rank(needles: list[str], patterns: list[re.Pattern[str]], query_lower: str,
         hay: str, phrases: list[str], named: set[str]) -> int:
    loose = sum(1 for n in needles if n in hay)
    words = [n for n, p in zip(needles, patterns, strict=True) if p.search(hay)]
    covered = max((sum(1 for n in needles if n in phrase) for phrase in phrases), default=0)
    return (
        (WHOLE_QUERY_WEIGHT if query_lower in hay else 0)
        + SYMBOL_WEIGHT * sum(1 for n in words if "_" in n)
        + NAME_WEIGHT * sum(1 for n in needles if n in named) // max(len(named), 1)
        + ONE_TRIGGER_WEIGHT * covered
        + WHOLE_WORD_WEIGHT * len(words)
        + loose
    )


def match(words: list[str]) -> list[str]:
    query = " ".join(w for w in words if w.strip())
    query_lower = query.lower()
    all_tokens = tokenize(query_lower)
    nonstop = [t for t in all_tokens if t not in STOPWORDS]
    if not nonstop:
        token_source: list[str] = []
    elif len(nonstop) < 2:
        token_source = all_tokens
    else:
        token_source = nonstop

    needles: list[str] = []
    seen = set()
    for t in token_source:
        if t not in seen:
            seen.add(t)
            needles.append(t)
    if not needles:
        return []
    floor = 1 if len(needles) == 1 else 2
    patterns = [edged(n) for n in needles]

    scored: list[tuple[int, int, str, str]] = []
    for order, (triggers, path) in enumerate(rows()):
        hay = triggers.lower()
        if sum(1 for n in needles if n in hay) < floor:
            continue
        phrases = [p.strip() for p in hay.split(",")]
        scored.append((rank(needles, patterns, query_lower, hay, phrases, address(path)),
                       order, triggers, path))

    scored.sort(key=lambda r: (-r[0], r[1]))

    hits = []
    for _, _, triggers, path in scored[:MAX_HITS]:
        near = next((t.strip() for t in triggers.split(",") if needles[0] in t.lower()), triggers)
        hits.append(f"{path}\t{near[:110]}")
    return hits


def log(query: str, hits: int, payload: int) -> None:
    entry = {
        "at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "q": query,
        "hits": hits,
        "bytes": payload,
        "outcome": "hit" if hits else "miss",
    }
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ask",
        description="Look a fact up in INDEX.tsv and log whether the lookup hit or missed.")
    parser.add_argument("words", nargs="+", help="the words you would type to find the fact")
    parser.add_argument("--cap", type=int, default=12, help="most rows to print")
    args = parser.parse_args(argv)

    hits = match(args.words)
    shown = hits[: args.cap]
    body = "\n".join(shown)
    log(" ".join(args.words), len(hits), len(body.encode("utf-8")))

    if not hits:
        print(f"miss: no row in INDEX.tsv carries all of {args.words}")
        print("narrow differently: drop a word, or try the word the leaf would be NAMED for.")
        return 1
    print(body)
    if len(hits) > len(shown):
        print(f"... {len(hits) - len(shown)} more rows; add a word to narrow.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
