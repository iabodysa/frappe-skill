---
name: server-script
description: Server Scripts are switched on only by server_script_enabled in common_site_config.json, and a script runs as the calling session with frappe.get_all and frappe.db.set_value in scope, so it is restricted Python and never elevated Python.
triggers: ["ServerScript", "safe_exec", "is_safe_exec_enabled", "server_script_enabled", "SAFE_EXEC_CONFIG_KEY", "ServerScriptNotEnabled", "get_safe_globals", "FrappeTransformer", "compile_restricted", "RestrictedPython", "read_sql", "check_safe_sql_query", "UNSAFE_ATTRIBUTES", "VALID_UTILS", "get_python_builtins", "run_server_script_for_doc_event", "get_server_script_map", "EVENT_MAP", "server_script_map", "execute_doc", "execute_method", "execute_scheduled_method", "execute_api_server_script", "get_permission_query_conditions", "setup_scheduler_events", "sync_scheduler_events", "clear_scheduled_events", "check_if_compilable_in_restricted_context", "restrict_commit_rollback", "safe_enqueue", "call_whitelisted_function", "run_script", "script_type", "doctype_event", "api_method", "allow_guest", "event_frequency", "cron_format", "enable_rate_limit", "Script Manager", "Server Scripts are disabled. Please enable server scripts from bench configuration.", "Compilation warning", "Query must be of SELECT or read-only WITH type.", "This action is only allowed for", "module has no attribute", "is an unsafe attribute", "Key starts with _", "server script not running", "how to enable server scripts", "python script in the desk", "permission query script", "i wrote a script in the interface and nothing happens when i save a record", "why is my script not running at all", "everything broke after i changed the config file no record will save now", "saving any record now throws an error about scripts being turned off", "the list is empty for everyone except me after i added a filter script", "only one of my two filter scripts for the same record type is taking effect", "how do i let an anonymous caller hit my script safely", "my script saved without complaint but blows up when it actually runs", "the script says it cannot find something only when it runs not when i save it", "i turned the script off in the database and it is still running", "my nightly script never fires and there is no log of it", "my changes to the shipped script disappear after an upgrade", "the script cannot commit and i get an error about it"]
product: frappe
---

# Server Script

## paths

frappe/core/doctype/server_script/server_script.py — ServerScript.validate, ServerScript.on_update, ServerScript.on_trash, ServerScript.clear_cache, ServerScript.get_code_fields, ServerScript.sync_scheduled_jobs, ServerScript.sync_scheduler_events, ServerScript.clear_scheduled_events, ServerScript.check_if_compilable_in_restricted_context, ServerScript.execute_method, ServerScript.execute_doc, ServerScript.execute_scheduled_method, ServerScript.get_permission_query_conditions, setup_scheduler_events, execute_api_server_script, enabled
frappe/core/doctype/server_script/server_script_utils.py — EVENT_MAP, run_server_script_for_doc_event, get_server_script_map
frappe/core/doctype/server_script/server_script.json — script_type, script, reference_doctype, doctype_event, api_method, allow_guest, event_frequency, cron_format, disabled, module, enable_rate_limit, rate_limit_count, rate_limit_seconds
frappe/utils/safe_exec.py — safe_exec, is_safe_exec_enabled, SAFE_EXEC_CONFIG_KEY, ServerScriptNotEnabled, get_safe_globals, FrappeTransformer, NamespaceDict, read_sql, check_safe_sql_query, get_python_builtins, VALID_UTILS, UNSAFE_ATTRIBUTES, _getattr_for_safe_exec, _getitem, _write, safe_enqueue, call_whitelisted_function, run_script, safe_exec_flags
frappe/handler.py — execute_cmd, run_server_script, is_valid_http_method
frappe/model/document.py — Document.run_method
frappe/model/db_query.py — DatabaseQuery.get_permission_query_conditions
frappe/model/sync.py — IMPORTABLE_DOCTYPES, get_doc_files, sync_for
frappe/modules/import_file.py — import_doc, load_code_properties
frappe/rate_limiter.py — rate_limit
frappe/__init__.py — get_common_site_config, only_for

## rules

