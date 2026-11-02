# cadences — a document played when its week is due

## What you write

In your package's manifest, under `contributes:`, a `cadences:` entry per work that comes back
every week:

    cadences:
      - {name: sighting, anchor: "@SETTINGS.sighting_day", record: sightings.jsonl,
         play: SIGHTING.md, at: boot.initialize}

- `anchor` — the weekday the work is due, read from a setting (`monday` … `sunday`, or `never`).
- `record` — the record the work writes when it is done; its last entry says when it was done.
- `since` (optional) — another record: the work is due only if that record moved since.
- `play` — the document to play, one of your package's procs.
- `at` — the point where it plays: a socket a proc opens, often `boot.initialize`.

## What you get

- At the point `at`, after what is attached there, the engine CALLs `play` when the anchored
  day has passed since the record's last entry (and, with `since`, when that record moved).
- An absent record is due; a record written since the day is not.
- `never` switches the work off.
- One run plays each week's work: the first boot of the week claims it, a second boot that week
  plays nothing.
- A `play` that resolves nowhere is skipped and said in the run's trace: a cadence never breaks
  a boot.
- A `checks:` entry with the predicate `record-crossing` on the same record pushes a signal when
  the work is due (see `automation/checks-and-signals`).
- Under the principal's conduction the same boot plays the same work.

## When to use it

- A digest, a pass, a review that comes back each week and must not be forgotten: the work is
  served when it is due, and only then.
- To play something at every entry rather than once a week, use `exec:` (`automation/exec`);
  to bring a document at every passage, a mount (`composition/mount`).

## What refuses

- At the build: a cadence without `play` refuses `contribution-malformed`; one whose `at` names
  a point no proc opens refuses `socket-unknown`; one whose `at` belongs to a package you do not
  require refuses `dependency-undeclared`.
- When the anchor is read: a value that is neither a weekday nor `never` refuses `anchor-invalid`.

## The demonstration

- `manifests/witness.yaml` — a package with the weekly `sighting`, a cadence `ghost` whose
  document is missing, and a check that pushes `sighting-due`.
- `manifests/playless.yaml`, `manifests/nowhere.yaml`, `manifests/unrequired.yaml` — a cadence
  without `play`, at a point no proc opens, at the base's point without requiring the base.
- `procs/SIGHTING.md` — the weekly digest the cadence plays.

## The test

`tests/patterns/automation/cadences.py` pins the witness and writes its setting and records,
then plays: the crossing, `never` and an anchor out of form; SIGHTING played at the boot and the
check pushing, the ghost skipped, nothing played once the record is written; two boots for one
week, one play and the claim traced; a forgotten claimant replaced; the same under the
principal's conduction; the three manifests refused at the build.
