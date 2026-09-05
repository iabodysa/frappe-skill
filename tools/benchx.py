# Copyright (c) 2026, iabodysa

from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

if sys.version_info < (3, 11):
    raise SystemExit("benchx needs Python 3.11 or newer; it reads TOML with the standard library.")

import tomllib

CONFIG_NAME = ".benchx.toml"
ENVIRONMENTS = ("dev", "staging", "production")
DEFAULT_TIMEOUT = 1800

GLOBAL_VALUE_FLAGS = {"--site"}
"""bench options that consume the token after them, so that token is a value and never the verb."""

READ = {
    "version", "list-apps", "find", "src", "doctor", "status", "--version",
    "show-config", "describe-database-table", "show-pending-jobs", "remote-urls",
    "validate-dependencies", "ready-for-migration",
}
"""Verbs that read and do not write. Every name here was found in the installed source.

`list-sites` and `get-config` were in this set and neither exists — `bench list-sites` and
`bench get-config` both answer `Error: No such command`. An invented read-only name is worse than a
missing one: it is the shape of an entry that says "this is safe", for a command that never runs.
`show-config` is genuinely read-only and genuinely prints `db_password` and `encryption_key` in
clear, which is why it is also in SECRET_BEARING; safe to RUN is not the same as safe to LOG.
"""

INTERACTIVE = {
    "console", "mariadb", "postgres", "db-console", "browse", "shell", "start", "jupyter",
    "ngrok", "serve", "watch", "worker", "worker-pool", "schedule", "run-ui-tests",
}
"""Verbs that own a terminal or never return. Capturing their output is the wrong shape, so benchx
refuses instead of hanging on them.

`browse` earns its place twice. It is interactive, and at `frappe/commands/site.py:1192` it prints
`Login URL: ...?sid=<session>` for Administrator — a live session token, on stdout, as one of the
last lines, which is exactly where a success excerpt looks.
"""

DANGEROUS = {
    "new-site", "drop-site", "reinstall", "restore", "partial-restore", "migrate",
    "install-app", "uninstall-app", "remove-from-installed-apps", "trim-database", "trim-tables",
    "clear-log-table", "run-patch", "reload-doc", "reload-doctype", "add-database-index",
    "transform-database", "bulk-rename", "data-import", "reset-perms", "destroy-all-sessions",
    "set-password", "set-admin-password", "disable-user", "execute", "request",
    "run-tests", "run-parallel-tests", "set-config", "use", "migrate-to",
    "set-maintenance-mode", "disable-scheduler", "purge-jobs", "bypass-patch",
    "update-translations", "import-translations", "migrate-translations",
    "migrate-csv-to-po", "update-csv-from-po", "update-po-files",
    "update", "retry-upgrade", "switch-to-branch", "switch-to-develop", "drop", "remove", "rm",
    "remove-app", "get", "get-app", "pip", "migrate-env", "restart", "disable-production",
    "remote-set-url", "remote-reset-url", "remove-common-config", "set-common-config",
    "set-mariadb-host", "set-redis-cache-host", "set-redis-queue-host", "set-redis-socketio-host",
    "set-nginx-port", "set-ssl-certificate", "set-ssl-key", "set-url-root", "install",
    "config", "setup",
}
"""Irreversible, able to reach arbitrary code and arbitrary SQL, or able to take a site off the air.

`execute` and `update` are here on purpose and they are the reason the list is not named after
deletion. `bench execute` runs any python in the site context and commits, which is strictly more
powerful than `drop-site`; `bench update` pulls remote code and migrates every site. A gate that
blocks the frightening names and waves those two through would let this tool tell an operator that
they are safe on production.

`remove`, `rm` and `get` are here because they are ALIASES — of `remove-app` and `get-app`
(`bench/commands/make.py:208,130`). Blocking the long name and not the alias is a gate that can be
walked around by typing two fewer letters.

`bypass-patch` is here by name and not by the unknown-verb fallback, for the same reason `sqlite` is
named in FIRST_SITE_ONLY: the fallback is luck and the day somebody classifies the verb it vanishes.
It is the most quietly destructive command in the list. `frappe/commands/site.py:1594` calls
`update_patch_log` with no `skipped` argument, so the row lands with `skipped=0`; `run_all` selects
pending work with `filters={"skipped": 0}` (`frappe/modules/patch_handler.py:56`), so the patch is
excluded forever and reads exactly like one that ran. Contrast `migrate --skip-failing`, which stamps
`skipped=1` with the traceback (`patch_handler.py:70,209-218`) — that patch retries on the next
migrate and its failure stays readable. `bypass-patch` erases the difference between "ran" and
"never ran", and the erasure is invisible to every later migrate.

`migrate` is destructive despite the harmless name: it runs patches and `sync_all()` schema changes
against a live database and takes NO backup of its own. `run-tests` is destructive because it
creates and destroys records on whichever site it is pointed at, and pointing it at production is a
one-word mistake.
"""

FIRST_SITE_ONLY = {
    "add-to-email-queue", "browse", "build-search-index", "bulk-rename", "compile-po-to-mo",
    "console", "create-po-file", "data-import", "db-console", "disable-user", "doctor",
    "generate-pot-file", "get-untranslated", "import-translations", "jupyter", "mariadb",
    "migrate-csv-to-po", "migrate-translations", "new-language", "ngrok", "partial-restore",
    "postgres", "ready-for-migration", "reinstall", "restore", "run-parallel-tests", "run-tests",
    "run-ui-tests", "scheduler", "serve", "set-last-active-for-user", "set-maintenance-mode",
    "show-pending-jobs", "sqlite", "transform-database", "update-po-files", "update-translations",
}
"""Verbs that accept `--site all` and then act on exactly ONE site, silently.

`bench --site all restore dump.sql` reads as "restore everywhere" and restores into the first site
in sorted order. Nothing in bench's output says so, so benchx refuses the combination rather than
report a success the operator will misread.

The set is READ from source by a STRUCTURAL classifier, and the word structural is the whole lesson.
Reaching the first site has two spellings — `get_site(context)`, which is
`context.sites[0]` (`frappe/commands/__init__.py:53-59`), and `context.sites[0]` written out by hand
— and seven commands use the second. A first attempt asked whether the AST dump contained the string
`sites`, which is true of `for site in context.sites` and of `context.sites[0]` alike, so it filed
every hand-written one as safely iterating: a substring where a token was meant, in the direction
that hides. It reported 29 first-site-only when the answer is 35.

Classify by shape, not by name: a Call to `get_site`, or a Subscript of `<x>.sites` with the constant
0, is first-site-only; a For whose iterable is `<x>.sites` iterates. On frappe 15.109.0 that gives
**35 first-site-only, 40 iterating, 16 neither, of 91 commands** — and printing all three bins is
what makes the arithmetic checkable, because two bins that do not sum to the population hide the
gap rather than show it.

Two entries move between 15 and 16, and neither disappears: `sqlite` arrives, and `new-language`
CHANGES SHAPE — unclassified on 15, first-site-only on 16 (`frappe/commands/translate.py:38`). Both
are listed, because benchx may be pointed at a bench it was not built beside, and because an
unknown verb being covered by the fail-closed tier is luck rather than the rule.

Under-listing is the direction that costs. Over-listing turns the guard into a blanket refusal of
`--site all`, and somebody notices a refusal; under-listing lets `bench --site all update-po-files`
write one site's translations and report nothing, which is the wrong-target class — it does not
fail, it succeeds somewhere else.

The ones that matter most are those benchx would otherwise RUN rather than refuse: `doctor`,
`show-pending-jobs`, `ready-for-migration`, `scheduler`, `build-search-index`, `add-to-email-queue`,
`get-untranslated`, `set-last-active-for-user`, and the six gettext verbs. On `doctor` and
`show-pending-jobs` the wrong answer is a DIAGNOSIS, which is worse than a failure because it is
believed and acted on.
"""

