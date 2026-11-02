# door — offer a proc the agent opens by its name

## What you write

In the front matter of a proc, the procs it offers at its steps:

    tools: |
      DOOR

or, to offer one at a proc you do not own, `+DOOR` in an overlay of it (see
`composition/overlay`). The agent opens an offered proc with `-s DOOR`, followed by
any words it wants to hand over.

## What you get

- The offered proc opens as a frame stacked over the step that offers it: its body is
  the brief, its laws are in force with those of the frames below, its steps play.
- When its last step is done, the run goes back to where it was; the call that opened
  it is not played again at the next passage.
- The words after the name are said back on the first line and kept in the run's trace.
- A door opened while a `WORK` step is pending takes that work with it: the door's own
  steps carry it, and the step that offered the door is not asked for it again.
- When one output carries several segments, each numbered `[n]`, each segment has its
  own offers. A name only one segment offers opens without a number; a name several
  segments offer must be addressed, `-s DOOR@<n>`, and the door then plays under the
  laws of that segment. Addresses belong to the output that showed them: once a new
  output is rendered, an old number no longer holds.
- A `§` in your proc closes the output there: the door is offered by the step before
  the break, in an output of a single segment.

## When to use it

- Give the agent a procedure it may open when the work calls for it, instead of a step
  it must always play.
- Offer a review, a check or a form at the step where it belongs.
- A run can also open on a door named when it starts; nothing in your proc changes for that.

## What refuses

- A name several segments offer, called without a number, refuses `address-ambiguous`.
- A number that no segment of the current output carries for that name refuses
  `address-stale`.
- A name the current step does not offer is refused under the pending block's
  deviation; nothing plays.

## The demonstration

- `procs/ROUTER.md` — offers `DOOR`, then calls `RINNER.md` between two steps: two segments.
- `procs/RINNER.md` — the called step: it offers `NOTETAKER`, its law `I1`.
- `procs/DOOR.md`, `procs/NOTETAKER.md` — the offered procs.
- `procs/BARRED.md` — offers `DOOR`, then `§`.
- `procs/NOTE.md`, `procs/ROUTE.md`, `procs/REVIEW.md` — doors opened from the turn: a note,
  a door taking a number, a door doing the work.
- `procs/TURN.offer.md` — the overlay of `TURN` that offers them, with its law `TB1`;
  it is placed at `.pp/procs/TURN.md`.

## The test

`tests/patterns/composition/door.py` plays them: ROUTER's output numbers its segments,
NOTETAKER routes to RINNER without a number, DOOR asks for `@1`, the routed door keeps
RINNER's law, a fresh output makes `@2` stale, BARRED keeps one segment; NOTE opens over
the turn with `TB1` and leaves nothing to the next passage; `-s ROUTE 7` says and traces
its argument; REVIEW takes the turn's work, under both conductions.
