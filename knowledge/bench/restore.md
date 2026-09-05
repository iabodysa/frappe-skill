---
name: restore
description: bench restore reads the one sql file it was given and nothing beside it, takes the two file archives only as paths passed to --with-public-files and --with-private-files, and exits 1 without touching the site when any of those three paths cannot be found.
triggers: ["restore", "_restore", "restore_backup", "partial_restore", "get_bench_relative_path", "extract_files", "is_partial", "is_downgrade", "validate_database_sql", "_new_site", "filelock", "decrypt_backup", "get_or_generate_backup_encryption_key", "with-public-files", "with-private-files", "encryption-key", "File {0} not found.", "Failed to detect type of backup file", "Decryption failed. Please provide a valid key and try again.", "Partial Backup file detected. You cannot use a partial file to restore a Frappe site.", "Table `__Auth` not found in file.", "Invalid path", "bench restore files", "restore site from backup", "the restore says it cannot find the file even though it is right there", "why did my attachments not come back after restoring", "restoring wiped the site data and then failed halfway", "how do i bring back the uploaded files along with the database", "it asks for a key and then says decryption failed", "restore refuses saying the file is only part of a backup", "it keeps asking me to confirm going back to an older version", "restore finished but the site is missing half its features", "two restores at once and the second one just died", "i pointed it at the wrong archive and now the database is gone", "does restoring bring back the site settings file too", "the restore crashed and i do not know if the old data is still there"]
product: frappe
---

# Restore

## paths

frappe/commands/site.py — restore, _restore, restore_backup, partial_restore
frappe/installer.py — extract_files, is_partial, is_downgrade, validate_database_sql, _new_site, get_old_backup_version
frappe/utils/__init__.py — get_bench_relative_path, execute_in_shell
frappe/utils/backups.py — decrypt_backup, get_or_generate_backup_encryption_key
frappe/utils/synchronization.py — filelock

## rules

MUST pass the database dump as the one argument; `_restore` reads that path alone and looks for no companion file, so the two files archives and the site_config_backup json are ignored unless a flag names them.
MUST expect a path that does not exist to be retried against `<site>/private/backups` and against the bench parent `..`, in that order, and to end in exit 1 with `File {path} not found.` when neither holds it.
MUST pass each files archive as a path rather than as a switch; `--with-public-files` and `--with-private-files` each take the tar file's path, and a wrong or missing path ends the run at exit 1 with `Invalid path` after the database has already been replaced.
MUST take the backup again or restore the files by hand when that happens, because the database restore has committed by the time `extract_files` runs and nothing rolls it back.
NEVER pass `--db-name` expecting it to be used; the option is declared on the command and is not forwarded to `_restore`, and `restore_backup` reads `frappe.conf.db_name` from the target site's own config.
MUST pass `--encryption-key` once for the dump and the archives together; the same value decrypts all three, and without it an AES dump falls back to `get_or_generate_backup_encryption_key`, which MINTS a key into site_config.json when the site has none and then fails to decrypt with it.
MUST read `Decryption failed. Please provide a valid key and try again.` as exit 1 before the database was touched.
MUST expect the restore to DROP and recreate the site database; `restore_backup` calls `_new_site` with force set, so the target site's current data is gone whether or not the dump loads.
MUST run `bench partial-restore` for a file whose name carries `-partial`; `is_partial` ends `bench restore` at exit 1 and prints the other command.
MUST answer the downgrade prompt or pass `--force`; `is_downgrade` compares the dump's recorded frappe version against the running one and `click.confirm` aborts the command when the answer is no.
MUST read `--force` as also disarming `validate_database_sql`, so an empty file and a dump with no `__Auth` table are printed and restored instead of refused.
NEVER run two restores of one site at once; `filelock("site_restore", timeout=1)` gives the second one second to acquire the lock and then fails it.
MUST pass `--install-app` for every app the dump's tables need, because `_new_site` installs only frappe and the apps that flag names.
MUST expect the tar to be extracted with `--strip 2` into the site directory after a copy of it is made there, and the copy to be removed on success only.

## values

argument: the database dump path, positional and required
search order for a missing dump: the given path, `<site>/private/backups/<path>`, `../<path>`
type detection: `file <path>` through execute_in_shell, and `AES` in its output means encrypted
two file flags: --with-public-files <tar path>, --with-private-files <tar path>
exit 1 paths: dump not found, `file` failed, decryption failed, partial dump, archive path invalid, _new_site raised
--force disables: the downgrade confirmation and the raise inside validate_database_sql
never restored by this command: site_config.json, the encryption_key inside it, Redis, the apps themselves
lock: site_restore, timeout 1 second

## how

The command has one input and two optional ones, and they fail at opposite ends of the run. The dump
is checked before anything is destroyed — not found, not readable, partial, undecryptable and empty
all exit 1 with the site untouched. The two archives are handled after the database is replaced,
and their only validation is that the path resolves, so a typo there leaves a restored database beside
the old files and an exit 1.

Order the flags accordingly: get the dump path right and the run is safe to repeat; get an archive
path wrong and the repeat is another full database restore.

The site the dump lands in is decided by the site's own config, not by the command. `--db-name` is
accepted and dropped, and the database named in site_config.json is dropped and rebuilt. Restoring
into the wrong site is therefore a one-word mistake with no confirmation attached to it.
