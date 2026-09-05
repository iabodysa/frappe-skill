---
name: frappe
description: >-
  Use before stating any Frappe, ERPNext, HRMS or frappe-ui behaviour, and after
  learning one. Three verbs: read a verified fact, record a new one, fold a lesson.
  Covers the save and submit sequence, permissions and permlevel, bench install and
  migrate, naming and autoname, scheduler and background jobs, translation, the Desk
  surface, the public site, and the frappe-ui data layer — createResource,
  createListResource, createDocumentResource, useDoc, useList, useCall, useNewDoc, the
  doc store and the Vue directives. Never answer from training data or a web tutorial;
  the installed source is the only authority, and this skill is where its ADDRESS lives — which
  checkout on this machine is the installed one and what version it is. Load it before searching for
  framework source, not after. Also carries the pipes that run against a
  Frappe app — translation scan and gate, version bump, changelog, record stamp,
  DocType schema read and seed dry-run.
---

# frappe

## Read

MUST open this lookup before any Frappe, ERPNext, HRMS or frappe-ui work, not only before answering a
question already asked, and MUST find a fact by one lookup from the skill root, for the words you
would type:

```
python3 tools/ask.py name empty
```

It returns the path of each matching leaf and the trigger phrase that matched, never the whole row.
Exit `0` is a hit, exit `1` is a miss, and a miss prints how to narrow instead of the index.
MUST use it rather than a bare `grep INDEX.tsv`, because a bare grep prints rows thousands of
characters wide and leaves no record; this one appends the query, the hit count and the bytes
returned to `state/frappe-ask.log`, so the miss RATE is measurable and any cap on this lookup can
be argued from a number.
MUST open the file in the `path` column of the row that matched, and read only that file.
MUST narrow a wide match with a second word — `python3 tools/ask.py hook order`.
NEVER grep `knowledge/` or `references/` for a fact; a file is named for the subject it settles, and
only the `triggers` column carries the words a reader arrives with.
NEVER read `INDEX.tsv` whole; it holds one row per leaf, chapter and task page, and reading it costs
more than every fact a narrowed grep would find.
NEVER open a second leaf because the first one was thin; a leaf holds ONE subject, so the fact still
missing is another set of trigger words and not the next file in the folder.
MUST read the `source` and `verified` columns as `-` on a leaf and mean it; the release is declared
once in `SOURCES.json` and the source files are listed in the leaf's own `## paths` section.
MUST open those source files at the release `SOURCES.json` names before stating any framework
behaviour.
NEVER answer from training data, from a web tutorial or from a remembered version.
MUST answer only from the installed source or a leaf, a chapter or a task page this tree holds.

## The eight houses

MUST expect one subject per leaf, under the house that owns the subject.
MUST keep a house at ten leaves or more; a house that falls below ten merges into the neighbour whose
subject already contains it, because a house too small to be worth opening is a name and not a home.

| house | answers |
|---|---|
| `knowledge/document/` | what save, submit and cancel run in order, what each hook may still change, how a document gets its name — autoname, naming series — and where a workflow state, transition and Workflow Action are checked |
| `knowledge/desk/` | the Desk surface — workspace, page, list indicator, formatters, what is metadata — and who may run a report, what it may read, and what print adds |
| `knowledge/bench/` | the commands, what install and migrate do to a fixture, a seed, a patch or a custom JSON, how a string is translated and where translation is skipped, and the test case, the runner, the rollback and the test records |
| `knowledge/job/` | when a background job runs, which queue it lands in, what stops it, and what actually sends against what only queues |
| `knowledge/ui/` | frappe-ui — which call refetches, which store is shared, what a reload empties |
| `knowledge/permission/` | who may read or change a record — docperm, role, permlevel, User Permission, the query hooks |
| `knowledge/web/` | the public site — routes, status codes, Jinja, the Web Form and its guards |
| `knowledge/api/` | calling out and being called — whitelisted methods, REST routes, webhooks, credentials |

MUST read a CHAPTER under `references/` as ONE verdict comparing two routes, never as a home for a
fact, and MUST reach it by the same grep.
MUST read a TASK PAGE under `tasks/` as the decisions one job forces, in the order the reader meets
them, and MUST start there when the job is known but the vocabulary is not.

## Record

