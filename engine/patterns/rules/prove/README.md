# prove — check the work against its laws before it leaves

## What you write

A `PROVE` line in your `proc:`, where the work must be checked — usually right after the
step that produces it.

    constraints.production: |
      Z1  say it plainly.
    proc: |
      INFER
      PROVE

## What you get

- `PROVE` is the one point of proof: no key arms it, nothing adds one for you, and without
  a `PROVE` nothing is ever asked.
- When something was produced since the last proof, the `PROVE` asks the agent one JSON
  array on stdin, presented as `INFER proof [<codes>]`: one object per code the line names,
  each `{"code", "evidence", "verdict"}`, the verdict `ok`, `fail` or `n/a`.
- The line names every law of production on screen: the document's own, its callers', a
  mounted document's (see `composition/mount`), and the laws a called document left due
  when it ended without its own `PROVE` — a caller's `PROVE` pays for its callee's work.
- Laws of behavior are never asked; a document with none of production gets no proof
  block: its `PROVE` resolves on one line. A `PROVE` with nothing produced since the last
  proof resolves on one line too.
- `ok` and `n/a` let the work leave; `n/a` says a law has no bearing on it. A `fail`
  replays the work (see `rules/repair`).
- The proof comes before the step's delivery: each part of the work proven before it
  leaves, and the AWAIT that ends the passage foresees nothing (see `control-flow/root`).
  A root replayed by the next message is proven again at its next passage.
- The same proof is asked under the agent's conduction and the principal's.

## When to use it

- After a step whose production must hold its laws before anything builds on it.
- Once at the end of a root, so that every passage's work is proven.
- After a `CALL` to a document that writes no `PROVE` of its own, to pay for its work under
  your laws.

## What refuses

Nothing refuses at the `PROVE` itself; a proof that misses repairs (see `rules/repair`):

- an empty array, or a proof naming no law of production;
- a code the line asks left unnamed;
- a code no law in force carries;
- a verdict other than `ok`, `fail` or `n/a`.

A code of a law of behavior named in addition passes.

## The demonstration

- `procs/ALONE.md` — a `PROVE` and no law: it resolves on its line.
- `procs/CLAIM.md` — one law of production, an `INFER`, a `PROVE`.
- `procs/COVERED.md` — three laws of production and one of behavior; `procs/MANY.md` —
  nineteen laws.
- `procs/CALLER.md` calling `procs/CRAFT.md` — the caller's law asked at the callee's
  `PROVE`.
- `procs/LATER.md` calling `procs/BARE.md` — the callee writes no `PROVE`, the caller's pays.
- `procs/NOPROVE.md`, and `procs/MUTECALL.md` calling `procs/MUTE.md` — laws and no
  `PROVE`: nothing is due.
- `procs/IDLE.md` — a `PROVE` before anything is produced, then one after.
- `procs/NOLAW.md` and `procs/QUIET.md` — a `PROVE` with no law of production.
- `procs/TWO.md` — a law of each section.
- `procs/LOOP.md` — a root proven at each passage; `procs/TFIN.md` — work proven before the
  passage ends; `procs/MFIN.md` — two deliveries, each proven; `procs/PLAIN.md` — no
  `PROVE`.
- `procs/TURN.overlay.md` — an overlay of the base's TURN that adds a law of production.

## The test

`tests/patterns/rules/prove.py` plays the demonstration: ALONE resolving on its line;
CLAIM's proof block and its verdicts; COVERED's codes left unnamed, complete, with a
behavior code in addition; MANY's nineteen codes; CRAFT asking CALLER's law and repairing
on a stranger code; LATER paying BARE's line; NOPROVE and MUTE owing nothing; IDLE's line;
NOLAW and QUIET without a proof block; TWO asking its production law alone; LOOP proven at
each passage; TFIN's bare frontier; MFIN's two checkpoints; PLAIN's trace without a proof;
the TURN overlay arming the root's `PROVE` before the AWAIT; CLAIM under the principal's
conduction.
