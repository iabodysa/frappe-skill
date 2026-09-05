---
name: hooks
description: A hooked method runs the decorated controller body first, then every handler registered for the DocType by name, then every handler registered for the wildcard, and the last value each returns overwrites the shared return value unless it is a dict.
triggers: ["hook", "compose", "composer", "add_to_return_value", "run_method", "run_trigger", "import_controller", "get_controller", "get_doc_hooks", "get_hooks", "get_attr", "remove_orphan_doctypes", "Error: Document has been modified after you have opened it", "Please check the value of", "Cannot make dict for single fieldname", "order of doc_events hooks", "hook not firing for a doctype", "my custom function never runs when the record is saved", "the extra validation i added does not fire on this form at all", "why does my handler run before the built in checks instead of after them", "another app's code runs before mine and i cannot change the order", "my function returns a value but something else overwrites it", "the value my handler returned came back empty", "the whole site got slow after i added a handler for every form", "my handler is firing on log records too and i only wanted one form", "after installing a second app the built in checks quietly stopped running", "submitting stopped doing anything and there is no error in the log", "two apps changed the same form and one of them silently won"]
product: frappe
---

# Hooks

## paths

frappe/model/document.py — hook, compose, composer, add_to_return_value, run_method, run_trigger
frappe/model/base_document.py — import_controller, get_controller
frappe/__init__.py — get_doc_hooks, get_hooks, get_attr
frappe/model/sync.py — remove_orphan_doctypes

## rules

MUST expect the decorated controller method to run before any `doc_events` handler, because `compose` calls it and then walks the handler list.
MUST expect handlers registered for the DocType by name to run before handlers registered for `"*"`, because `composer` concatenates the two lists in that order.
MUST expect a `"*"` entry to fire for every DocType on the site, including `Version`, `Error Log` and `Activity Log`, so it runs inside every save the site performs.
MUST return a dict or nothing from a hooked method; `add_to_return_value` merges a dict into the shared return value and assigns anything else, so one non-dict return discards what the controller body and every earlier handler returned.
MUST read `override_doctype_class` as taking the last entry the hook resolution collected, so two installed apps overriding one DocType is neither an error nor a merge — the app later in the resolution retires the other's class.
MUST read the overriding class as REPLACING the DocType's own controller rather than wrapping it; the only structural check is that it subclasses `BaseDocument`.
NEVER let an overriding class inherit from `Document` when the original controller defined behaviour, because every `validate`, `on_submit` and `on_trash` the original defined is then gone with no import error.
MUST subclass the original controller and call `super()` where an override is genuinely needed, and MUST treat a second app claiming the same DocType as a collision to detect.
MUST reach for `doc_events` to ADD behaviour and for `override_doctype_class` only to REMOVE shipped behaviour.
NEVER expect `remove_orphan_doctypes` to report a broken override; it skips every DocType named in `override_doctype_class` before it tries to load a controller.

## values

order on a hooked event: the decorated controller method, doc_events for the DocType, doc_events for "*"
within each group: the order the hooks resolution returns, which follows the installed app order
return value merge: dict updates the shared value, None leaves it, anything else replaces it
override_doctype_class selection: the last entry for that DocType
override_doctype_class check: issubclass of BaseDocument, and an ImportError when the class name is absent from the module

## how

Two hooks reach the same controller and they are opposites. `doc_events` adds a handler onto a list the framework already walks, so the shipped behaviour keeps running and yours runs after it. `override_doctype_class` swaps the class the framework will instantiate, so the shipped behaviour stops existing. Nothing in the names says which is which, and the destructive one fails quietly: an override that forgot to inherit from the original imports cleanly and simply stops validating.

The wildcard entry is the other quiet cost. It reads as a small addition — one handler, registered once — and it is a handler on every DocType the site has, which includes the log rows the framework writes during the very request being handled. Before registering one, count what a single request already saves.

The return value is shared rather than per handler, which is why the framework's own guidance is to set properties on the document instead of returning. If a hooked method must return, make it a dict: a dict merges and anything else silently replaces every earlier contribution, including the controller's own.
