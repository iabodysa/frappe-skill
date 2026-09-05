---
name: client-script
description: Every enabled Client Script for a DocType is concatenated into one __custom_js or __custom_list_js string by creation order and run through new Function, and a DocType Layout drops __custom_js entirely.
triggers: ["ClientScript", "on_update", "on_trash", "dt", "view", "enabled", "script", "set_only_once", "FormMeta.add_custom_script", "FormMeta.add_code", "add_code_via_hook", "__custom_js", "__custom_list_js", "__js", "__list_js", "doctype_js", "doctype_list_js", "ScriptManager", "get_event_handler_list", "frappe.ui.form.on", "frappe.ui.form.off", "frappe.ui.form.trigger", "cscript", "doctype_layout", "Error in Client Script", "client script not running", "form script vs list script", "frappe.ui.form.on refresh", "one custom script broke and now none of my scripts run", "all my scripts on that record type stopped working after i added a new one", "why would adding a script stop the older scripts from running?", "my script works on the form but does nothing on the list", "the script used to run on this form and now it is ignored", "custom code silently does nothing on one form only", "i changed which record type the script belongs to and it did not move", "my new handler does not replace the old one both of them run", "the form comes up completely blank and there is only an error in the console", "i edited the script directly in the database and the old version keeps running", "changes to the script only show up after a restart", "why does my script run twice on every save?"]
product: frappe
---

# Client Script

## paths

frappe/custom/doctype/client_script/client_script.py — ClientScript, on_update, on_trash
frappe/custom/doctype/client_script/client_script.json — dt, view, enabled, script, module, set_only_once
frappe/desk/form/meta.py — FormMeta.add_custom_script, FormMeta.add_code, FormMeta.add_code_via_hook, __custom_js, __custom_list_js, __js, __list_js, doctype_list_js
frappe/hooks.py — doctype_js
frappe/public/js/frappe/form/script_manager.js — ScriptManager, get_event_handler_list, frappe.ui.form.on, frappe.ui.form.off, frappe.ui.form.trigger, cscript
frappe/public/js/frappe/model/model.js — __custom_list_js

## rules

MUST set `view` to List for a script that must run on the list; add_custom_script files a Form row into `__custom_js` and a List row into `__custom_list_js`, and the two strings are never crossed.
MUST expect every enabled Client Script on one DocType to become one concatenated string ordered by `creation` asc, so an early script that throws at parse time takes every later script on that DocType with it.
NEVER change `dt` or `view` after insert; both carry set_only_once, so moving a script between DocTypes or between the list and the form means a new row.
MUST read a Client Script that stopped running on an existing form as a DocType Layout: setup runs `__custom_js` only when `this.frm.doctype_layout` is unset, and appends the layout's own `client_script` to `__js` instead.
MUST expect only `__custom_js` to be wrapped; a throw there raises the "Error in Client Script" msgprint, while a throw in the app's `__js` escapes ScriptManager.setup and leaves the form unrendered with nothing but a console trace.
MUST ship a script an app owns as `<doctype>.js` beside the DocType file or through the `doctype_js` hook, and NEVER as a Client Script row, because add_code returns before reading any file when the DocType is `custom`.
MUST expect frappe.ui.form.on to APPEND to the handler list get_event_handler_list returns, so declaring the same event twice runs both handlers in declaration order and neither replaces the other.
NEVER call frappe.ui.form.off to remove one handler; it empties the whole list for that doctype and fieldname.
MUST expect a `setup` handler to run immediately and synchronously, while every other event is queued and run serially, so a promise returned from `setup` is not awaited.
MUST expect a handler named `custom_<event>` or `<event>` on `frm.cscript` to be called with the old `(doc, cdt, cdn)` arguments, and a handler registered through frappe.ui.form.on with `(frm, doctype, name)`.
MUST clear the DocType cache after writing a Client Script row outside the form; on_update and on_trash are what call frappe.clear_cache, and the script lives in the cached meta.

## values

Client Script query: dt equals the DocType, enabled 1, order by creation asc
view Form: appended to __custom_js
view List: appended to __custom_list_js
app-owned form script: <doctype>.js beside the DocType file, plus regional/<country>.js
app-owned list script: <doctype>_list.js, plus regional/<country>_list.js
hooks: doctype_js and doctype_list_js append to the same __js and __list_js
custom DocType: add_code and add_html_templates both return at once, so no file on disk is read
run order in setup: __js, then the DocType Layout client_script, then __custom_js
error handling: __custom_js in try/catch with a msgprint, __js and the layout script bare

## how

A Client Script is not a file the desk loads; it is a row the meta builder pastes into a string. add_custom_script reads every enabled row for the DocType, sorts by creation, and joins them into one blob per view. The browser then runs the blob with `new Function`, so the unit of failure is the blob and not the row: a stray brace in the oldest script disables every script written after it, and the form gives one message that names no row.

The split between what an app ships and what an operator writes runs along `custom`. add_code walks the module folder for `<doctype>.js` and the `doctype_js` hook, and it returns immediately when the DocType is custom. So a DocType created in the UI can only ever be scripted by a Client Script row, and a DocType an app ships should be scripted by a file — the file loads first, uncaught, and survives a DocType Layout.

The DocType Layout is where this breaks. A form opened through a layout runs `__js` plus the layout's own script and skips `__custom_js` completely. Nothing is logged and the form renders, so the symptom is a rule that silently stops applying for one group of users.

Handlers accumulate rather than replace. Registering the same event from two scripts runs both, and `off` is a reset for the whole event rather than a removal of one function. Where one script must win, it has to change what the earlier one wrote, not re-register the event.
