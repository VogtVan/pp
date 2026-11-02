# due — play a step only when a value says so

## What you write

At the end of a step line, `^ @<Document>.<field>`: the step plays only when that field of
that document says it is due.

    proc: |
      CALL NOTE.md ^ @PACE.every
      INFER

The field lives in the front matter of any document the instance can read — a document of
your own, as `PACE.md` here, or `SETTINGS.md`, whose keys left out take their default.

## What you get

The field's value decides, at the start of each exchange:

- `true` — the step plays in every exchange, from the first one.
- `false`, `0`, or no value at all — the step never plays.
- a whole number n — a pace: the step plays every n completed exchanges, never in the
  first one. With `every: 3` it plays in the fourth exchange, then the seventh.

A step that is not due is skipped silently: the procedure goes on with the next step, and
the agent keeps no count of its own.

## When to use it

- A chore that must come back on a rhythm: a note every few exchanges, a digest, a check.
- A step the operator switches on or off in a setting, without editing the procedure.
- To cite a value inside a law's text, write a tag instead (see `context/tags`).

## What refuses

- A value that is not `true`, `false` or a whole number, or a number below 0, refuses
  `guard-invalid` when the step is reached; nothing plays.

## The demonstration

- `procs/DIARY.md` — the root: `CALL NOTE.md ^ @PACE.every`, then an `INFER`.
- `procs/NOTE.md` — the step that plays when due: one `INFER`.
- `procs/PACE.md` — the document that holds the pace: `every: 3`.

## The test

`tests/patterns/control-flow/due.py` plays `DIARY.md` over several exchanges with `every` set
to 1, then 3, then `true`, `false` and left out, and checks in which exchanges NOTE opens;
then sets it to a word and to -1, which refuse `guard-invalid`.
