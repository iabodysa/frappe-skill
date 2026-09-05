---
name: new-site
description: db_name is the name of the database, the MariaDB user and the grantee at once, --force drops whatever already answers to it, and a repeated new-site keeps the first run's site_config.json including its password.
triggers: ["make_conf", "make_site_config", "get_conf_params", "install_db", "setup_database", "get_root_connection", "drop_user_and_database", "bootstrap_database", "DbManager.create_user", "create_database", "grant_all_privileges", "delete_user", "drop_database", "flush_privileges", "new_site", "bench new-site database name", "create a new site", "creating a new site wiped out an existing database", "i lost a whole site because i forced the creation of a new one", "does creating a site with the same name destroy the old data", "it refuses to create the site saying the database already exists", "why does site creation stop and complain the name is taken", "i retried creating the site and now it cannot log into the database", "access denied for the database user after a failed site creation and retry", "the second attempt at creating the site uses the wrong password", "it never asked me for the root password when creating a site", "the database password is sitting in a config file in plain text", "i renamed the database in the config and everything broke"]
product: frappe
---

# New site

## paths

frappe/installer.py — make_conf, make_site_config, get_conf_params, install_db
frappe/database/mariadb/setup_db.py — setup_database, get_root_connection, drop_user_and_database, bootstrap_database
frappe/database/db_manager.py — DbManager.create_user, create_database, grant_all_privileges, delete_user, drop_database, flush_privileges
frappe/commands/site.py — new_site

## rules

MUST read db_name as the name of THREE things — the database, the MariaDB user and the grantee. setup_database creates the user under db_name, creates the database under db_name and grants db_name to db_name, so renaming one of them in site_config.json orphans the other two.
NEVER pass --force to new-site on a bench whose databases you have not listed. force short-circuits the existence test, so delete_user and drop_database run against the name already in use with no confirmation and no backup.
MUST expect `Database <db_name> already exists` from setup_database and treat it as the refusal that protected the existing site; without force the site is not created.
MUST delete the site directory before repeating new-site after a failure. make_site_config writes site_config.json only when the file is ABSENT, so the second run keeps the first run's db_password while setup_database creates the user with the password it reads from that same file.
MUST read root_password out of sites/common_site_config.json before assuming new-site will prompt. get_root_connection consults frappe.flags.root_password, then that key, and only then calls getpass — so a root password left in the common config hands the database superuser to every site creation and every drop_user_and_database on the bench without a line of output.
MUST expect the root connection to be cached on frappe.local.flags.root_connection and returned unchanged on every later call; a change to the file mid-process is not picked up.
MUST read mariadb_user_host_login_scope as reaching delete_user, create_user and grant_all_privileges only. It never reaches drop_database or create_database, so the host scope narrows who may connect and never what exists.
MUST treat site_config.json as a plaintext credential file. get_conf_params returns a random_string of 16 as db_password when the caller passes none, so an operator who never typed a database password still has one and it is written there in clear.
NEVER set a value on frappe.local.conf before make_conf and expect it to survive; make_conf calls frappe.destroy then frappe.init, and the freshly written file is what the rest of the command reads.

## values

named after db_name: the database, the MariaDB user, the grantee
generated password: random_string(16), written to site_config.json
root password order: frappe.flags.root_password, frappe.conf.root_password, the `MySQL root password:` prompt
root connection: cur_db_name None, so one connection can drop one database and create another
force: skips the existence test only, and the branch it enters deletes the user and drops the database

## how

Ask what a name owns before renaming it. The framework spends one identifier on three objects here, so
a value that looks like a database name is also an account and a grant, and the three drift apart the
moment one is edited by hand.

Read new-site as not idempotent in the direction people assume. Re-running it does not rebuild the
site from scratch: the config file survives and the database does not, so the second run reuses the
first run's secret against a database it just destroyed. The recovery is to remove the site directory,
not to add force.

Treat a root password in the common config as the decision it is. It removes the last interactive step
from a command whose force branch drops databases, and every site on the bench inherits that. Where a
prompt is wanted, the key must be absent — there is no flag that restores it.
