# input — have a document open on the production of another

## What you write

On a called document — or on a successor (see `control-flow/next`) — `input: <form>`: the
form it takes.

    input: json

The document before it produces in that form (see `outputs/formats`): `output: json`.

## What you get

- The production of the step before the `CALL` goes to the tool, is judged on its form, and
  the called document opens on it. A form written on the call's line (`line`) travels
  there; a piped one (`json`) on the call's standard input.
- The last production of a called document flows out with it to its caller's next step: a
  `PICK` elects from it, a `CALL` whose callee declares `input:` takes it.
- A called document that opens on an `INFER` or a `WORK` sees what it received under
  `input`, served once when it opens, as received (a `json` rendered as JSON), under the
  agent's conduction and the principal's, and again after a compaction. One that opens on a
  `PICK` sees it as its OPTIONS alone.
- `input: any` takes every form.
- A production proven by a `PROVE` before the `CALL` is handed over once proven: the called
  document plays after the proof.

## When to use it

- Split a procedure where data passes from one part to the next: the first part produces,
  the second works on it.
- Keep a document reusable: it says the form it takes, not who gives it.

## What refuses

- A called document whose `input:` is not the form the step before it produces refuses
  `format-mismatch`, next to the caller or across a called document's end.
- A list that reaches a `PICK` from another document without being judged as a list refuses
  `options-invalid` when it is not one (see `steps/pick`).

## The demonstration

- `procs/SEEDER.md` calling `procs/NAMED.md` — a line handed over.
- `procs/MISMATCH.md` and `procs/STRICT.md` — a table handed to `procs/SHIP.md`, which takes
  JSON: they refuse.
- `procs/PICKER.md` calling `procs/LISTER.md` — a callee's list elected by the caller.
- `procs/CHAIN.md` — `procs/MAKERJ.md`'s JSON taken by SHIP across the end of MAKERJ.
- `procs/TOLERANT.md` — `procs/MAKERT.md`'s table taken by `procs/ANYONE.md`.
- `procs/FEEDTAKER.md` calling `procs/TAKER.md`, `procs/FEEDELECTOR.md` calling
  `procs/ELECTOR.md` — a consumer that opens on an INFER, one that opens on a PICK.
- `procs/PIPER.md` — a JSON value proven, then handed to SHIP.

## The test

`tests/patterns/outputs/input.py` plays the demonstration: NAMED opening on SEEDER's line,
MISMATCH refusing, LISTER's list elected by PICKER, CHAIN shipping across the end of MAKERJ,
ANYONE taking a table, STRICT refusing; TAKER's `input` section under both conductions and
after a compaction, ELECTOR's OPTIONS; PIPER's value shipped after its proof.
