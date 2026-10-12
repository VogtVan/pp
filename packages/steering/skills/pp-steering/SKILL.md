---
name: pp-steering
description: Reference for the step and thread dictionaries, lifecycle commands, status rendering, verification, settings and named refusals.
---

# pp-steering — thread and step reference

`pp-steering` is the only writer of `.sys/records/threads.json` (the two
dictionaries and their counters) and `threads-closed.jsonl` in the same directory
(closures). Use its commands for every change; mutations use the engine's lock
and atomic state replacement.

## Data model

Two dictionaries by id. An id has no meaning: `<member>.s.<n>` for a step,
`<member>.f.<n>` for a thread, minted at the member's counters (`counters.s`,
`counters.f`, never rewound); the member part exists for uniqueness across a
federation only and is never read. `owner` names the member that minted a record.

| Thread field | Meaning |
|---|---|
| `name` | The thread's identity: kebab-case, unique among the open threads of this member at this instant; what the front shows. It changes by `rename`; the id stays. |
| `owner` | Creator member; a received copy keeps the source's id and owner. |
| `steps` | Ordered list of the ids of the steps the thread holds: the whole of its order. |
| `next` | Suggested step id, or `null`. |
| `note` | Optional: the thread's why, then what to know now -- one line under `steering_note_budget`. Written by `open --note` and `note`; it never dates the thread. |
| `opened_at`, `worked_at` | Opening, and the date of the WORK: a step's status moved, a step added or reordered, the thread closed, opened or reopened. An amend, a note and a rename leave it alone. |

| Step field | Meaning |
|---|---|
| `owner` | Member that minted the step. |
| `name` | The step's identity: kebab-case, unique in its thread, what designates it everywhere. It changes by `amend --as`. |
| `thread` | The id of the thread the step was born in, kept for good; the thread that lists it is where it stands. |
| `text` | A complement to the name, written freely by the agent -- a precision, a figure, a pointer; empty allowed; whitespace normalised to one line, under `steering_step_budget`. |
| `status` | `open`, `done`, `redo`, `blocked` or `dropped`. |
| `key` | Optional `<family>:<slug>`, verified, unique in the dictionary: one step per key. |
| `from` | Optional source step id of a received copy. |
| `reason` | Waiting reason set by `block`. |

A third record, `threads-seen.json`, holds per run what the run has SEEN: the
snapshot `{<thread id>: worked_at}` of the open threads as the table was last
served to it by `status --due`, and the exchange it was served at; `status --due`
compares it to the open threads now before serving. It is written by this script
alone, born at the first table served. Each time `status --due` serves the table,
the runs whose slot is gone leave it.

A step is the unit of work and does not change when it moves; a thread only
orders steps. One open thread at a time lists a step: `move` takes it from one
thread's list to another's. A thread lists ids of this dictionary alone: a record
that lists one it does not hold, or a braid (`braid: true`, a shape the model had
before 0.6.0), is of a former shape -- refused `state-legacy` at every read. A
closed thread goes to history with its ids; its steps stay in the dictionary.

## Calls and lifecycle

Use the workspace console and current run key:

    ./pp <key> -s pp-steering <verb> <arguments>

Every verb but `open` takes the thread's ID: a name labels, an id identifies —
a name is unique only among this member's open threads at this instant, the
history and the neighbours may wear it. A name given to any other verb refuses
`thread-addressed-by-name`, naming the id it labels. `id` is a thread id or a
step id (`#` in front tolerated), and `rank` a 1-based position. `reopen` names a
closure in history by its id. The ids of the open threads arrive with the
session's first block (`steering-ledger`); a thread or a step minted later says
its id in the output of the call that minted it.

### Create and extend

    open <name> [--note <text>]
    attach <thread id> --as <name> [--key <family:slug>] [<text ...>]
    attach <thread id> --from <step id> --owner <member> --name <name> [<text ...>]
    amend <thread id> <step id> [--as <name>] [--key <family:slug>|-] [<text ...>]
    note <thread id> <text ...>

`open` requires at least one line on stdin. A line mints a step as `open`, born
in this thread: `<name>` alone, `<name> | <text>`, `<name> | <family:slug>` to
key it, `<name> | <family:slug> | <text>`; a bare id line refuses. The thread is
minted, points to its first open step, and its id is said back
(`opened -- <name> [<thread id>]`). For example:

    ./pp <key> -s pp-steering open search-results --note "the order users asked for" <<'STEPS'
    the-order | Specify the search result order.
    the-implementation
    STEPS