SITE_VERBS = {
    "migrate", "install-app", "uninstall-app", "backup", "restore", "partial-restore", "console",
    "execute", "clear-cache", "clear-website-cache", "clear-log-table", "list-apps", "run-tests",
    "run-parallel-tests", "set-config", "show-config", "export-fixtures", "export-csv", "export-doc",
    "export-json", "import-doc", "reinstall", "enable-scheduler", "disable-scheduler", "scheduler",
    "set-maintenance-mode", "trigger-scheduler-event", "add-system-manager", "add-user", "browse",
    "set-admin-password", "set-password", "reload-doc", "reload-doctype", "add-to-hosts",
    "build-search-index", "rebuild-global-search", "add-database-index", "describe-database-table",
    "destroy-all-sessions", "disable-user", "data-import", "bulk-rename", "reset-perms", "request",
    "run-patch", "trim-database", "trim-tables", "transform-database", "doctor", "purge-jobs",
    "ready-for-migration", "show-pending-jobs", "start-recording", "stop-recording", "db-console",
    "mariadb", "postgres", "jupyter", "ngrok", "publish-realtime", "set-last-active-for-user",
    "add-to-email-queue", "serve", "bypass-patch", "sync-desktop-icons", "new-language",
}
"""Verbs that take `--site`, so benchx supplies the declared one rather than let bench guess.

Getting this set wrong is not a refusal, it is a WRONG TARGET. bench falls back to `default_site`
from `sites/common_site_config.json` (`frappe/utils/bench_helper.py:49-69`), so a site verb missing
from this set does not fail — it runs against whichever site somebody last passed to `bench use`.

`--site` is declared once, on the click GROUP (`frappe/utils/bench_helper.py:38-46`), which is why
it must be injected BEFORE the subcommand. After it, bench answers `Error: No such option: --site`
and exits 2.
"""

SECRET_BEARING = {
    "set-config", "show-config", "new-site", "restore", "set-admin-password", "set-password",
    "reinstall", "drop-site", "browse", "console", "execute", "db-console", "mariadb", "postgres",
}
"""Verbs whose output or arguments carry a credential, so their transcript is redacted before it lands.

`show-config` is the worst of them: `frappe/commands/utils.py:162-210` prints the whole
`site_config.json` with no redaction at all — `db_password`, `encryption_key`,
`backup_encryption_key`, mail passwords, API secrets.
"""

SECRET = re.compile(
    r"(?i)((?:pass(?:word)?|secret|token|api[_-]?key|auth|credential|private[_-]?key"
    r"|encryption[_-]?key|\bsid)[ \t:=\"',|]{0,24})(\S+)")
"""No word boundary before the alternation, and that is the whole point: the key an operator
actually loses is `db_password`, where the character before `pass` is an underscore — a word
character — so an anchored pattern skips the one line it exists for. `sid` carries its own
boundary because it is three letters and would otherwise match inside ordinary words.

The separator run is generous on purpose: bench prints a config as an aligned TABLE, so the value
sits many spaces from its key. It excludes the newline, so a key at the end of a line cannot swallow
the line under it.
"""

HOSTNAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
USERNAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CONTAINER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")
BINARY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

