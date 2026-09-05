# Framework Knowledge

Store source-backed Frappe, ERPNext, HRMS, and frappe-ui facts here. Keep methods in the
owning skill and project decisions in project memory.

## Authority

1. Installed framework source is final authority.
2. A verified leaf is a source-discovery shortcut for the release `SOURCES.json` declares.
3. Project memory may point here and record only project-specific consequences.

MUST re-open the cited source before relying on a leaf when the installed version differs from the
one `SOURCES.json` names.

## Storage

MUST keep one narrow framework fact per Markdown leaf, under the house that owns its subject.
MUST build the leaf to the shape `TEMPLATE.md` declares.
MUST name the source files and the symbols read from them in the leaf's own `## paths` section.
NEVER write a line number into a leaf; code moves and the line dies while the file and the symbol live.
MUST merge a correction into the leaf that already holds the fact.
NEVER open a second home for a fact a leaf, a chapter or `SKILL.md` already carries.
MUST keep this store to framework facts; testing, reuse, task and guard policy live in the skill references.

## Retrieval

MUST find a fact by one grep over `INDEX.tsv` at the skill root, for the words a reader would type.
MUST open only the file in the `path` column of the row that matched.
NEVER grep `knowledge/` for a fact; only the `triggers` column carries the words a reader arrives with.
NEVER read `INDEX.tsv` whole.
MUST confirm the installed product version before stating a behaviour from a leaf.

## Verification

MUST prove a leaf's citations still open by running the symbol check from the skill root:

```bash
python3 tools/symbol_check.py
```

It reads every leaf's `## paths` section, opens each file it names inside the installed product, and
checks that each symbol named beside it still appears in that file. It reports `FILE GONE` when the
path opens nothing, `SYMBOL GONE` when the file no longer carries the name, and `POINTER DEAD` when a
chapter or task page links a store page that does not exist. It prints the population it read and
runs three positive controls first, so a zero cannot be read as a clean tree.

MUST regenerate both generated files after adding, moving or deleting a leaf:

```bash
python3 tools/build_index.py index
python3 tools/build_index.py relations
```

NEVER edit `INDEX.tsv` or `RELATIONS.tsv` by hand; both are built from the tree, and `--check` exits 1
without writing when either disagrees with it.

MUST get the installed tree's path, product and version from `python3 tools/bench_source.py`.
NEVER write a bench path into this file, a leaf or a tool.

## Promotion

MUST write a leaf the moment a behaviour is settled from source, and MUST open the source to settle it.
NEVER promote a discovery on a claim, a training-data recollection or a web tutorial.
NEVER hold a settled fact for task end; the session closes with it unwritten and the next reader pays
for the same read.
No command promotes a lesson; a reader who read the source writes the leaf.
