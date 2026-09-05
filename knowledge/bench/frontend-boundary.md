---
name: frontend-boundary
description: The desk is handed the whole merged dictionary in its boot payload while a portal page is handed none at all, so the same `__()` call translates in the desk and returns English on the portal.
triggers: ["get_messages_for_boot", "send_translations", "__messages", "_messages", "frappe._", "get_all_messages_from_js_files", "get_messages_from_include_files", "extract_messages_from_javascript_code", "get_messages_from_file", "get_boot_data", "portal string not translated", "__() returns english on website page", "the text is translated inside the admin screens but comes out english on the public page", "why is my customer facing page still in english when the back office is translated", "so annoyed that the same label translates in one place and not the other", "the public website page ignores the language completely", "i added the translation row and the public page still shows english", "adding the translation did nothing for the portal page what am i missing", "the string never made it into the translation file for extraction", "some labels are picked up for translation and others are silently skipped", "how do i get translated text onto a page outside the admin area", "nothing in the browser tells me whether the translation is missing or was never sent"]
product: frappe
---

# The desk and portal translation boundary

## paths

frappe/translate.py — get_messages_for_boot, get_all_translations, send_translations, get_messages_for_app, get_all_messages_from_js_files, get_messages_from_include_files, get_messages_from_file, extract_messages_from_javascript_code
frappe/boot.py — get_messages_for_boot
frappe/www/app.html — frappe.boot, _messages
frappe/templates/base.html — frappe.boot
frappe/website/utils.py — get_boot_data
frappe/public/js/frappe/provide.js — frappe._messages
frappe/public/js/frappe/translate.js — frappe._, window.__
frappe/public/js/frappe/request.js — __messages
frappe/public/js/frappe/model/meta.js — __messages
frappe/public/js/desk.bundle.js — translate.js
frappe/public/js/frappe-web.bundle.js — translate.js

## rules

MUST expect the built bundle to carry the source strings and no translation at all; every translated string reaches the browser at run time in the boot payload or in a response.
MUST expect the desk to receive the entire merged dictionary for the language in one payload, because the boot info carries it and the desk page assigns it to `frappe._messages` before any bundle runs.
MUST expect a portal page to receive none of it: the website boot dict has no messages key, the portal template assigns `frappe.boot` alone, and `frappe._messages` stays the empty object that `provide.js` created — so `__()` there returns its own argument.
NEVER read an untranslated string on a portal page as a missing CSV row; MUST first ask whether that page was served any dictionary at all.
MUST call `send_translations` in the server method behind a portal page to put the rows that page needs into the response, because the response handler merges a `__messages` key into `frappe._messages`, and a form response merges the same key off the document.
MUST expect `__()` to fall back to its own argument on a miss and to log nothing, so a missing translation and a page that was served no dictionary look identical in the browser.
MUST pass the context as the third argument to `__()`, which looks up `source:context` first and the bare source second.
MUST keep a translatable string in a `.js`, `.html` or `.vue` file under the app's `public` directory, because the extractor walks that directory alone plus the bundled assets named by `app_include_js` and `web_include_js`, and skips the framework's own `js/lib`.
NEVER pass a variable or an expression as the first argument to `__()`; the extractor keeps a call only when its first argument is a literal, and drops it silently otherwise, so the string never reaches the POT.
MUST expect both bundles to carry `__`, so the function exists on the desk and on the portal alike, whether or not the page holds a dictionary.

## values

desk dictionary: the boot key `__messages`, assigned in `frappe/www/app.html`
portal dictionary: none — the website boot dict carries lang, apps_data, sysdefaults, time_zone, assets_json, sitename, is_fc_site
holder in the browser: `frappe._messages`, created empty by `provide.js`
run-time top-ups: a response `__messages` key merged by the request handler, and a document `__messages` key merged by the meta handler
server writer of those: `send_translations`, which updates `frappe.local.response["__messages"]`
lookup order: `source:context`, then `source`, then the source text itself
extractor roots: every `.js`, `.html` and `.vue` file under `<app>/public`, plus the bundled asset behind each `app_include_js` and `web_include_js` entry
extractor skips: `frappe/public/js/lib`

## how

There are two front ends and only one of them is translated by default. The desk trades payload size for completeness: it ships every string for the language on every load, so any `__()` anywhere in the desk resolves. The portal trades the other way and ships nothing, so its translated text has to come from the server with each response, or from Jinja's `_()` at render time.

That makes the fix for an English string on a portal page a server-side one. Either render the text through Jinja, where the server translates before the HTML leaves, or have the method behind the page call `send_translations` with the rows the page needs. Adding the row to the CSV changes nothing on the portal on its own.
