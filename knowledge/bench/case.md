---
name: case
description: FrappeTestCase is gone, split into UnitTestCase and IntegrationTestCase(UnitTestCase); set_user restores the user the block was entered with rather than Administrator, and change_settings, patch_hooks, switch_site and timeout are module-level context managers in frappe.tests.classes.context_managers registered onto the case as staticmethods rather than hand-written methods.
triggers: ["FrappeTestCase", "UnitTestCase", "IntegrationTestCase", "BaseTestCase", "UnitTestCase.set_user", "UnitTestCase.freeze_time", "UnitTestCase.enable_safe_exec", "IntegrationTestCase.switch_site", "IntegrationTestCase.primary_connection", "IntegrationTestCase.secondary_connection", "IntegrationTestCase.assertQueryCount", "IntegrationTestCase.assertRedisCallCounts", "IntegrationTestCase.assertRowsRead", "UnitTestCase.assertQueryEqual", "UnitTestCase.assertDocumentEqual", "UnitTestCase.assertSequenceSubset", "UnitTestCase.normalize_html", "UnitTestCase.normalize_sql", "MockedRequestTestCase", "registerAs", "change_settings", "patch_hooks", "timeout", "timeout_context", "ValidationError", "MandatoryError", "UpdateAfterSubmitError", "LinkValidationError", "NameError", "Document._validate_mandatory", "Document.validate_update_after_submit", "Error: Document has been modified after you have opened it", "frappe test case set_user", "change_settings and patch_hooks in tests", "a later test runs with full rights it should not have", "my tests pass on their own but fail when run together", "why does one test change who the next test runs as", "the test still passes after i deleted the rule it was supposed to protect", "the test proves nothing because it passes with the code removed", "how do i make a failure test actually check my own rule", "the helper i want to use cannot be found on the test class", "importing the settings helper for a test fails", "where do the test helpers for changing settings live", "the clock i froze in the test is off by the time zone", "the setup on my test class is silently skipped", "which test case do i inherit from", "my test has no database connection", "AttributeError FrappeTestCase"]
product: frappe
---

# Case

## paths

frappe/tests/classes/unit_test_case.py — BaseTestCase, BaseTestCase.registerAs, UnitTestCase, UnitTestCase.assertQueryEqual, UnitTestCase.assertSequenceSubset, UnitTestCase.assertDocumentEqual, UnitTestCase.normalize_html, UnitTestCase.normalize_sql
frappe/tests/classes/integration_test_case.py — IntegrationTestCase, IntegrationTestCase.primary_connection, IntegrationTestCase.secondary_connection, IntegrationTestCase.assertQueryCount, IntegrationTestCase.assertRedisCallCounts, IntegrationTestCase.assertRowsRead
frappe/tests/classes/mocked_request_test_case.py — MockedRequestTestCase
frappe/tests/classes/context_managers.py — freeze_time, set_user, patch_hooks, enable_safe_exec, debug_on, timeout_context, timeout, trace_fields, change_settings, switch_site
frappe/exceptions.py — ValidationError, MandatoryError, UpdateAfterSubmitError, LinkValidationError, NameError
frappe/model/document.py — Document._validate_mandatory, Document.validate_update_after_submit

## rules

