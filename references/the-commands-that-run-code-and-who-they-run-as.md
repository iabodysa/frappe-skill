# The commands that run code, and who they run as

All five run as Administrator, so every permission check inside them answers yes — and that is the
only thing they share. Which site they bind, when the work is committed and what an unhandled
exception leaves behind differ in every row, so a script proved safe under one is not safe under
another. Administrator is not `ignore_permissions`: it is exempted before the check is reached.

| Command | Site it binds | When it commits | What an unhandled exception leaves |
|---|---|---|---|
| `bench execute` | every site `--site` resolved to | once, after the call returns | no later site runs, and the method may already have run twice |
| `bench console` | the first site only | never on its own | a rollback at exit, so the session may never have landed |
| `bench run-tests` | the first site only | test records as they are made, then once at the end | the site with its scheduler still switched off |
| `bench migrate` | every site `--site` resolved to | three times, one per phase | the failing phase rolled back and the phases before it committed |
| the scheduler entry | none — it loops over the sites itself | once per job | a Failed log row, the run stamp standing, the next tick unaffected |

A command written for one site takes the first entry of an expanded `--site all` and touches no
other; `migrate` is the one that loops.

## Settled by

| what it settles | leaf |
|---|---|
| the first-entry rule and the console rollback at exit | `knowledge/bench/site-commands.md` |
| the three phases and their separate commits | `knowledge/bench/migrate.md` |
| what a rollback discards and which queues it empties | `knowledge/document/transaction.md` |
| the one call that reads the pause settings | `knowledge/job/scheduler.md` |
| the commit on return and the rollback on exception | `knowledge/job/execution.md` |
| why Administrator is not the same as `ignore_permissions` | `knowledge/permission/accessor.md` |
| the exit code a failing suite reports | `knowledge/bench/runner.md` |
