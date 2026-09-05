---
name: setup
description: Every bench setup generator rewrites common_site_config.json as a side effect, and three of its writers default their target to the current working directory instead of the bench they were handed.
triggers: ["setup_config", "default_config", "get_config", "put_config", "update_config", "update_config_for_frappe", "make_ports", "get_gunicorn_workers", "generate_supervisor_config", "sync_socketio_port", "can_enable_multi_queue_consumption", "make_nginx_conf", "prepare_sites", "get_bench_name", "get_limit_conn_shared_memory", "update_site_config", "sync_domains", "get_domains", "bench setup commands", "regenerate common_site_config", "the settings i put in the config file got wiped after i ran the setup command", "why do my hand written config values keep reverting to the defaults", "how do i make a config value survive regenerating the config", "i edited the web server config by hand and the change disappeared", "my changes to the generated server file are gone after a deploy", "where am i supposed to change the port because editing the generated file does nothing", "the command ran fine but it changed the wrong bench", "i pointed it at another folder and it wrote into the one i was standing in", "turning on request throttling broke the config generation with a hashing error", "the number of workers is wrong on the server it looks like my laptop cpu count", "the two generated files differ every run even when nothing changed", "restarting behaviour changed by itself after i regenerated the process config"]
product: bench
---

# Setup

## paths

bench/config/common_site_config.py — setup_config, default_config, get_config, put_config, update_config, update_config_for_frappe, make_ports, get_gunicorn_workers
bench/config/supervisor.py — generate_supervisor_config, sync_socketio_port, can_enable_multi_queue_consumption
bench/config/nginx.py — make_nginx_conf, prepare_sites, get_bench_name, get_limit_conn_shared_memory
bench/config/site_config.py — update_site_config, sync_domains, get_domains

## rules

MUST re-apply any hand-set value for the nine keys in default_config after `bench setup config`; setup_config reads the existing file and then applies default_config ON TOP of it.
MUST pass a value that has to survive `bench setup config` through additional_config, which is the only map applied after the defaults.
MUST expect `bench setup supervisor` to set restart_supervisor_on_update to True and restart_systemd_on_update to False unconditionally; generating that file is also the act that chooses supervisor over systemd for the update path.
MUST run any command reaching update_config, update_site_config or sync_socketio_port from INSIDE the target bench directory. All three default bench_path to `"."`, sync_domains holds a real bench_path and hands the default to update_site_config, and sync_socketio_port reads with the given bench_path and writes without it.
NEVER turn allow_rate_limiting on at this version. make_nginx_conf passes get_bench_name's str to hashlib.sha256, which raises `TypeError: Strings must be encoded before hashing` before the file is written, so the previous nginx.conf stays in place and the bench keeps serving.
MUST change webserver_port, socketio_port, http_timeout or allow_rate_limiting in sites/common_site_config.json and re-run the generator; a hand edit of config/nginx.conf is lost the next time anything calls make_nginx_conf.
NEVER diff config/nginx.conf to decide whether anything changed; random_string is seven fresh lowercase letters on every run, so two generations of an unchanged bench differ.
MUST read gunicorn_workers and background_workers as computed from the CPU count of the machine that RAN the generator, not of the machine that will serve; get_gunicorn_workers and the `or 1` fallback both fire on a bench that never set them.
MUST expect update_config_for_frappe to fill redis_cache, redis_queue, redis_socketio, webserver_port, socketio_port and file_watcher_port only when the key is ABSENT, so those six survive setup_config while the nine defaults do not.

## values

default_config: restart_supervisor_on_update False, restart_systemd_on_update False, serve_default_site True, rebase_on_pull False, frappe_user the invoking user, shallow_clone True, background_workers 1, use_redis_auth False, live_reload True
setup_config order: existing config, default_config, get_gunicorn_workers, update_config_for_frappe, additional_config
supervisor side effects: restart_supervisor_on_update True, restart_systemd_on_update False, redis_socketio set to redis_cache
nginx template inputs: sites_path, http_timeout, sites, webserver_port, socketio_port, bench_name, error_pages, allow_rate_limiting, random_string
bench_path default: "." in update_config, update_site_config and the sync_domains call
overwrite prompt: nginx.conf returns on a declined confirm, supervisor.conf aborts

## how

Treat every generator as a writer of common_site_config.json first and a writer of its own file
second. Asking "what does `bench setup supervisor` do" and answering "it writes supervisor.conf" is
the mistake: it also decides the restart mechanism for the whole bench and copies one Redis port over
another. Read the tail of each generator before running it on a bench whose config someone tuned.

Three writers here take a bench path, use it for the READ and omit it on the WRITE, where the
parameter defaults to `"."`: sync_domains hands `bench_path="."` to update_site_config, and
sync_socketio_port calls get_config with the path it was given and update_config without it. The
values written are the named bench's and the file they land in is the shell's, so nothing raises and
the flag looks applied.

A generated file is not a place to edit. The inputs live in common_site_config.json and the output is
rewritten from them, so a change made in config/nginx.conf or config/supervisor.conf survives exactly
until the next generation and no error marks its loss.
