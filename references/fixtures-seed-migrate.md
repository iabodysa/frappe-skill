# Who owns a row once the operator has edited it

Five ways put a row on a site and they differ on ONE question: who owns the row after an operator
has edited it. A fixture takes it back on every migrate; module JSON gives it up the moment the site
touches the record; a patch writes once and is stamped forever; an `after_install` or
`after_migrate` hook writes once per site and never returns; custom JSON merges by key. Pick by
ownership, never by convenience.

| How the row is written | When it writes | Who wins after an operator edit |
|---|---|---|
| fixture | every migrate, with force, committing per file | the app — the edit is overwritten |
| module JSON (`IMPORTABLE_DOCTYPES` folders) | install, and every migrate until the site touches the record | the operator — permanently |
| custom JSON | every migrate, and only where `sync_on_migrate` is truthy | per key — four keys, four semantics |
| Custom DocPerm rows | whenever written | the last writer; one row replaces the whole shipped block |
| an `after_install` or `after_migrate` hook | once per the hook that carries it | the operator — nothing returns |
| patch | once, then stamped in Patch Log | the operator — a stamped patch never runs again |

An install-only hook never reaches an existing site and a migrate-only hook never reaches a new one,
so a record that must exist on both is declared in both places or in neither.

## Settled by

| what it settles | leaf |
|---|---|
| the forced re-import, the per-file commit, and `in_import` | `knowledge/bench/fixtures.md` |
| the nineteen importable folders and the permanent skip | `knowledge/bench/standard-json.md` |
| the four keys, `sync_on_migrate`, and the links-only export | `knowledge/bench/custom-json.md` |
| one row replacing the shipped permissions block | `knowledge/bench/custom-docperm.md` |
| when an install hook is the only correct way, and the hooks that exist | `knowledge/bench/seeds.md` |
| the transaction around the body and the stamp on any normal return | `knowledge/bench/patches.md` |
| the phase each of these runs in | `knowledge/bench/migrate.md` |
| the app recorded installed before a single hook has run | `knowledge/bench/install-app.md` |
| the per-record savepoint, and the record lost to the list's own order | `knowledge/document/make-records.md` |
