---
name: app-over-framework
description: Apps are merged in install order with frappe first, so an app CSV row for a string the framework already ships silently replaces the framework's own wording for every user of that string.
triggers: ["get_translations_from_apps", "get_translations_from_csv", "get_translation_dict_from_file", "get_translations_from_mo", "get_installed_apps", "get_all_apps", "RateLimiter.reject", "Cannot make dict for single fieldname", "Either key or IP flag is required.", "You hit the rate limit because of too many requests. Please try after sometime.", "app translation overrides framework translation", "translation merge order", "installing an app changed the wording of a message everywhere else", "a standard message suddenly reads differently after we added our app", "why did the text of a built-in message change when i installed another app", "the same sentence is translated two different ways in different screens", "our translation of a shared message keeps getting overwritten", "which app wins when two apps translate the same sentence", "my translation stopped working after the upgrade and i never touched it", "the wording i set is gone again after updating", "why does my translated text revert after an update", "changing the translation for one screen broke the wording on another screen"]
product: frappe
---

# App rows and framework rows

## paths

frappe/translate.py — get_translations_from_apps, get_translations_from_csv, get_translation_dict_from_file
frappe/gettext/translate.py — get_translations_from_mo
frappe/__init__.py — get_installed_apps, get_all_apps
frappe/rate_limiter.py — RateLimiter.reject

## rules

MUST look a source string up in the installed apps' own translation files before adding a row for it to an app CSV.
NEVER add an app row for a string the framework already translates; the app row wins and replaces the framework's wording everywhere that string is raised, including inside framework code the app never calls.
MUST read an app that raises a framework sentence byte for byte as raising the FRAMEWORK's string, so the translation belongs to the framework and the app owes no row.
MUST change the English source string when an app wants different wording, never the translation of the framework's string, because the key is the English text and a different key is the only way to hold a different translation.
NEVER read a duplicate row as harmless because both translations look correct; the app row survives a framework wording change and the two silently diverge at the next upgrade.
MUST expect an app's own MO to beat its own CSV, since the CSV is loaded first and the MO updates over it.

## values

app order: install order from the `installed_apps` global, frappe first
within one app: CSV first, MO second — the MO wins
collision rule: plain `dict.update()`, so the later source wins and nothing warns
key: the English source string, plus `:context` where a context is given
the app cannot lose a key it declares: no priority field, no override marker, no way for the framework to hold its own row

## how

`get_translations_from_apps` walks the installed apps in order and calls `translations.update()` for
each app's CSV and then its MO. Precedence is position and nothing else, so the last app to declare a
key owns it. Frappe is always first, which makes every other app's row an override of the framework's.

This bites where an app re-raises a sentence the framework already raises. The app looks like it is
translating its own message; it is replacing the framework's, for every code path in every app that
raises the same English text. The rate-limit rejection is the shape of it — an app helper that throws
the same sentence `RateLimiter.reject` throws inherits the framework's translation for free, and adding
a row for it takes that translation away from the framework and hands it to the app.

Ask of any proposed app row: does the installed framework already carry this key? If it does, the row is
not a translation, it is a silent fork of one.
