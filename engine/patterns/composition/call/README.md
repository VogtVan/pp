# call — open another document as a step of yours

## What you write

One line in your `proc:`: `CALL <NAME>.md`. The name is any document's name; it
resolves the way every name does (see `context/addressing`).

## What you get

- The called document's body is served first, as the brief of its first step.
  Your own body stays above it as information.
- The called document plays in a frame of its own. Its laws (see `rules/laws`) and its
  offers are added to yours while it plays, and they leave when it ends. The heading shows
  the path: `GATE ▸ REVIEW{1/1}` while REVIEW plays, `GATE{2/2}` once you are back.
- When its last step is done, your procedure resumes on the step after the `CALL`.
  That step receives the called document's last production, and uses it only if
  it consumes it (see `outputs/input` and `steps/pick`); otherwise the production
  was said to the principal at its own step.
- The `serve:` sections of the called document are not served by the `CALL`:
  each needs its own `SERVE` step in that document (see `context/serve`). Its
  `payloads:` render as sections when it enters (see `context/payload`).
- The setting `proc_body_serve` decides whether a body already served is served
  again: `once` serves it the first time only, `always` at every `CALL`.

## When to use it

- Split a long procedure into documents that each carry their own laws and readings.
- Reuse the same sequence of steps in several procedures.
- Hold a law only for the part of the work where it applies: it lives in the
  called document and leaves with it.
- To let procs you do not name play at a point of yours, hook them (see
  `composition/hook`); to bring laws and readings without a step, mount a document
  (see `composition/mount`); to act once when a proc starts, use its entry (see
  `composition/initialize`); to let the agent open a proc only when the work calls for
  it, offer it (see `composition/door`).

## What refuses

- A `CALL` whose name resolves nowhere refuses `document-missing`; nothing plays.
- A called document that declares `input:` refuses `format-mismatch` when the step
  before your `CALL` produces another form (see `outputs/input`).

## The demonstration

- `procs/GATE.md` — the caller: its law `G1`, then `CALL REVIEW.md`, then one `INFER`.
- `procs/REVIEW.md` — the called document: its law `R1` and one `INFER`.
- `procs/LOST.md` — a `CALL` to `ABSENT.md`, a name that resolves nowhere: it refuses.

## The test

`tests/patterns/composition/call.py` plays the three documents: REVIEW's body comes
first, `G1` and `R1` stand together while REVIEW plays, `R1` leaves at the return to
GATE, and `LOST.md` refuses `document-missing`.
