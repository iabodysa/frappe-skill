---
name: lookup
description: A string wrapped in `_()` still shows in English when the extractor never saw it as a literal, or when it did and the merged translation cache in Redis was never told to forget the old value.
triggers: ["arabic text not translated", "arabic string not translated", "text not translated", "translation not showing", "translation not working", "wrapped in gettext and still english", "_() does nothing", "marked the string for translation and it still shows english", "added an arabic translation and the ui still shows english", "translated csv row exists but the page shows the source text", "edited the po file and the site still shows the old text", "why does the extractor skip this string", "template literal never gets translated", "f-string never gets translated", "string built from concatenation never picked up for translation", "frappe._messages", "get_all_translations", "merged_translations cache", "TRANSLATE_PATTERN", "is_translatable", "translation only updates after a hard reload", "translation only updates after bench build", "user translation from desk works but csv edit does not", "Translation doctype saves instantly but the csv file does not"]
product: frappe
---

# Translation lookup

## paths

frappe/gettext/extractors/utils.py — TRANSLATE_PATTERN, extract_messages_from_code, is_translatable
frappe/gettext/extractors/python.py — extract
frappe/translate.py — get_all_translations, get_translations_from_apps, get_translations_from_csv, get_user_translations, clear_cache, MERGED_TRANSLATION_KEY, USER_TRANSLATION_KEY
frappe/__init__.py — non_translated_string
frappe/boot.py — get_bootinfo, __messages
frappe/public/js/frappe/translate.js — _messages
frappe/public/js/frappe/request.js — __messages
frappe/core/doctype/translation/translation.py — on_update, on_trash, clear_user_translation_cache
frappe/utils/redis_wrapper.py — hget, hdel

## rules

MUST write the argument to `_()` as a literal quoted string; the Python extractor wraps babel's
tokenizer and the JS/HTML extractor matches `TRANSLATE_PATTERN`, and both read source text, never a
runtime value, so an f-string, a `+` concatenation or a plain variable produces no message and the
string never reaches a POT, a PO or a CSV.
NEVER wrap the string in backticks; `TRANSLATE_PATTERN`'s quote group is `["']{,3}` and never matches
a backtick, so a JS template literal inside `_()` is invisible to extraction even though it reads like
a normal string.
MUST expect `is_translatable` to drop a string with no letter in it, one starting with `fa fa-`, one
ending in `px`, and one starting with `eval:`, regardless of what `_()` wraps it in.
MUST run `bench build`, `bench migrate` or `bench clear-cache` after editing a translation CSV or a PO
file by hand; none of those files is re-read once `get_all_translations` has already cached the merged
result for that language, and only those commands (or a call to `frappe.translate.clear_cache()`) drop
the cached value.
MUST expect a Translation doctype record saved or deleted from Desk to appear without any of the
above; `Translation.on_update` and `on_trash` call `clear_user_translation_cache`, which deletes that
one language's field from both the `lang_user_translations` and `merged_translations` Redis hashes on
save.
NEVER treat "I edited the CSV/PO by hand" and "I saved a Translation record from Desk" as the same
case; only the file edit needs a manual cache clear.
MUST expect the client to hold a second, separate copy in `frappe._messages`, filled once from
`bootinfo.__messages` at page load and merged again from `data.__messages` on every ajax response; a
worker whose Redis cache was cleared still shows old text in a tab that has not reloaded, because nothing
pushes the new dict to an open page.
NEVER expect a missing key to raise: `frappe._()` on the client returns the original text when
`frappe._messages[key]` is undefined, and `_()` on the server returns `non_translated_string` when
`get_all_translations(lang)` has no entry for it; both fail silently to the English source with no
error and no log line.

## values

extractable: a literal quoted string passed directly to `_()`
excluded regardless: no letter, `fa fa-` prefix, `px` suffix, `eval:` prefix
merge order: `get_all_translations` layers app CSV, then app MO, then parent-language result, then
`Translation` doctype rows, per language
server cache: Redis hash `merged_translations`, field = language
user-translation cache: Redis hash `lang_user_translations`, field = language
client cache: `frappe._messages`, seeded from `bootinfo.__messages`, extended from `data.__messages`
auto-invalidated: a `Translation` doctype record saved or deleted from Desk
NOT auto-invalidated: a CSV row or a PO/MO file edited on disk
manual invalidation: `bench build`, `bench migrate`, `bench clear-cache`, `frappe.translate.clear_cache()`

## how

A string a developer marks for translation has to survive two separate gates before Arabic ever
reaches the screen. The first gate is extraction: `_()` is not special syntax, so both extractors read
plain source text for a literal string next to the call and skip anything assembled at runtime — an
f-string, a concatenation, a template literal. A string that fails this gate never reaches a CSV or a
PO file, and the Translation Tool in Desk has nothing to show for it because nothing put it there.

The second gate is the merged cache. `get_all_translations` is expensive enough that its result is
kept in a Redis hash keyed by language, and every later `_()` call in that process reads the hash
instead of the files. Nothing in the file-reading path watches the CSV or the PO/MO for changes, so a
hand edit to either is invisible until something calls `clear_cache()` — a `bench build`, a `migrate`,
or `clear-cache` itself. The `Translation` doctype takes a different path: its own `on_update` and
`on_trash` hooks delete only that language's field from the same hash, so a change made through Desk
looks instant next to a file edit that looks broken, though both are reading the same cache.

Ask, in order: is the string a literal next to `_()`, or built at runtime? Is it long enough to carry
a letter, and does it avoid `fa fa-`, `px` and `eval:`? If both hold, was the change a Desk save (self
-clearing) or a file edit (needs `bench build`/`migrate`/`clear-cache`)? Only after the cache holds the
right value does the client's own copy in `frappe._messages` need a reload to catch up.
