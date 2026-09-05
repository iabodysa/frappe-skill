---
name: page-cache
description: with_page serves a Desk Page out of localStorage under `_page:<name>` before it asks the server, so a deployed change to `<page>.js` or `<page>.css` keeps rendering the old asset in a browser that already visited, and the Page record's own `modified` is what the eviction walk compares.
triggers: ["frappe.views.pageview.with_page", "with_page", "_page:", "localStorage", "frappe.model.sync", "frappe.boot.developer_mode", "developer_mode", "frappe.desk.desk_page.getpage", "getpage", "_dynamic_page", "frappe.assets.check", "clear_local_storage", "init_local_storage", "_last_load", "_version_number", "metadata_version", "is_reload", "page_info", "sync_pages", "check_metadata_cache_status", "Clear Cache", "Cleared App Cache.", "localStorage cleared", "desk page script not updating", "old javascript still running frappe", "hard refresh does not update desk page", "page shows old code after deploy", "why is my page js cached", "the page still shows the old code after i deployed", "my changes to the page script are not showing up in the browser", "why does the page keep running last week's script", "i shipped a fix and users still get the old behaviour refreshing does nothing", "it works on my machine but not for anyone else", "clearing the browser cache did not help the old page is still there", "how do i force everyone's browser to pick up a new page script", "the page is correct in a private window and wrong in my normal one", "the styling change on the page is ignored until i clear the cache from the menu", "one user sees the new page and another still sees the old one"]
product: frappe
---

# Desk Page cache

## paths

frappe/public/js/frappe/views/pageview.js — frappe.views.pageview.with_page
frappe/public/js/frappe/assets.js — check, clear_local_storage, init_local_storage, is_reload
frappe/public/js/frappe/desk.js — sync_pages, check_metadata_cache_status
frappe/core/doctype/page/page.py — Page.load_assets
frappe/desk/desk_page.py — get, getpage

## rules

MUST read a Desk Page served on a second visit as coming from `localStorage["_page:" + name]` rather than from the server, because with_page reaches getpage only when that key is absent or `frappe.boot.developer_mode` is 1.
MUST bump the Page record's `modified` when a deployed change lives in `<page>.js` or `<page>.css` alone, because sync_pages evicts `_page:<name>` only where the booted `page_info` stamp differs from the stored one, and reading a file leaves that stamp untouched.
NEVER read one hard refresh as proof the browser now runs the deployed script; the refresh drops the HTTP cache and leaves localStorage standing.
MUST reload a second time within five seconds to force the eviction by hand, because check clears the store when the gap since `_last_load` is under 5000 milliseconds and the navigation type reads as a reload.
MUST reproduce a report of stale Desk-page behaviour in a private window or after Clear Cache before reading the code, because two browsers on one deploy run two different scripts.
MUST expect a site running with `developer_mode` set to 1 to never take the cached branch, so the defect is invisible to the developer who shipped it.
NEVER expect the cache to hold a page whose response carries `_dynamic_page`; with_page writes the key only for a response without it.

## values

key: `_page:<name>`, holding the JSON of the docs getpage returned
read when: the key exists AND `frappe.boot.developer_mode != 1`
written when: getpage answered AND the response carries no `_dynamic_page`
branches ahead of the read: a registered `frappe.standard_pages[name]`, and a `locals.Page[name].script` already synced or the name matching `window.page_name`
evicted by: a changed `window._version_number`, a changed `frappe.boot.metadata_version`, a `_last_load` older than two days, a reload under 5000 ms after the last load, a changed `page_info` stamp for that name, the navbar's Clear Cache
survives: a hard refresh, a logout, a new tab, a rebuilt bundle whose version number is unchanged

## how

The server side has no cache at all. Every getpage runs load_assets, which reads `<page>.js` and `<page>.css` off disk at request time, so the response always carries the file as deployed. The staleness is entirely in the browser: with_page writes that whole response into `localStorage` under `_page:<name>`, and on the next visit it syncs the stored copy into the model and calls back without asking the server anything.

The eviction walk that looks like it covers this does not. sync_pages compares the booted `page_info[name].modified` against the copy it stored at the previous boot and deletes the key when they differ, so a change made through the Page record — its title, its role rows, its own `script` field — evicts correctly. A change made by editing the sibling file does not touch the record, so the stamp matches, the key survives, and the browser keeps running last week's script against this week's server.

Diagnose it by which browser rather than by which code. The developer sees the fix because `developer_mode` sends them down the getpage branch; the user does not, and the user's own hard refresh does not help them, because clearing the HTTP cache and clearing localStorage are separate acts and only the second one matters here. The two things that work from the deploy side are bumping the Page record so the stamp walk fires, and bumping the asset version number so check wipes the whole store.
