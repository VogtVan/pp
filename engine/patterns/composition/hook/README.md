# hook — let other procs play at a point of yours

## What you write

- In your proc, the host: one line `HOOK <proc>.<hook>` where the others may play,
  your proc's name in lowercase, then a name for that point (`HOOK desk.open` in DESK).
- In each proc that plays there, the contributor: `attach: <proc>.<hook>` in its front
  matter (`attach: desk.open`).

## What you get

- At the `HOOK` line, every proc that attaches to that point is called, one after the
  other: each plays in a frame of its own, like a `CALL` (see `composition/call`), with
  its own laws while it plays.
- Several contributors play by name. A contributor of a package plays before those of
  your instance; `order:` changes that order (see `composition/qualifiers`).
- When the last contributor is done, your proc goes on with the step after the `HOOK`.
- A point that no proc attaches to plays nothing: your proc goes straight on.
- The host never names its contributors: adding a proc that attaches is enough to make
  it play there; its own `when:` can keep it out (see `composition/qualifiers`).

## When to use it

- Leave a place in your proc where other procs, written later or by someone else, add
  their own steps.
- Let a package play inside a proc it does not own, at a point that proc offers.
- To bring laws and readings without any step, mount instead (see `composition/mount`);
  to act once when a proc starts, use its entry (see `composition/initialize`); to let the
  agent choose whether a proc plays, offer it (see `composition/door`).

## What refuses

- A proc that writes the same `HOOK` twice refuses `socket-doubled` when the instance is
  built: a point names one place in the flow.
- A contributor whose point no proc hooks plays nowhere: the build warns
  `attach-unhooked` and goes on; in a package, the same refuses.

## The demonstration

- `procs/DESK.md` — the host: `HOOK desk.open`, then one `INFER`.
- `procs/ALPHA.md`, `procs/BRAVO.md` — two contributors, `attach: desk.open`, one
  `INFER` each.
- `procs/BARE.md` — a host whose point nobody attaches to.
- `procs/TWICE.md` — the same `HOOK` written twice: it refuses.

## The test

`tests/patterns/composition/hook.py` plays them: DESK calls ALPHA then BRAVO, each in its
own frame, then takes its own step; BARE goes straight to its step; TWICE refuses
`socket-doubled`; ALPHA and BRAVO attached to a point nobody hooks are named by the
`attach-unhooked` warning while the build passes.
