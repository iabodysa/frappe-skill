# What a backup carries, and what a restore cannot bring back

A backup run writes FOUR files and `bench restore` reads ONE of them; only `--with-files` adds the
two `files` folders. Plan a restore as THREE acts — load the dump, hand the archives back with their
flags, then carry `encryption_key` across by hand — because a site that skips the third act starts,
serves pages, and throws on the first read of a stored password.

| File a run writes | What it holds | Who reads it back |
|---|---|---|
| the database dump | every table, `__Auth` included, always gzipped | `bench restore`, as its one argument |
| the public files archive | the public `files` folder only | `bench restore --with-public-files` |
| the private files archive | the private `files` folder only | `bench restore --with-private-files` |
| the site config copy | `encryption_key`, and the rest of `site_config.json` | nothing — you carry it by hand |

The `.enc` suffix is a name rather than a fact; `--compress` touches the archives and never the
dump; and every run deletes everything older than a day in the backup folder before it starts.

## Settled by

| what it settles | leaf |
|---|---|
| what a default run dumps, what it deletes first, and what it omits | `knowledge/bench/backup.md` |
| where `encryption_key` lives and what reads it | `knowledge/bench/config.md` |
| the site a restore is loaded into | `knowledge/bench/new-site.md` |
| the one sql file it reads, and the exit before it touches the site | `knowledge/bench/restore.md` |
