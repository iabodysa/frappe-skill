# Writing a test the framework will actually run

The runner finds `test_<slug>.py` only beside the DocType, so a test kept anywhere else is invisible
to that path and its fixture has nothing to serve. Test records are built once per site and the
record of that build is a file on the site, so an edited `test_records.json` is never read again.
And the rollback is queued for the CLASS, not the test, so every row one test writes is still there
for the tests that follow it.

| What you were about to rely on | What the framework does | What to type instead |
|---|---|---|
| the test file living where you put it | only `test_<slug>.py` beside the DocType is discovered | keep the file beside its DocType |
| a fresh `test_records.json` on every run | it is imported once per site and logged | drop the site's test log, or name the records in the test |
| a rollback between tests | `_rollback_db` is queued with `addClassCleanup` | write each test to tolerate the previous one's rows |
| `set_user` restoring Administrator | it restores the user the block was entered with | enter the block as the user you want back |
| `change_settings` as a method on the case | it is module-level in `frappe.tests.utils` | import it from there, with `patch_hooks` and `timeout` |
| a non-zero exit from a red suite | `sys.exit` is called only under `CI` | set `CI` in the environment that grades the run |
| `before_tests` firing for every app | it fires for the app under test only | put shared setup in that app |
| asserting on a value you wrote with `db_set` | `before_change` and `on_change` still ran | assert through the same entry point the product uses |

## Settled by

| what it settles | leaf |
|---|---|
| the `CI` branch and the green exit on a red suite | `knowledge/bench/runner.md` |
| the once-per-site build and the site's test log | `knowledge/bench/records.md` |
| the class-level cleanup and the rows that survive a test | `knowledge/bench/rollback.md` |
| what `set_user` restores, and where `change_settings` lives | `knowledge/bench/case.md` |
| the handlers a `db_set` still reaches | `knowledge/document/db-set.md` |
| the entry point a test should cross | `knowledge/document/save.md` |
| what a rollback discards | `knowledge/document/transaction.md` |
| the checked call a permission test has to use | `knowledge/permission/accessor.md` |