MUST subclass `UnitTestCase` for a test needing no site connection, and `IntegrationTestCase` for one needing a site, an automatic connection and automatic test-record loading; `FrappeTestCase` no longer exists and importing it raises `ImportError`.
MUST import both from `frappe.tests` — `from frappe.tests import UnitTestCase, IntegrationTestCase` — and MUST call `super().setUpClass()` from any `setUpClass` of your own or the base class does nothing.
NEVER hand-write a `try: … finally:` that saves and restores state the class already carries; each one is one of the context managers below and the hand-written form is usually worse.
NEVER restore the literal `"Administrator"` after switching user. `set_user` restores `frappe.session.user` as it was on entry, and a hand-written restore to Administrator leaves every later test in the class running with full rights while reporting green.
MUST import `change_settings`, `patch_hooks`, `switch_site` and `timeout` from `frappe.tests.classes.context_managers` when using them outside a test method; each is a plain module-level function, then registered onto a case class with `BaseTestCase.registerAs(staticmethod)` so it is also callable as `self.change_settings(...)` on the class it was registered against.
MUST expect `set_user`, `freeze_time`, `enable_safe_exec` and `timeout` on `UnitTestCase` and therefore on `IntegrationTestCase` too, and MUST expect `change_settings` and `switch_site` on `IntegrationTestCase` ONLY; calling either on a bare `UnitTestCase` raises `AttributeError`.
MUST use `change_settings` as a decorator on the method or as a `with` block, passing the DocType and either a dict or keyword arguments.
MUST use the case's `freeze_time` rather than `freezegun.freeze_time` directly; it localises the value to the system time zone and converts to UTC first.
MUST use `primary_connection` and `secondary_connection` (`IntegrationTestCase` only) to act as two users at once; the second connection is opened on first use and `secondary_connection` registers `_rollback_connections` with `addCleanup`, so both connections roll back at the end of that test.
NEVER assert bare `frappe.ValidationError` on a field carrying `reqd` or on a change after submit. `MandatoryError` and `UpdateAfterSubmitError` both subclass `ValidationError`, and the framework raises them from `_validate_mandatory` and `validate_update_after_submit` on every save, so the assertion passes with the controller rule deleted.
MUST name a phrase only the controller emits, through `assertRaisesRegex`, before treating an exception assertion as proof of the app's own rule.
MUST treat `Document._validate_mandatory`, `Document._validate_links`, `Document._validate_selects` and `frappe/model/naming.py:set_new_name` as already enforcing `reqd`, Link existence, Select options and `naming_series` before any app-level test runs; a test that only re-asserts one of these DocField-declared properties duplicates a validator the framework's own suite already covers.

## values

classes: BaseTestCase (mixin, in unit_test_case.py) -> UnitTestCase(unittest.TestCase, BaseTestCase) -> IntegrationTestCase(UnitTestCase) -> MockedRequestTestCase(IntegrationTestCase)
on UnitTestCase: assertQueryEqual, assertSequenceSubset, assertDocumentEqual, normalize_html, normalize_sql, and registered: set_user, freeze_time, enable_safe_exec, debug_on, timeout_context, trace_fields
on IntegrationTestCase only: primary_connection, secondary_connection, assertQueryCount, assertRedisCallCounts, assertRowsRead, and registered: change_settings, switch_site
plain functions, not registered onto any case: timeout (decorator wrapping timeout_context)
set_user restores: frappe.session.user as it was on entry
ValidationError subclasses met on an ordinary save: MandatoryError, UpdateAfterSubmitError, LinkValidationError

## how

`FrappeTestCase` was replaced by a two-class split. `UnitTestCase` needs no database and carries the assertions and context managers that do not touch a site — user switching, time freezing, safe-exec, HTML/SQL normalisation. `IntegrationTestCase` extends it and adds everything that needs a live connection — the settings and site-switch context managers, the query-count and Redis-call assertions, the dual-connection helpers, and automatic test-record loading. Picking the wrong parent fails at attribute-access time, not at import time: a test that calls `self.change_settings(...)` on a bare `UnitTestCase` subclass raises `AttributeError` on that line, not on the class declaration.

Almost everything a Frappe test wants to do temporarily — be another user, change a Single, override a hook, freeze the clock, hold a second connection, count queries — is already a context manager, and the hand-written equivalent is where the subtle test-pollution bugs come from. The worst of them is the user switch, because the hand-written version restores a literal Administrator instead of whatever was there, and the damage does not land in the test that caused it. It lands in a later test in the same class, which now runs with rights it never asked for and passes for the wrong reason. Reach for the class's version before writing a `finally`.

Where a helper lives is worth knowing before the import fails: each of `set_user`, `change_settings`, `patch_hooks`, `switch_site`, `freeze_time`, `enable_safe_exec` and `timeout_context` is written once as a plain function in `context_managers.py` and attached to `UnitTestCase` or `IntegrationTestCase` by the `@registerAs(staticmethod)` decorator at import time, so the same function is both a `self.` method on the case and importable directly when a plain `with` block is wanted outside a test method.

An assertion about a refusal needs one more thought than it looks like it does. Frappe's exception tree puts the metadata refusals under `ValidationError`, so a test that asserts `ValidationError` on a required field is asserting that the field is required — which the DocType JSON already guarantees — and it keeps passing after someone deletes the controller rule it was written to protect. Ask what text only your own code produces, and assert on that.
