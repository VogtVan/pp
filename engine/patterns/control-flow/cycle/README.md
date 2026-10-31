# cycle — a door that turns on the elements a skill renders

## What you write

Two documents. The DOOR, a procedure that is CALLed, names a token:

    cycle: laps

The PROVIDER, a document that names the same token and the skill that renders the element still
due:

    provides: laps
    with: pp-laps next

The skill prints the element that remains to be done, or nothing when none is left. It is asked,
it keeps the count: the element moves on only when the work done on it is recorded — by the
door's `sink:`, which hands each production to a skill (see `outputs/sink`), or by any other
gesture of that skill.

## What you get

- At the door's entry the skill is asked. When it prints an element, the door plays its steps on
  it: a LAP. The element is served under the token's name.
- At the end of a lap the skill is asked again: a new element opens the next lap, from the door's
  first step; nothing left, and the door leaves like any CALLed document — its caller goes on
  with the last production.
- Each lap is proven at the `PROVE` the door writes, under every law on screen — the door's own
  and those of a document mounted during the passage, which stays mounted from lap to lap.
- Nothing due at the entry: no lap opens, the line under the token says so, and the caller goes
  on.
- A skill that fails ends the cycle: no lap opens on a breakdown, and its refusal is said under the
  token.
- A compaction during a lap asks the skill again: it renders the same element, since nothing was
  recorded.
- A door that is the run's root parks the run when nothing is left — at once if nothing was due.

## When to use it

- Work that repeats over a list the instance already holds: the files still to review, the sources
  still to read, the entries still to answer.
- The list lives outside the conversation and a skill knows what remains: the agent never counts.
- When the agent itself must say what the list is, write `field:` instead (`control-flow/field`).

## What refuses

- When the door opens: a token no document provides (`cycle-unprovided`).
- At the build: `cycle:` and `field:` on one door (`cycle-and-field`, see `control-flow/field`);
  a provider whose `with:` names no skill (`reference-unknown`).

## The demonstration

- `procs/ROUNDS.md` — the caller: `CALL SWEEP.md`, then an `INFER`.
- `procs/SWEEP.md` — the door: `cycle: laps`, its productions handed to `pp-laps`, a line and its
  `PROVE` per lap.
- `procs/LAPS.md` — the provider of `laps`: `with: pp-laps next`.
- `procs/ORPHAN.md` — a door whose token nobody provides.

The skill `pp-laps` is yours to write in your instance's `skills/`: the demonstration documents
declare it, the test writes one.

## The test

`tests/patterns/control-flow/cycle.py` writes a skill that renders the next element of a list and
records the ones handed to it, puts a law on the door and mounts a document with a law of its
own, then plays ROUNDS over three elements; then an empty list, a skill that fails, ORPHAN, a
compaction during a lap, SWEEP as the run's root, and the three laps again under the principal's
conduction.
