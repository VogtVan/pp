# continuity

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.2.0`

`continuity` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace a durable memory of its work: recent operations return at boot,
the agent records a fact worth keeping as soon as it holds one, and a weekly digest connects
the period's decisions and milestones.

The package keeps recall separate from narration. Earlier work is supplied as ground
for the agent and is mentioned only when the current answer needs it.

## Role

A conducted run holds the procedure and its immediate context, but useful work often
outlives one session. `continuity` preserves the small set of facts that a later
session needs without turning every new conversation into a replay of the record.

It provides a method for answering three recurring questions:

- Which recent facts should ground this session before new work begins?
- What progress, regression or decision from the current span is worth preserving?
- What does the accumulated work amount to over the week?

## Features

### `RECALL` — ground a new session

Brings recent operations into the boot block in recording order. The configured
period defines how far back it reads; a value of zero recalls nothing.

The recall is working context, not a report. The agent uses it to avoid repeating
work and cites a recorded fact only when the current answer needs it. It is served
again after a declared context compaction so the restored run regains the same
ground.

### Operations — preserve facts worth another session

The package adds a section to the standing orders of every run: it tells the agent
what an operation is and to record one with `pp-continuity register` whenever a fact
is worth keeping, at any moment of an exchange. No procedure asks for it at a set
rhythm, so a fact is recorded when it happens, not a few exchanges later.

Each operation is one concise, dated fact that stands on its own for a reader who was
absent: progress, a regression, a decision, a measure with its figure. An entry is
never edited; a wrong one is corrected by a new entry that names it.

### `HISTORY` — give the week at a glance

Synthesizes the period since the previous digest into one durable paragraph. It
connects recorded work, decisions and milestones rather than reproducing the
operation log, then gives the same digest to the operator.

The digest is anchored to a configurable weekday and runs at the first boot at or
after that point. Setting the anchor to `never` disables it.

### Cadence and budgets

The package adds four `continuity_` settings to the instance:

- `continuity_history_day` selects the weekly digest's weekday or disables it with
  `never`.
- `continuity_recall_days` sets the boot recall period; `0` disables recall.
- `continuity_entry_budget` limits one operation to 500 characters by default.
- `continuity_digest_budget` limits one digest to 1,500 characters by default.

A budget of zero removes that limit. Text over an active budget is refused and the
record is left untouched.

### The records

`operations.jsonl` and `history.jsonl` are written by `pp-continuity` alone, one line
per entry, appended under the record's lock: two sessions of one workspace never mix
their lines. A reader skips a last line still being written; a line that does not
parse anywhere else refuses -- the file is not for hand edits.

## Installation

`continuity` requires the `kit`; the installer pulls it automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> continuity -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add continuity
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start). Recall joins the boot automatically; the
agent records operations as it works, and the digest appears when its day is due.

## Quick start

The defaults recall seven days of operations and anchor the weekly digest on Monday.
Start a new conducted conversation and work normally: the package supplies recent
facts at boot, and the agent records new ones as they happen.

Tune the behavior in `.pp/SETTINGS.md` when the workspace needs a different rhythm:

```yaml
continuity_history_day: friday
continuity_recall_days: 14
continuity_entry_budget: 500
continuity_digest_budget: 1500
```

Use a shorter recall for a fast-moving workspace, a longer one for work spread over
several sessions, and `never` when a weekly digest would add no value. The operation
and digest records remain concise by design: they carry durable facts and synthesis,
not full transcripts.