SIGNATURES: list[tuple[str, str]] = [
    (r"ssh: connect to host .* (Operation timed out|Connection refused|No route to host)",
     "the SSH host did not answer"),
    (r"Could not resolve hostname", "the SSH host name does not resolve"),
    (r"Permission denied \(publickey", "SSH refused the key"),
    (r"(?:command not found|No such file or directory).{0,20}\bbench\b|\bbench\b.{0,20}command not found",
     "the SSH login reached the host but `bench` is not on PATH there — a non-interactive shell "
     "does not read the profile that puts it there"),
    (r"Error: No such container|Cannot connect to the Docker daemon", "the container is not running"),
    (r"Error: No such option: --site", "--site came AFTER the subcommand; bench declares it on the "
                                       "group, so it only parses before"),
    (r"Error: No such option", "bench does not accept that option for this subcommand"),
    (r"Error: No such command", "that is not a bench command on this bench"),
    (r"Command not being executed in bench directory", "target.bench does not name a bench"),
    (r"Failed to aquire lock", "another process holds the bench lock; wait for it or clear the lock file"),
    (r"Site named .* doesn't exist|Site .* does not exist", "the site named does not exist on this bench"),
    (r"Site .* already exists", "the site already exists; restore or reinstall it instead of creating it"),
    (r"App .* not installed on Site", "the app is not installed on this site"),
    (r"App .* already installed", "the app is already installed on this site"),
    (r"App .* is Incompatible with Site", "the app requires a different framework version"),
    (r"App .* is a dependency of", "another installed app depends on this one; uninstall that first"),
    (r"App .* not in apps.txt", "the app is not in the bench's apps.txt"),
    (r"Service (\w+) is not running|Cannot run bench migrate without the services running",
     "a service the site needs is down — mariadb, postgres or one of the redis instances"),
    (r"Can't connect to (MySQL|MariaDB) server|OperationalError.*2003", "the database is not reachable"),
    (r"Access denied for user", "the database credentials are refused"),
    (r"redis.*ConnectionError|Error \d+ connecting to ", "redis is not reachable"),
    (r"DocumentLockedError", "a document is locked by another process"),
    (r"Address already in use|port is already", "the port is already bound"),
    (r"ModuleNotFoundError: No module named ['\"]?([\w.]+)", "a python module is missing"),
    (r": failed: STOPPED|PatchError", "a patch failed during migrate and stopped it"),
    (r"Partial Backup file detected", "that dump is a partial backup; `restore` needs a full one"),
    (r"Table .__Auth. not found in file|is an empty file", "the restore file is not a usable dump"),
    (r"Backup failed for Site", "the backup step failed, so the operation it guarded did not run"),
    (r"Cannot remove non-empty bench directory", "the bench still holds sites; drop them first"),
    (r"bench: command not found|No such file or directory: ['\"]?bench", "bench is not on PATH at the target"),
    (r"error Command failed with exit code|Module build failed", "the frontend build failed"),
    (r"MergeError|CONFLICT \(content\)", "a merge conflict blocks the tree"),
    (r"Aborted!|EOFError", "bench asked for a confirmation; benchx runs with no terminal, so it "
                           "answered end-of-input and bench aborted"),
    (r"frappe\.exceptions\.ValidationError", "the framework raised a validation error"),
    (r"SiteNotSpecifiedError|Please specify --site", "no site named, and the config declares none"),
]
r"""Ordered, and `classify` returns the FIRST match, so a generic pattern placed early silently
answers for every specific one under it. `Please specify --site` appears in bench usage text after
unrelated argument errors; first in the list it reported a missing site for a ValidationError.
Specific patterns go above generic ones, and a pattern that can fire on an unrelated traceback is
deleted rather than demoted — a confidently wrong cause is worse than none, because it gets acted on.

Every literal here was read out of the installed source, not remembered. Three that were remembered
were wrong and one could never fire: `App .* is not installed` has no `is` in frappe
(`frappe/installer.py:382` says `App {app} not installed on Site {site}`); `Failed to execute patch`
is printed ONLY under `--skip-failing`, where the exit code is zero and this list is never consulted;
`Error \d+ connecting to .*637\d` hardcoded redis's upstream default port, and a frappe bench never
uses it. There is no CLI string for maintenance mode at all — the flag is read by the web layer and
the scheduler, never printed by a bench subcommand — so the signature that claimed to detect it is
gone rather than kept as a guess.
"""

HINTS: list[tuple[str, str]] = [
    (r"Identity file (\S+) not accessible",
     "ssh could not read the identity file in the config and fell back to its other keys"),
    (r"A newer version of bench is available", "bench is behind its latest release"),
]
"""Things worth telling the operator that are NOT the cause, printed under the verdict as hints.

`Identity file ... not accessible` was a SIGNATURE and it could never legitimately fire: ssh only
ever emits it as a `Warning:` and then carries on, so any run that showed it died of something else.
As a cause it was wrong every time; as a hint it is useful every time — a key path that does not
resolve is a real thing to fix, just never the reason this run stopped.
"""

FALSE_SUCCESS: list[tuple[str, str]] = [
    (r": failed: STOPPED|Failed to execute patch",
     "a patch FAILED and --skip-failing swallowed it; the schema is now partly migrated"),
    (r"FAILED \((failures|errors)=", "the test run reported failures; bench still exited 0"),
    (r"Testing is disabled for the site", "no test ran at all; the site has allow_tests unset"),
    (r"App .* not installed on Site", "nothing was uninstalled; the app was not on this site"),
    (r"App .* already installed", "nothing was installed; the app was already there"),
]
"""Output that means the command did NOT do its job, on an exit code of zero.

This list exists because bench's exit code is not a verdict. `bench run-tests` returns 0 on a failing
suite outside CI (`frappe/commands/utils.py:806-809` only propagates the status when `$CI` is set),
and prints `Testing is disabled for the site!` and returns 0 when the site forbids tests, so a
wrapper that trusts `returncode` reports a green suite that never ran. `migrate --skip-failing`
prints the broken patch and exits 0 by design.

A verdict built only on the exit code is wrong in the one direction that matters: it says yes.
"""

ADMIN_PASSWORD_ENV = "BENCHX_ADMIN_PASSWORD"
ADMIN_PASSWORD_VERBS = {"new-site", "restore", "reinstall"}
"""The three verbs that create a site's Administrator, and where benchx reads the password it pins.

benchx ships no password. It reads `safety.dev_admin_password`, then the variable above, and
REFUSES the verb when neither is set and the caller passed no `--admin-password` of his own — a
refusal, because omitting it is not "no password": `frappe/installer.py:177` falls back to
`frappe.conf.admin_password` and creates the site with a value the operator never chose.

What it does pin sits at the ARGV of one invocation, is redacted out of the transcript by `report`,
and is supplied on `dev` alone; elsewhere a known password is not a convenience, it is the account.
"""

AFTERMATH = {
    "update": "a failed `bench update` leaves maintenance_mode and pause_scheduler set for EVERY "
              "site — they are written before the first step and cleared only after the last one "
              "succeeds (bench/utils/bench.py:466,494), so the bench is offline until you clear them",
    "migrate": "under --site all, migrate stops at the first site that fails and never attempts the "
               "sites after it; the exit code cannot tell you how many ran",
    "install-app": "install-app commits only when every app in the run succeeded, so a failure on "
                   "one app discards the apps that installed before it in the same command",
}
"""What a FAILURE of this verb leaves behind. Printed under the verdict, because the state the
machine is in afterwards is the operator's next problem and bench never mentions it.
"""

TRACE = re.compile(r"^(?:\w[\w.]*Error|\w[\w.]*Exception)\b.*")

EXIT_OK = 0
EXIT_USAGE = 64
EXIT_CONFIG = 65
EXIT_REFUSED = 66
EXIT_TIMEOUT = 67
EXIT_NO_BINARY = 68
"""benchx's own codes, in the `sysexits` range so a caller can tell them apart from bench's.

bench and click own 0, 1 and 2, and the first version answered `2` for both "your config is broken"
and "bench rejected your arguments" — so the exit code, the only part of the contract a script can
act on, carried no information. Anything not listed here is bench's own code, passed through.
"""


