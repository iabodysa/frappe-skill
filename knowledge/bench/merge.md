---
name: merge
description: Five sources are merged into one dict per language in a fixed order, country names are applied last and win every collision, and the three highest sit inside one suppress(Exception) that drops all of them together.
triggers: ["get_all_translations", "get_translations_from_apps", "get_user_translations", "get_parent_language", "clear_cache", "MERGED_TRANSLATION_KEY", "USER_TRANSLATION_KEY", "get_translated_countries", "Translation", "clear_user_translation_cache", "how are translations merged", "country names override translation", "the country name will not translate no matter what i add", "i translated the country and it keeps coming back in english", "why does my translation for a country get ignored every time", "suddenly the whole page is english again but some words still translate", "translations disappeared for everything except the ones shipped with the app", "why did all the custom translations stop working at once", "i changed a translation and the site still shows the old one", "how long until a new translation actually shows up on the site", "the translation only appears after i restart or clear something", "my dialect translations are being replaced by the main language ones", "which translation wins when two of them define the same text"]
product: frappe
---

# Merging the translation sources

## paths

frappe/translate.py — get_all_translations, get_translations_from_apps, get_user_translations, get_parent_language, clear_cache, MERGED_TRANSLATION_KEY, USER_TRANSLATION_KEY
frappe/geo/country_info.py — get_translated_countries
frappe/core/doctype/translation/translation.py — Translation, clear_user_translation_cache

## rules

NEVER add a `Translation` row for a country name; `get_translated_countries` runs last and overwrites it on every rebuild.
MUST expect a failure in the parent-language `Translation` read to cost the child-language rows and the country names too, because one `with suppress(Exception)` covers all three.
MUST read an all-English page whose CSV strings still translate as that suppressed block having raised.
MUST clear the cache after writing a translation outside the `Translation` doctype; only its `on_update` and `on_trash` delete the two keys for that language.
NEVER expect `get_all_translations` to raise outside a test; it logs "Unable to load translations" and returns an empty dict.
MUST write a dialect's own rows against the dialect code, since the parent language is loaded first and the dialect overwrites it.

## values

order, lowest first: parent-language app CSV and MO, dialect app CSV and MO, parent-language `Translation` rows, dialect `Translation` rows, `get_translated_countries`
suppressed together: the last three
cache key, merged: `merged_translations`, one field per language
cache key, user rows: `lang_user_translations`, one field per language
`clear_cache` deletes: `bootinfo`, `lang_user_translations`, `merged_translations`
per app order inside a language: CSV first, MO second

## how

The merged dict is built by assignment and `.update()`, so precedence is nothing but position — the
later source wins the key, and there is no override, no priority field, and no way for a lower source
to hold a key against a higher one. The country names sit at the end, which makes them the one
set of strings a site cannot change through the `Translation` doctype.

Ask of a wrong translation: which of the five sources holds that key last? Ask of a missing one:
whether the source that holds it is above or below the `suppress`, because everything under it fails as
a group and leaves only the app files behind.

The result is cached per language, so a change to any source is invisible until the two cache keys are
deleted. The `Translation` doctype deletes them for its own language on save and on delete; every other
writer has to call `clear_cache` itself.
