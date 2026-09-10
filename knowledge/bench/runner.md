---
name: runner
description: bench run-tests now exits non-zero on any failure with no CI gate; bench run-parallel-tests still exits 0 on a failing suite unless CI is set in the environment. The old test_runner.py module is deprecated and empty of logic; discovery, categorisation (unit vs integration) and before_tests wiring live in frappe/testing/ and fire before_tests only ahead of the integration category.
triggers: ["main", "discover_all_tests", "discover_doctype_tests", "discover_module_tests", "_add_module_tests", "TestRunner", "TestRunner.iterRun", "TestConfig", "IntegrationTestPreparation", "ParallelTestRunner", "ParallelTestRunner.before_test_setup", "ParallelTestRunner.print_result", "get_all_tests", "run_tests", "run_parallel_tests", "app_group", "before_tests", "get_hooks", "_load_app_hooks", "sync_for", "get_doc_files", "run_all", "get_server_messages", "application", "test-category", "unit test category", "integration test category", "Cannot make dict for single fieldname", "Invalid request arguments", "bench run-tests exit code", "bench run-parallel-tests exit code", "run_tests sys.exit CI", "the tests failed on screen but the pipeline says everything passed", "why does a failing test run still report success", "my automation never catches a broken test", "i added a second test file next to the form and it never runs", "it says the module cannot be found when i target one form", "how do i make sure the whole app is actually being tested", "the setup routine i wrote never runs before the tests", "before_tests never runs for my unit tests", "the tests create a company in dollars and the wrong country", "one test errors about a missing warehouse type on a fresh site", "the parallel run skips the preparation step my tests need", "i removed test files before deploying and things broke", "how do i get a real failure signal out of the test command", "ModuleNotFoundError test_runner", "frappe.test_runner deprecated"]
product: frappe
---

# Runner

## paths

frappe/testing/discovery.py — discover_all_tests, discover_doctype_tests, discover_module_tests, _add_module_tests, TestRunnerError
frappe/testing/runner.py — TestRunner, TestRunner.iterRun, TestRunner._prepare_category, TestRunner._has_tests, CATEGORY_PRIORITIES
frappe/testing/environment.py — _initialize_test_environment, _cleanup_after_tests, IntegrationTestPreparation, IntegrationTestPreparation._run_before_test_hooks
frappe/testing/config.py — TestConfig, TestParameters
frappe/commands/testing.py — main, run_tests, run_parallel_tests, run_tests_in_light_mode
frappe/parallel_test_runner.py — ParallelTestRunner, ParallelTestRunner.before_test_setup, ParallelTestRunner.print_result, get_all_tests
frappe/test_runner.py — main, get_modules, get_dependencies, get_test_record_log, make_test_objects, make_test_records, make_test_records_for_doctype, print_mandatory_fields, xml_runner_wrapper
frappe/utils/bench_helper.py — app_group
frappe/hooks.py — before_tests
frappe/__init__.py — get_hooks, _load_app_hooks
frappe/model/sync.py — sync_for, get_doc_files
frappe/modules/patch_handler.py — run_all
frappe/translate.py — get_server_messages
frappe/app.py — application

## rules

MUST grade `bench run-tests` on its exit code alone; `commands/testing.py:main` computes `success = all(r.wasSuccessful() for _, _, r in results)` and calls `sys.exit(1)` on failure UNCONDITIONALLY — no `CI` check gates it any more.
MUST still grade `bench run-parallel-tests` on its printed result rather than its exit code alone off CI; `ParallelTestRunner.print_result` calls `sys.exit(1)` on a failure or an error only `if os.environ.get("CI")`, so the single-process and parallel commands disagree with each other.
NEVER assume the two test commands share one exit-code rule; `run-tests` is now honest everywhere, `run-parallel-tests` is honest only under `CI`.
MUST run the whole app with `--app` (or no selector) when the result is load-bearing; `discover_all_tests` walks the app path and takes every file starting with `test_` and ending in `.py`, skipping dot-folders, `node_modules`, `locals`, `public`, `__pycache__`, any path under `doctype/doctype/boilerplate`, and the filename `test_runner.py`.
NEVER treat a green `--doctype` run as evidence about a DocType's tests. `discover_doctype_tests` builds one module name with `get_module_name(doctype, module, "test_")` and imports exactly it; there is no discovery, so a second test file beside the DocType is never reached, and it additionally raises `TestRunnerError` when the doctype's declaring app does not match `--app`.
MUST read `ModuleNotFoundError` from `--doctype` as a name that does not match `test_<scrubbed doctype>.py`, never as a missing test, and MUST fix it by moving the content into that filename.
MUST expect `_add_module_tests` to sort every loaded test into `unit`, `integration`, or `unspecified-category` by matching `UnitTestCase`/`IntegrationTestCase` with a `match` statement, and MUST use `--test-category unit|integration|all` to run only one category.
MUST declare `before_tests` in the app's own `hooks.py`, but MUST expect it to fire for `bench run-tests` ONLY ahead of that app's `integration` category, through `IntegrationTestPreparation._run_before_test_hooks`, which calls `frappe.get_hooks("before_tests", app_name=app)`; an app whose suite is all `unit` tests never runs its `before_tests` hook through this path at all.
MUST expect `bench run-parallel-tests` to wire `before_tests` differently: `ParallelTestRunner.before_test_setup` calls the same `frappe.get_hooks("before_tests", app_name=self.app)` once for the whole app, unconditionally, with no category gate.
MUST pass `--skip-before-tests` to `run-tests` to suppress the hook explicitly; MUST copy the shape of `hrms.tests.test_utils.before_tests` rather than the values of `erpnext.setup.utils.before_tests`, whose company is USD and United States.
MUST read `--app` as the `before_tests` scope; `--doctype`, `--module` and `--module-def` are what select the tests.
MUST run a suite once on a site nobody has completed the setup wizard on before citing it as coverage; a Company insert on a bare site raises `LinkValidationError: Could not find Warehouse Type: Transit` because `install_fixtures` creates that record and `bench install-app erpnext` does not.
NEVER strip `test_*.py` or `test_records.json` from a tree before deploying to make install, migrate or start cheaper. Discovery lives in `discover_all_tests` and `get_all_tests` alone, both imported inside their own command bodies.
NEVER match test data with `test_*` or `find -name 'test*'`; `test_records.json` is data the runner reads and only `test_*.py` is a test module.
NEVER import from `frappe.test_runner` in new code; every name it re-exports comes from `frappe.deprecation_dumpster` and the module's own docstring says it is removed in v17.