def redact(text: str) -> str:
    return SECRET.sub(lambda m: f"{m.group(1)}[redacted]", text)


def find_config(start: Path) -> Path | None:
    for directory in [start, *start.parents]:
        candidate = directory / CONFIG_NAME
        if candidate.is_file():
            return candidate
    fallback = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "benchx" / "config.toml"
    return fallback if fallback.is_file() else None


def load(start: Path | None = None) -> tuple[dict, Path | None]:
    path = find_config(Path(start or Path.cwd()).resolve())
    if path is None:
        return {}, None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8")), path
    except (tomllib.TOMLDecodeError, OSError) as error:
        return {"_unreadable": str(error)}, path


def verb_of(args: list[str]) -> str:
    index = 0
    while index < len(args):
        item = args[index]
        if not item.startswith("-"):
            return item
        index += 2 if item in GLOBAL_VALUE_FLAGS else 1
    return ""


def tier(verb: str) -> str:
    if verb in READ:
        return "read"
    if verb in INTERACTIVE:
        return "interactive"
    if verb in DANGEROUS or verb == "":
        return "danger"
    return "write" if verb in SITE_VERBS or verb in KNOWN_WRITE else "danger"


KNOWN_WRITE = {
    "build", "backup", "backup-all-sites", "clear-cache", "clear-website-cache", "app-cache",
    "export-fixtures", "export-csv", "export-doc", "export-json", "import-doc",
    "enable-scheduler", "trigger-scheduler-event", "add-system-manager", "add-user",
    "add-to-hosts", "add-to-email-queue", "build-search-index", "rebuild-global-search",
    "set-last-active-for-user", "publish-realtime", "start-recording", "stop-recording",
    "new-app", "make-app", "create-patch", "init", "include-app", "exclude-app",
    "new-language", "generate-pot-file", "create-po-file", "compile-po-to-mo", "get-untranslated",
    "build-message-files", "download-translations", "create-rq-users", "renew-lets-encrypt",
}
"""Verbs that change something and are recoverable — the middle tier, and the only one that has to
be enumerated at all.

`read` is a courtesy and `danger` is the default, so a name missing from here costs a refusal, never
a silent run. That asymmetry is deliberate: the cost of forgetting a verb is an operator who has to
add it, and the cost of the opposite default is a destructive command nobody classified.
"""


class Target:

    def __init__(self, config: dict, origin: Path | None):
        target = config.get("target", {}) if isinstance(config.get("target"), dict) else {}
        self.unreadable = str(config.get("_unreadable") or "")
        self.origin = origin
        self.kind = str(target.get("kind") or "local")
        self.bench = str(target.get("bench") or "")
        self.site = str(target.get("site") or "")
        self.host = str(target.get("host") or "")
        self.user = str(target.get("user") or "")
        self.identity = str(target.get("identity_file") or "")
        self.container = str(target.get("container") or "")
        self.binary = str(target.get("bench_binary") or "bench")
        self.env = str(target.get("env") or "dev")
        output = config.get("output", {}) if isinstance(config.get("output"), dict) else {}
        self.max_excerpt = int(output.get("max_excerpt_lines") or 40)
        self.log_dir = str(output.get("log_dir") or default_log_dir())
        self.timeout = int(output.get("timeout_seconds") or DEFAULT_TIMEOUT)
        safety = config.get("safety", {}) if isinstance(config.get("safety"), dict) else {}
        self.allow_destructive = bool(safety.get("allow_destructive"))
        self.declared_admin_password = str(safety.get("dev_admin_password") or "")
        self.admin_password = self.declared_admin_password or os.environ.get(ADMIN_PASSWORD_ENV, "")

    @property
    def local_bench(self) -> Path:
        return Path(self.bench).expanduser()

    def apps_dir(self) -> str:
        return f"{self.bench.rstrip('/')}/apps"

    def problems(self) -> list[str]:
        if self.unreadable:
            return [f"{self.origin} is not valid TOML: {self.unreadable}"]
        if self.origin is None:
            return [f"no {CONFIG_NAME} found — run `benchx :setup` and declare the target once"]
        found = []
        if not self.bench:
            found.append("target.bench is empty; benchx will not guess a bench directory")
        if self.kind not in {"local", "ssh", "docker"}:
            found.append(f"target.kind {self.kind!r} is not local, ssh or docker")
        if self.env not in ENVIRONMENTS:
            found.append(f"target.env {self.env!r} is not {', '.join(ENVIRONMENTS)}")
        if not BINARY.match(self.binary):
            found.append(f"target.bench_binary {self.binary!r} is not a bare command name")
        if self.kind == "local" and self.bench and not (self.local_bench / "sites").is_dir():
            found.append(f"{self.bench} holds no sites/ directory, so it is not a bench")
        if self.kind == "ssh":
            if not self.host:
                found.append("target.kind is ssh but target.host is empty")
            elif not HOSTNAME.match(self.host):
                found.append(f"target.host {self.host!r} is not a host name; a value starting with "
                             f"'-' is an ssh OPTION and would run before any connection")
            if self.user and not USERNAME.match(self.user):
                found.append(f"target.user {self.user!r} is not a user name")
        if self.declared_admin_password and self.env != "dev":
            found.append(f"safety.dev_admin_password is set but target.env is {self.env}; benchx "
                         f"never supplies an admin password outside dev, so the key promises "
                         f"something it will not do — remove it")
        if self.kind == "docker":
            if not self.container:
                found.append("target.kind is docker but target.container is empty")
            elif not CONTAINER.match(self.container):
                found.append(f"target.container {self.container!r} is not a container name")
        return found

    def refusal(self, verb: str, confirmed: str) -> str | None:
        level = tier(verb)
        if level == "interactive":
            return (f"{verb or 'that'} owns a terminal or never returns; benchx captures output and "
                    f"would report a hang as a timeout — run bench directly")
        if level in {"read", "write"}:
            return None
        if not self.allow_destructive:
            known = "destructive" if verb in DANGEROUS else "not a verb benchx knows, so it is treated as destructive"
            return f"{known}; set safety.allow_destructive in {CONFIG_NAME} to permit it"
        if self.env == "dev":
            return None
        if not self.site:
            return f"destructive on {self.env}, and no site is declared to confirm against"
        if confirmed != self.site:
            return (f"destructive on {self.env}; re-run with --confirm={self.site} "
                    f"to say which site you mean")
        return None

    def pins_admin(self, args: list[str], verb: str) -> bool:
        if self.env != "dev" or verb not in ADMIN_PASSWORD_VERBS:
            return False
        return not any(item == "--admin-password" or item.startswith("--admin-password=")
                       for item in args)

    def missing_admin(self, args: list[str], verb: str) -> str | None:
        if not self.pins_admin(args, verb) or self.admin_password:
            return None
        return (f"{verb} creates the Administrator account and benchx holds no password for it; "
                f"pass --admin-password to bench, set safety.dev_admin_password in {CONFIG_NAME}, "
                f"or export {ADMIN_PASSWORD_ENV} — benchx ships no default")

    def fan_out(self, args: list[str], verb: str) -> str | None:
        wanted, carries = "", False
        for index, item in enumerate(args):
            if item.startswith("--site="):
                wanted, carries = item.split("=", 1)[1], True
            elif item == "--site":
                carries = True
                if index + 1 < len(args):
                    wanted = args[index + 1]
        if not carries and verb in SITE_VERBS:
            wanted = self.site
        if wanted != "all":
            return None
        if verb in FIRST_SITE_ONLY:
            return (f"--site all reaches {verb} but {verb} acts on ONE site — the first in sort "
                    f"order — and says nothing about the rest; name the site instead")
        if verb in DANGEROUS:
            return f"--site all on {verb} is destructive against every site at once; name one site"
        return None

    def blocked(self) -> list[str]:
        return sorted(verb for verb in DANGEROUS | INTERACTIVE if self.refusal(verb, ""))

    def build(self, argv: list[str]) -> list[str]:
        args = list(argv)
        verb = verb_of(args)
        carries_site = any(item == "--site" or item.startswith("--site=") for item in args)
        if self.site and verb in SITE_VERBS and not carries_site:
            args = ["--site", self.site, *args]
        if self.pins_admin(args, verb) and self.admin_password:
            args = [*args, "--admin-password", self.admin_password]
        remote = shlex.join([self.binary, *args])
        if self.kind == "local":
            return [self.binary, *args]
        if self.kind == "ssh":
            options = ["-o", "BatchMode=yes"]
            if self.identity:
                options += ["-i", str(Path(self.identity).expanduser())]
            if self.user:
                options += ["-l", self.user]
            inner = f"cd {shlex.quote(self.bench)} && {remote}"
            return ["ssh", *options, "--", self.host, f'"$SHELL" -lc {shlex.quote(inner)}']
        return ["docker", "exec", "-w", self.bench, "--", self.container, self.binary, *args]


