# The instance on disk

This file covers what an installed instance holds on disk, how runs and maintenance
share it, and how the build composes the marble and judges the composition.

Contents:

- [The instance on disk](#the-instance-on-disk)
  - [The marble, in layers](#the-marble-in-layers)
  - [What the build refuses](#what-the-build-refuses)
- [See also](#see-also)

## The instance on disk

```
workspace/                  # yours — whatever you actually work on, plus the doors
├── pp · pp.cmd             # the conductor's console — MACHINE-owned, self-repairing
├── CLAUDE.md, AGENTS.md, … # the wired harnesses' doors — written once, per flag
├── .claude/                # if you wired Claude Code — your own committed config
└── .pp/                    # the instance `install` seeded (default name; a parameter)
    ├── MEMBER.md · SETTINGS.md · FORMATS.md    # YOURS — identity, tuning, forms
    │                       # seeded in two layers: the engine's template (SETTINGS,
    │                       # FORMATS, the shelf of procs), then the base's user/ layer
    │                       # (the kit's MEMBER.md) — a base without user/ seeds no member
    ├── procs/              # YOURS — where a procedure of your own gets written
    └── .sys/               # the machine — nothing in it is yours to edit
        ├── engine/ · vendor/ · instance.yaml   # copied, pinned, repaired by `doctor`
        │                   # instance.yaml: source, slug, engine, the pins -- and `base:`
        │                   # when `-install … -base` named another base than the kit
        │                   # engine/system/SYSTEM.COMMON.md, SYSTEM.CONDUCT.md and
        │                   # engine/refs/PP.COMMON.md, PP.CONDUCT.md: the orders and the cards, the engine's
        │                   # own, compiled into system.md and system.common.md
        ├── records/        # operations.jsonl · history.jsonl · the records ·
        │                   # claims.jsonl (which run plays what is due once)
        └── state/          # session-<key>.json (a run's saved state) · its trace
                            # session-<stamp>Z-<key>.jsonl · its call lock,
                            # session-<key>.call.lock · a launcher's own files beside it
                            # (the agent package's session-<key>.wake.lock and .wake.log) ·
                            # maintenance.lock (the machine's: shared by every pp process,
                            # exclusive while a maintenance verb rewrites the machine)
```

`workspace/` is your project: your productions, your references, committed however
you like.

`.pp/` is the conductor's own home. `doctor` repairs it at constant pins; `upgrade`
re-materializes it at the source's current versions. `.pp/procs/` is where you
develop a procedure of your own, before it ever graduates into a package of its own.
The instance carries **everything** it runs on, the engine included.

#### How the root is seeded

The root is seeded in two layers:

1. The engine's template puts down what is the protocol's own: `SETTINGS.md`,
   `FORMATS.md`, the `_`-shelved procs.
2. The base then places its `user/` layer over it. The kit's is `MEMBER.md`, the
   member's identity. A base without `user/` seeds no member at all.

One package at most may carry a `user/` layer of its own (daneel does); it replaces
the base's. Two such packages refuse `user-packages-conflict`.

A file still equal to a seed swaps silently on `add`; an edited one is saved to
`.old` first.

#### One run, several calls

A run's saved state is written by one call at a time. Every keyed call of the console
except `-peek` holds the run's CALL lock (`session-<key>.call.lock`) from its start to
its exit. A harness that runs two tools at once, or a second terminal on the same key,
waits for it.

The wait is bounded: `call_lock_wait` seconds (SETTINGS, 30 by default). After that
the call refuses `call-busy` and plays nothing. Replay it once the first call has
answered.

A reader (`-peek`, `-stats`, the keyless `./pp`) takes no call lock and blocks no
call. Like every pp process, it holds the machine's maintenance lock shared.

A process a call launches (a skill) inherits `PP_CALL=<instance>:<key>`, the run its
parent holds. If that process calls the run back, it refuses `call-reentrant` instead
of waiting for ever.

A key is reserved by its SLOT, the same way for every run:

- `-new` creates the slot of the key it draws, exclusively.
- A LAUNCHER opens a run by playing `-new` itself, under the principal's mark
  (`./pp agent run`), and reads the key on the output's first line.
- A key whose slot stands is never drawn.

A launcher's own files beside a run are its own affair: the engine names none of
them. For example, `./pp agent run` holds its lock `session-<key>.wake.lock` for the
wake-up's whole life; see [packages/agent/README.md](../../packages/agent/README.md).

Every write of the saved state arrives whole: a temporary of its own, then one
rename. A trace is named by its run's key and created once, so two runs opened in the
same second have two traces.

#### Maintenance under living runs

The machine has ONE maintenance lock, `state/maintenance.lock`, beside the runs of
the instance that carries the machine. Every instance that borrows the machine uses
that same lock. It has two modes:

- **shared**: every pp process takes it when it starts and keeps it until it ends —
  a keyed call, `-new`, `-peek`, `-stats`, the keyless `./pp`, a package's command,
  the detached child of `agent start`. A process that launches a harness keeps it as
  long as it lives, so a wake-up keeps it for its whole length. Shared holders never
  block each other.
- **exclusive**: `upgrade`, `doctor`, `add`, `remove` and `-sync` try it without
  waiting.

If any pp process holds the lock shared, the exclusive verb refuses
`maintenance-busy`, reads and writes nothing, and names the processes that hold the
machine. Each pp process writes a marker `maintenance.d/<pid>` beside the lock for
its life (its command and the hour); a marker left by a process that is gone is
removed. Replay the verb once that process has ended.

While a verb holds the lock exclusive, every other pp process refuses
`maintenance-in-progress` when it starts and plays nothing.

An engine that a maintenance verb launches (a newer engine finishing the verb) plays
under its parent's hold: the parent writes a fresh token into the lock file and hands
it in `PP_MAINTENANCE`.

Under the exclusive lock no pp process lives, so `upgrade` takes no lock of a run. It
moves the pins, RENEWS every run of the machine and of its borrowers (see
[A run an upgrade renewed](#a-run-an-upgrade-renewed)), and sweeps the files of runs
already gone.

`-reset` is not a maintenance verb. It forgets each run under that run's call lock,
tried without waiting; a run whose call is under way refuses `call-busy`.

A call whose reader of stdout is gone before the console prints (`| head -c 0`) has
PLAYED: the run's state is saved before anything prints. The console says so in one
stderr line and exits 0, and `-peek` shows the block that stands.

#### Purging runs

`-reset` forgets a run and keeps its history: its trace stays, and `-stats` still
counts it. `./pp -purge` removes it for good: its slot or renewal mark, every
`session-<key>.*` beside it (its call lock, whatever a launcher put there), and every
trace of its key.

| Form | What it removes |
|---|---|
| `./pp -purge <key> [<key> ...]` | The runs named. A key no file belongs to refuses `run-unknown`. |
| `./pp -purge --before <YYYY-MM-DD>` | Every run whose last write (its newest trace, or its slot when it has none) is older than the date, and every trace older than it that names no run (written before a trace carried its key). A malformed date refuses `purge-invalid`. |

How the verb plays:

- Without `--yes` it writes nothing: it says, run by run, the files and bytes it
  would remove, then the total. With `--yes` it removes them and says the same.
- `-json` renders that count as one object `{dry, runs: [{key, files, bytes}], files, bytes}`
  for a program.
- Each run is handled under ITS call lock, tried without waiting. A run whose call is
  under way refuses `call-busy`, and NOTHING is removed.
- The call lock's own file is removed last, once the lock is released: a purge never
  removes a file it holds open (Windows refuses it). A file another process holds open
  -- a call that took the lock in between, the wake lock of the launcher that asked the
  purge -- is left in place, and the purge says so on stderr.
- The claims of `records/claims.jsonl` stay: a claim whose run's slot is gone is void
  already.

The verb plays on any instance: a house, or an agent that borrows its machine, from
its own console. What a package's script writes (its records) is that script's to
purge.

#### A run an upgrade renewed

A run's state binds to the versions it was played on; its key does not. The upgrade
replaces the slot of every run standing — a chat waiting for its message, a wake-up
between two calls, at the machine and at every borrower — by a RENEWAL MARK at the
same path, `session-<key>.json`:
`{"renewed": {"at", "from", "to"}, "log", "turns", "off", "awaits"}`.

| Field | Holds |
|---|---|
| `renewed` (`at`, `from`, `to`) | the versions that moved |
| `log` | the trace's name |
| `turns` | the exchanges completed |
| `off` | the packages the run switched off |
| `awaits` | what the run awaits: `message` or `production` |

The run's other files (`session-<key>.*`: its call lock, a launcher's file) go. Its
trace stays and says `renewed`. The console says `n run(s) renewed by the update`. A
launcher's reservation that no opening took holds no run: it is dropped.

What follows a renewal:

- The next keyed call on the key REOPENS the run under it. The boot is served as at
  an opening, the trace continues (`reopened`), the exchanges are counted on, and the
  boot is set there (`context.is_boot()` holds at the reopened exchange). The packages
  the run switched off stay off. One key, one trace: `-stats <key>` counts one run.
- The text that call carries is the principal's message when the run waited for it
  (traced `prompt`, served as `-new <message>` serves it). A production, a value or a
  verb (`-s`, `-compacted`, `-disable`) is NOT played, and the first block says so in
  its DEVIATION section.
- `-peek` and `./pp` on a mark print one line (the run renewed, the versions, the
  call that reopens it) and write nothing.
- A mark holds no cadence claim: the period is free for the next boot.
- A mark crosses a further upgrade: `to` follows, `at` and `from` are kept. It stands
  until its run reopens or `-reset` forgets it. `run-unknown` answers only a key
  forgotten or never handed.
- The upgrade that first installs this behaviour is played by the engine it
  replaces, which still closes the runs; the upgrades after it renew them.

#### Locks under POSIX and Windows

The lock is `flock` under POSIX. Under Windows it is `LockFileEx` on one byte far past
the file's content (a Windows lock forbids other processes to read the bytes it
covers). This Windows path is written but NOT tested.

#### What is due once is played once

A cadence (`HISTORY`, a dated step) is played by ONE run per period. The boot that
finds it due CLAIMS its period (the cadence's name and the last passage of its
anchored weekday) at `records/claims.jsonl`, under that record's lock, before the
document is injected. A boot that finds the period claimed by a living run injects
nothing and says so in its trace (`cadence-claimed`).

A claim holds while its run's saved state stands — one rule for every run, whoever
launched it — and is void once that state is gone; the next boot re-claims. A run
that died during its exchange keeps the period until it is forgotten: one period lost
at most. There is no clock: the date is still computed from the records.

The checks pushed at boot are not claimed: a signal is the reminder of one run.

The shared records (the house's journals, continuity's two) are appended under their
lock, and a reader skips a last line still being written. Every compiled artifact
(`tools.md`, `output.md`, `system.md`, `receipts.yaml`) arrives whole, by a temporary
and one rename.

### The marble, in layers

The marble compiles SECTION BY SECTION, ONE ARTIFACT PER
[CONDUCTION MODE](block.md#the-two-conduction-modes):

- `.sys/system.md` for a run the LLM conducts;
- `.sys/system.common.md` for a run its principal conducts.

Every section — the engine, the base, each package — gives the marble at most TWO
files of its `system/`, and the build reads no other:

| File | Holds | Compiled into |
|---|---|---|
| `SYSTEM.COMMON.md` | what holds in both modes | both artifacts |
| `SYSTEM.CONDUCT.md` | what tells the agent to make pp advance when it conducts the run itself: the first call, the call each block names, the closings, the chunks, the compaction, the parenthesis, and the words only that mode uses | `system.md` alone |

A file absent, or without a body, adds nothing. The rest of `system/` is free for
another use.

The sections compile in the order of the imports, each its COMMON then its CONDUCT:

1. **The engine.** First `engine/system/SYSTEM.COMMON.md` (its orders, written on the
   word *principal*, the one a run answers to, and naming no base), then
   `engine/system/SYSTEM.CONDUCT.md`. Last of the engine's section come the engine's
   cards: `engine/refs/PP.COMMON.md` (both modes) and `engine/refs/PP.CONDUCT.md` (the
   LLM's mode alone).
2. **The base.** Its precision: who the principal is here. The kit's COMMON says
   *the operator*, in their message, declares where a response lands and says the end
   of a passage; its CONDUCT says the conducted turn and the parenthesis.
3. **Every other package**, in the requires topology.

#### Receipts, replaces and the received card

Each artifact has its build receipt; `doctor` names both. Under `SYSTEM_PROMPT.md`
with `override: true`, each has its replace: `system.replace.md` and
`system.common.replace.md`.

The boot serves the run's own artifact (`standing orders`), and so does the re-serve
of `-compacted`. A stale receipt of that artifact refuses the opening
(`artifact-stale`). Adapters and launchers pass `system.md`: a harness session is one
the LLM conducts.

The card a harness RECEIVES (`.claude/skills/pp/SKILL.md`, `.agents/skills/pp/SKILL.md`,
gemini's `/pp`) is the card followed by the engine's `SYSTEM.CONDUCT.md`. It is one
composition, written by every adapter, and compared by `doctor` and by the boot's
`card-drift` at the two skill homes. Gemini's `/pp` is written, never compared.

#### The base

The base is the package `base:` names at `instance.yaml` (the kit when the key is
absent). The engine resolves it by that role alone:

- its sockets are their own address;
- its settings keys are bare;
- its `BOOT.md` opens the run and its `TURN.md` plays the turn.

A base without `system/` compiles a marble of the engine's orders and card alone. A
base that lacks `procs/BOOT.md` or `procs/TURN.md` refuses `base-incomplete`.

### What the build refuses

Every build (`-build`, install, `add`, `doctor`, `upgrade`, `remove`) judges the
composition WHOLE before writing anything: first the manifests' contract (the
contributions, their sockets, verbs and skills), then the topology.

Every reference a package's document or manifest carries is resolved to its owner and
refused by name. Such a reference is a `CALL`, a `SERVE` row, a `tools:` offer, an
overlay, an `attach:`, a `sink:`, a contribution's skill, an `output:` format, or a
`@SETTINGS` key.

| Refusal | When |
|---|---|
| `dependency-undeclared` | the owner is a package the referrer does not require |
| `reference-unknown` | nothing carries the name |
| `socket-undeclared` | a package's proc HOOKs a socket its manifest does not declare |
| `name-unprefixed` | a public name wears nobody's package |
| `name-ambiguous` | two packages carry the same proc or ref as a base |

#### Names wear their package

The names a package exposes wear its name; the base package alone stays bare:

| Name | Form |
|---|---|
| console verbs, vector families, payload tokens | `<package>-<name>` |
| skills | `pp-<package>` |
| settings keys | `<package>_<key>` |

A name wearing another package's prefix joins that package's thing and needs it
required. Procs and refs stay bare and are ONE base across the packages.

A socket is declared and HOOKed in the same short form, `<proc>.<hook>`. Its ADDRESS
carries the package that opens it: `<pkg>.<proc>.<hook>`, three segments. The base's
sockets and your own are addressed by the two segments they write.

#### Your own documents

Your own documents are the top of the composition: they reference every pin and
offer what your harness carries. A `serve:` token is judged on its owner alone: a
reading still to build or a file of your repository is the run's matter, never the
build's.

## See also

- [console.md](console.md) — the console verbs (`install`, `doctor`, `upgrade`, `add`, `remove`) that write this instance.
- [agent-face.md](agent-face.md) — the keyed calls (`-new`, `-peek`, `-reset`, `-stats`) that use the runs stored here.
- [../../packages/agent/README.md](../../packages/agent/README.md) — the house, its launchers and their files beside a run.
- [../../packages/team/README.md](../../packages/team/README.md) — the teams a house runs on this machine.
