---
name: pp-steering
description: Reference for the steps of work -- the record, the verbs that add, comment, close, label, list, archive and recall steps, the settings and the named refusals.
---

# pp-steering — the steps of work

`pp-steering` is the only writer of `.sys/records/steps.json`. Use its verbs for every
change; never open the record yourself. Every write takes the engine's lock and
replaces the record whole, or writes nothing.

    ./pp <key> -s pp-steering <verb> <arguments>

Outside a run, the console reads the steps with `./pp steering <verb>`: `board`, `labels`,
`list` (without `--sweep`), `show` and `review`, the same output as in a run. It changes
nothing: a move is played in a run.

## What a step is

A step is one unit of work owed in this workspace. It holds:

| Field | Meaning |
|---|---|
| `id` | `<member>.s.<n>`, from a counter that never goes back. Every verb takes it, whole or short: `s.<n>` for a step of this instance's member. |
| `name` | Lowercase words joined by hyphens, such as `the-first-step`. The step's name for the principal. Fixed when the step is added. |
| `work` | What to do, where and why, written to be understood alone, months later. Fixed when the step is added. |
| `comment` | What happened to the step since: a figure, a pointer, the state reached. Rewritten freely. |
| `status` | `open`, `waiting`, `done` or `dropped`. |
| `reason` | Why the step waits, or why it was dropped. Empty otherwise. |
| `labels` | The labels the step carries: none, one or several. |
| `key` | Optional `<family>:<slug>`: the address of this work in another package, verified, one step per key. |
| `at` | When the step was added. |
| `touched` | When its comment or its status last moved. |
| `closed` | When `done` or `drop` closed the step; empty while it is still to do. |
| `archived` | When `sweep` archived the step; empty while the step is active. |
| `recalled` | When `recall` last brought the step back; empty otherwise. |

When you report to the principal, name a step by its `name`; give its `id` beside it
when a next call needs it. Every text rendering of this script shows both, the id short;
the data (`--json`) gives the whole id.

A step's AGE runs from `recalled` when it is set, from `touched` otherwise.

The `name` and the `work` never change. When the work itself changes, drop the step with
its reason and add a new one.

A name is unique among the steps still to do (`open`, `waiting`). Once a step is `done`
or `dropped`, its name is free again.

## What a label is

A label is a name, written like a step name, that groups steps: a large task broken into its steps, steps
to treat together, or a line of thought that produces steps. A label holds a `note` (why
it exists) and an `order` (the ids of its steps, in the order wanted). Dissolving a label
removes it from the record and from every step; the steps stay as they are.

## The verbs

    add <name> <work ...> [--label <label>]... [--key <family:slug>]
    comment <id> <text ...>
    done <id>
    drop <id> <reason ...>
    wait <id> <reason ...>
    open <id>
    label <id> +<label> | -<label> ...
    note <label> <text ...>
    order <label> <id> ...
    dissolve <label>
    list [--label <label>] [--status <status>]... [--key <family>]... [--older <n>d] [--newer <n>d]
         [--since <date>] [--before <date>] [--all | --archived]
         [--by label|age|status] [--sweep] [--json]
    show <id> [--json]
    board [--json]
    labels [--all | --archived] [--json]
    apply -
    view <verb> <arguments>
    sweep
    recall <id>
    review [--json]

