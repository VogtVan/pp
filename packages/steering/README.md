# steering

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `0.7.3`

`steering` is a package for [Procedural Prompting](../../README.md). It gives a
conducted workspace an operator-facing work surface: initiatives become named
threads, their required units of work become ordered steps, and every answer closes
on the current front and the decisions still owed.

The package makes the agent responsible for keeping the work organised. The operator
supervises priorities and decisions without having to maintain the thread register.

## Role

Long-running work rarely follows one uninterrupted checklist. New findings create
steps, priorities change, some work waits, and several initiatives may need the same
result. `steering` keeps that changing structure explicit between exchanges while
leaving discussion, findings and reports in the chat.

It provides a method for answering four recurring questions:

- Which initiatives are open, and why does each one matter now?
- Which units of work remain, in what order, and under which initiative?
- What changed in the work during this exchange?
- Which decisions or actions should the operator consider next?

## Features

### `LEDGER` — restore the open work at boot

Brings every open thread into the first session block with its id, name, note and
unfinished steps. Each step carries its own id, name, text or waiting reason, and any
key that relates it to another package's work.

The ledger is the session's source of truth. It is served again after a declared
context compaction; between those points the agent relies on the ledger and on the
changes made during the current session instead of repeatedly reading the records.

### `THREADS` — keep initiatives and steps true

Runs at the tail of every turn. The agent detects initiatives in the operator's asks,
breaks them into units of work and keeps their order, notes and progress aligned with
what the exchange established.

A thread represents an initiative and its reason. A step represents a result that
cannot be skipped. Steps may move to the initiative they serve, but their identity
and any key remain stable. Work still due stays visible; a thread closes only after
all of its listed steps have been completed or deliberately dropped, with at least
one completed step.

The agent may open, reorder, move, annotate and close work on its own. An initiative
the operator names remains theirs: it is not renamed, emptied or closed without their
word. Every change made during the pass is reported in one short line, and the pass
ends by naming the top thread and what remains to finish it.

### `NEXT` — end on the current front

Closes the answer with the rendered steering surface. Active threads appear as a
table with their note, progress, age and next actions. Waiting steps move to the `⏸`
line, while older inactive work may fold into the `💤` line so the live front stays
readable without hiding anything due.

After the front, the agent offers at most two key actions that still require the
operator. Each choice names the work it unlocks and where that need came from. When
no operator decision is due, no choice is invented.

### Stable identities and bounded records

The family `steering-thread:<thread id>` lets another package refer to one thread
without depending on its display name. The thread and step ids are available from
the boot ledger and from the result that creates a new entry.

The package adds `steering_` settings for step text, names, notes, front rows, next
actions, waiting lines and dormancy. Names use kebab-case; notes hold an initiative's
reason and current context; step text complements the step's name instead of
restating it. Invalid whole-number settings or text over an active budget are
refused rather than silently accepted; when another package projects a longer step
text across the package boundary, the text is shortened to the budget and reported.

## Installation

`steering` requires the `kit`; the installer pulls it automatically.

For a new workspace:

```sh
uv run procedural-prompting/engine/pp.py -install <workspace> steering -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add steering
```

Then start the configured host as described in the main
[Quick start](../../README.md#quick-start). The open-work ledger joins the boot, and
the thread pass and steering surface join the end of each turn.

## Quick start

Work normally and let the agent derive initiatives and steps from the conversation.
You can also name an initiative when its identity or priority matters:

```text
Treat reducing the boot cost as one initiative. First measure the current block,
then identify the largest avoidable reading, and keep the implementation behind my
GO.
```

The agent keeps the initiative's note current, records the dependent steps in order
and shows the live front at the end of the answer. Correct its organisation in plain
language when needed:

```text
Move the documentation step under the release initiative.

This thread is waiting for the upstream API decision.

The migration initiative is now the priority.
```

The register is the agent's responsibility; those instructions express operator
intent rather than a requirement to maintain ids or records by hand.
