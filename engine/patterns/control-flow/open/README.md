# open — enter a space the messages stay in

## What you write

A step `OPEN <document>` in your `proc:`, anywhere among its steps. The document must be a
proc that plays steps of its own and never leaves by itself: no `next:`, no `cycle:`, no
`field:`.

    proc: |
      WORK
      OPEN SPACE.md
      INFER
      PROVE

The agent can open the same kind of space itself: `./pp <key> -open <name>`, on a name the
current output offers under TOOLS (the same rule as `-s`).

## What you get

- The opened document is a SPACE. It enters like a `CALL` (see `composition/call`): its body,
  its readings, its laws and its offers arrive, and what it mounts at its own entry
  (`mount: space.initialize`) stays mounted while the space stands.
- The space becomes the ROOT of the passage, wherever its `OPEN` stands: when its last step is
  done, the passage ends there (see `control-flow/root`). The run waits for the principal's
  next message, the exchange is counted, the documents mounted for that passage are taken
  down, and the next message replays the space from its first step.
- The steps of the caller after the `OPEN` do not play while the space stands, and neither
  does its `PROVE`: the messages stay in the space.
- A space can open another space: the deepest one is the root.
- `./pp <key> -close` leaves the deepest space, with anything stacked over it; a step pending
  there is dropped, what was said stays said. The caller takes up where it stood -- the step
  after its `OPEN`, or the step that was pending when `-open` opened the space -- in the same
  passage. What the space produced is still owed to the caller's next `PROVE`, with the laws
  of the space: that `PROVE` asks them beside the caller's own.
- The first line of every output names the root: `▌ pp · run <key> · root SPACE · …`.
- `-compacted` inside a space serves the space again; it stays the root.
- In a run its principal conducts, `-open` and `-close` answer one line, `pp: opened` and
  `pp: closed`; what follows comes at the principal's next call.
- The run's trace says `opened` with the name of the space the agent opened, and `closed`
  when a space leaves.

## When to use it

- A piece of work spans several messages and has its own rules: a review, an interview, a
  planning session. Open it as a space; close it when it is settled.
- Put `OPEN` where the work always needs the space; offer the proc under `tools:` when the
  agent decides when to open it.

## What refuses

- `OPEN` to a document that resolves nowhere: `reference-unknown`, at the build.
- `OPEN` or `-open` to a document without `proc:`, or with `next:`, `cycle:` or `field:`:
  `open-unplayable` -- at the build for `OPEN`, at the call for `-open`.
- `-open` on a name the output does not offer: the pending block answers, as for `-s`.
- `-close` with no space open: `space-none`.

## The demonstration

- `procs/CALLER.md` — a root: a `WORK`, `OPEN SPACE.md`, then an `INFER` and a `PROVE` under
  its law C1.
- `procs/SPACE.md` — the space: an `INFER` and a `WORK` under its law S1.
- `procs/NOTES.md` — a reading mounted at the space's entry (`mount: space.initialize`).
- `procs/LOBBY.md` — a root that offers DEEP to the agent.
- `procs/DEEP.md` — a space that opens another one between its two steps.
- `procs/INNER.md` — the space DEEP opens.

## The test

`tests/patterns/control-flow/open.py` plays CALLER: SPACE parks the run, the count moves,
the passage's reading leaves and NOTES stays, CALLER's tail stays undone, the next message
replays SPACE, the heading names it, `-compacted` keeps it; `-close` gives CALLER back at its
`INFER`, its `PROVE` asks C1 and S1. On LOBBY it opens DEEP with `-open`, DEEP opens INNER,
and two `-close` give it all back. It checks the refusals, the console verbs under both
conductions, and the build.
