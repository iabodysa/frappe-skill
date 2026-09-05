# Raw bench and benchx (§18)

This file is INSTRUCTION. It carries no citation and no `file:line`. The live surface is
`benchx :help`, `benchx :explain <verb>`, `benchx :where` and `benchx :argv <bench args>`; a verb
this page names is a worked example of a judgement, never the register of what benchx knows.
MUST NOT open `tools/benchx.py` to learn what benchx does; the only reason to read that source is a
fix TO benchx — a missing signature, a misclassified verb, a wrong refusal.

The verdict this page settles: **raw `bench` and `benchx` are not two styles of one call.** They
differ on what a zero exit means, on what a flag reaches, and on what the run leaves behind. Every
part below names a place where the raw call succeeds and the operator is wrong.

---

## Part 1 — the four ways raw bench lies quietly

MUST assume each of these is present until benchx has ruled it out. None of them raises, none of
them prints a warning, and every one of them ends in exit code zero.

1. **A zero exit over a failing suite.** Outside CI, `bench run-tests` returns zero while its own
   summary line reports failures. The exit code is not the verdict; the summary line is.
2. **A fan-out flag that reaches one site.** `restore`, `reinstall`, `console`, `run-tests` and
   `set-maintenance-mode` accept `--site all`, then act on the FIRST site alone and say nothing
   about the rest. benchx refuses that pair rather than letting it run.
3. **A password nobody chose.** Omitting the Administrator password on site creation is not "no
   password"; frappe falls back to a value the operator never picked, and a site nobody can log
   into has to be rebuilt.
4. **State left set by a failed run.** A verb that writes a flag before its first step and clears
   it after its last one leaves that flag set when a middle step fails — `update` is the worked
   case, and it leaves the whole bench offline. The failure message names the step, never the flag.

MUST read the `after` line of `benchx :explain <verb>` before running any verb whose tier is
`danger`, because the recovery is per-verb and only that line carries it.

---

## Part 2 — the tier decides the call, and the tier is benchx's word

Every verb carries exactly one tier. MUST read the tier as the instruction for how to call it.

| tier | what it means | the move |
|---|---|---|
| `read` | no write reaches the site | call it; read the verdict and stop |
| `write` | it changes the bench or the site and is recoverable | call it; read the excerpt on FAIL |
| `danger` | it destroys, migrates, reinstalls or takes the bench offline | read `:explain` first; on `staging` and `production` type `--confirm <site>` |
| `interactive` | it owns a terminal and never returns under capture | do NOT route it through benchx; run bench directly |

MUST treat a verb benchx does not know as destructive; it blocks every verb absent from the
`blocked` line of `benchx :where`. An unknown verb is not a permission to improvise — it is the
signal that the tier table has a gap, and the gap is a fix to benchx.

MUST NOT read `console` as an exception worth arguing. benchx captures output, so an interactive
verb reports a healthy prompt as a timeout. The refusal is the correct answer.

---

## Part 3 — reading the verdict, and the one that is not a failure word

Three verdicts, and only two of them are obvious.

- `OK` — MUST stop at the verdict line. The transcript beneath it is for a later question, not for
  this one.
- `FAIL` — the excerpt under it is the lines that CAUSED it, not the tail of the log. MUST widen
  `[output] max_excerpt_lines` when an excerpt cuts a cause in half, and MUST read the widened
  excerpt rather than guessing the missing half.
- `SUSPECT` — bench exited zero and its own output says the work did not happen. MUST treat it as a
  failure: a suite that reported failures, a patch that was skipped, an app that was already
  installed. This is the verdict raw bench cannot produce, and it is the whole reason for the tool.

MUST treat `no known signature matched` as a real answer and not as a benchx defect. The classifier
missed; the failure is still on the screen and in the log. MUST add the signature to
`tools/benchx.py` once its cause is known — that is the one edit to benchx this page authorises.

---

## Part 4 — a refusal names the move; MUST NOT work around it

| refusal | the move it names |
|---|---|
| `no .benchx.toml found` | `benchx :setup` — the target lives in the config, never in the source |
| a missing key by name | fill that key; a raw bench call would only say this is not a bench directory |
| `--site all` refused on a first-site verb | name exactly one site |
| destructive verb blocked | the environment blocks it; `safety.allow_destructive` is machine-wide, not per-command |
| a destructive verb on `staging` or `production` | type `--confirm <site>` at the call site |
| an Administrator password declared outside `dev` | benchx reports a declared password on `staging` and `production` as a problem; supply it at the call site instead |

MUST NOT rename a route around a refusal. A wrapper bypasses identically, and the refusal was the
only thing standing between a typed command and a live database.

---

## Part 5 — the environment is a fact, not a lever

`target.env` decides what may run: `dev` runs whatever the safety switch allows; `staging` and
`production` refuse a destructive verb until the site name is typed as `--confirm <site>`, because a
confirmation given by reflex has confirmed nothing.

MUST keep `env` at what the machine actually is. Lowering it to get a command through converts a
refusal into a production incident, and the config keeps no record that it was lowered.

MUST read the `blocked` line of `benchx :where` before promising an operator that a command is safe,
and MUST NOT answer that question from this page.

---

## Part 6 — the ssh composition is the one thing a local success does not vouch for

The ssh branch builds a SHELL STRING; the local branch builds an argv. A command that ran correctly
against a local bench proves nothing about the same command against a remote one — quoting,
expansion and word splitting all enter on the remote path and on no other.

MUST audit a remote target with `benchx :argv <bench args>` before trusting it, and MUST read the
printed line rather than reconstructing it mentally from the flags that were passed.

---

## Part 7 — the colon is the namespace

MUST reach benchx's own verbs through a LEADING COLON. A bare word reaches bench itself, verbatim.
`bench init`, `bench setup` and `bench doctor` are real bench commands, and reserving those names
inside benchx would make them unreachable — which is why benchx owns `:setup` and not `setup`.

---

## What this page does not hold

The consequences of a specific bench verb are FACTS and live as leaves, not here:
[[bench-setup-config-writes-the-defaults-over-nine-keys-the-operator-set]],
[[generating-the-supervisor-conf-writes-three-config-keys-and-one-lands-in-the-current-directory]],
[[the-nginx-conf-is-rendered-from-the-common-config-and-rate-limiting-raises-a-typeerror]],
[[the-mariadb-root-password-is-read-from-the-common-config-before-any-prompt]],
[[a-second-new-site-keeps-the-first-site-config-and-its-password]].

The per-verb register — tier, site injection, secret handling, fan-out and the `after` line — lives
in `benchx :explain <verb>` and is read at call time, because a register copied into prose is a
second home that will disagree with the tool.
