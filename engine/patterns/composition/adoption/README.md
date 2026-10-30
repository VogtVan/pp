# adoption — offer a skill or a proc that your instance does not carry

## What you write

`+<name>` among the offers of a proc, usually in an overlay of `TURN`:

    tools: |
      +housestyle
      +REVUE

The name is one your instance does not compose. pp looks for it, only because you
offered it, in two places: your harness's skill folder (`<name>/SKILL.md`), then, for an
instance that lives under a house and uses its machine, the house's `procs/<name>.md`.

## What you get

- A skill found in your harness's folder with a front matter and a `description:` is
  adopted: it appears in your catalog with its description, its laws join your
  registry, and `-s <name>` plays it like a call — a frame of its own, its laws in force
  while it lives, its body the brief; when it closes, its laws leave.
- A skill found there without a front matter or a description stays offered by its name
  alone; the build warns `offered-not-conductible` and says what it lacks; calling it
  plays nothing and tells the agent that the harness runs it.
- A name found nowhere is offered by its name alone, and calling it does the same.
- A proc of the house is adopted the same way: described in your catalog, opened with
  `-s <name>` as a door (see `composition/door`), its laws in your registry. It never
  plays by itself in your instance: what it hooks or mounts in the house sleeps here.
- A skill in your harness's folder that you do not offer is not a name for pp, and a
  skill or a proc you copy there changes nothing in what pp shows.

## When to use it

- Bring a skill you keep for your harness into the conducted work, under its own laws.
- Let the instances under a house share the house's procs without copying them.
- Name a tool the harness runs, so the agent sees it offered where it belongs.

## What refuses

- Calling a name that is not offered at the current step is refused under the pending
  block's deviation, even when the harness's folder holds it.
- A `+<name>` the instance already offers refuses `overlay-adds-existing` in an overlay
  (see `composition/overlay`).

## The demonstration

- `procs/TURN.offer.md` — an overlay of `TURN` offering `+housestyle`, `+rawtool` and
  `+brainstorm`; placed at `.pp/procs/TURN.md`.
- `procs/TURN.house.md` — an overlay of `TURN` offering `+REVUE`, for an instance under a house.
- `procs/REVUE.md` — the house's proc: its law `RV1`, one `WORK`.
- `procs/HOUSE.md` — the house's common ground: its law `HS1`.

## The test

`tests/patterns/composition/adoption.py` writes the harness's skills (a conductible
`housestyle`, a bare `rawtool`, an unoffered `hidden`) and plays them: housestyle in the
catalog and the registry, rawtool name-only with its warning, hidden nowhere, brainstorm
offered bare, both orienting without playing; housestyle opened as a call on the parked
run and closed clean; a copy in the harness's folder changing nothing; then a house and a
borrower: REVUE described in the borrower's catalog, opened as a door, never mounted, RV1
in its registry.
