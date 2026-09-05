---
name: context
description: Context is not a field in the loaded dict but part of the key — every source stores a contextual string under `source:context`, and `_()` tries that key first and the bare source second.
triggers: ["get_translation_dict_from_file", "get_user_translations", "get_translations_from_mo", "Translation", "Cannot make dict for single fieldname", "translation context key", "_() with context argument", "the same word is translated on one screen but stays english on another", "my translation shows up in one place and not the other and i cannot see why", "why does one english word need two different translations in different screens", "the translation file has the text but the page still shows english", "i added the translation and nothing changed on the page", "how do i give one english word two meanings in another language", "adding a note beside a string made the translation stop working", "my translation with a note only works on some buttons", "why is the text translated only when i remove the extra note column", "translating one word broke the other place the same word is used"]
product: frappe
---

# Translation context

## paths

frappe/__init__.py — _
frappe/translate.py — get_translation_dict_from_file, get_user_translations
frappe/gettext/translate.py — get_translations_from_mo
frappe/core/doctype/translation/translation.py — Translation

## rules

MUST pass the same context string to `_()` that the source row carries, because the key is built by concatenation and any difference makes a different key.
NEVER expect a contextual translation to serve a call without context; the MO reader writes only the `source:context` key even though its docstring says otherwise.
MUST fill the third CSV column, the PO `msgctxt` or the `Translation` context field to give a string a context; there is no other route.
NEVER leave the third CSV column empty on a row meant to carry a context — the row falls to the bare source key and overwrites the context-free translation.
MUST expect a call with a context to fall back to the context-free translation when the contextual key is absent.

## values

key with context: `source:context`
key without context: `source`
separator: a single colon, no escaping
CSV: third column
PO and MO: `msgctxt`, decoded from bytes before the key is built
`Translation` doctype: the `context` field
`_()` lookup order: `source:context`, then `source`, then the untranslated string

## how

Context exists to let one English word carry two translations. It is carried in the key rather than
beside the value, so every source has to spell it the same way and a colon inside a source string is
indistinguishable from the separator.

Ask of a string that translates in one place and not another: do the two call sites pass the same
context? A call with no context can never reach a key that has one, and the fallback runs only in the
other direction.

The docstring on the MO reader describes a fallback that the code does not perform, so a PO file that
only ever declares `msgctxt` leaves every context-free call untranslated. Declare the string twice
where both call shapes exist.