def default_log_dir() -> str:
    base = Path(os.environ.get("XDG_STATE_HOME", "~/.local/state")).expanduser()
    return str(base / "benchx" / "logs")


ADVISORY = re.compile(r"^\s*(?:warning|note|info|debug|deprecat\w*)\b[: ]", re.IGNORECASE)
"""A line a tool prints and then CARRIES ON past. It is never the cause of anything.

`ssh` says `Warning: Identity file /x not accessible` and keeps going, so a run with a bad key path
and an unresolvable host dies on the host and reports the key. The operator fixes the key, re-runs,
and gets the identical failure under a different explanation — which is worse than an unrecognised
failure, because the evidence looks complete. Found by an adversarial run that gave the same fatal
error twice with only the key path changed, and got two different causes.
"""


def classify(text: str) -> str | None:
    fatal = "\n".join(line for line in text.splitlines() if not ADVISORY.match(line))
    for pattern, cause in SIGNATURES:
        if re.search(pattern, fatal, re.IGNORECASE):
            return cause
    return None


def suspect(text: str) -> str | None:
    for pattern, doubt in FALSE_SUCCESS:
        if re.search(pattern, text, re.IGNORECASE):
            return doubt
    return None


def excerpt(text: str, limit: int) -> list[str]:
    lines = text.splitlines()
    hits = [index for index, line in enumerate(lines) if TRACE.match(line.strip())]
    if hits:
        start = max(0, hits[-1] - min(12, limit // 2))
        return lines[start:start + limit]
    for pattern, _ in SIGNATURES:
        for index, line in enumerate(lines):
            if re.search(pattern, line, re.IGNORECASE):
                return lines[max(0, index - 2):index + limit - 2]
    return [line for line in lines if line.strip()][-limit:]


def write_log(target: Target, verb: str, text: str) -> Path:
    directory = Path(target.log_dir).expanduser()
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    safe = re.sub(r"[^\w.-]", "_", verb) or "bench"
    stem = f"{safe}-{time.strftime('%Y%m%dT%H%M%S')}-{os.getpid()}"
    for attempt in range(1000):
        path = directory / (f"{stem}.log" if attempt == 0 else f"{stem}-{attempt}.log")
        try:
            handle = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            continue
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(text)
        return path
    raise OSError(f"could not open a log file under {directory}")


def report(target: Target, verb: str, code: int, text: str) -> None:
    if verb in SECRET_BEARING:
        text = redact(text)
    log = write_log(target, verb, text)
    where = f"{target.kind}:{target.bench}" + (f" · {target.site}" if target.site else "")
    if target.env != "dev":
        where = f"[{target.env.upper()}] {where}"
    if code == 0:
        doubt = suspect(text)
        if doubt:
            print(f"SUSPECT {verb} · exit 0 · {doubt}")
            for line in excerpt(text, target.max_excerpt):
                print(f"  {line}")
            print(f"  log {log}")
            return
        print(f"OK {verb} · {where}")
        if verb not in SECRET_BEARING:
            for line in [line for line in text.splitlines() if line.strip()][-3:]:
                print(f"  {line}")
        else:
            print("  output withheld — this verb carries credentials; the log is redacted")
        print(f"  log {log}")
        return
    cause = classify(text)
    print(f"FAIL {verb} · exit {code} · {cause or 'no known signature matched'}")
    for line in excerpt(text, target.max_excerpt):
        print(f"  {line}")
    if cause is None:
        print("  the classifier did not recognise this failure; the log holds the whole run")
    for pattern, note in HINTS:
        if re.search(pattern, text, re.IGNORECASE):
            print(f"  hint   {note}")
    if verb in AFTERMATH:
        print(f"  after  {AFTERMATH[verb]}")
    print(f"  log {log}")


def split_confirm(argv: list[str]) -> tuple[list[str], str]:
    args, confirmed = [], ""
    for item in argv:
        if item.startswith("--confirm="):
            confirmed = item.split("=", 1)[1]
            continue
        if item == "--confirm":
            confirmed = "\x00space-form"
            continue
        args.append(item)
    return args, confirmed


def run(target: Target, argv: list[str]) -> int:
    argv, confirmed = split_confirm(argv)
    if confirmed == "\x00space-form":
        print(f"REFUSED · write --confirm={target.site or '<site>'} with an equals sign; "
              f"the spaced form would eat the next argument")
        return EXIT_REFUSED
    verb = verb_of(argv)
    refusal = (target.fan_out(argv, verb) or target.missing_admin(argv, verb)
               or target.refusal(verb, confirmed))
    if refusal:
        print(f"REFUSED {verb or '(no verb)'} · {refusal}")
        return EXIT_REFUSED
    if target.pins_admin(argv, verb) and target.admin_password:
        print(f"  admin password pinned for this run from the declared target; env is {target.env}")
    command = target.build(argv)
    cwd = str(target.local_bench) if target.kind == "local" else None
    try:
        done = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=target.timeout)
    except FileNotFoundError as error:
        print(f"FAIL {verb} · exit {EXIT_NO_BINARY} · {command[0]} is not on PATH here")
        print(f"  {error}")
        return EXIT_NO_BINARY
    except subprocess.TimeoutExpired:
        print(f"FAIL {verb} · exit {EXIT_TIMEOUT} · no answer within {target.timeout}s; "
              f"raise output.timeout_seconds or run it directly")
        return EXIT_TIMEOUT
    report(target, verb, done.returncode, (done.stdout or "") + (done.stderr or ""))
    return done.returncode


LANE_PATTERN = re.compile(r"^lane-[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.localhost$")
"""A lane site name, and nothing else. `is_lane_site` is the one gate `:lane drop` trusts, so it is
checked against whatever site is resolved — from `--name` or from the declared target — never against
the flag alone, because the declared target can still be `apex.localhost` or `ci.localhost` when a
worktree's own `.benchx.toml` was never written.
"""


def is_lane_site(site: str) -> bool:
    return bool(site) and bool(LANE_PATTERN.match(site))


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "lane"


def lane_site(lane_id: str) -> str:
    return f"lane-{lane_id}.localhost"


def default_lane_id() -> str:
    """The basename of the current git worktree, lowercased, slugified. Falls back to the bare cwd
    name outside a git checkout, so `:lane new` never refuses only for lack of a `--name`.
    """
    top = ""
    try:
        done = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                              text=True, timeout=5, stdin=subprocess.DEVNULL)
        if done.returncode == 0:
            top = done.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return slugify(Path(top).name if top else Path.cwd().name)