MUST write a leaf the moment a behaviour is settled from source.
NEVER hold a settled fact for task end; the session closes with it unwritten and the next reader pays
for the same read.
MUST build the file to the shape `TEMPLATE.md` declares — frontmatter `name`, `description`,
`product`, then `## paths`, `## rules`, `## how`, and `## values` only where the subject has a table.
NEVER write a line number into a leaf; code moves and the line dies while the file and the symbol
live, so `## paths` names the file and the symbols in it.
MUST merge a correction into the leaf that already holds the subject.
NEVER open a second home for a fact a leaf, a chapter or this file already carries; a correction then
lands in one home and not the other.
MUST record the non-obvious consequence — the behaviour a name or a docstring is wrong about.
NEVER record what the code obviously does.
MUST regenerate both generated files after adding or moving anything:

```
python3 tools/build_index.py index
python3 tools/build_index.py relations
```

NEVER edit `INDEX.tsv` or `RELATIONS.tsv` by hand; both are built from the tree, the suite fails when
the shipped file disagrees with it, and `--check` exits 1 without writing.
MUST give the filename and the `description` the words a future agent will actually type; the index
builds `triggers` from them.
MUST write a quoted block, where one is needed at all, as a fence whose first line is
`# <path from the product root>:<first>-<last>` and whose remaining lines are byte-exact against that
range.
NEVER paraphrase a source line inside such a block and NEVER widen the range so a quote fits; the
gate compares byte for byte and reads a paraphrase as a fabrication.
NEVER add a path to the gate's ignore list and NEVER shorten a citation to stop it complaining; the
gate names the range that moved and the fix is to re-read the source at its new lines.

## Fold

MUST fold a lesson into the owning skill, then delete the leaf in the same commit.
NEVER delete the leaf in a later commit than the fold; the tree between the two states the fact twice
or not at all.
MUST name the folded lessons in that commit subject.

## Verify

MUST read the installed tree, and MUST get its path, its product and its version from one run of
`python3 tools/bench_source.py`, which prints `bench`, `product`, `version` and `source_root`.
NEVER search the disk for the installed tree; an order to read installed source is unfinished until
it names the command that resolves it.
NEVER write a bench path into this file, a leaf or a tool; a path is right on one machine and wrong on
every other.
MUST read frappe-ui at `apps/<app>/<ui-root>/node_modules/frappe-ui`.
NEVER cite the first `frappe-ui` a search finds; two apps on one bench ship different versions, so name
the app whose `node_modules` the quote came out of.
MUST confirm the installed version before citing it — read `apps/<app>/<app>/__init__.py` in the bench.
NEVER cite a version remembered from another site or read from a changelog.
NEVER offer a passing test as proof of framework behaviour; the test proves the app, so the proof is
the source.

## Run — `benchx`

MUST treat `benchx` as an AUTHORITATIVE surface this file already documents: call it, and NEVER open
`tools/benchx.py` to learn what it does. The only reason to read that source is a fix TO benchx
itself — a missing signature, a misclassified verb, a wrong refusal.
MUST answer a question about a verb with `benchx :explain <verb>`, a question about the command line
with `benchx :argv <bench args>`, and a question about the target with `benchx :where`.
NEVER run a verb to find out what it does; `:explain` and `:argv` answer without touching the target.
MUST answer `no .benchx.toml found` with `benchx :setup`; the tool is not broken and its source
holds no target, because the target lives in the config the message names.
NEVER read `tools/benchx.py` looking for the bench path; no target is written in it.
MUST run every bench command through `benchx`, which supplies the bench path, the `--site` flag and the
`ssh` line at a call site; the target is declared once in `.benchx.toml` and `benchx` resolves it.
NEVER type a raw `bench` command, and NEVER paste a bench path, a `--site` flag or an `ssh` line at a
call site; each one is a second declaration of a target that is already declared.
MUST run `benchx :setup` then `benchx :check` before the first command on an unfamiliar machine; a
refusal here names the missing key, where raw bench only says it is not a bench directory.
MUST read the verdict line and stop there when it says OK; the excerpt under a FAIL is the lines that
caused it, and the whole transcript is at the log path on the last line.
NEVER open the log path on an OK, and NEVER read a transcript whole on a FAIL; the excerpt under the
verdict is the cause.
MUST treat `SUSPECT` as a failure. It means bench exited zero and its own output says the work did not
happen — a test suite that reported failures, a patch that was skipped, an app that was already there.
MUST read the suite's own summary line, because outside CI `bench run-tests` returns zero on a failing suite.
NEVER read a zero exit as a pass; the exit code is not a verdict, and `SUSPECT` is what says so.
MUST widen `[output] max_excerpt_lines` when an excerpt truncates a cause, and MUST read the widened excerpt.
NEVER name a cause from a truncated excerpt.
MUST name exactly one site for `restore`, `reinstall`, `console`, `run-tests` and
`set-maintenance-mode`; each accepts it and then acts on the FIRST site alone, silently, which is why
benchx refuses the pair.
NEVER pass `--site all` to one of those five; it is destructive against every site at once.
MUST treat `no known signature matched` as a real answer — the classifier missed, the failure is still
there — and MUST add the signature to `tools/benchx.py` once its cause is known.
NEVER read `no known signature matched` as no failure.
MUST give `benchx` the dev Administrator password once — `$BENCHX_ADMIN_PASSWORD`, or
`safety.dev_admin_password` in an ignored `.benchx.toml` — and MUST leave the call site without one;
benchx ships no default and REFUSES `new-site`, `restore` and `reinstall` on `dev` until it holds one,
because an omitted password is not "no password" — frappe falls back to a value the operator never
chose, and a test site nobody can log into has to be rebuilt.
MUST prefer the environment variable over the file wherever the tree is published or shared; benchx
pins the value at the ARGV of one invocation and redacts it out of the transcript on the way to disk.
MUST supply the `staging` and `production` password yourself; benchx refuses to.
NEVER declare `safety.dev_admin_password` outside `dev`; benchx never supplies a password there, so the
key promises one it will not give and is reported as a problem rather than ignored.
NEVER flip `safety.allow_destructive` to get past one refusal; it is machine-wide, not per-command, so
it stays on for every command after it.

