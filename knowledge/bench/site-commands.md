---
name: site-commands
description: A command written for one site takes the first entry of the expanded --site all list and touches no other, and bench console registers a rollback at exit so an uncommitted mutation is discarded after it appeared to succeed.
triggers: ["get_site", "pass_context", "console", "_console_cleanup", "store_logs", "get_app_groups", "main", "run a bench command on every site", "bench --site all", "i ran it for all sites and only the first one changed", "why did the command exit successfully but only touch one site", "how do i actually run something on every site instead of just one", "my change vanished after i left the interactive shell", "i saved the document in the shell and nothing was saved in the database", "the value looked right in the shell and is still the old one in the browser", "why does everything i do in the interactive shell get thrown away", "the fix i applied by hand is missing on a site restored from a backup", "new sites do not have the change i applied manually", "what is the right way to apply a data change so every site gets it forever", "no error appeared but most of my sites were skipped"]
product: frappe
---

# Site commands

## paths

frappe/commands/__init__.py — get_site, pass_context
frappe/commands/utils.py — console, _console_cleanup, store_logs
frappe/utils/bench_helper.py — get_app_groups, main

## rules

NEVER read a zero exit from a `--site all` run as proof every site was reached. get_site returns context.sites[0], and a command written for one site touches that site alone with no error and no warning when the list holds more.
MUST loop the sites yourself, naming one site per invocation, for any command that calls get_site.
MUST expect frappe.SiteNotSpecifiedError when no site is given, and MUST read a caller passing raise_err=False as one that continues with no site rather than refusing.
MUST type frappe.db.commit() in bench console before leaving the shell. console registers _console_cleanup with atexit, and that function calls frappe.db.rollback() then frappe.destroy(), so every uncommitted write is discarded at exit.
NEVER read a successful doc.save() in the console as a landed write; a get_value straight after it reads the new value from inside the still-open transaction.
NEVER use bench console as a delivery mechanism even with the commit typed. It connects to one site and records nothing about what it did, so a site restored from an older backup, a site created later and a second site on the same bench never receive the change and no command can tell which sites did.
MUST ship a change that has to reach every site as a patch in patches.txt instead; the Patch Log row makes the change once per site and migrate carries it to a site installed long after the patch was written.

## values

get_site: context.sites[0], IndexError or TypeError raises SiteNotSpecifiedError
atexit order: reverse of registration, so store_logs runs before _console_cleanup
_console_cleanup: frappe.db.rollback then frappe.destroy
console namespace: every installed app imported by name, the ones that fail listed under `Failed to import`

## how

`--site all` is an expansion, not a broadcast. Whether it reaches every site is decided by the command
body, not by the flag, and the two shapes are indistinguishable from the outside: both exit zero and
both print nothing about the sites they skipped. Read the command before trusting the flag, and prefer
an explicit loop where the answer matters.

The console's rollback is the feature and the trap at once. Inspection is safe there precisely because
a half-written row cannot escape, and that is the same mechanism that throws away an operator's
deliberate fix. Anything worth doing twice belongs in a patch; the console is for looking.