def execute(target: Target, argv: list[str]) -> subprocess.CompletedProcess:
    """The same subprocess call `run()` makes, pulled out so a lane verb can issue one bench call
    without going through `run()`'s DANGEROUS/allow_destructive gate — a lane verb carries its own
    guard (`is_lane_site`) and must not additionally demand `safety.allow_destructive`, which is
    machine-wide and would wave through every other destructive verb along with it.
    """
    command = target.build(argv)
    cwd = str(target.local_bench) if target.kind == "local" else None
    return subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL, timeout=target.timeout)


def site_exists(target: Target, site: str) -> bool:
    done = execute(target, ["list-apps", "--site", site])
    if done.returncode == 0:
        return True
    text = (done.stdout or "") + (done.stderr or "")
    if classify(text) == "the site named does not exist on this bench":
        return False
    return True  # unknown failure — refuse the create rather than risk two agents on one site


def declared_apps(target: Target) -> list[str]:
    """The apps the resolved bench already declares — `sites/apps.txt` locally, `list-apps` remotely
    — never a list this tool invents; a lane installs exactly what the target already carries.
    """
    if target.kind == "local":
        path = target.local_bench / "sites" / "apps.txt"
        if path.is_file():
            return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return []
    done = execute(target, ["list-apps"])
    if done.returncode != 0:
        return []
    return [line.split()[0] for line in (done.stdout or "").splitlines() if line.strip()]


def trash_home() -> Path:
    return Path("~/.claude/trash").expanduser()


def trash_site(target: Target, site: str, reason: str) -> Path:
    """MOVES whatever bench left of the site — never deletes. `bench drop-site` may archive the
    directory under `sites/archived_sites/` or remove it outright depending on version; either way
    this checks both spots and relocates what it finds with `shutil.move`, and writes the sidecar
    even when it finds nothing, because the removal itself is still the fact to record.
    """
    original = target.local_bench / "sites" / site if target.kind == "local" else Path(site)
    source = None
    if target.kind == "local":
        for candidate in (target.local_bench / "sites" / site,
                          target.local_bench / "sites" / "archived_sites" / site):
            if candidate.is_dir():
                source = candidate
                break
    dest_dir = trash_home() / time.strftime("%Y-%m-%d")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / site
    if source is not None:
        shutil.move(str(source), str(dest))
    sidecar = dest_dir / f"{site}.trash.txt"
    sidecar.write_text(
        f"source: {original}\n"
        f"removed_in: :lane drop @ {time.strftime('%Y-%m-%dT%H:%M:%S')}\n"
        f"reason: {reason}\n"
        f"restore: move {dest} back to {original}\n",
        encoding="utf-8")
    return dest if source is not None else sidecar


def pin_lane(target: Target, site: str) -> Path:
    lines = ["# Written by `benchx :lane new`. Pins this worktree to its own lane.", "[target]",
             f'kind = "{target.kind}"', f'env = "{target.env}"', f'bench = "{target.bench}"',
             f'site = "{site}"']
    for key, value in (("host", target.host), ("user", target.user),
                       ("identity_file", target.identity), ("container", target.container)):
        if value:
            lines.append(f'{key} = "{value}"')
    lines += ["", "[output]", f"max_excerpt_lines = {target.max_excerpt}",
              f"timeout_seconds = {target.timeout}", "", "[safety]",
              f"allow_destructive = {str(target.allow_destructive).lower()}"]
    if target.declared_admin_password:
        lines.append(f'dev_admin_password = "{target.declared_admin_password}"')
    path = Path.cwd() / CONFIG_NAME
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ignore_logs(Path.cwd())
    return path


