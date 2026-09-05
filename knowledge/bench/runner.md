---
name: runner
description: run_tests calls sys.exit only inside `if os.environ.get("CI")`, so a failing suite ends the process at 0 and anything reading the exit code records a red run as green.
triggers: ["main", "run_all_tests", "run_tests_for_doctype", "run_tests_for_module", "_run_unittest", "_add_test", "get_modules", "ParallelTestRunner", "ParallelTestRunner.before_test_setup", "get_all_tests", "run_tests", "run_parallel_tests", "app_group", "before_tests", "get_hooks", "_load_app_hooks", "sync_for", "get_doc_files", "run_all", "get_server_messages", "application", "Cannot make dict for single fieldname", "Invalid request arguments", "bench run-tests exit code", "run_tests sys.exit CI", "the tests failed on screen but the pipeline says everything passed", "why does a failing test run still report success", "my automation never catches a broken test", "i added a second test file next to the form and it never runs", "it says the module cannot be found when i target one form", "how do i make sure the whole app is actually being tested", "the setup routine i wrote never runs before the tests", "the tests create a company in dollars and the wrong country", "one test errors about a missing warehouse type on a fresh site", "the parallel run skips the preparation step my tests need", "i removed test files before deploying and things broke", "how do i get a real failure signal out of the test command"]
product: frappe
---

# Runner

## paths

frappe/test_runner.py — main, run_all_tests, run_tests_for_doctype, run_tests_for_module, _run_unittest, _add_test, get_modules
frappe/parallel_test_runner.py — ParallelTestRunner, ParallelTestRunner.before_test_setup, get_all_tests
frappe/commands/utils.py — run_tests, run_parallel_tests
frappe/utils/bench_helper.py — app_group
frappe/hooks.py — before_tests
frappe/__init__.py — get_hooks, _load_app_hooks
frappe/model/sync.py — sync_for, get_doc_files
frappe/modules/patch_handler.py — run_all
frappe/translate.py — get_server_messages
frappe/app.py — application

## rules

MUST grade a run on its output — `OK` against `FAILED` — or launch it with `CI` set in the environment, because `run_tests` reaches `sys.exit` only when `CI` is set and otherwise returns from the callback at 0.
NEVER read exit 0 from `bench run-tests` as a passing suite.
MUST run the whole app with `--app` when the result is load-bearing; `run_all_tests` walks the app path and takes every file that starts with `test_` and ends with `.py`, skipping `test_runner.py` and the folders `locals`, `.git`, `public` and `__pycache__`.
NEVER treat a green `--doctype` run as evidence about a DocType's tests. `run_tests_for_doctype` builds one module name with `get_module_name(doctype, module, "test_")` and imports exactly it; there is no discovery, so a second test file beside the DocType is never reached.
MUST read `ModuleNotFoundError` from `--doctype` as a name that does not match `test_<scrubbed doctype>.py`, never as a missing test, and MUST fix it by moving the content into that filename.
MUST declare `before_tests` in the app's own `hooks.py`. `main` calls `frappe.get_hooks("before_tests", app_name=app)` and `get_hooks` loads only that app's hooks when `app_name` is given, so naming a custom app suppresses `frappe.utils.install.before_tests` and `erpnext.setup.utils.before_tests`.
MUST copy the shape of `hrms.tests.test_utils.before_tests` rather than the values of `erpnext.setup.utils.before_tests`, whose company is USD and United States.
MUST read `--app` as the `before_tests` scope; `--doctype`, `--module` and `--module-def` are what select the tests.
MUST wire `before_tests` for both commands: `run-tests` reaches it through `main` and `run-parallel-tests` through `ParallelTestRunner.before_test_setup`.
MUST run a suite once on a site nobody has completed the setup wizard on before citing it as coverage; a Company insert on a bare site raises `LinkValidationError: Could not find Warehouse Type: Transit` because `install_fixtures` creates that record and `bench install-app erpnext` does not.
NEVER strip `test_*.py` or `test_records.json` from a tree before deploying to make install, migrate or start cheaper. Discovery lives in `run_all_tests` and `get_all_tests` alone, both imported inside their own command bodies.
NEVER match test data with `test_*` or `find -name 'test*'`; `test_records.json` is data the runner reads and only `test_*.py` is a test module.

## values

exit 1 on failure: only when CI is set in the environment
run-tests selectors: --doctype, --module, --module-def, --doctype-list-path, --test, --case
run-tests switches: --skip-test-records, --skip-before-tests, --failfast, --profile, --coverage, --junit-xml-output
--app: scopes before_tests, does not select tests
discovery: full-app walk in run_all_tests and get_all_tests; --doctype derives one module name
walk skips: locals, .git, public, __pycache__, test_runner.py
before_tests call sites: main, ParallelTestRunner.before_test_setup
before_tests declared by: frappe.utils.install.before_tests, erpnext.setup.utils.before_tests, hrms.tests.test_utils.before_tests
schema sync collector: get_doc_files, one listdir per importable doctype folder, opens only <dir>/<dir>.json
patches: read from patches.txt by name
the one reader of a test file outside a run: get_server_messages, which reads text and never imports

## how

Two things about the runner decide whether a result means anything, and both are about what it did NOT do.

The first is the exit code. The command computes a result, zeroes it when there were no failures and no errors, and then hands it to `sys.exit` inside a branch that only fires when `CI` is set. Off CI the callback simply returns, click exits 0, and the words `FAILED (failures=6)` scroll past above a shell that says success. Anything automated that reads `$?` is measuring whether the process crashed, not whether the tests passed.

The second is which tests ran. There are two ways in and they do not agree. The full-app path walks the tree and globs, so it sees every `test_*.py`. The `--doctype` path derives one module name from the DocType and imports it, so it sees one file and dies with an import error when that exact name is absent. A DocType whose behaviour lives in a file named for the behaviour is invisible to it. Grade with the full run; use `--doctype` only to iterate on one thing you already know is named right.

`before_tests` is where a suite gets a site it can run on, and it fires for the app under test only. An app that declares none has never had its site prepared, which is invisible on a bench whose setup wizard someone completed by hand and appears the first time the suite meets a site nobody has touched. That is also the run to make before believing any coverage number.

The suspicion that shipped tests cost a deploy something is checkable and comes back empty. The schema sync does not walk for `.py` files at all — it lists fixed importable-doctype folders and can only open a file whose name equals its parent directory. Patches come from a list of names. The web process imports a hard-coded set. The only code that ever reads a test file outside a test run reads it as text to extract translatable messages, and never imports it. What shipping tests costs is disk.
