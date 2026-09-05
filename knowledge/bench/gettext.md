---
name: gettext
description: A PO file is compiled to an MO under sites/assets/locale only when the MO is missing or older than the PO by mtime, so an MO whose timestamp runs ahead of its PO is never rewritten and no error says so.
triggers: ["get_po_dir", "get_po_path", "get_pot_path", "get_mo_path", "get_locale_dir", "compile_translations", "_compile_translation", "write_binary", "get_translations_from_mo", "generate_pot", "update_po", "new_po", "migrate", "build", "po file to mo file", "translation mo file not updating", "i edited the translation file and the site still shows the old wording", "why does the build say the translation is already up to date when i just changed it", "raging that my translation edits never reach the running site", "translations stopped updating after we restored a backup", "after pulling the code again the translations froze at an older version", "the new wording shows on my machine but not on the server", "how do i force the translations to be rebuilt from scratch", "no error appears but the translated text never changes", "the language with a region code seems to be ignored entirely", "a whole language file looks like it is not being read and nothing complains"]
product: frappe
---

# PO, POT and MO files

## paths

frappe/gettext/translate.py — get_po_dir, get_po_path, get_pot_path, get_mo_path, get_locale_dir, compile_translations, _compile_translation, write_binary, get_translations_from_mo, generate_pot, update_po, new_po, migrate
frappe/commands/gettext.py — compile_translations
frappe/commands/utils.py — build

## rules

MUST pass `--force` to `bench compile-po-to-mo` or to `bench build` after touching a PO file whose MO could be newer, because `_compile_translation` compares mtime and never content.
NEVER read "MO file already up to date" as proof the MO matches the PO.
MUST recompile after any step that writes an MO after its PO — a restore, a `git checkout`, a copy in a deploy — because that step is what puts the MO ahead.
NEVER expect a missing MO to raise; `get_translations_from_mo` returns an empty dict when `gettext.find` locates nothing.
MUST spell a dialect with a dash in Frappe and expect an underscore on disk; `get_translations_from_mo` replaces the dash before it searches.

## values

po: `<app>/locale/<locale>.po`
pot: `<app>/locale/main.pot`
mo: `sites/assets/locale/<locale>/LC_MESSAGES/<app>.mo`
skip condition: the MO exists, the PO mtime is lower than the MO mtime, and `force` is false
skip message: `MO file already up to date at <path>`
write message: `MO file created at <path>`
compile fan-out: `multiprocessing.Pool(processes=4)` over app and locale
locale separator: dash in Frappe, underscore in the file name

## how

The PO file lives inside the app and the MO lives in the bench's shared assets, so the two are not
moved by the same operations. Every judgement about whether the MO is current is one mtime against
another, taken at compile time; nothing at read time checks that the MO came from the PO beside it.
That makes the failure one-directional and permanent — once the MO leads, every later compile skips
it, and only `force` breaks the cycle.

Ask of a translation that changed in the PO and did not change in the app: did the compile print
"MO file created" for that app and locale, or "already up to date"? The two lines are the whole
verdict.

`generate_pot` extracts sources into the POT, `update_po` folds POT keys into each PO, and
`compile_translations` turns each PO into an MO. Only the last step feeds a running site; the first
two change files a developer edits.
