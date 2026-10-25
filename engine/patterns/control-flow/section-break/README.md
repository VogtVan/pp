# section-break — end an output at a step you choose

## What you write

A line `§` alone in your `proc:`, before the step that must open a new output. A line
that starts with `# ` is a comment: pp skips it, and removing the `# ` arms the line.

    proc: |
      INFER
      §
      INFER
      # §
      INFER

## What you get

- When the instance joins several steps into one output (see `control-flow/fusion`), it
  never joins across a `§`: the output ends just before the marked step, on a CONTINUE,
  and the marked step opens the next call.
- The break holds whatever the marked step is: before a `SERVE`, the reading arrives
  with the next output, not with the one the `§` closed.
- A `# ` line is not read: a commented `# §` cuts nothing, and the steps after it join
  the output before it (`PACED{1/3}`, then `PACED{2-3/3}`).
- A `§` is not the end of the passage: the run waits for the next call, not for the
  principal's next message, and the passage goes on (see `control-flow/root`).
- In a run its principal conducts, the outputs are cut at the same place; the CONTINUE
  carries no command, and the principal's call opens the marked step.

## When to use it

- The agent must finish one production before it reads what comes next: an estimate
  before the facts, a plan before the reading.
- An output would be too long if the instance joined every step into it.
- Keep a step written but switched off: comment it with `# `.

## What refuses

Nothing: a `§` takes no argument, and a `# ` line is never read.

## The demonstration

- `procs/PACED.md` — an `INFER`, a `§`, an `INFER`, a commented `# §`, then an `INFER`.
- `procs/READAHEAD.md` — an `INFER`, a `§`, then `SERVE NOTES.md` and an `INFER`.
- `procs/NOTES.md` — the document READAHEAD reads after its break.

## The test

`tests/patterns/control-flow/section-break.py` sets the instance to join every step it can,
plays `PACED.md` and checks the two outputs and their headings, plays `READAHEAD.md` and
checks that the notes arrive with the second output, then plays `PACED.md` under the
principal's conduction.