MUST put `server_script_enabled` in `sites/common_site_config.json`; is_safe_exec_enabled reads get_common_site_config and nothing else, so the same key written into a site's own site_config.json leaves every script off.
MUST read the off state as a throw and not a skip: safe_exec throws ServerScriptNotEnabled before it compiles anything, so removing the key breaks the save of every DocType that has an enabled DocType Event script and breaks every frappe.get_list on a DocType that has a Permission Query script.
NEVER treat a Server Script as elevated code. get_safe_globals binds `frappe.user` and `frappe.session.user` to the live session, and it hands the script frappe.get_all, frappe.db.get_value, frappe.db.set_value and frappe.db.exists, which ignore permissions there exactly as they do in a controller — so an API script with allow_guest gives an anonymous caller everything those calls reach.
MUST read `allow_guest` as the only permission check an API script has; execute_api_server_script raises PermissionError when the session user is Guest and the flag is unset, and nothing else in the path examines the caller.
MUST expect exactly one Permission Query script per DocType to run: get_server_script_map stores `permission_query` as one script name per reference_doctype, so a second enabled script for the same DocType silently replaces the first, while DocType Event scripts append to a list and every one of them runs.
MUST assign to the name `conditions` in a Permission Query script; get_permission_query_conditions seeds locals with `conditions` set to the empty string, reads only that name back, and ANDs the string with whatever the permission_query_conditions hooks returned.
NEVER expect a Permission Query script to reach frappe.get_all, frappe.get_doc or a direct SQL read; only DatabaseQuery calls it, so it applies to frappe.get_list and the calls built on it.
MUST expect a DocType Event script to run AFTER the controller method and after the app hooks and the webhooks for that event; Document.run_method calls run_server_script_for_doc_event last, so a script cannot pre-empt controller code.
MUST expect frappe.db.commit, frappe.db.rollback and frappe.db.add_index to be missing inside a DocType Event script only; safe_exec pops them when restrict_commit_rollback is set, and execute_doc is the single caller that sets it — the API, Scheduler Event and Permission Query paths keep all three.
MUST write only SELECT, EXPLAIN, or on MariaDB a WITH into frappe.db.sql; check_safe_sql_query throws PermissionError "Query must be of SELECT or read-only WITH type." and also refuses any query containing INTO OUTFILE or INTO DUMPFILE. NEVER read that as a read-only script — frappe.db.set_value and the commit hooks are still in the namespace.
NEVER write an import statement, a name starting with an underscore, a subscript key starting with an underscore, or an attribute named `format` or `format_map`; compile_restricted with FrappeTransformer refuses the syntax, and _getattr_for_safe_exec throws SyntaxError for every name in UNSAFE_ATTRIBUTES and for any value that resolves to a module, a code object, a traceback or a frame.
MUST reach a builtin only through the sixteen names get_python_builtins returns and a date or number helper only through the VALID_UTILS names on `frappe.utils`; a name that is not in the namespace comes back from NamespaceDict as a function that raises AttributeError "module has no attribute" when it is called, so the failure appears at run time and never at save.
MUST read the "Compilation warning" popup as advisory only: check_if_compilable_in_restricted_context catches every exception from compile_restricted and msgprints it, so a script that cannot compile still saves and still fails later at execution.
MUST hold the Script Manager role to save a Server Script — validate calls frappe.only_for("Script Manager", True) — and MUST expect that check to be skipped for Administrator, in tests, and on import, because import_doc sets ignore_validate.
MUST expect DocType Event scripts to be dead during install and migrate; run_server_script_for_doc_event returns early on frappe.flags.in_install and frappe.flags.in_migrate, so a patch that writes documents never fires them.
NEVER flip `disabled` with a direct database write. The whole map is cached under `server_script_map` and only ServerScript.clear_cache and on_trash delete that key, so a script disabled outside the document keeps running until the cache is cleared.
MUST expect a Scheduler Event script to own a Scheduled Job Type whose method is `frappe.scrub("<script name>-<frequency>")`; on_update creates or re-frequencies it, and clear_scheduled_events deletes it permanently the moment event_frequency, cron_format, or script_type changes.
MUST read a missing Scheduled Job Log as the frequency, not a failure: setup_scheduler_events sets create_log only when the frequency is neither All nor Cron.
MUST return an API script's payload by assigning into `frappe.flags`; execute_api_server_script returns that dict and run_server_script overwrites response.message only when it is non-empty, so a script that leaves flags empty must write into frappe.response itself.
MUST set rate_limit_count and rate_limit_seconds when enable_rate_limit is checked; the fallbacks are 5 calls per 86400 seconds, and rate_limit counts per IP by default.
MUST ship a Server Script as `<module>/server_script/<scrubbed name>/<scrubbed name>.json` beside a `<scrubbed name>.py`; get_code_fields returns `{"script": "py"}` so load_code_properties fills the `script` field from the sibling file on import, and the JSON should not carry the code.
NEVER edit a shipped Server Script in the Desk and expect it to survive: sync_for re-imports every such JSON on migrate, and import_doc deletes the existing record before it inserts the file's version.

## values

script_type DocType Event: called by run_server_script_for_doc_event from Document.run_method, keyed on reference_doctype plus doctype_event
script_type Scheduler Event: called by a Scheduled Job Type through execute_scheduled_method
script_type Permission Query: called by DatabaseQuery.get_permission_query_conditions, one script per DocType
script_type API: called by handler.execute_cmd through the `_api` map, keyed on api_method
enable key: server_script_enabled, common_site_config.json only
doc event locals: doc
permission query locals: user, conditions
api script return: _globals.frappe.flags, only when non-empty
sql allowed: select, explain, and with on mariadb
commit removed in: DocType Event only
map cache key: server_script_map, cleared by save and delete of a Server Script
scheduled job method: scrub("<script name>-<frequency>")
create_log: set for every frequency except All and Cron
rate limit defaults: 5 calls, 86400 seconds, per IP
save role: Script Manager, skipped for Administrator, in tests, and on import
shipped files: <module>/server_script/<name>/<name>.json and <name>.py

## how

The name says script and the record behaves like four unrelated records. One field, script_type, decides who calls the code, what names are in its locals, and what is taken out of its globals — and nothing warns when the code in the box belongs to a different type. A Permission Query body pasted into an API script returns nothing and raises nothing; it just sets a local that no one reads.

The security question is the one people get backwards. RestrictedPython narrows what the syntax may do, not what the user may reach. The session is the caller's, and the namespace it is handed contains frappe.get_all and frappe.db.set_value, which are the permission-ignoring calls. So safe_exec stops a script from reading a frame or importing os, and does nothing at all to stop it from reading and writing rows the caller could never touch through the UI. The two checks that matter are the Script Manager role on writing a script and allow_guest on an API script; treat every enabled script as trusted server code, because that is what it is.

The disabled state is a failure and not a fallback. Once a Permission Query script exists on a DocType, the site cannot list that DocType with the key removed, because safe_exec throws before it looks at the script. So `server_script_enabled` is not a feature flag that can be turned off on a site that has been using it; removing it takes list views and saves down with it.

Everything on disk is one-way at migrate. A shipped script's Python lives in the sibling `.py` and the record is deleted and re-inserted from the JSON on every migrate, so the Desk editor is a viewer for anything an app ships and an editor only for what a site created.