| call | does |
|---|---|
| `benchx :setup --kind ssh --env production --host … --user … --key … --site …` | declare the target from flags |
| `benchx :setup --env dev --admin-password …` | declare the dev Administrator password; without one benchx refuses to create a site |
| `benchx :where` | the resolved target, its environment, and every verb blocked there |
| `benchx :check` | prove the config resolves, then run `bench version` |
| `benchx :explain <verb>` | what benchx would do with it, without running it |
| `benchx :argv <bench args>` | the exact command line it would run, printed and not run |
| `benchx :help` | the seven own verbs; everything without a leading colon is bench's, verbatim |
| `benchx <bench args>` | run it at the target, answer with a verdict |
| `benchx :lane new [--name <id>]` | create this agent's own site, install the target's declared apps, pin it |
| `benchx :lane drop [--name <id>]` | drop the agent's own lane site; refuses every other site by name |
| `benchx :lane ls` | list every `lane-*.localhost` site on the resolved bench, with its size and its age |

MUST pass `--confirm <site>` to `migrate` on `staging` and `production`; it runs patches and schema
changes against a live database and takes NO backup of its own.
NEVER start that `migrate` without a backup taken outside benchx.
MUST declare `target.env`; it, not a boolean, decides what may run. `dev` runs anything the switch
allows; `staging` and `production` refuse a destructive verb until the site name is typed at the call
site as `--confirm <site>`, because a confirmation given by reflex has confirmed nothing.
MUST read the `blocked` line of `benchx :where` before promising an operator that a command is safe.
MUST treat a verb absent from that line as destructive; benchx blocks every verb it does not know.
NEVER read a verb's absence from `blocked` as permission to run it.
MUST audit a remote target with `benchx :argv` before trusting it, rather than by reading the code and
copying the command line into your head; the ssh branch builds a SHELL STRING where the local branch
builds an argv, so it is the one composition a local success cannot vouch for.
MUST reach benchx's own verbs through a LEADING COLON; a bare word reaches bench itself. `bench init`, `bench setup`
and `bench doctor` are real commands, and reserving their names made them unreachable.
NEVER type a benchx verb without its colon; `benchx setup` reaches `bench setup` and runs it.
MUST keep `env` at what the machine actually is.
NEVER lower `target.env` to reach a blocked verb; the environment is a fact, not a lever.

## Lane — one agent, one site