def lane_new(target: Target, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="benchx :lane new",
                                     description="Create this agent's own site and pin it as the lane target.")
    parser.add_argument("--name", default="", help="Lane id; defaults to the current git worktree's basename")
    parsed = parser.parse_args(argv)

    site = lane_site(slugify(parsed.name) if parsed.name else default_lane_id())

    if site_exists(target, site):
        print(f"REFUSED :lane new · {site} already exists — a lane is never reused; two agents "
              f"sharing one lane is the exact failure this verb stops")
        return EXIT_REFUSED

    build_argv = ["new-site", site]
    for app in declared_apps(target):
        build_argv += ["--install-app", app]
    missing = target.missing_admin(build_argv, "new-site")
    if missing:
        print(f"REFUSED :lane new · {missing}")
        return EXIT_REFUSED
    if target.pins_admin(build_argv, "new-site") and target.admin_password:
        build_argv += ["--admin-password", target.admin_password]

    done = execute(target, build_argv)
    report(target, "new-site", done.returncode, (done.stdout or "") + (done.stderr or ""))
    if done.returncode != 0:
        return done.returncode

    pin_path = pin_lane(target, site)
    print(f"lane   {site}")
    print(f"bench  {target.bench}")
    print(f"pin    {pin_path}")
    return EXIT_OK


def lane_drop(target: Target, argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="benchx :lane drop",
                                     description="Drop this agent's own lane site; refuses everything else.")
    parser.add_argument("--name", default="")
    parser.add_argument("--reason", default="lane torn down by its own agent")
    parsed = parser.parse_args(argv)

    site = lane_site(slugify(parsed.name)) if parsed.name else target.site
    if not is_lane_site(site):
        print(f"REFUSED :lane drop · {site or '(no site declared)'} does not match lane-*.localhost — "
              f"apex.localhost, ci.localhost and every other site are unreachable by this verb")
        return EXIT_REFUSED

    done = execute(target, ["drop-site", site, "--force", "--no-backup"])
    report(target, "drop-site", done.returncode, (done.stdout or "") + (done.stderr or ""))

    moved = trash_site(target, site, parsed.reason)
    print(f"trash  {moved}")

    if done.returncode != 0:
        return done.returncode

    cfg_data, cfg_path = load(Path.cwd())
    pinned_site = str((cfg_data.get("target") or {}).get("site") or "")
    if cfg_path is not None and cfg_path.parent == Path.cwd() and pinned_site == site:
        cfg_path.unlink()
        print(f"pin    removed {cfg_path}")

    return EXIT_OK


def human_size(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "K", "M", "G"):
        if value < 1024 or unit == "G":
            return f"{value:.0f}{unit}" if unit == "B" else f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}G"


def human_age(seconds: float) -> str:
    seconds = max(0.0, seconds)
    if seconds < 3600:
        return f"{int(seconds // 60)}m"
    if seconds < 86400:
        return f"{int(seconds // 3600)}h"
    return f"{int(seconds // 86400)}d"


def lane_ls(target: Target, argv: list[str]) -> int:
    if argv:
        print("benchx :lane ls · takes no arguments")
        return EXIT_USAGE
    if target.kind != "local":
        print(f"REFUSED :lane ls · needs local filesystem access to size and age each site; kind is {target.kind}")
        return EXIT_REFUSED
    sites_dir = target.local_bench / "sites"
    if not sites_dir.is_dir():
        print(f"FAIL :lane ls · {sites_dir} is not a directory")
        return EXIT_CONFIG
    lanes = sorted(p for p in sites_dir.iterdir() if p.is_dir() and is_lane_site(p.name))
    if not lanes:
        print("no lane-*.localhost sites on this bench")
        return EXIT_OK
    now = time.time()
    for p in lanes:
        size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        print(f"{p.name}\t{human_size(size)}\t{human_age(now - p.stat().st_mtime)} old")
    return EXIT_OK


def lane_main(target: Target, argv: list[str]) -> int:
    if not argv:
        print("usage: benchx :lane <new|drop|ls> [--name <id>]")
        return EXIT_USAGE
    sub, rest = argv[0], argv[1:]
    if sub == "new":
        return lane_new(target, rest)
    if sub == "drop":
        return lane_drop(target, rest)
    if sub == "ls":
        return lane_ls(target, rest)
    print(f"benchx :lane {sub} · unknown; use new, drop or ls")
    return EXIT_USAGE


def compose(parsed) -> str:
    lines = ["# Written by `benchx setup`. Where bench runs, declared once.", "[target]",
             f'kind = "{parsed.kind}"', f'env = "{parsed.env}"', f'bench = "{parsed.bench}"']
    for key, value in (("site", parsed.site), ("host", parsed.host), ("user", parsed.user),
                       ("identity_file", parsed.key), ("container", parsed.container)):
        if value:
            lines.append(f'{key} = "{value}"')
    lines += ["", "[output]", "max_excerpt_lines = 40", f"timeout_seconds = {DEFAULT_TIMEOUT}",
              "", "[safety]", f"allow_destructive = {str(parsed.env == 'dev').lower()}"]
    if parsed.env == "dev" and parsed.admin_password:
        lines.append(f'dev_admin_password = "{parsed.admin_password}"')
    return "\n".join(lines) + "\n"


def ignore_logs(root: Path) -> None:
    if not (root / ".git").is_dir():
        return
    path = root / ".gitignore"
    body = path.read_text(encoding="utf-8") if path.is_file() else ""
    if ".benchx/" in body:
        return
    path.write_text(body + ("" if body.endswith("\n") or not body else "\n") + ".benchx/\n",
                    encoding="utf-8")


def setup(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="benchx :setup",
                                     description="Declare where bench runs and how risky it is.")
    parser.add_argument("--kind", default="local", choices=["local", "ssh", "docker"])
    parser.add_argument("--env", default="dev", choices=list(ENVIRONMENTS),
                        help="production and staging refuse a destructive verb without --confirm")
    parser.add_argument("--bench", default="~/frappe-bench", help="Bench directory AT THE TARGET")
    parser.add_argument("--site", default="", help="Default site; injected only where bench takes one")
    parser.add_argument("--host", default="", help="SSH host or address")
    parser.add_argument("--user", default="", help="SSH user")
    parser.add_argument("--key", default="", help="SSH identity file")
    parser.add_argument("--container", default="", help="Container name when kind is docker")
    parser.add_argument("--admin-password", default="", dest="admin_password",
                        help=f"Administrator password benchx pins on dev; also read from ${ADMIN_PASSWORD_ENV}, and never supplied on staging or production")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing config")
    parsed = parser.parse_args(argv)

    path = Path.cwd() / CONFIG_NAME
    if path.exists() and not parsed.force:
        print(f"{path} already exists; pass --force to replace it")
        return 1
    path.write_text(compose(parsed), encoding="utf-8")
    ignore_logs(Path.cwd())
    target = Target(*load())
    problems = target.problems()
    print(f"wrote {path} · {parsed.kind} · {parsed.env}")
    if parsed.env != "dev":
        print(f"  destructive verbs on {parsed.env} need safety.allow_destructive and "
              f"--confirm={parsed.site or '<site>'}")
    for problem in problems:
        print(f"  unresolved: {problem}")
    return 1 if problems else 0