## values

run-tests exit code: 1 on any failure, unconditionally (commands/testing.py:main)
run-parallel-tests exit code: 1 on failure or error, only when CI is set (ParallelTestRunner.print_result)
run-tests selectors: --doctype, --module, --module-def, --doctype-list-path, --test, --case, --test-category {unit,integration,all}
run-tests switches: --skip-test-records (deprecated, no effect), --skip-before-tests, --failfast, --profile, --coverage, --junit-xml-output, --lightmode, --debug
--app: scopes before_tests, does not select tests
discovery: full-app walk in discover_all_tests and get_all_tests; --doctype and --module-def derive one module name per doctype
walk skips: dot-folders, node_modules, locals, public, __pycache__, doctype/doctype/boilerplate, test_runner.py
category order run-tests executes in: unit (priority 1) before integration (priority 2)
before_tests call sites: IntegrationTestPreparation._run_before_test_hooks (run-tests, integration category only), ParallelTestRunner.before_test_setup (run-parallel-tests, whole app, every run)
before_tests declared by: frappe.utils.install.before_tests, erpnext.setup.utils.before_tests, hrms.tests.test_utils.before_tests
schema sync collector: get_doc_files, one listdir per importable doctype folder, opens only <dir>/<dir>.json
patches: read from patches.txt by name
the one reader of a test file outside a run: get_server_messages, which reads text and never imports

## how

The exit code split is the fact worth carrying first. `commands/testing.py:main` calls `sys.exit(1)` on any failure with no environment check, so `bench run-tests` is trusted by its exit code alone. `ParallelTestRunner.print_result` checks `os.environ.get("CI")` before exiting non-zero, so `bench run-parallel-tests` exits zero on failure off CI and has to be graded by its printed summary.

`frappe/test_runner.py` is not where any of this logic lives any more. Its own docstring says it is deprecated and removed in v17, and every name it still exposes is a straight re-export from `frappe.deprecation_dumpster`, kept only so old imports do not crash. The real discovery, categorisation and execution code is under `frappe/testing/`: `discovery.py` finds tests, `runner.py`'s `TestRunner` groups them into categories and iterates them in priority order, `environment.py` sets up and tears down the process, and `config.py` carries the run's options.

Categorisation decides what `before_tests` means. Every discovered test is sorted into `unit` or `integration` by which of `UnitTestCase`/`IntegrationTestCase` it subclasses, and `TestRunner.iterRun` calls the `before_tests` preparation step only ahead of the `integration` category, so a suite made entirely of `UnitTestCase` subclasses never triggers the hook through `run-tests`. `run-parallel-tests` does not categorise; `ParallelTestRunner.before_test_setup` runs the hook once for the whole app ahead of everything.

The `--doctype` landmine is unchanged in shape even though the code moved: `discover_doctype_tests` still derives one module name from the DocType and imports it, so it sees one file and dies with an import error when that exact name is absent, now also raising when the doctype's own app disagrees with `--app`. Grade with the full run; use `--doctype` only to iterate on one thing you already know is named right.

The suspicion that shipped tests cost a deploy something is still checkable and still comes back empty. The schema sync does not walk for `.py` files at all — it lists fixed importable-doctype folders and can only open a file whose name equals its parent directory. Patches come from a list of names. The web process imports a hard-coded set. The only code that ever reads a test file outside a test run reads it as text to extract translatable messages, and never imports it. What shipping tests costs is disk.
