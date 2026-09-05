# frappe

A knowledge store of verified Frappe, ERPNext, HRMS and frappe-ui behaviour, for coding agents and
for the people who supervise them. Every fact names the files and the symbols it was read from, and
one file declares the release they were read at.

- **159 facts** in eight houses, each house named for a thing a Frappe developer says out loud
- **27 chapters** that settle a verdict between routes the framework offers
- **9 task pages** for a job you know by name but not by vocabulary

The read path is one grep over `INDEX.tsv` — a header line and 195 rows, one per leaf, chapter and
task page — for the words you would actually type:

```
$ grep -i "name empty" INDEX.tsv
```

One row comes back. Open the file its `path` column names, and read only that file:

```
triggers   autoname, naming runs a fixed sequence of steps and the first one that sets a name ends it, …
path       knowledge/document/autoname.md
source     -
verified   -
```

Narrow a wide match with a second word rather than reading the index whole:

```
$ grep -i hook INDEX.tsv | grep -i order
```

`source` and `verified` are `-` because a leaf carries no line number. The files it read are listed
in its own `## paths` section, and the release is declared once in `SOURCES.json`.

## Why

Ask a model how `autoname` behaves and you get a fluent answer built from what it read while
training. It is often right. When it is wrong it is wrong quietly: a renamed function, a hook that
now fires in a different order, a flag removed two releases ago. Nothing in the answer tells you
which one you got.

This store answers with a pointer instead of a paragraph, and the pointer opens.

## Install

**Claude Code**

```
git clone https://github.com/iabodysa/frappe-skill ~/.claude/skills/frappe
```

The skill loads by name from there. Nothing else is installed and nothing is compiled.

**Anywhere else**

Clone it and read it. The index is a tab-separated file and the facts are markdown, so any agent,
editor or shell can use it.

```
git clone https://github.com/iabodysa/frappe-skill
grep -i "name empty" frappe-skill/INDEX.tsv
```

## The eight houses

A house holds ten leaves or more; one that falls below ten merges into the neighbour whose subject
already contains it.

| house | facts | answers |
|---|---|---|
| `knowledge/bench/` | 30 | the commands, what install and migrate do to a fixture, a seed, a patch or a custom JSON, how a string is translated, and the test case, the runner, the rollback and the test records |
| `knowledge/document/` | 29 | what save, submit and cancel run in order, what rename, delete and `db_set` skip, how a document gets its name, and where a workflow state and transition are checked |
| `knowledge/desk/` | 29 | the Desk surface — workspace, page, list indicator, formatters, what is metadata — and who may run a report, what it may read, and what print adds |
| `knowledge/job/` | 21 | when a background job runs, which queue it lands in, which utility frappe already ships in place of a stdlib import, and what actually sends against what only queues |
| `knowledge/ui/` | 20 | frappe-ui — which call refetches, which store is shared, what a reload empties |
| `knowledge/api/` | 10 | calling out and being called — whitelisted methods, REST routes, webhooks, credentials |
| `knowledge/permission/` | 10 | who may read or change a record — docperm, role, permlevel, User Permission, the query hooks, CSRF |
| `knowledge/web/` | 10 | the public site — routes, status codes, Jinja, the Web Form and its guards |

## What one entry is

| store | count | one entry is |
|---|---|---|
| the eight houses | 159 leaves | ONE subject: the files it was read from, the rules it forces, the tables it settles |
| `references/` chapters | 27 | ONE verdict comparing routes a reader could take |
| `tasks/` pages | 9 | the decisions one job forces, in order, each naming the leaf that settles it |
| `INDEX.tsv` | 195 rows | every leaf, chapter and task page on one grep-able line |
| `RELATIONS.tsv` | 251 routes | the hops from a task page, through a chapter, to the leaf that settles it |

Start at a task page when you know the job but not the vocabulary — shipping a customisation,
deciding who may read a record, writing tests. Start at the index when you already have the words.

One file declares what the store was read against — the version, the tag and the repository of each
product:

```
SOURCES.json
```

Build the link to any cited file from it:

```
<repository>/blob/<tag>/<file>
```

## How a fact stays true

Nothing enters on a claim. The gates:

```
python3 tools/symbol_check.py
python3 tools/build_index.py index --check
python3 tools/build_index.py relations --check
python3 -m unittest discover -s tests -t tests
```

`symbol_check.py` reads every leaf's `## paths` section, opens each file it names inside the
installed product, and checks that each symbol named beside it still appears in that file. It
reports `FILE GONE` when the path opens nothing, `SYMBOL GONE` when the file no longer carries the
name, and `POINTER DEAD` when a chapter or task page links a store page that does not exist. It
prints the population it read — leaves, path lines, pointers — so a zero cannot be mistaken for a
clean run, and three positive controls run first, so a broken checker cannot report a clean tree.

That is the whole of it, and it is less than it sounds: the check proves a symbol still exists in
the file a leaf cites. It says nothing about whether the sentence written about that symbol is
true. Only a reader opening the source settles that.

`build_index.py` regenerates `INDEX.tsv` and `RELATIONS.tsv` from the tree; `--check` exits 1
without writing when either file disagrees with it. Neither is ever edited by hand.

These commands are the maintainer's. A reader never runs them.

## Honest limits

It does not cover the framework. 159 facts against a codebase that size is a thin, deliberate slice:
the places where behaviour contradicts the name. There is no leaf for what the code obviously does.

It cannot tell you a fact it does not hold. On a miss you get nothing, and nothing is the honest
answer.

**What it is worth, measured.** Twelve questions about Frappe behaviour were put to two agents: one
reading this store, one reading nothing but its own training. The store answered 10 correctly, got 1
wrong and refused 1. The model with no store answered 9 correctly, got 2 wrong and refused 1. That
is a gap of one answer. Both arms got the same question wrong — both said
`frappe.get_all()` respects permissions when the caller asks it to, and `frappe/__init__.py` sets
`ignore_permissions` to true unconditionally, so the caller's argument is discarded — and both
refused the same one. The store's whole measured advantage
on that set was one wrong answer avoided. It is not a large claim and it is not made larger here.

On a question whose answer sits in one small file you can already name, `grep` over the source beats
this store and you should use it.

## License

Copyright (c) 2026 iabodysa.
