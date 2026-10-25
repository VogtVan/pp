# exec — a script played when a document enters

## What you write

On a proc or on a document that is mounted, `exec:` names a script and its words:

    exec: pp-stamp stamp @STAMPED.mode @SETTINGS.max_harness_tool_output plain

- In a document of your instance, the first word is a skill of your instance, the rest are its
  words. In a package's document, the words go to the package's own skill (`exec: stamp` plays
  `pp-<package> stamp`).
- A word written `@Doc.field` or `@SETTINGS.<key>` takes the value a guard would read (see
  `context/tags`); any other word passes as it is.
- The base of a document and each overlay of it may write their own `exec:` (see
  `composition/overlay`); `order: exec before <package>` or `exec after <package>` sets the rank
  of the one written there, and of that one alone.

## What you get

- The script plays once at every ENTRY of the document: when it is CALLed (see
  `composition/call`), when it is mounted — at every passage when it mounts itself at a point
  (see `composition/mount`) — and at each lap of a door that turns (see `control-flow/cycle`).
- It plays before the body and before anything the document serves: a payload it names reads
  what the script has just written (see `context/payload`).
- It never plays when nothing enters: not on `-peek`, a compaction, a repair that replays the
  document (see `rules/repair`), the next chunk of a long block, or the rewind of the run's root.
  The root itself is entered by no CALL: its own `exec:` never plays.
- A mounted document whose `when:` is false does not enter, and its script does not play (see
  `composition/qualifiers`).
- What the script prints goes to the instance's bus alone: a `::push` line stands as a signal
  (see `automation/checks-and-signals`); nothing else is shown. An exec PREPARES, it serves
  nothing.
- Several `exec:` on one document play in the order of their packages' requirements, the
  instance last; an `order:` moves the file that writes it — just before the first file of the
  package it names, or just after the last — and nothing else; a preference toward a package
  that is not there changes nothing.
- `-stats` counts the scripts played by each run.
- Under the principal's conduction the same entries play the same scripts, once each.

## When to use it

- A record must be brought up to date at the moment a document enters, before the agent reads
  anything: a stamp, a count, a list of what is due.
- A signal must be pushed when a step of work begins.
- To serve the script's output to the agent, use a payload instead (`context/payload`); to hand
  the agent's production to a script, a sink (`outputs/sink`).

## What refuses

- When the document enters: a script that exits with any code but 0 refuses `exec-refused` —
  the CALL pushes nothing, the mount is not written; a `::mount` line in its output refuses
  `exec-mount`; a `@Doc.field` whose value is empty refuses `exec-argument-empty`.
- When the instance builds: a skill nobody carries, or a `@Doc.field` that resolves nowhere,
  refuses `reference-unknown`; an `exec:` on a document that is never entered — a package's
  document with neither steps nor a `mount:` line, a reference — refuses `exec-unplayable`;
  two `order:` lines that want each other first refuse `order-cycle`.

## The demonstration

- `procs/DESK.md` — calls `STAMPED.md`.
- `procs/STAMPED.md` — stamps `fast`, a setting's value and `plain` at its entry, then reads the
  stamp back through the payload `alpha-seen`.
- `procs/TRIAL.md` — calls `JUDGED.md`, a proc that stamps at its entry, then lists and picks.
- `procs/LOOP.md` — a root that opens its own point, `loop.open`, at every passage; its own
  `exec:` never plays.
- `procs/RESET.md` — mounted at `loop.open`: it stamps at every passage.
- `procs/GATE.md`, `procs/GATED.md` — a closed gate, and a document mounted at `loop.open`
  only while the gate is open.
- `procs/ROUNDS.md` — calls `LAPPED.md`, a door that turns on `laps` (provided by
  `procs/LAPS.md`) and stamps at each lap.
- `procs/SPOILT.md` — a document whose script fails; `procs/ASKER.md` calls `BROKEN.md`, a proc
  whose script fails.
- `procs/PUSHER.md` — its script pushes a signal; `procs/MOUNTER.md` — its script tries to
  mount a document.
- `procs/READER.md` — calls `BIG.md`, a proc whose body is served in several chunks.
- `procs/HALL.md` — calls `ENTRY.md`, a package's proc; `procs/ENTRY.overlay.md`,
  `procs/ENTRY.ahead.md`, `procs/ENTRY.gamma.md` — another package's overlays of it, without a
  preference, before `alpha`, after an absent `gamma`; `procs/ENTRY.opposed.md` — a base that
  wants to go before the overlay's package.
- `procs/IDLE.md` — a package's document nobody enters; `procs/UNSKILLED.md` — an `exec:` naming
  no skill; `procs/UNTAGGED.md` — an argument naming a document nobody has.

The skills `pp-stamp` and `pp-laps` are yours to write in your instance's `skills/`; the
packages behind `alpha-seen`, `ENTRY` and its overlays are written by the test.

## The test

`tests/patterns/automation/exec.py` writes the scripts and the packages, then plays the
demonstration: STAMPED stamped before its payload, its words resolved; no script on `-peek`,
a compaction, JUDGED's repair or BIG's chunks; RESET at every passage of LOOP, GATED never; one
stamp per lap of LAPPED; SPOILT and BROKEN refused with nothing written; PUSHER's signal standing,
MOUNTER refused, the count of `-stats`; ENTRY's scripts in each order, the opposed pair refused;
the build refusals; one script for one entry under the principal's conduction.