MUST read a LANE as four things bound together: its own git worktree, its own `.benchx.toml`
inside that worktree, its own site named `lane-<id>.localhost`, and its own log directory.
NEVER read an agent as holding a lane when it shares any one of those four with another agent.
MUST create a lane with `benchx :lane new [--name <id>]`; it derives `<id>` from the basename of
the current git worktree when `--name` is omitted, installs the apps the resolved target already
declares, and writes `.benchx.toml` in the CURRENT directory so every later `benchx` call from
that worktree targets the lane with no flag.
MUST read a REFUSAL from `:lane new` naming a site that already exists as final; a lane is never
reused, and re-running it is not a retry, it is a second agent about to share the first one's site.
MUST drop a lane with `benchx :lane drop [--name <id>]`; it refuses, non-zero exit, naming the
site, unless the site matches `lane-*.localhost` — every other site, `apex.localhost` and
`ci.localhost` included, is unreachable by this verb.
NEVER pass `:lane drop` a `--name` expecting it to reach a non-lane site; the verb derives
`lane-<id>.localhost` from `--name` exactly as `:lane new` does and refuses anything else.
MUST list lanes with `benchx :lane ls`; it prints every `lane-*.localhost` site on the resolved
bench with its size and its age, so an abandoned lane is visible.
MUST forbid `apex.localhost` to every agent; it is a hand-maintained demo site, and changes on it
are tried by hand rather than through automation.
MUST forbid two agents sharing `ci.localhost` at any one time; the suite writes test records there,
and a second runner rebuilds the records the first one is reading.
MUST name the agent's lane in a subagent brief the same way the brief names its write scope.
MUST require the agent to drop its own lane with `benchx :lane drop` before it returns, and MUST
require it to report the drop command and its exit code as evidence in the same reply.
NEVER accept a subagent's report of a finished task while its lane is still listed by
`benchx :lane ls`.

## Pipe — `frappe-pipes`

MUST run every one of these through `tools/frappe-pipes <verb>`, the only home they have.
MUST run it from the project root, or pass `--root`; it resolves the app from `.ctl.toml`, then
`sites/apps.txt`, then a `*/modules.txt`, and refuses when none of the three names one.
NEVER answer a refusal by removing the input it named; `changelog` rejects a headline the operator
cannot check, `bump` rejects a version with no `--kind`, and `seed` rejects an unknown key by name, and
each of the three names the field to fix.

| call | does |
|---|---|
| `frappe-pipes translates --json` | scan for translatable strings, write the todo report, change no CSV |
| `frappe-pipes translates --apply --apply-file rows.jsonl` | write supplied translations into the CSV |
| `frappe-pipes check-translations --json` | exit 1 while any string is missing or stale |
| `frappe-pipes bump X.Y.Z --kind batched` | rewrite the version in `__init__.py`, `pyproject.toml` and `setup.py` |
| `frappe-pipes bump-smart --json` | read the diff and propose the semver step, writing nothing |
| `frappe-pipes changelog X.Y.Z --summary … --bullet …` | write the native changelog note and its index |
| `frappe-pipes stamp --changed --dry-run` | list the record JSON git reports as edited |
| `frappe-pipes schema <DocType>` | the shipped shape — mandatory, Select, Link, child tables; no bench |
| `frappe-pipes model-audit --root <repo>` | the model's own defects read from the shipped DocType JSON — dead fields, invalid Link targets, required-Link cycles; writes nothing into the repo it reads |
| `frappe-pipes seed <file>.toml --dry-run --no-site` | resolve every Link and Select, write nothing |

MUST prove a change to any tool with `python3 -m unittest discover -s tests -t tests`.
NEVER edit a test, a baseline or a gate to make that suite green.

## Gates

MUST define at least one `unittest.TestCase` subclass in a new test file; `python3 -m unittest
discover` silently skips a file written as plain `test_*` functions and reports it inside "Ran 0
tests" with no error, while `pytest` still collects and runs that same file.
MUST NOT treat `python3 -m unittest discover -s tests -t tests` alone as proof of a tool change; MUST
also run `grep -L "TestCase" tests/*.py` and require it to print nothing, because that is the check
that the changed test file actually defines a `TestCase` subclass and was not silently skipped.

| command | proves |
|---|---|
| `python3 tools/build_index.py index --check` | `INDEX.tsv` agrees with the tree, writing nothing |
| `python3 tools/build_index.py relations --check` | `RELATIONS.tsv` agrees with the tree, writing nothing |
| `python3 -m unittest discover -s tests -t tests` | the tools and the shape of the tree |
| `grep -L "TestCase" tests/*.py` | every test file defines a `TestCase`, printing nothing on pass |

## Instruction pages

- `docs/benchx.md` — raw bench against benchx, worked judgements; the live surface is `benchx :help`
- `docs/what-it-costs.md` — the measured comparison against grepping the source directly
