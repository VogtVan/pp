# steering

> **Experimental package.** Its procedures, records and user-facing behavior
> may change between versions.
>
> **Current version:** `1.2.0`

`steering` is a package for [Procedural Prompting](../../README.md). It keeps the
work owed in a conducted workspace as **steps**: a defect to fix, an idea to explore,
a follow-up, a question to settle. The agent adds, closes and drops them as it works,
the way it uses a shell; nothing waits for a procedure to ask.

## Role

Work rarely fits one checklist. Findings create work, priorities move, some work
waits, and what was owed is easy to lose when an exchange ends. `steering` keeps that
work in one record, `steps.json`, written by its skill `pp-steering` alone.

It answers four questions:

- What is still owed in this workspace, and since when?
- What did this exchange add, close or drop?
- What is old, waiting, or grouped under the same label?
- How fast is work closed?

## Features

### Steps and labels

A **step** is one unit of work owed, from one exchange of real work to a few: never a
single gesture such as merging a pull request or running an upgrade. A step has a
name, a work text written to be understood alone, a comment that says what happened
to it since, a status (`open`, `waiting`, `done`, `dropped`), the date it was added,
the date it was closed, and optional labels and key. Its name and its work never
change; its comment does.

A **label** groups steps: a large task broken into steps, steps to treat together, or
a line of thought that produces steps. Dissolving a label leaves its steps as they are.

### What the agent sees

- **At the start of every run**, the steps left untouched for `steering_life_days`
  (15 by default), or beyond `steering_active_max` (60), are archived, then the active
  steps still to do are served one line each. A last line names the steps archived at
  that moment.
- **During the exchange**, the standing orders tell the agent to carry every piece of
  work of a step's size by a step, to add what it notices is owed, and to close what it
  delivers.
- **At the end of its work**, before the choices, the agent writes one line that names
  the steps the exchange added, closed and dropped: `Steps: + name · ✓ name · ✗ name`.
  No line when nothing moved.
- **At the end of every answer**, `NEXT` offers the two best next choices.

### Views and batch changes

`pp-steering` reads the steps by their fields, never by their text:

| verb | what it shows |
|---|---|
| `board` | the counts by status, the last 7 days, the time to closure and the age of the steps still to do, the least recently touched, each label with its freshest steps |
| `labels` | one line per label, its note and its counts |
| `list` | the steps, filtered by label, status, family of key (`--key plan-lot`, repeatable), age (`--older 7d`, `--newer 3d`) or birth date (`--since`, `--before`), grouped with `--by label`, `--by age` or `--by status` |
| `show`, `review` | one step whole; the steps still to do, the least recently touched first |

The agent may build a view of its own from these on request ("the steps about the
engine"), and change many steps at once with `apply`: all the changes are written in
one go, or none.

### The STEERING space

`-open STEERING` opens a space where the principal has the agent work on the steps as
a whole. It opens on the board, said as tables: the steps by status, the last 7 days,
how long steps take to close and how old the steps still to do are, the least recently
touched, and each label with its freshest steps. From there the principal asks for any
view, has the agent group the steps under labels, close what is done, drop what is no
longer due or bring an archived step back; a change to several steps is shown first in
one table, then made in one batch. `-close` gives the turn back.

### Reading the steps outside a run

```sh
./pp steering board
./pp steering list --by label
./pp steering labels --json
```

The console verb reads only: `board`, `labels`, `list`, `show` and `review`. Every
change is made by the agent, in a run.

## Installation

`steering` requires the `kit`; the installer pulls it automatically.

For a new workspace:

```sh
uv run pp/engine/pp.py -install <workspace> steering -<provider>
```

For an existing pp instance, from the workspace root:

```sh
./pp add steering
```

## Settings

| key | default | what it tunes |
|---|---|---|
| `steering_step_budget` | 100 | the characters a work, a comment or a reason holds |
| `steering_name_max` | 60 | the characters a step name or a label holds |
| `steering_note_budget` | 80 | the characters a label's note holds |
| `steering_life_days` | 15 | the days a step stays active without being touched |
| `steering_active_max` | 60 | the steps still to do that stay active at most |
| `steering_board_per_label` | 3 | the steps `board` shows under each label |

## Quick start

Work normally: the agent adds the steps it finds owed and closes them as the work
lands. Then ask for a view:

```text
Show me the steps older than a week, grouped by label.

Drop the ones about the old thread model, and close those the last release delivered.
```

The agent answers with the view, proposes the changes in one table, and applies them
in one batch on your word.