| Verb | Effect |
|---|---|
| `add` | A new step, `open`, dated now. It answers with the name and the id. A label named by `--label` is created when it does not exist yet. |
| `comment` | Rewrites the comment; an empty text clears it. Dates `touched`. |
| `done` | The work is delivered. Clears the reason. Dates `touched` and `closed`. |
| `drop` | The work no longer has to be done; the reason says why. Dates `touched` and `closed`. |
| `wait` | The work waits; the reason says for what. Dates `touched`, empties `closed`. |
| `open` | The step is back to work, its reason cleared. Dates `touched`, empties `closed`. A step reopened takes its name back: no other step still to do may wear it. |
| `label` | Adds (`+`) or removes (`-`) labels. A new label is created; the step joins the end of its order. |
| `note` | Rewrites a label's note. |
| `order` | Puts the given steps first in the label's order, in the order given; the others follow as they were. |
| `dissolve` | Removes the label from the record and from every step. |
| `list` | The active steps still to do, the most recently touched first, one line each: name, id, status when not `open` (with its reason), labels, key, age, then the work. `--all` adds the steps `done` and `dropped`; `--status` keeps the statuses named, closed ones included; `--archived` shows the archived steps instead, whatever their status; `--label` keeps the steps of one label; `--key <family>` keeps the steps whose key is of that family, such as `plan-lot`, and may be repeated; `--older <n>d` and `--newer <n>d` keep the steps older or younger than n days of age; `--since <date>` and `--before <date>` keep the steps born from that date, or before it. `--by label`, `--by age` or `--by status` groups the lines under one title per group with its count: a step with several labels stands under each, the steps without a label last; the age slices are under 1 day, 1-3, 3-7, 7 to `steering_life_days`, and beyond. `--sweep` sweeps first, then lists, and names on a last line the steps it has just archived. `--json` returns the same steps as data, each with its `id`, in groups under `--by`. No filter reads a step's work, comment or name. |
| `board` | The steps at a glance, read from their fields: the counts by status, active and archived; the last 7 days (born, done, dropped, archived, recalled); the time from birth to closure and the age of the steps still to do (the median, the value nine steps in ten stay under, and the longest); the five least recently touched; each label with its counts and its `steering_board_per_label` most recently touched steps; the steps without a label. `--json` returns it as data. |
| `labels` | One line per label: its note, its counts by status, its least and most recently touched step -- among the active steps still to do, all active steps with `--all`, the archived ones with `--archived`. |
| `view` | Plays one reading -- `board`, `labels`, `list` without `--sweep`, `show`, `review` -- and refuses anything else. The console verb `./pp steering` is `view`. |
| `apply` | Reads moves on its standard input, one per line: `done`, `drop`, `wait`, `open`, `comment`, `label` or `recall`, then the id and the words the verb takes. Every move is judged in order before anything is written: they are all written at once, or none. One line is said per move. |
| `show` | One step, whole; `--json` returns it as data. |
| `sweep` | Archives every step whose age passes `steering_life_days`, then, among the steps still to do, the least recently touched past `steering_active_max`. One line per step archived. It changes `archived` and nothing else. |
| `recall` | Brings an archived step back: `archived` emptied, `recalled` set now, so its age restarts. It changes those two fields and nothing else. |
| `review` | The active steps still to do, the least recently touched first, each line saying whether the step has a comment. Read it to close what is done, drop what no longer has to be done, and comment what moved. |

A verb that changes nothing refuses: `done` on a step already `done` refuses
`status-invalid`.

## Settings

| Key | Default | Meaning |
|---|---|---|
| `steering_step_budget` | 100 | Characters a work, a comment or a reason holds, on one line. |
| `steering_name_max` | 60 | Characters a step name or a label holds. |
| `steering_note_budget` | 80 | Characters a label's note holds. |
| `steering_life_days` | 15 | Days a step stays active without being touched or recalled. |
| `steering_active_max` | 60 | Steps still to do that stay active at most. |
| `steering_board_per_label` | 3 | Steps still to do `board` shows under each label. |

A value that is not a whole number refuses `setting-invalid`.

## The clock

The script reads the current date and time from `PP_NOW` when it is set, written like
`2026-10-25T16:00:00+00:00`, and from the system otherwise. Any other value refuses
`clock-invalid`.

## Refusals

Every refusal exits with code 2 and writes nothing.

| Code | When |
|---|---|
| `step-invalid` | A call that does not fit its verb, an id that is not `<member>.s.<n>`, a step added without its work, `wait` or `drop` without a reason, a label change that is not `+<label>` or `-<label>`, `order` naming a step without that label, `list` with both `--all` and `--archived`, an age that is not `<n>d`, a date that is not a date, an unknown status or grouping, a move of `apply` off its form. |
| `step-unknown` | An id the record does not hold. |
| `status-invalid` | The step already has that status. |
| `name-invalid` | A name or a label that is not lowercase words joined by hyphens, or longer than `steering_name_max`. |
| `name-taken` | A name another step still to do wears. |
| `budget` | A work, a comment, a reason or a note longer than its budget. |
| `key-invalid` | A key that is not `<family>:<slug>`. |
| `step-taken` | A key another step holds. |
| `label-unknown` | A label the record does not hold. |
| `step-active` | `recall` on a step that is not archived. |
| `view-read-only` | `view` (and so `./pp steering`) given a verb that is not a reading, or `list --sweep`. |
| `apply-refused` | A move of `apply` refused: the refusal of that move is said first, then its line; nothing of the batch is written. |
| `state-malformed` | A record that is not the steps with their counter. |
| `state-unmigrated` | A `threads.json` of the former model stands without `steps.json`. It is never read: the operator ports it first. |

A key the family's verifier refuses is refused under the engine's own code, such as
`family-unknown` or `vector-unverified`.
