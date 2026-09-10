---
name: require
description: frappe.require starts every path loading and running independently and in parallel, with no ordered evaluation step any more, so a script that depends on an earlier one in the same call is safe only by luck of network timing; it still skips any path already evaluated in this page load, so a second call for the same file resolves without re-running it.
triggers: ["frappe.require", "frappe.assets.execute", "eval_assets", "bundled_asset", "_executed", "_version_number", "load a second js file on a desk page", "load javascript at runtime", "share javascript between desk pages", "script loaded twice", "script did not reload after deploy", "assets js cache busting", "carry a module in the app public folder", "my click handler fires twice for a single click", "why is the same script running two times on one page load", "a counter in my shared file starts at double what it should", "the same listener gets attached twice and i cannot find where", "the browser keeps serving the old javascript after i deployed a change", "i cleared the cache and the page still runs the old version of the file", "how do i force everyone to pick up the new javascript", "i dropped a new file into the public folder and the server returns not found", "the new asset works on my machine but not on the other server", "how do i load a second javascript file from a desk page", "the whole screen greys out and locks up while my extra files load", "why did calling the loader again not re-run my file"]
product: frappe
---

# Require

## paths

frappe/public/js/frappe/assets.js — frappe.require, AssetManager.execute, AssetManager.load_asset, AssetManager.extn, bundled_asset
frappe/public/js/frappe/dom.js — frappe.dom.eval, frappe.dom.freeze, frappe.dom.unfreeze
frappe/utils/__init__.py — get_build_version
frappe/build.py — make_asset_dirs, generate_assets_map, link_assets_dir, clear_broken_symlinks
frappe/desk/form/meta.py — get_js, get_code_files_via_hooks
frappe/core/doctype/page/page.py — Page.load_assets

## rules

MUST pass either a single path or an array; a string is wrapped into a one-element array before anything else happens.
MUST read the return value as a Promise that settles after every listed path has been evaluated, and MUST use either that Promise or the callback, because both fire from the same place.
NEVER rely on list order for a JS dependency between two paths in one call; execute maps each path straight to load_asset, which creates its `<script>` element and appends it on the spot without setting `.async = false`, so a dynamically created script defaults to async and each one runs whenever its own fetch resolves, not in array order.
MUST list a dependency in its OWN separate frappe.require call, awaited or chained, when one script must run before another; that is the only ordering the API still gives.
NEVER call it twice for a side effect; a path already evaluated in this page load is skipped by path string, so the second call resolves without running the file again.
NEVER spell one file two ways across an app; a plain path is passed through untouched, so a relative spelling and an absolute one are two keys, the file is evaluated twice, and every top-level side effect in it happens twice with no error to show for it.
MUST read a handler that fires twice, a listener bound twice, or two dependent scripts that sometimes work and sometimes throw depending on network timing, as this rather than as a bug in the module; nothing in the console names either the double evaluation or the race.
MUST expect only a name carrying `.bundle.` and not already under the assets route to be rewritten before the skip is tested; every other path is compared exactly as the caller wrote it.
MUST expect the file to be evaluated as a script element appended to the head, so everything it declares at top level lands in the same global scope the page script gets.
NEVER count on a browser picking up a changed file after a deploy without the cache key moving, because a path that is not a bundle gets the build version appended as a query parameter and that version is the modification time of the site's asset manifest.
NEVER expect a cache clear to make a browser fetch a changed module, because the version appended to the path is the modification time of the asset manifest and clearing the cache re-reads that file without writing it.
MUST write the asset manifest to move the version, and MUST expect every user to re-download every non-bundle asset once when it moves.
MUST read the freeze as part of the contract; the screen is frozen for the whole fetch and unfrozen once, so a long list blocks the page rather than filling it progressively.
MUST expect a new file under the app's public folder to be reachable at once on a bench whose asset directory is LINKED, because the link points at the folder and not at a copy of its contents.
NEVER expect that on a bench whose asset directory was built with hard links, because that path copies the folder rather than pointing at it, and a file added afterwards exists only in the app.
MUST read the app's whole public folder as the unit that is linked or copied, not the individual file, so the choice is made once per bench and not per asset.
MUST reach for this rather than the include directive when the file is a second module rather than a fragment, because the directive is expanded on the server into one script and this leaves the files separate for the editor and the browser.

## values

argument: a path string, or an array of them
each item: passed through bundled_asset before fetching
bundled_asset rewrite: only a path containing `.bundle.` that does not already start with the assets route
every other path: returned unchanged, so the caller's spelling is the key
fetch and evaluation: every item independently, each script appended to the head as soon as its own load_asset call runs, executing whenever its own load fires (default async on a created script element) — array order is not evaluation order
already evaluated in this page load: skipped, by the path string as listed
return: a Promise, settled after the last evaluation
callback: called immediately after the Promise resolves
handler chosen by: the path extension
javascript handler: a script element appended to the head
cache key on a non-bundle path: `?v=` plus the build version
build version: the modification time of the site's asset manifest
developer mode or dev server: the current timestamp instead
asset route: the app's `public` folder, exposed as `assets/<app>`
default link: a symlink to the folder, so a file added later is served with no further step
hard-link build: a copy of the folder, so a file added later is not served until it runs again
broken links: cleared before the map is rebuilt
screen: frozen for the fetch, unfrozen once at the end

## how

There is no order guarantee to reason about any more. `execute` maps each path to `load_asset` and lets `Promise.all` wait for all of them, but each `load_asset` builds its own `<script>` element and appends it to the head immediately, without setting `.async = false`; a script element created this way defaults to async, so the browser runs it whenever ITS OWN fetch resolves, not in the order it was appended. A module that depends on another, listed first or not, now runs correctly only when the network happens to return the dependency first.

The skip is a memory of path strings and not of files. It is what makes a second require harmless, and it is also why a file listed once under one spelling and once under another runs twice, declaring everything at top level a second time in the same global scope. Spell a path one way across the app and the question does not arise. What makes it expensive to find is that the second evaluation is silent: nothing is logged, nothing throws, and the only trace is the module's own top-level work happening twice, which surfaces later as a handler that fires on every click twice or a listener that cannot be removed because two were bound.

The cache key is where a deploy goes quiet. The query parameter is appended only to paths that are not bundles, and its value is the modification time of the site's asset manifest rather than of the file that changed. A file replaced in the app's public folder is served immediately by the server and can still be read from the browser's cache, so the change appears to have not deployed. Touching the manifest moves the key for every non-bundle path at once, and developer mode sidesteps it entirely by using the current time.

The public folder is exposed by linking, and the link is made once for the folder rather than for each file in it. That is why a new module dropped into the app's public folder is served immediately on an ordinary bench, with no build and no restart, and it is the whole reason this route is cheaper than the include directive for a second file. The exception is worth knowing before relying on it: the same setup can be asked to hard-link instead, which copies the folder rather than pointing at it, and there a file added after the copy is present in the app and absent from what the site serves. The symptom is a request that answers with nothing while the file plainly exists on disk.
