# Delivering to a site that is already running

A `bench migrate` is THREE transactions, not one — the before-hooks, then patches and schema, then
everything else — each committed separately, so a failure late in the run leaves the earlier phases
standing on the site. That clock never reaches a site being installed. On the bench side, every
`bench setup` generator rewrites `common_site_config.json` as a side effect, and three of its writers
default their target to the current working directory rather than the bench they were handed.

| What you run against a live site | What it commits | What it overwrites without asking |
|---|---|---|
| `bench migrate`, phase 1 | the before-migrate hooks | nothing on disk |
| `bench migrate`, phase 2 | `patches.txt`, then the schema | a column, an index, a Patch Log row |
| `bench migrate`, phase 3 | jobs, fixtures, dashboards, customisations, after-migrate hooks | every fixture row, by force |
| `bench setup nginx`, `supervisor`, `config` | nothing in a site database | `common_site_config.json`, and a file in the current directory |
| `bench --site all <command>` | depends on the command | only `migrate` loops; a one-site command takes the first entry and stops |
| `bench console` | nothing unless you commit by hand | nothing — a rollback is registered at exit |

A record already touched on the site is a separate question from the run order: module JSON is kept
out forever once the site has written the record, while a fixture returns on every migrate.

The bench-side defect is one shape repeated, and reading it as three separate bugs is what makes it
survive. A writer takes a bench path, uses it for the READ, and drops it on the WRITE, where the
default is the process's current directory. So `--bench-path` looks applied — the values written are
the named bench's — and they land in whichever bench the shell is standing in. On a host carrying one
bench nothing is visible, on a host carrying two the damage is silent and crosses benches, and no
single writer looks wrong on its own. Judge the class rather than the call: the only protection that
holds for all of them is the working directory, so run anything that reaches a bench config writer
from inside the target bench and treat a correct path argument as decoration.

## Settled by

| what it settles | leaf |
|---|---|
| the three phases, their order, and the sync order inside the last | `knowledge/bench/migrate.md` |
| the generators that rewrite the common config and mistake their target | `knowledge/bench/setup.md` |
| the merge order that decides what a site actually reads | `knowledge/bench/config.md` |
| `--site all`, and the console rollback at exit | `knowledge/bench/site-commands.md` |
| the forced re-import and the per-file commit | `knowledge/bench/fixtures.md` |
| the skip that keeps a touched record's file out forever | `knowledge/bench/standard-json.md` |
| `sync_on_migrate`, and the four write semantics | `knowledge/bench/custom-json.md` |
| what a build writes into `sites/assets`, and the prebuilt download it takes instead | `knowledge/bench/build.md` |

A transport's exit status is not a delivery receipt. An archive built from a partial checkout can omit files, extract the rest, and return clean, which leaves the site running new code under an old shell with nothing to show for it. Compare a digest of every intended file against the local copy before calling a delivery complete, and treat the exit status as evidence that the transport ran and as evidence of nothing else.
