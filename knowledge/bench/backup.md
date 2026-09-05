---
name: backup
description: A default backup dumps every table including __Auth, deletes everything older than a day in the backup folder before it starts, and carries neither the site config nor the key that decrypts what it holds.
triggers: ["BackupGenerator", "setup_backup_tables", "set_backup_file_name", "backup_encryption", "get_recent_backup", "backup_files", "copy_site_config", "take_dump", "delete_temp_backups", "get_or_generate_backup_encryption_key", "get_backup_encryption_key", "decrypt_backup", "fetch_latest_backups", "new_backup", "scheduled_backup", "base_tables", "BACKUP_ENCRYPTION_CONFIG_KEY", "get_command", "restore", "_restore", "restore_backup", "partial_restore", "is_partial", "extract_files", "execute_in_shell", "gzip not found in PATH! This is required to take a backup.", "what does bench backup include", "restore a site backup", "the dump file we shared has everyone's passwords in it", "is it safe to hand a database dump to an outside developer", "the backup includes tables i did not expect it to include", "my exported file disappeared from the backup folder overnight", "something deleted yesterday's backup and now there is nothing to restore", "why do old files vanish from the backup directory on their own", "nobody can log in after we restored the database", "all the users lost their passwords after the restore", "why are stored passwords unreadable on the restored copy", "the file says it is encrypted but it opens as plain text", "attachments are missing after restoring even though the records are there", "the restore finished fine but half the system is empty"]
product: frappe
---

# Backup

## paths

frappe/utils/backups.py — BackupGenerator, setup_backup_tables, set_backup_file_name, backup_encryption, get_recent_backup, backup_files, copy_site_config, take_dump, delete_temp_backups, get_or_generate_backup_encryption_key, get_backup_encryption_key, decrypt_backup, fetch_latest_backups, new_backup, scheduled_backup, base_tables, BACKUP_ENCRYPTION_CONFIG_KEY
frappe/database/__init__.py — get_command
frappe/commands/site.py — backup, restore, _restore, restore_backup, partial_restore
frappe/installer.py — is_partial, extract_files
frappe/utils/__init__.py — execute_in_shell

## rules

MUST read __Auth as INSIDE a default dump. With no --include, no --exclude and no backup key in site_config.json both lists stay empty, get_command appends the database name alone, and every password hash and Fernet-encrypted secret on the site is in the file.
NEVER hand a default .sql.gz to anyone who is not allowed the site's passwords.
MUST expect `bench backup --include` to produce a dump with no __Auth, __global_search and __UserSettings. base_tables is appended to the site-config include list only, never to the CLI one, so a partial restore of that file leaves every restored user without a password.
MUST list the doctypes under backup.includes in site_config.json when the partial file has to carry credentials; -i and --only are the same option as --include.
MUST set backup.excludes in site_config.json to drop a table from every scheduled backup; a CLI --exclude reaches the one command that carries it, and the site-config branch is read only when both CLI lists are empty.
NEVER store anything meant to survive in the site's private/backups. new_backup calls delete_temp_backups first, and that function lists the whole directory with no name pattern and no extension test, so an export or a hand-copied dump is removed once it is a day old — and the deletion runs before the dump, so a backup that then fails has already removed yesterday's file.
MUST set keep_backups_for_hours in site_config.json to change that window; there is no CLI flag and no per-run override.
MUST run `file <path>` and read AES in the output before treating a -enc file as encrypted. The suffix comes from the encrypt_backup checkbox in System Settings at naming time, and a gpg failure is caught, printed and swallowed while the file keeps the name and the command still exits 0.
MUST store the site_config_backup json where the encrypted dump may not go. backup_encryption encrypts the database dump and the two file archives only, so that file stays plaintext JSON carrying db_password, encryption_key and backup_encryption_key.
NEVER read the CLI's encryption reminder as proof a key exists; it tests encryption_key while backup_encryption uses backup_encryption_key, so it stays silent on a site that has only the backup key.
MUST treat the backup passphrase as exposed twice. get_or_generate_backup_encryption_key mints it into site_config.json on the first encrypted backup with nobody asked and nobody shown, and the same value is formatted into a shell string that execute_in_shell runs with shell=True, so it is an argument in the process table for as long as gpg runs.
MUST copy encryption_key from the source site's site_config_backup json into the target site_config.json BEFORE the first read of a stored password; the dump carries __Auth encrypted with the source site's key and get_encryption_key generates a fresh one into a site missing it.
MUST pass --with-files on any backup taken before a destructive change. backup_files tars public/files and private/files and joins "files" to each, so private/backups, logs, locks, error-snapshots and site_config.json are in no archive, and a file attached to a record is a tabFile row plus bytes on disk while the dump carries only the row.
MUST pass --with-public-files and --with-private-files to bench restore; the restore never looks for the archives beside the dump.
NEVER expect fetch_latest_backups or the Download Backups page to list an archive taken with --compress. get_recent_backup globs for .tar and never for .tgz, and the caller reads None as "no backup exists"; a -partial file is invisible to the same glob unless partial=True is passed.
NEVER gzip a .sql.gz a second time before restoring. take_dump always gzips and no flag turns it off, and restore detects the type with `file`.
MUST install every app the dump's tabInstalled Application rows name, at the version those rows name, before bench migrate; the dump records the frappe version and branch as two header lines and nothing more, and a restore into a bench missing an app leaves orphan tables.
MUST re-enqueue anything that was in flight after a restore. No backup step reads Redis, so a queued job, a scheduled-job lock, a rate-limit counter and the cache are gone.

## values

always dumped: every table, including __Auth
base_tables: __Auth, __global_search, __UserSettings, appended to backup.includes only
four files: <stamp>-<site>-database.sql.gz, -site_config_backup.json, -files.tar, -private-files.tar
--compress: changes the two file archives to .tgz and nothing else
encrypted paths: the database dump, the public files archive, the private files archive
never in any archive: common_site_config.json, private/backups, logs, locks, error-snapshots, Redis
delete window: keep_backups_for_hours, default 24
partial marker: `-partial` in the database file name, and bench restore refuses it and points at bench partial-restore

## how

Ask what a backup does NOT hold, because that is where restores fail. It holds tables and two files
folders. It does not hold the code, the bench-wide config, the key that makes the credentials in it
readable, or anything Redis was holding. Every one of those is a separate step a human has to take, and
none of them raises when skipped — the restore succeeds and the failure shows up at the first password
read or the first missing app.

Read every encryption signal as a name rather than a result. The -enc suffix is written before gpg
runs, the reminder tests a different key from the one used, and a gpg failure prints and continues. The
only test that answers the question is running `file` on the path, which is what the restore itself
does.

The backup folder is scratch space with a timer. Anything put there by hand is deleted by the next
backup once it is old enough, and the deletion happens before the dump, so a failed run still consumed
yesterday's file. Copy a backup somewhere else the moment it is taken.

A partial backup and a partial restore are their own pair of commands, and the CLI include list drops
exactly the tables that make a restored user able to log in. Where a partial file has to be usable, the
include list belongs in site_config.json, not on the command line.
