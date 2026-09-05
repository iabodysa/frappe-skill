---
name: case
description: FrappeTestCase.set_user restores the user the block was entered with rather than Administrator, and change_settings, patch_hooks and timeout are module-level in frappe.tests.utils rather than methods on the case.
triggers: ["FrappeTestCase", "FrappeTestCase.set_user", "FrappeTestCase.switch_site", "FrappeTestCase.freeze_time", "FrappeTestCase.primary_connection", "FrappeTestCase.secondary_connection", "FrappeTestCase.assertQueryCount", "FrappeTestCase.assertRedisCallCounts", "FrappeTestCase.assertRowsRead", "FrappeTestCase.assertQueryEqual", "FrappeTestCase.assertDocumentEqual", "FrappeTestCase.assertSequenceSubset", "FrappeTestCase.normalize_html", "FrappeTestCase.normalize_sql", "FrappeTestCase.enable_safe_exec", "MockedRequestTestCase", "change_settings", "patch_hooks", "timeout", "ValidationError", "MandatoryError", "UpdateAfterSubmitError", "LinkValidationError", "NameError", "Document._validate_mandatory", "Document.validate_update_after_submit", "Error: Document has been modified after you have opened it", "frappe test case set_user", "change_settings and patch_hooks in tests", "a later test runs with full rights it should not have", "my tests pass on their own but fail when run together", "why does one test change who the next test runs as", "the test still passes after i deleted the rule it was supposed to protect", "the test proves nothing because it passes with the code removed", "how do i make a failure test actually check my own rule", "the helper i want to use cannot be found on the test class", "importing the settings helper for a test fails", "where do the test helpers for changing settings live", "the clock i froze in the test is off by the time zone", "the setup on my test class is silently skipped"]
product: frappe
---

# Case

## paths

frappe/tests/utils.py — FrappeTestCase, FrappeTestCase.set_user, FrappeTestCase.switch_site, FrappeTestCase.freeze_time, FrappeTestCase.primary_connection, FrappeTestCase.secondary_connection, FrappeTestCase.assertQueryCount, FrappeTestCase.assertRedisCallCounts, FrappeTestCase.assertRowsRead, FrappeTestCase.assertQueryEqual, FrappeTestCase.assertDocumentEqual, FrappeTestCase.assertSequenceSubset, FrappeTestCase.normalize_html, FrappeTestCase.normalize_sql, FrappeTestCase.enable_safe_exec, MockedRequestTestCase, change_settings, patch_hooks, timeout
frappe/exceptions.py — ValidationError, MandatoryError, UpdateAfterSubmitError, LinkValidationError, NameError
frappe/model/document.py — Document._validate_mandatory, Document.validate_update_after_submit

## rules

MUST subclass `FrappeTestCase`, and MUST call `super().setUpClass()` from any `setUpClass` of your own or the base class does nothing.
NEVER hand-write a `try: … finally:` that saves and restores state the class already carries; each one is one of the context managers below and the hand-written form is usually worse.
NEVER restore the literal `"Administrator"` after switching user. `set_user` restores `frappe.session.user` as it was on entry, and a hand-written restore to Administrator leaves every later test in the class running with full rights while reporting green.
MUST import `change_settings`, `patch_hooks` and `timeout` from `frappe.tests.utils`; they are module-level and are not methods on the case.
MUST use `change_settings` as a decorator on the method or as a `with` block, passing the DocType and either a dict or keyword arguments.
MUST use `freeze_time` on the class rather than `freezegun.freeze_time` directly; it localises the value to the system time zone and converts to UTC first.
MUST use `primary_connection` and `secondary_connection` to act as two users at once; the second connection is opened on first use and `secondary_connection` registers `_rollback_connections` with `addCleanup`, so both connections roll back at the end of that test.
NEVER assert bare `frappe.ValidationError` on a field carrying `reqd` or on a change after submit. `MandatoryError` and `UpdateAfterSubmitError` both subclass `ValidationError`, and the framework raises them from `_validate_mandatory` and `validate_update_after_submit` on every save, so the assertion passes with the controller rule deleted.
MUST name a phrase only the controller emits, through `assertRaisesRegex`, before treating an exception assertion as proof of the app's own rule.

## values

class: FrappeTestCase, in frappe/tests/utils.py
on the case: set_user, switch_site, freeze_time, primary_connection, secondary_connection, assertQueryCount, assertRedisCallCounts, assertRowsRead, assertQueryEqual, assertDocumentEqual, assertSequenceSubset, normalize_html, normalize_sql, enable_safe_exec
module-level: change_settings, patch_hooks, timeout
also shipped: MockedRequestTestCase
set_user restores: frappe.session.user as it was on entry
maxDiff: 10000
ValidationError subclasses met on an ordinary save: MandatoryError, UpdateAfterSubmitError, LinkValidationError

## how

Almost everything a Frappe test wants to do temporarily — be another user, change a Single, override a hook, freeze the clock, hold a second connection, count queries — is already a context manager, and the hand-written equivalent is where the subtle test-pollution bugs come from. The worst of them is the user switch, because the hand-written version restores a literal Administrator instead of whatever was there, and the damage does not land in the test that caused it. It lands in a later test in the same class, which now runs with rights it never asked for and passes for the wrong reason. Reach for the class's version before writing a `finally`.

Where a helper lives is worth knowing before the import fails: the ones that need the test instance hang off the case, while `change_settings`, `patch_hooks` and `timeout` are plain module-level context managers you import and can also use as decorators.

An assertion about a refusal needs one more thought than it looks like it does. Frappe's exception tree puts the metadata refusals under `ValidationError`, so a test that asserts `ValidationError` on a required field is asserting that the field is required — which the DocType JSON already guarantees — and it keeps passing after someone deletes the controller rule it was written to protect. Ask what text only your own code produces, and assert on that.
