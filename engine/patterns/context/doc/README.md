# doc — a document that is read, never played

## What you write

A document with `kind: doc` and no `proc:`. Its front matter may carry laws
(`constraints.production:`, `constraints.behavior:`), offers (`tools:`) and readings
(`serve:`, see `context/serve`); its body is prose for the agent.

## What you get

- Served by a proc (`SERVE <NAME>.md`), its body rides the block of that proc's own
  step, under its title. No frame opens on it and its laws stay out: a served
  document is information, not a scope.
- Mounted (see `composition/mount`), its laws and its offers are in force at the step
  it joins, for as long as the mount stands, and its body is served when the mount asks
  for it.
- A document that carries a `proc:` outside a kind the engine plays is named by the
  build's lint: the flow it writes would never play. A proc that carries one is not
  named.

## When to use it

- Write a charter, a glossary, a style or a set of laws once, and let several procs
  read it or mount it.
- Bring laws and offers to a step without adding a step: mount the document instead of
  calling a proc.
- Keep a body out of the flow: what the agent should know, not what it should do.
- To have a proc serve readings section by section, see `context/serve`; to have a
  skill's output rendered as a section, see `context/payload`.

## What refuses

- Nothing in a doc refuses by itself: a `SERVE` whose name resolves nowhere is said
  gone in the block (see `context/serve`), a mount of a missing document refuses at the
  mount (see `composition/mount`).
- A `proc:` in a document no kind plays does not refuse: the build's lint names it.

## The demonstration

- `procs/CHARTER.md` — the doc: its law `DC1`, its offer `LOOKUP` and a body.
- `procs/READER.md` — a proc that serves CHARTER by `SERVE CHARTER.md`, then one `INFER`.
- `procs/LOOKUP.md` — a proc of one `INFER`, the step CHARTER is mounted on.
- `procs/STRAY.md` — a note with a `proc:` and no kind: placed at the top of the instance,
  the lint names it. A folder of the operator's own, such as `plans/`, is never read.

## The test

`tests/patterns/context/doc.py` plays the demonstration: READER's step carries
CHARTER's body while no CHARTER frame opens and `DC1` stays out; CHARTER mounted on
LOOKUP puts `DC1` in force, offers `LOOKUP` and serves its body; STRAY placed at the
top of the instance is named by the lint, READER is not.
