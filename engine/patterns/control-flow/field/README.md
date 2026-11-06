# field — a door that turns on the elements the agent lists

## What you write

In the front matter of a procedure that is CALLed, `field:` says in prose what the door turns on:

    field: |
      The accounts of @LEDGER.accounts, one lap each.

A `@Document.field` in the prose is replaced by that field's value. No skill is written.

## What you get

- At the door's entry the agent gets one more step: the prose as its brief, its answer ONE JSON
  array of the elements, piped back.
- The array is judged on its form alone (the engine's form `field`, see `outputs/formats`): valid JSON, an array, each element a string or a number,
  none empty, none twice. A fault of form plays the step again, the fault named. What the
  elements mean is never judged: numbers, or paths that exist nowhere, are accepted.
- Each element opens a LAP: the door plays its steps on it, the element served under `field`.
  The lap that closes drops its element; the next one opens on the following element, from the
  door's first step. Nothing left, the door leaves like any CALLed document — its caller goes on.
- Each lap is proven at the `PROVE` the door writes, under every law on screen.
- An empty array opens no lap: the line under `field` says nothing is due, and the caller goes on.
- The elements left stay with the door: looking at the run moves nothing, and a compaction serves
  the same element again.
- A door that is the run's root parks the run when nothing is left — at once on an empty array.
- A lap weighs what a lap of a door that turns on a skill weighs (`control-flow/cycle`).

## When to use it

- Work that repeats over a list only the agent can draw up: the claims of a text, the files a
  change touches, the questions a message asks.
- When a skill can say what remains, write `cycle:` instead (`control-flow/cycle`).

## What refuses

- At the build: `cycle:` and `field:` on one door (`cycle-and-field`); a `field:` that says
  nothing (`field-empty`); `field:` on a document with no steps (`field-unplayable`).
- In the steps: a `FIELD` written by hand (`field-keyword`) — the step is the engine's.
- When the door opens: a `@Document.field` of the prose that names nothing
  (`field-argument-empty`).

## The demonstration

- `procs/MONTH.md` — the caller: `CALL ACCOUNTS.md`, then an `INFER`.
- `procs/ACCOUNTS.md` — the door: `field:` reading `@LEDGER.accounts`, a line and its `PROVE` per
  lap.
- `procs/LEDGER.md` — the value the prose reads.
- `procs/HOLLOW.md` — a field whose reference names nothing.
- `procs/BOTH.md`, `procs/BLANK.md`, `procs/LOOSE.md`, `procs/WRITTEN.md` — one refusal each.

## The test

`tests/patterns/control-flow/field.py` puts a law on ACCOUNTS and plays MONTH over the three
accounts; then an empty array, five faults of form beside an array of numbers and one of paths,
two looks and a compaction during a lap, HOLLOW, ACCOUNTS as the run's root, the laps in the
trace, the weight of a lap beside the door of `control-flow/cycle`, the three laps again under the
principal's conduction, and each refusing document alone at the build.