`attach` mints an `open` step in the thread of that id and lists it, filling an
empty `next`; the text is optional; the thread's id and the step's are said back
(`attached -- <name> [<thread id>] <step id>`). With `--from` and `--owner` (read
at the source's record by the caller), it lands a crossing in the thread of that
id whatever its name here; when no thread stands under it, `--name` births the
copy with that id and owner, and an occupied name refuses. The received step is
minted here with `from`; a source already crossed refuses; a text over the budget
is cut to it and the cut is said.

`amend` changes the text, the name, the key or several, preserving id, status and
rank; `--key -` removes the key; a changed key is verified and checked for
uniqueness in the dictionary. `note` rewrites the thread's note; an empty text
removes it. Neither dates the thread.

### Deliver, resume or wait

    done <thread id> <step id>
    renext <thread id> <step id>
    block <thread id> <step id> <reason ...>
    drop <thread id> <step id>

| Verb | Step transition | Effect on `next` |
|---|---|---|
| `done` | Any status to `done`; clears the reason. | The thread pointing at it advances. |
| `renext` | `done` to `redo`; `blocked` or `dropped` to `open`, clearing the reason; `open` and `redo` stay as they are. | Points to this id in this thread. |
| `block` | Any status to `blocked`; stores the supplied reason, under the step budget. | The thread pointing at it advances. |
| `drop` | Any status to `dropped`; clears the reason, retains the step and key. | The thread pointing at it advances. |

`done`, `block`, `drop` and `amend` take a step the named thread lists
(`step-unknown` otherwise). Advancing selects the next `open` or `redo` step in
list order, wrapping to the start, or `null` if none remains. Completing the steps
does not close their thread. A status that moves dates the thread (`worked_at`);
`renext` on a step already open dates it too.

### Change the organisation

    reorder <thread id> <step id> <rank>
    move <thread id> <step id> <target thread id>
    rename <thread id> <new>

`reorder` changes rank within the list, preserving the pointer, and dates the
thread. `move` takes a step out of this thread's list and puts it at the end of
the target's; `reorder` then places it. The step does not change: its id, name,
key, status, text and `thread` stay as they were. If this thread pointed at the
step, its pointer advances; if the target pointed at nothing and the step is
`open` or `redo`, the target points at it. Both threads are dated. `move` refuses,
and writes nothing, when the target is the same thread (`step-invalid`), no open
thread (`thread-unknown`) or given by its name (`thread-addressed-by-name`), when
the target already has a step of that name (`name-taken`), when the step crossed
from another member (`step-crossed`), and when either thread belongs to another
member (`thread-foreign`). `rename` preserves the id and the list, and does not
date the thread.

### Close and reopen

    close <thread id>
    reopen <thread id>

`close` asks the engine for any guard on `steering-thread:<thread id>`. A
refusal returns `thread-guarded` with its reason; the thread stays open. No
declared guard means none is called. Closure dates the thread and writes it
with its ids (`id`, `name`, `owner`, `steps`, `opened_at`, `worked_at`,
`closed_at`, and `note` when it has one) to history and removes it from the open
threads; the steps stay in the dictionary. `closed_as` is `delivered` if every
listed step is done or dropped and at least one is listed, `dropped` otherwise:
unfinished work can also close, and a thread listing nothing delivers nothing.

`reopen` restores the closure of that id with its name, owner, note and ids,
`worked_at` now, `next` recalculated to the first `open` or `redo`. An id already
open refuses, and so does a name another thread wears meanwhile. A closure that
is a braid, or that lists an id this dictionary does not hold, refuses
`state-legacy`. History retains the entry with `reopened_at`.

## Read the state

    status [<thread id>] [--all [--open] | --due]

`status` is the front the NEXT pastes, without any id: a TABLE, then the `⏸`
line, then the `💤` footer, each present only when it has content.

The table `initiative | note | progress | age | next action(s)` has one row per
open thread that has a step still to do (`open` or `redo`), sorted by decreasing
`worked_at`, ties by name, no rank. A thread whose remaining steps all wait has no
row: its steps stand at the `⏸` line.

- `initiative`: `🔗` for a thread another member owns, then the bare name.
- `note`: the thread's note, or `—`.
- `progress`: a bar of five cells `▰▱` filled at the ratio delivered / total,
  rounded to the nearest cell, then `delivered/total`, then `🔄n` when n steps are
  reopened -- total counts the done, redo, open and blocked steps, dropped steps
  excluded.
- `age`: the time elapsed since `worked_at`: `now`, `12 min`, `1h 35 min`,
  `> 1 day`, `3 days`, `2 weeks`, `~3 months`, `~1.4 years`.
- `next action(s)`: the pointed step, then the following `open` and `redo`
  steps in the thread's order, wrapping to the start, up to `steering_next_max`
  names between backticks separated by ` · `, then `…` when more remain; each name
  with its mark (`🔄` `📥` `✉️`).

The `⏸` line names every `blocked` step of the open threads, freshest thread
first, as `<thread> › `<step>` (<reason>)`, separated by ` · `: up to
`steering_line_max`, then `+n`.

The `💤` footer: a thread with a step to do and no work for
`steering_dormant_days` days folds there -- but only once the table holds
`steering_front_min` rows: the freshest threads stay at the table, dormant or not,
so the front is never empty while threads stand. A folded thread reads
`<name> `<pointed step>`<mark> (<age>)`, separated by ` · `. Asked by its id, a
thread renders alone by the same rules.

`status --due` is what the NEXT's provider serves: the front when the table is
DUE to the run -- no run names the script, the run boots (its first exchange, or
a compaction declared this exchange), it has seen no table, the table was served
to it at this same exchange already, or the open threads differ from the table it
last saw: a thread added, closed, or worked since (a step's status moved, a step
added, reordered, pointed), by this run or by any other hand, during a turn or
between two -- and otherwise the one line
`thread table not changed since the last turn`. The front served under the flag
is kept as what the run has seen. An amend, a note or a rename moves no
`worked_at`: it does not make the table due. `status` without the flag always
renders the front, whatever the snapshot, and keeps nothing.

`status --all` is the ledger, the agent's view: `~ <name> [<thread id>]
(<owner>)` and ` — <note>` when the thread has one, then every hosted id with its
mark, its name, its text, then its reason in parentheses for a waiting step --
its reason alone when it carries no text -- and its key.
`--open` keeps the steps still to do (`open`, `redo`, `blocked`): it is what the
`LEDGER` document serves at the session's first block (`steering-ledger`), and
again after a declared compaction. No open thread gives `pp-steering: no open
thread`.

    data [--bare]

`data` gives the member's open threads as data, for another package: one JSON
object, read-only, printed by the script of the member it describes, wherever it
is run from. To read another member's threads, run that member's own copy of
this script; never read its record.

    {"version": 3, "member": "<member>",
     "threads": [{"id", "name", "owner", "note"?, "opened_at", "worked_at",
                  "counts": {"done", "redo", "open", "blocked"},
                  "next": "<step id>" | null,
                  "steps": [<step>, …]}],
     "closed": ["<thread id>", …]}

`threads` holds the open threads, most recently worked first, `note` when the
thread has one. `steps` lists the thread's `open`, `redo` and `blocked` steps in
the thread's order; a `done` or `dropped` step is never in it. A step appears
under the thread that lists it, as `{"id", "name", "text", "status"}` with `key`,
`from` and `reason` when set. `next` is the id of the pointed step, `null` when none. `closed` lists the
ids of the threads the history holds and that are not open now, in the history's
order, once each: what a reader needs to know a thread closed, without reading the
record. `--bare` serves the same object without any `text`, `reason` or `note` --
the form a renderer reads when it needs states and names alone. `version` changes
when the shape changes; a reader of another version refuses by the number. Any
other argument prints the usage and exits 2.

Display marks: `🔄` redo; `⛔` blocked and `🗑️` dropped at `--all`; `📥` received
(`from`); `✉️` addressed (text starts with `@`); `🔗` before a name, a thread
another member owns; `⏸` heads the line of the waiting steps; `💤` heads the
footer of the threads without recent work. In `--all`, `✓` means done and `->`
next.

## Verification and settings

The engine calls `verify` with `steering-thread:<thread id>` on stdin:
read-only, exit 0 if an open thread carries the id, exit 2 otherwise.
Renaming keeps the vector valid; closure invalidates it.

| Setting | Default | Meaning |
|---|---|---|
| `steering_step_budget` | 100 | Characters per normalised step text or blocking reason. |
| `steering_name_max` | 60 | Characters per kebab-case thread name or step name. |
| `steering_note_budget` | 80 | Characters per thread note. |
| `steering_dormant_days` | 7 | Whole days without work before a thread may fold to `💤`. |
| `steering_next_max` | 3 | Next actions a row names before `…`. |
| `steering_line_max` | 7 | Waiting steps the `⏸` line names before `+n`. |
| `steering_front_min` | 5 | Rows the table keeps before any thread folds. |

The skill reads effective instance values through the engine. Budgets require
integers. The front renders with a setting's default when its value is invalid.

## Refusals

Refusals exit 2 before saving the requested mutation, with the reason.

| Code | Cause |
|---|---|
| `not-an-instance` | The script cannot locate an installed instance. |
| `thread-taken`, `thread-unknown` | Occupied name or id, absent open thread, or no closure of that id to reopen. |
| `thread-addressed-by-name` | A thread's name given where its id is due; the refusal names the id. |
| `state-malformed`, `state-legacy` | Invalid JSON, or a record of a former shape -- a step without its `name` or its `thread`, a thread without `worked_at`, a thread listing an id the dictionary does not hold (at every read; at `reopen` for a closure of the history), a braid, the shapes before them. |
| `step-invalid`, `step-unknown` | A step line without its name, a bare id line, malformed id, missing flag value, invalid rank, a `move` to the same thread, an id the thread does not list. |
| `step-taken` | A key already minted, or a source already crossed. |
| `step-crossed`, `thread-foreign` | A `move` of a step crossed from another member, or to or from a thread another member owns. |
| `key-invalid` | Work key outside `<family>:<slug>` syntax. |
| `name-invalid`, `name-taken`, `budget` | Invalid or excessive name, a step name already worn in the thread or in the target of a `move`, or excessive text, reason or note. |
| `thread-guarded` | The engine's closure guard refuses. |
| `setting-invalid` | Non-integer setting. |
| `family-foreign` | `verify` receives another family's vector. |

Key verification also relays engine refusals such as `family-unknown`,
`vector-unverified` and `verifier-missing`. An unknown verb or invalid call
arity prints usage and exits 2.
