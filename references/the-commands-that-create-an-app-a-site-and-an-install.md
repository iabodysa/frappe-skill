# The commands that create an app, a site and an install

The seven split into two families that never touch each other: `new-app`, `get-app` and `remove-app`
write the bench and no site database, `install-app` and `uninstall-app` write ONE site's database and
nothing on disk, and `new-site` and `drop-site` write both. So an app that exists and imports is
absent from every Desk until the install command is typed.

| Command | What it writes | What undoes it | What it leaves behind |
|---|---|---|---|
| `bench new-app` | a directory under `apps/`, an editable install, the two registries | `bench remove-app` | nothing on any site |
| `bench get-app` | a clone, then the same editable install | `bench remove-app` | nothing on any site |
| `bench new-site` | the database, its MariaDB user, and `site_config.json` | `bench drop-site` | a repeated run keeps the first `site_config.json` and its password |
| `bench install-app` | one site's database, and `installed_apps` before any hook runs | `bench uninstall-app` | the app recorded installed even when a hook then failed |
| `bench uninstall-app` | one site's database | re-installing | every Role, Custom DocPerm row and profile the app created |
| `bench drop-site` | an archive of the site directory | restoring the archive by hand | the database user, unless dropped as well |
| `bench remove-app` | the bench only | `bench get-app` | every row the app ever wrote on every site |

`db_name` names the database, the MariaDB user and the grantee at once, so `--force` drops whatever
already answers to it.

## Settled by

| what it settles | leaf |
|---|---|
| `db_name` as three names, `--force`, and the kept config | `knowledge/bench/new-site.md` |
| the registry write ahead of the hooks, and the uninstall cleanup | `knowledge/bench/install-app.md` |
| the generators that rewrite the common config | `knowledge/bench/setup.md` |
| the merge order behind every value a command reads | `knowledge/bench/config.md` |
| what `--site all` reaches and what it does not | `knowledge/bench/site-commands.md` |
| the bare whitelisted call that returns ok on a site already set up | `knowledge/desk/setup-wizard.md` |
