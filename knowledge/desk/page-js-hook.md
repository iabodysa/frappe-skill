---
name: page-js-hook
description: The page_js hook appends a second script from any installed app onto a Desk Page it does not own, read from disk and concatenated after the page's own script, and the entry only reaches a running site after the process is restarted because clearing the cache recomputes the hook table from a module Python has already imported.
triggers: ["page_js", "get_code_files_via_hooks", "get_js", "get_hooks", "_load_app_hooks", "app_hooks", "global_cache_keys", "clear_global_cache", "hooks.py", "read_file", "get_app_path", "add javascript to a page from another app", "extend a desk page you do not own", "second script on a desk page", "customise a standard desk page", "hook not taking effect", "hooks.py change does nothing", "clear-cache did not pick up a hook", "restart after editing hooks", "i added extra javascript for a page from my own app and nothing happens", "my change to the app configuration file does nothing until i restart", "why does clearing the cache not pick up my new setting", "the extra script for the page is just ignored with no error anywhere", "it works on the development site but not on the live one", "how do i add my own javascript to a page another app owns", "the file i pointed at is never loaded and there is no message at all", "my added script runs but it cannot replace what the page already did", "two apps add code to the same page which one wins", "the customisation only appeared after we restarted the server"]
product: frappe
---

# page_js hook

## paths

frappe/core/doctype/page/page.py — Page.load_assets, get_code_files_via_hooks, get_js
frappe/desk/form/meta.py — get_code_files_via_hooks, get_js
frappe/hooks.py — page_js
frappe/__init__.py — get_hooks, _load_app_hooks, get_app_path, get_pymodule_path
frappe/cache_manager.py — global_cache_keys, clear_global_cache
frappe/model/utils/__init__.py — render_include

## rules

MUST declare the hook as a dict keyed by the Page's NAME — the record's name, which is the hyphenated route and not the page title — mapping to one path or a list of paths inside the declaring app.
MUST write the path relative to the app PACKAGE and not to the repository root, because it is resolved through get_app_path, which is the app's python package directory.
NEVER put a capital letter or a hyphen in a path segment other than `public`; every join part is scrubbed on the way through, so a mixed-case filename resolves to a lower-case name that does not exist and the file is silently absent.
MUST expect the hook's script to be APPENDED after the page's own script, so it runs later and can only add to or overwrite what the page already declared; it cannot replace it.
MUST expect every installed app to be asked, so two apps can each hang a script on the same page and both land, in installed-app order.
NEVER read a missing file as an error; the path is read with read_file and a falsy result is skipped without a message, so a typo shows up only as behaviour that never happens.
MUST read a page_js file as the TARGET of the include expansion rather than as included text, so its own backslashes are never re-templated; a `{% include %}` written inside it is still expanded and still carries the include hazards — see [[render-include]].
MUST restart the application processes after adding or changing the entry, and NEVER expect a cache clear to be enough. Outside developer_mode the hook table is memoised in the cache under `app_hooks`, which clear-cache does drop, but the recomputation imports the app's hooks module through importlib and gets back the object already in that worker's module table, so the new entry is invisible until the worker is replaced.
MUST expect a site running with developer_mode set to 1 to skip the cache and rebuild the table on every call, so the entry appears at once there and the restart requirement is invisible to whoever wrote it.
MUST prefer the page's own sibling file when the page belongs to your app; the hook exists for reaching a page another app owns, and it costs a restart that the sibling file does not — see [[page]].

## values

shape: `page_js = {"<page name>": "public/js/<file>.js"}` or a list of paths
resolved against: the declaring app's python package directory
order: after the page's own script, apps in installed order
missing file: skipped in silence
takes effect after: a process restart, not a cache clear
developer_mode: no cache, no restart needed

## how

A Desk Page normally serves exactly the script sitting beside its record on disk, which means the app that owns the page owns its behaviour. The hook is the one seam: another app names the page and hands over a file, and the framework concatenates it onto the end of what the owning app produced.

That makes it the right tool for customising a standard page and the wrong tool for splitting your own page into modules, because the split pays a restart on every change while a sibling file and a runtime load do not.

The restart is the part that gets misread. The hook table looks cached, and it is, and dropping the cache looks like the fix. It is not, because the value the cache is rebuilt from is read out of a python module the worker imported once at boot. Two things have to move for a new hook to be live: the cached table and the process. The second one implies the first.
