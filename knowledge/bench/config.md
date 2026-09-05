---
name: config
description: A site's configuration is common_site_config.json merged under site_config.json, then six keys rewritten from the process environment, then extra_config merged last, so neither JSON file is the final answer.
triggers: ["get_site_config", "get_common_site_config", "init", "conf", "_update_config_file", "update_site_config", "get_site_config_path", "filelock", "Cannot make dict for single fieldname", "site_config.json vs common_site_config.json", "where does frappe read site configuration", "the site keeps connecting to the wrong database even though the config file says otherwise", "i changed the database host in the config and it still goes to the old one", "why does the site ignore what i wrote in the site configuration file", "i set a value from the command line but the background workers still use the old one", "the setting only takes effect after i restart everything", "why do some processes see the new setting and others keep the old one", "i saved the word false as a setting and it came back as something else", "the value i typed as a number is not stored as a number anymore", "how do i remove a setting completely instead of leaving it empty", "my check for a missing setting never fires even though i never set it", "the configuration file is broken and nothing warns me it just quietly uses the old values"]
product: frappe
---

# Config

## paths

frappe/__init__.py — get_site_config, get_common_site_config, init, conf
frappe/installer.py — _update_config_file, update_site_config, get_site_config_path
frappe/utils/synchronization.py — filelock

## rules

MUST call get_common_site_config for a bench-wide setting; frappe.conf needs a site and carries that site's own keys over the common ones.
NEVER read an empty dict from get_common_site_config as proof a key is unset. A missing file and unparsable JSON both return the same empty _dict, the second after printing `common_site_config.json is invalid` in red, and neither raises.
MUST read FRAPPE_DB_HOST, FRAPPE_DB_PORT, FRAPPE_DB_TYPE, FRAPPE_DB_SOCKET, FRAPPE_REDIS_CACHE and FRAPPE_REDIS_QUEUE in the supervisor or systemd environment before believing what either JSON file says; the environment is read first for all six and nothing logs the substitution.
MUST ask whether frappe.conf.db_host is 127.0.0.1 rather than whether the key is present. db_type, db_host, db_port, redis_cache and redis_queue end in a literal fallback and are never absent after get_site_config returns; db_socket alone stays None.
NEVER store the strings `0`, `1`, `true` or `false` through set-config or set-common-config. _update_config_file rewrites the first two to int and the last two to bool before writing.
MUST pass the string `None` to set-config to remove a key; that branch deletes it and is the only unset the writer offers.
MUST restart the workers after a config write. _update_config_file writes the new value into frappe.local.conf of the calling process alone, so every other worker keeps what it loaded at frappe.init.
MUST expect an extra_config callable to be merged LAST, over the environment and both files, and a failure inside it to print `Config hook <name> failed` with a traceback and continue with the config unextended.
MUST expect get_site_config to raise IncorrectSitePath when site_path is set, site_config.json is absent and local.flags.new_site is not set; an invalid site_config.json instead prints `<site>/site_config.json is invalid` and leaves the common values standing.
NEVER pass a value to update_site_config expecting `validate` to check it; the parameter is accepted and never read.

## values

merge order: common_site_config.json, site_config.json, the six environment keys, extra_config
environment keys: FRAPPE_DB_HOST, FRAPPE_DB_PORT, FRAPPE_DB_TYPE, FRAPPE_DB_SOCKET, FRAPPE_REDIS_CACHE, FRAPPE_REDIS_QUEUE
fallbacks: db_type mariadb, db_host 127.0.0.1, db_port from the engine's default_port, redis_queue redis://127.0.0.1:11311, redis_cache redis://127.0.0.1:13311
db_socket: no fallback, stays None
set-config coercions: "0" to 0, "1" to 1, "true" to True, "false" to False, "None" deletes the key
extra_config: one dotted callable or a list of them
lock: config/site_config.lock when the path contains common_site_config, otherwise sites/<site>/locks/site_config.lock

## how

Read the config as a pipeline, not as a file. Four writers contribute in order and each one wins over
the last, so the question "what is db_host" has one answer only after get_site_config has run — and
the answer can come from a variable in a unit file that nobody edited this year. When a site connects
somewhere unexpected while both JSON files name the right host, the environment is the place to look
and it will not appear in any diff.

The literal fallbacks change what a check can ask. A key with a fallback is never absent, so
`if not frappe.conf.db_host` is dead code and the only meaningful test is against the fallback value
itself. db_socket is the one key where absence is still observable.

Writing is coarser than reading. There is one writer behind every set-config, it coerces five strings
without asking, and the only way to unset a key is to write the word that deletes it — which is
indistinguishable from a typo that meant to store that word. Keep a value the writer would mangle out
of the CLI and put it in the file.

The lock scope is chosen by a substring of the path, so a site named after the common file would take
the global lock. Nothing else picks up a mid-process file change: a value read at frappe.init is held
for the life of the process.