SELF_VERBS = (":setup", ":where", ":check", ":explain", ":argv", ":help", ":lane")
"""benchx's own words, every one behind a colon that no click command can ever start with.

Reserving bare words was wrong twice over. `init` and `doctor` are real bench commands and the first
version made them unreachable; `setup` is worse still — `bench setup` is a click GROUP of around
twenty-five subcommands (nginx, supervisor, production, systemd, requirements), and it is precisely
what an operator runs on the unfamiliar remote machine this tool exists to serve.

A prefix beats a list. The rule an agent can apply to a verb it has never seen is one sentence — a
leading colon is benchx's own, everything else is bench, verbatim — where a reserved-word list has
to be memorised and goes stale the next time bench gains a command.
"""


def show_argv(target: Target, args: list[str]) -> int:
    problems = target.problems()
    if problems:
        print("FAIL config" + (f" · {target.origin}" if target.origin else ""))
        for problem in problems:
            print(f"  {problem}")
        return EXIT_CONFIG
    args, confirmed = split_confirm(args)
    verb = verb_of(args)
    refusal = (target.fan_out(args, verb) or target.missing_admin(args, verb)
               or target.refusal(verb, confirmed))
    command = target.build(args)
    print(f"verb    {verb or '(none)'}")
    print(f"kind    {target.kind}")
    print(f"would   {'RUN' if refusal is None else 'REFUSE'}"
          + ("" if refusal is None else f" — {refusal}"))
    print("argv")
    for item in command:
        print(f"  {item}")
    print(f"joined  {shlex.join(command)}")
    if target.kind == "ssh":
        print("at the target, unwrapped — this is what the login shell actually runs:")
        for depth in shlex.split(command[-1])[2:]:
            print(f"  {depth}")
    if target.pins_admin(args, verb) and target.admin_password:
        print("  note: the Administrator password above is supplied by benchx on a dev target only")
    return EXIT_OK


def describe(target: Target, verb: str) -> int:
    level = tier(verb)
    refusal = target.missing_admin([verb], verb) or target.refusal(verb, target.site)
    print(f"verb   {verb}")
    print(f"tier   {level}" + ("  (unknown to benchx, so treated as destructive)"
                               if level == "danger" and verb not in DANGEROUS else ""))
    print(f"site   {'injected' if verb in SITE_VERBS and target.site else 'not injected'}")
    print(f"secret {'redacted from the log' if verb in SECRET_BEARING else 'no'}")
    if verb in ADMIN_PASSWORD_VERBS:
        if target.env != "dev":
            print("admin  yours to pass; benchx pins one on dev only")
        elif target.admin_password:
            print("admin  pinned by benchx from the declared target")
        else:
            print(f"admin  none declared; benchx refuses {verb} until one is given "
                  f"(--admin-password, safety.dev_admin_password, or ${ADMIN_PASSWORD_ENV})")
    if verb in FIRST_SITE_ONLY:
        print("fanout --site all refused; this verb acts on the first site only and says nothing")
    if verb in AFTERMATH:
        print(f"after  on failure: {AFTERMATH[verb]}")
    print(f"here   {refusal or 'runs'}")
    if refusal is None and level == "danger" and target.env != "dev":
        print(f"       only because --confirm={target.site} was assumed for this explanation")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])

    if args and args[0] == ":setup":
        return setup(args[1:])

    if not args or args[0] in {":help", "--benchx-help"}:
        print("benchx — run bench at the target declared in .benchx.toml, and refuse there what the environment blocks.")
        print("\nusage: benchx <bench arguments>          run it at the declared target")
        for name, gist in ((":setup", "declare the target from flags"),
                           (":where", "the resolved target and every verb blocked there"),
                           (":check", "prove the config resolves, then run `bench version`"),
                           (":explain <verb>", "what benchx would do with it, without running it"),
                           (":argv <bench args>", "the exact command line it would run, and no run"),
                           (":lane new [--name]", "create this agent's own site and pin it"),
                           (":lane drop [--name]", "drop the agent's own lane site, refuse every other"),
                           (":lane ls", "list every lane-*.localhost site with its size and age")):
            print(f"       benchx {name:22s} {gist}")
        print("\nA leading colon is benchx's own. Everything else is bench, verbatim — "
              "`bench init`, `bench setup`, `bench doctor` all pass through untouched.")
        return EXIT_OK

    target = Target(*load())

    if args[0] == ":where":
        if target.origin is None:
            print(f"no {CONFIG_NAME} found")
            return EXIT_CONFIG
        print(f"kind   {target.kind}" + (f" · {target.user}@{target.host}" if target.host else ""))
        print(f"env    {target.env}")
        print(f"bench  {target.bench}")
        print(f"apps   {target.apps_dir()}")
        print(f"site   {target.site or '(none declared)'}")
        print(f"config {target.origin}")
        print(f"logs   {target.log_dir}")
        blocked = target.blocked()
        print(f"blocked {' '.join(blocked) if blocked else '(nothing — every verb runs here)'}")
        print("        plus any verb benchx does not know, which it treats as destructive")
        return EXIT_OK

    if args[0] == ":argv":
        return show_argv(target, args[1:])

    if args[0] == ":explain":
        return describe(target, args[1] if len(args) > 1 else "")

    problems = target.problems()
    if problems:
        print("FAIL config" + (f" · {target.origin}" if target.origin else ""))
        for problem in problems:
            print(f"  {problem}")
        return EXIT_CONFIG

    if target.origin is not None and target.origin.parent != Path.cwd():
        print(f"using {target.origin} · {target.env} · {target.kind}")

    if args[0] == ":check":
        return run(target, ["version"])
    if args[0] == ":lane":
        return lane_main(target, args[1:])
    return run(target, args)


if __name__ == "__main__":
    raise SystemExit(main())
