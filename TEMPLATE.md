# The shape of a file in this store

## A leaf — one subject

The filename names the SUBJECT. The description carries the fact. The index carries the words a
reader types.

```markdown
---
name: naming
description: The first route that produces a name ends the sequence, and every later route is skipped without a warning.
product: frappe
---

# Naming

## paths

frappe/model/naming.py — set_new_name, NamingSeries, make_autoname
frappe/model/document.py — _set_defaults

## rules

MUST expect a naming_series to be skipped when a Document Naming Rule already produced a name.
MUST declare one route per DocType.
NEVER read the absence of an error as proof that the route you declared is the route that ran.

## values

routes: field, naming_series, hash, prompt, format, autoincrement
wins: the first route that produces a name
announces: nothing — no error, no warning, no log
counter: tabSeries, one row per prefix, shared by every writer

## how

Six routes run in a fixed order and each runs only while the name is still empty, so the first route
that produces a name ends the sequence and the rest are skipped in silence. Declaring two routes
does not combine them; it disables the second.

Choose by what the name must survive. A name a person reads aloud needs a readable series. A name
only the database joins on is better as a hash, because a series is one shared counter and a shared
counter is contended by everyone writing at the same moment.
```

`paths`, `rules` and `how` are required. `values` is written only where the subject has a table.
The section names and their order are enforced by the suite, not repeated in the frontmatter.

## A chapter — one verdict

The verdict stands in the first three lines. Then the competing routes, one line each for what a
route carries and what it drops. Then pointers to the leaves. It holds no fact of its own and no
relations table, and it stays under twelve thousand bytes.

## A task page — one job

The title is the job. Numbered decisions in the order the reader meets them, three lines each: the
question, the answer, the leaf that settles it. It holds no fact.

## The generated files

`INDEX.tsv` and `RELATIONS.tsv` are built from the tree and never written by hand. A row in
`RELATIONS.tsv` is a route: the hops in order, then the file, then the leaf, and the depth is open.

`SOURCES.json` is written by hand, because it is a decision rather than a result. It names the
version, the tag and the repository of every product, so no file repeats a version and no citation
carries a line number.

## What no file carries

A second subject — it becomes its own file.
A line number — code moves and the line dies while the file and the symbol live.
A date of audit, or any sentence saying where a fact came from or whether it was checked.
A word the framework does not use, unless the framework has no word and the chapter says so once.
An instruction to go and read the source as the answer.
A sentence that would not change what the reader does.
A quoted block that is not byte-exact from the file it names.
