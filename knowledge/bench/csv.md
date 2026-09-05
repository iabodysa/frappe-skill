---
name: csv
description: An app's translation CSV is read into a plain dict in file order, so the last row for a key wins, and a row that is neither two nor three columns is written to the Error Log and skipped.
triggers: ["get_translations_from_csv", "get_translation_dict_from_file", "read_csv_file", "update_csv_from_po", "csv_to_po", "translation csv file format", "app csv duplicate key", "some rows in my translation file load and some just do not", "why are half the lines in my translation file ignored", "i added a line to the translation file and nothing happened on the site", "a translation i wrote earlier got replaced by a later line with the same text", "the same english text appears twice in my file and only one of them wins", "the file is inside the app but the site loads no translations from it at all", "where exactly do i put the translation file so it gets picked up", "a broken line in my translation file is skipped without telling me", "how do i put a line break inside a translated text", "one translation keeps overwriting another and there is no error anywhere"]
product: frappe
---

# Translation CSV

## paths

frappe/translate.py — get_translations_from_csv, get_translation_dict_from_file, read_csv_file
frappe/gettext/translate.py — update_csv_from_po, csv_to_po

## rules

MUST place the file at `<app>/translations/<lang>.csv`, because `get_translations_from_csv` joins that path and returns an empty dict when it does not exist.
MUST write two columns for a source without context and three for a source with one.
NEVER write two rows carrying the same key, because `translation_map[key] = ...` keeps the last one and drops the earlier with no error and no Error Log entry.
NEVER read the absence of an Error Log entry as proof that every row loaded.
MUST write `\n` in a cell where the source string carries a newline, because only columns one and two are unescaped.
MUST pass `throw=True` to `get_translation_dict_from_file` when a bad row has to stop the caller; `get_translations_from_csv` leaves it `False`.

## values

path: `<app>/translations/<lang>.csv`
columns: source, translated, context
key with context: `source:context`
key without context: `source`
collision: last row in file order wins
row of any other width: `frappe.log_error` titled "Error in translation file", then skipped
whitespace: `strip` is applied to the translated cell only

## how

The reader is a loop over rows with no key set and no duplicate check, so a CSV is a list that happens
to be read as a mapping. Two rows that mean different things collide the moment they produce the same
key, and the file gives no sign of it — the count of rows and the count of loaded keys are never
compared.

Ask of a translation that will not appear: is the key the row builds the key `_()` looks up? A three
column row whose third cell is empty does not build a context key at all; it takes the two column
branch and lands on the bare source, on top of whatever the bare source already held.

The CSV is the older of the two file formats. `csv_to_po` and `update_csv_from_po` move strings
between it and the PO file, and both formats load on every request, so a string can be present in one
and absent from the other without anything failing.
