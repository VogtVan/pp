---
name: pp-monitoring
description: >-
  Set up an ANALYSIS over one or several packages, play its scenario and render
  the analyses: `setup` declares {repo, scenario, packages} in monitoring.json
  (this skill's own record), `run` drives the declared repo's console through a
  scripted session -- gated by the `monitoring_capture` setting -- and collects
  its trace, `report` renders the volume by function and package, the engine's
  own effort, and the agent time where a `turn-end` stamp closed the tail.
  Deterministic, atomic, budget-guarded.
---

# `pp-monitoring` — the analyses of the measure

## What it is

A **local, deterministic script**: the one writer of `monitoring.json` — an
analysis is `{repo, scenario, packages}`, declared once, played and read as
many times as needed. The MEASURE itself is the engine's (every block weighed,
payloads itemized, engine-run skills named): this skill only exploits the
trace. The reference `METRICS.md` says the frame — the fields, the functions
they discriminate, the token estimator (~10 % at worst, no dependency).

## How to call it

```
./pp <key> -s pp-monitoring setup <name> <repo> <playbook>
./pp <key> -s pp-monitoring setup <name> <archive-dir>
./pp <key> -s pp-monitoring derive <dir> [--fusion none|max|<n>]
./pp <key> -s pp-monitoring run <name>
./pp <key> -s pp-monitoring report <name>
./pp <key> -s pp-monitoring conduite <name>
./pp <key> -s pp-monitoring list
./pp <key> -s pp-monitoring wire <provider>
```

`<repo>` is an installed instance (its meta, or a workspace holding one); the
PLAYBOOK is the one codified scenario book -- `refs/PLAYBOOK.md` says its
grammar (the required composition, `## S<n>` sessions each played as its own
run, an optional `shell:` fixture, the `|id|gesture|expected|` table).
`derive <dir>` builds the disposable repo from THIS instance -- the engine and
the pins copied whole, the operator's SETTINGS and FORMATS with them, a
NEUTRAL member, records born empty -- the repo a playbook is meant to play on.
`wire claude` writes the harness link — the Stop hook that plays `./pp monitoring-stamp`
(this package's command, SILENT while the switch is off) — into an ABSENT
`.claude/settings.json`; a present file is never touched: the exact snippet is
printed and the skip said (`providers/claude/` carries the data and its
reference). `run` drives the repo's own console — `-new`, the messages, minimal answers —
so it works on any instance the operator declares, and refuses `capture-off`
while `monitoring_capture` is false: the switch works in production, off by
default. `conduite` renders the session as it HAPPENED — per turn, the operator's
message, the `pp` calls with the conduction blocks they served, and the agent's
chat — read from the Claude transcript paired with the run (claude provider only).
`report` reads the collected traces: volume by SUBJECT and by
PACKAGE (tokens always said `~`), the by-turn table (the operator's message,
the functions the turn touched, its volume, its agent seconds, the engine ms),
the engine's providers and sinks with their milliseconds, the AGENT TIME per
function where `turn-end` stamps exist — said unknown otherwise, never
guessed — and the LEVERS: one line per setting, its value as the source's
SETTINGS spell it and the figure the traces charge to it (the bodies re-served
within a run, the readings, the laws' share, the proofs, the repairs, the cuts,
the blocks per turn, each package's tokens by the provider lines they left).

An ARCHIVE analysis — `setup <name> <archive-dir>` — reads the directory a
campaign left its traces in (`session-*.jsonl` directly under it, a
`transcripts/` folder beside them for the operator's messages and the LLM, the
`SETTINGS.md` and `instance.yaml` it kept for the header): `report` and
`conduite` play on it with the same grammar as on a live instance, `run` never
does. What the archive did not keep is said unknown; its composition is not
known, so the volume by package attributes the protocol's own alone.

## Guards (exit 2, nothing written)

- `analysis-unknown` · `analysis-taken` — the record decides, never memory;
- `name-invalid` — kebab-case, 60 characters at most; `budget` — 20 analyses;
- `repo-not-instance` — no `.sys/instance.yaml` at or under the given path;
- `scenario-missing` — no session with gestures;
- `composition-short` — the repo's pins lack a package the playbook requires;
- `fixture-failed` — a session's `shell:` fixture returned non-zero;
- `target-not-empty` — `derive` refuses a directory that holds files;
- `capture-off` — `monitoring_capture` is false: the measure is not armed;
- `archive-empty` — no `session-*.jsonl` directly under the archive directory;
- `analysis-archived` — `run` on an archive analysis: an archive is read, never played;
- `provider-unknown` — no `providers/<name>/` in this package (claude only, today);
- `transcript-missing` — no Claude transcript for the analysis's repo (`conduite`);
- run outside an installed instance refuses — there is nowhere to write.

## What you never do

- You never edit `monitoring.json` by hand — this script is its only writer.
- You never run a scenario against the production instance itself — declare a
  disposable repo; the codified derivation is the phase's own batch.
