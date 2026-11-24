# laws — tell the agent what must hold while it works

## What you write

In a document's front matter, one or both of two keys, one law per line: its CODE, two
spaces, then its text.

    constraints.production: |
      P1  the line is under ten words.
    constraints.behavior: |
      H1  say what you do before you do it.

- `constraints.production` — what the agent MAKES must hold: these laws are asked at the
  next `PROVE` (see `rules/prove`).
- `constraints.behavior` — what the agent does, says or reads must hold: these laws ride
  every block and are never asked at a proof.

## What you get

- While the document is on screen — played as a frame, or mounted (see
  `composition/mount`) — its laws ride every block in full text, under one CONSTRAINTS
  title: `production:` first, then `behavior:`, each group opening on its label. They
  leave with the document. A called document adds its laws to its caller's (see
  `composition/call`); an overlay adds its own in the section of its key (see
  `composition/overlay`); a law may cite a value of another document (see `context/tags`).
- The proof line of a `PROVE` names the production codes it asks: `INFER proof [P1]`.
- Under the operator's setting `verbatim_constraints: false`, a law's text renders the first
  time it appears in the run, its code alone after that; a law new in a frame says its text.
  After a compaction is declared, every law says its text again.
- A law said by its code keeps the section it first appeared in, from one call to the next:
  a door opened from a step, lap after lap, shows its own law under `production:` and the
  laws it inherits under `behavior:`.

## A system law

A law that binds every block of every run is a SYSTEM law. Two files declare them, and no
other: the engine's `system/SYS.md`, beside its standing orders, and the instance's
`.pp/system/SYS.md`. A base or a package declares none.

    ---
    name: SYS
    kind: sys
    description: the instance's system laws.
    constraints.production: |
      SYS3  every answer names the file it read.
    ---

- The file holds its laws and nothing else: `name`, `description`, `kind: sys` and the two
  `constraints.*` keys, no body. A system law's code is `SYS<n>`, a number no other law holds.
- A system law is in force at every block: the boot, a turn, an open space, a door, a mount,
  a repair. Every output says its full text once, at the head of its group in the first
  CONSTRAINTS section, under `verbatim_constraints` true or false. It never comes back as its
  code alone.
- A system law of production is named at every proof line; a system law of behavior never is.

## When to use it

- Say what the agent must keep to while a piece of work is done, and how that is seen.
- Put a law of production where its work happens, and write the `PROVE` that checks it.
- Keep a code unique in your instance: the code is how a proof, an overlay and a reader
  name the law.

## What refuses

- A law line without its code refuses `constraint-malformed` when the document is played.
- When the instance builds, a code declared twice, or a line out of form, in your own
  documents is a warning: the build passes, the first holder keeps the code, the line out of
  form is dropped. The same defect in a package's documents refuses (`constraint-doubled`,
  `constraint-malformed`).
- A bare `constraints:` key, with no section, refuses `constraints-unsectioned`.
- When the instance builds, a `system/SYS.md` under a base or a package refuses
  `sys-misplaced`, and so does a `SYS<n>` code a document declares; a SYS.md that carries more
  than its laws, or a law whose code is not `SYS<n>`, refuses `sys-shape`; a code both SYS.md
  declare, or one SYS.md twice, refuses `law-twice`.
- A mounted document that declares the code of a system law refuses `mount-collision`.

## The demonstration

- `procs/RIDE.md` — a step under two laws of behavior.
- `procs/TWO.md` — a line under a law of each section, then a `PROVE`.
- `procs/CODED.md`, calling `procs/FRESH.md` — a law said once, then by its code, while the
  called document's new law says its text.
- `procs/DESK.md` — a WORK under a law of behavior, offering `procs/LAPS.md` (a door that
  turns on elements its prose describes) and `procs/ROUTE.md`, whose `procs/STAGE.md`
  leaves to `procs/LEFT.md` or `procs/RIGHT.md`.
- `procs/SHIFTED.md` and `procs/SHIFTED.overlay.md` — a proc and its overlay, which adds a
  law to each section; the overlay is placed at `.pp/SHIFTED.md`.
- `systems/SYS.md` — the instance's system law of production, placed at `.pp/system/SYS.md`.
- `procs/TORN.md` — a line without its code; `procs/DOUBLE.md` and `procs/TWIN.md` — one
  code declared twice; `procs/OLD.md` — laws under a key with no section.

## The test

`tests/patterns/rules/laws.py` plays the demonstration: RIDE's laws in full text; TWO's one
title, production first, its proof line naming P1; TORN refusing; under codes mode CODED's
law said once, then by its code, FRESH's law in full, every text back after a compaction;
DESK's doors opened through the console, the laps keeping LP1 under `production:` and B1
under `behavior:`, the successor without a `production:` section; SHIFTED's overlay adding
in the section of its key; the build warning on the author's double and line out of form,
refusing them in a package written into the base's copy, refusing OLD; the system law SYS3
placed, its text whole in two outputs in a row under codes mode, heading `production:`, its code
on TWO's proof line.
