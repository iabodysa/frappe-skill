---
name: credential-storage
description: A Password field moves the value into __Auth on save and leaves a mask of asterisks in the row, so reading the field directly returns the mask and frappe.db.set_value writes the secret in clear text.
triggers: ["BaseDocument._save_passwords", "get_password", "is_dummy_password", "get_decrypted_password", "set_encrypted_password", "remove_encrypted_password", "encrypt", "decrypt", "get_encryption_key", "Database.set_value", "set_single_value", "Please check the value of", "Most probably your password is too long.", "Encryption key is in invalid format!", "how does frappe store passwords", "password field encryption", "the password field just shows a row of stars when i read it", "reading the secret back gives me asterisks instead of the real value", "why does my api key come back as stars in code", "the check that the key is filled passes even though it is garbage", "our secret is sitting in the database in plain text for anyone to read", "the api key is visible in the table and i never put it there", "how did the password end up unencrypted in the database", "everything works fine but i think the secret is stored wrong", "after restoring a copy of the site every secret fails to decrypt", "moved the site to a new server and now all the passwords are broken", "why did all our stored keys stop working after the restore", "i cleared the field but the old secret is still there", "deleting the credential does not actually remove it", "the integration library errors instead of telling me the key is missing"]
product: frappe
---

# Credential storage

## paths

frappe/model/base_document.py — BaseDocument._save_passwords, get_password, is_dummy_password
frappe/utils/password.py — get_decrypted_password, set_encrypted_password, remove_encrypted_password, encrypt, decrypt, get_encryption_key
frappe/database/database.py — Database.set_value, set_single_value

## rules

MUST declare a credential as `fieldtype: "Password"` and read it back with `doc.get_password(fieldname)`; reading the field directly returns the mask, because the save replaced the value with one asterisk per character.
NEVER test a credential with an equality check against the field; `is_dummy_password` is what tells a mask from a value, and the mask is truthy, so a truth test only catches a field that was never filled.
MUST set a Password field through the document and `save()`; `frappe.db.set_value` and `frappe.db.set_single_value` run one UPDATE, call no document event, and leave `__Auth` empty while the column holds the secret in clear text.
NEVER read a working integration as proof the secret is stored correctly; `get_password` returns the column value whenever it is not a mask, so a clear-text write reads back fine and shows the secret to anyone with read permission on the DocType.
MUST carry `encryption_key` from `site_config.json` alongside the database; `get_encryption_key` generates and writes a NEW key when the setting is missing, so the site starts in silence and every `get_password` then throws `Failed to decrypt key`.
MUST clear the field to delete a secret; an empty value calls `remove_encrypted_password`, and nothing else removes the `__Auth` row.
MUST read `raise_exception=False` as turning a missing or undecryptable secret into `None`; the failure then appears inside the provider's library rather than in frappe.
MUST pass the fieldname the DocType actually declares; `get_password` on an unknown fieldname finds no row and, with `raise_exception=False`, returns `None` without a word.
MUST set `flags.ignore_save_passwords` to a list of fieldnames, or to `True`, to skip the move; `True` skips every Password field on the document.

## values

table: `__Auth`, keyed by doctype, name and fieldname, with `encrypted = 1`
cipher: Fernet, under the site's `encryption_key`
mask: one asterisk per character of the original
mask test: every character of the value is `*`
missing key behaviour: a new key is generated and written into site config
read failure message: `Failed to decrypt key <doctype>.<name>.<fieldname>`
missing row message, raising: `Password not found for <doctype> <name> <fieldname>`
too long: `Most probably your password is too long.`

## how

A Password field is not a column that holds a secret; it is a column that holds a placeholder while the secret lives in one shared table under one site-wide key. Everything surprising follows from that split. The value you read off the document is the placeholder. The value survives only where the save path ran. And the whole set of secrets on the site is readable exactly while one key in site config is intact.

That is why `frappe.db.set_value` is the call to watch: it is the ordinary way to write one field and it is the one way that skips the split. The column then holds the real secret, `__Auth` holds nothing, and no read ever complains — `get_password` hands back the column when it is not a mask. Nothing about a working integration distinguishes the two storage states, so the state has to be asked directly rather than inferred.

The other quiet failure is the key. A restore without `encryption_key` does not refuse to start; it mints a new key and carries on, and the first symptom is a decrypt failure on an unrelated screen weeks later. Treat the key as part of the database, not part of the configuration.
