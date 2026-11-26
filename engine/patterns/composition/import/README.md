# import — take the documents a document stands on, for as long as it lives

## What you write

`imports:` in the front matter of a document or a proc, one address per line, in the order you
want them:

```yaml
imports: |
  GROUND.md
```

An overlay of the document may write `imports:` too: its lines are added after the
document's.

## What you get

- The documents named enter the view with yours, before it, in the order written: each with its
  laws, its offer, its body and its readings (its `serve:` rows). Each imported entry names the
  document that imports it. Their offer comes before yours; mounted, your document's block
  carries their laws before its own.
- An imported document that imports enters with its own imports, before it. A document already
  in the view does not enter a second time: its laws stand once.
- Each imported document is judged by its own `when:`: when its guard is not due, it does not
  enter.
- An imported document lives as long as the document that imports it. Imported by a document
  a skill mounts with `::mount`, it leaves with it at the end of the passage. Imported by a
  document mounted at a point with `mount: <point>`, it leaves with it at the end of the passage
  and comes back with it at the next one.
- Imported by a proc, it enters once when the proc starts, before what mounts at the proc's
  `initialize`, and the proc's frame holds it: its laws stay at the end of every passage and at
  the next one, its body is served once. The trace `initialize` of the proc names its imports.
  It leaves when the proc ends, and the trace says `released`.
- A document already in the view for the passage that a proc imports when it starts — directly or
  through what it imports — takes the hold of the proc's frame and names its importer there: the
  end of the passage leaves it in the view, and it leaves with the frame.
- A document a frame holds keeps, at the end of the passage, a document of the passage it
  imports: that one takes the same hold. What counts is what the document imported when it
  entered: its file rewritten since, without its `imports:`, changes nothing.
- When a frame pops, what it imported stays if another document still in the view imports it:
  it then names that document.
- A document replaced by a skill's `replaces` takes what it imported with it, except what
  another document still in the view imports: that one stays, naming that document. The trace
  says `released` by `replaces`.
- An overlay adds imports: an overlay of a proc, its imports entering after the proc's own; an
  overlay of an instance's TURN, its imports held by TURN's frame from the first block. An
  overlay never removes an import: a line that removes refuses (below).

## When to use it

- A light document of work — a plan's node, a task a skill mounts — that takes the ground of
  laws of its domain without repeating it.
- A ground every agent of a house shares: an agent's TURN imports it.

## What refuses

- A document that imports itself through its imports refuses `import-cycle`, when the instance
  is built and when it is mounted.
- An address found nowhere refuses `reference-unknown` when the instance is built.
- A value that is not one address per line — a list, two names on a line, a line that removes
  (`-name`) — refuses `imports-malformed`.
- A front matter that still writes the old `mounts:` table refuses `mounts-gone`, the file
  named.

## The demonstration

- `procs/CHARTER.md` — the charter of the domain: its law `IM1`.
- `procs/GROUND.md` — the ground of the domain: it imports CHARTER, its law `IM2`, the offer
  `LEDGER`.
- `procs/LEDGER.md` — the ground's offer: one `INFER`.
- `procs/TASK.md` — the work a skill mounts, a light plan: it imports GROUND, its law `IM3`.
- `procs/AUDIT.md` — a second document that imports CHARTER: its law `IM4`.
- `procs/DESK.md` — a proc with the point `desk.open`, then one `WORK`.
- `procs/POST.md` — mounted at `desk.open`: it imports GROUND, its law `IM5`.
- `procs/STUDY.md` — a proc that imports GROUND and SEAL, then one `WORK`.
- `procs/PIN.md` — mounted at `study.initialize`: its law `IM6`.
- `procs/SEAL.md` — imported by STUDY, guarded by `@SWITCH.open`: its law `IM7`.
- `procs/SWITCH.md` — the field SEAL's guard reads.
- `procs/ROUND.md` — calls STUDY, then one `INFER`.

## The test

`tests/patterns/composition/import.py` plays them: a skill mounts TASK, CHARTER and GROUND
enter before it and leave at the park; GROUND mounted first, TASK enters alone; POST comes back
at each passage with what it imports; TASK replaced, GROUND leaves and CHARTER stays for AUDIT;
an offer imported comes before its importer's; STUDY holds GROUND and CHARTER before PIN over
two passages, SEAL entering only when the switch is open and in the order written, the trace
`initialize` naming them; a document of the passage STUDY imports takes STUDY's hold, a held
document keeps what it imported at its entry, a frame's import another document imports stays at
the pop; a document imported brings its `serve:` rows; ROUND's call to STUDY releases them; an overlay of STUDY and an overlay of an
instance's TURN add an import; the refusals `import-cycle`, `reference-unknown`,
`imports-malformed`, `mounts-gone`.
