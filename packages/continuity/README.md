# continuity

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.1.0`

`continuity` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace a durable memory of its work: recent operations return at boot,
facts worth keeping are consigned at the turn's tail, and a weekly digest connects
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

### `OPERATIONS` — preserve facts worth another session

Opens at the tail of a due turn and covers the work since the previous consignation,
including the current exchange. It keeps progress, regressions and decisions that
will still matter to a reader who was absent.

Each operation is one concise, dated fact that stands on its own. When nothing in
the span deserves durable memory, the record remains unchanged. The frequency is
configurable and follows the package's effort preset unless the workspace chooses
its own cadence.

### `HISTORY` — give the week at a glance

Synthesizes the period since the previous digest into one durable paragraph. It
connects recorded work, decisions and milestones rather than reproducing the
operation log, then gives the same digest to the operator.

The digest is anchored to a configurable weekday and runs at the first boot at or
after that point. Setting the anchor to `never` disables it.

### Cadence and budgets

The package adds five `continuity_` settings to the instance:

- `continuity_memory_frequency` controls how many exchanges pass between operation
  consignations; `0` disables them.
- `continuity_history_day` selects the weekly digest's weekday or disables it with
  `never`.
- `continuity_recall_days` sets the boot recall period; `0` disables recall.
- `continuity_entry_budget` limits one operation to 500 characters by default.
- `continuity_digest_budget` limits one digest to 1,500 characters by default.

A budget of zero removes that limit. Text over an active budget is refused and the
record is left untouched.

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
[Quick start](../../README.md#quick-start). Recall joins the boot automatically;
operation consignation and the digest appear only when their cadence is due.

## Quick start

The defaults recall seven days of operations, consign work every three exchanges at
the medium effort level, and anchor the weekly digest on Monday. Start a new conducted
conversation and work normally: the package supplies recent facts at boot and offers
to preserve new ones at the configured tail of the turn.

Tune the behavior in `.pp/SETTINGS.md` when the workspace needs a different rhythm:

```yaml
continuity_memory_frequency: 1
continuity_history_day: friday
continuity_recall_days: 14
continuity_entry_budget: 500
continuity_digest_budget: 1500
```

Use a shorter recall for a fast-moving workspace, a longer one for work spread over
several sessions, and `never` when a weekly digest would add no value. The operation
and digest records remain concise by design: they carry durable facts and synthesis,
not full transcripts.
