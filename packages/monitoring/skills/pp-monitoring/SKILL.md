---
name: pp-monitoring
description: Declare an analysis over an instance or an archive of traces, play its playbook on a disposable repo, and render the measure -- the volume by function and package, the engine's effort, the agent's time. The one writer of monitoring.json.
---

# `pp-monitoring` — the analyses of the measure

## Entities

The MEASURE is the engine's: every block weighed, the payloads itemized, the
skills it runs named, all of it in the run's trace. This script only exploits
that trace. `refs/METRICS.md` says the frame — the fields, the functions they
discriminate, the token estimator (~10 % at worst, no dependency).

| Entity | Storage and fields |
|---|---|
| Analysis | `.sys/records/monitoring.json`: name → `{repo, scenario, packages}`, or `{archive}` |
| Playbook | one codified scenario book, grammar at `refs/PLAYBOOK.md`: the required composition, `## S<n>` sessions each played as its own run, an optional `shell:` fixture, the `\|id\|gesture\|expected\|` table |
| Derived repo | a disposable instance built from THIS one: engine and pins copied whole, the operator's SETTINGS and FORMATS with them, a NEUTRAL member, records born empty |
| Trace | the `session-*.jsonl` files a run leaves under `.sys/state/` — what `report` reads |
| Archive | a directory a campaign left its traces in: `session-*.jsonl` directly under it, a `transcripts/` folder beside them, the `SETTINGS.md` and `instance.yaml` it kept |
| Transcript | the harness's own log of the session (Claude today), paired with a run by `conduite` |

An analysis is declared once and played or read as many times as needed. An
ARCHIVE analysis reads what a campaign kept; what the archive did not keep is
said unknown, and its composition being unknown, the volume by package
attributes the protocol's own alone.

## Commands

Prefix each form with `./pp <key> -s pp-monitoring`:

    ./pp <key> -s pp-monitoring setup nightly ./derived refs/PLAYBOOK.md

| Form | Effect |
|---|---|
| `setup <name> <repo> <playbook>` | Declare an analysis over an installed instance (`<repo>` is its meta, or a workspace holding one) and a playbook. |
| `setup <name> <archive-dir>` | Declare an analysis over an archive: `report` and `conduite` play on it, `run` never does. |
| `derive <dir> [--fusion none\|max\|<n>]` | Build the disposable repo a playbook is meant to play on, from this instance; `--fusion` pins the derived SETTINGS. |
| `run <name>` | Drive the declared repo's own console through the playbook — `-new`, the messages, minimal answers — and collect its traces. Refuses `capture-off` while `monitoring_capture` is false. |
| `report <name>` | Render the analyses from the collected traces (below). |
| `conduite <name>` | Render the session as it HAPPENED, per turn: the operator's message, the `pp` calls with the blocks they served, the agent's chat — read from the transcript paired with the run (claude provider only). |
| `list` | The declared analyses. |
| `wire <provider>` | Write the harness link: for `claude`, the Stop hook that plays `./pp monitoring-stamp` into an ABSENT `.claude/settings.json`; a present file is never touched, the snippet is printed and the skip said. |
| `stamp` | The `turn-end` stamp on the freshest trace — the package's console command `./pp monitoring-stamp` plays it; silent while the switch is off. |

**What `report` renders.** The volume by SUBJECT and by PACKAGE (tokens always
said `~`); the by-turn table — the operator's message, the functions the turn
touched, its volume, its agent seconds, the engine's milliseconds; the engine's
providers and sinks with their milliseconds; the AGENT TIME per function where
`turn-end` stamps exist, said unknown otherwise, never guessed; and the LEVERS —
one line per setting, its value as the source's SETTINGS spell it and the
figure the traces charge to it: the bodies re-served within a run, the
readings, the laws' share, the proofs, the repairs, the cuts, the blocks per
turn, each package's tokens by the provider lines they left.

## Effective settings

| Key | Default | Effect |
|---|---:|---|
| `monitoring_capture` | false | Arms `run` and the Stop hook's stamp; off by default so the switch works in production. |

## Refusals

Refusals exit 2 and write nothing:

| Code | When |
|---|---|
| `analysis-unknown` · `analysis-taken` | the record decides, never memory |
| `name-invalid` | not kebab-case, or over 60 characters |
| `budget` | more than 20 analyses |
| `repo-not-instance` | no `.sys/instance.yaml` at or under the given path |
| `scenario-missing` | no session with gestures |
| `composition-short` | the repo's pins lack a package the playbook requires |
| `fixture-failed` | a session's `shell:` fixture returned non-zero |
| `target-not-empty` | `derive` on a directory that holds files |
| `capture-off` | `monitoring_capture` is false: the measure is not armed |
| `archive-empty` | no `session-*.jsonl` directly under the archive directory |
| `analysis-archived` | `run` on an archive analysis: an archive is read, never played |
| `provider-unknown` | no `providers/<name>/` in this package (claude only, today) |
| `transcript-missing` | no Claude transcript for the analysis's repo (`conduite`) |

Running outside an installed instance refuses: there is nowhere to write. An
unknown verb prints the usage and exits 2.

## What you never do

- You never edit `monitoring.json` by hand: this script is its only writer.
- You never run a scenario against the production instance itself: declare a
  disposable repo (`derive`), and play there.
