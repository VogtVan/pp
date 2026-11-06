# The bus, the diagnostics and the misses

This file covers the engine's bus of operational signals, the diagnostics it renders from them, and what happens when an answer misses: the repair, the bound, the stop and the refusal.

- [The bus and the diagnostics](#the-bus-and-the-diagnostics)
  - [The bus](#the-bus)
  - [A diagnostic is a signal with a level](#a-diagnostic-is-a-signal-with-a-level)
  - [The operator's hand](#the-operators-hand)
- [When an answer misses](#when-an-answer-misses)
  - [What counts as a miss](#what-counts-as-a-miss)
- [See also](#see-also)

## The bus and the diagnostics

The engine keeps ONE bus of operational signals, and says the ones that
matter itself.

### The bus

A signal is PUSHED where its fact happens.

**By the engine, for its own:**

| Signal | Fact |
|---|---|
| `card-drift` | a projected card differs from the contract |
| `refused` | a call the engine refused by name |
| `repaired` | a document replayed after a miss |
| `serve-stale` | |
| `serve-shadowed` | |
| `material-unknown` · `material-missing` | a reading whose tag or path moved |
| `mount-gone` | a standing mount whose document no longer answers its address |

**By a package**, for the ones its manifest declares under `contributes: events:`:

- `signals`, their `sector` and `priority`;
- `vectors`, the families a signal may point at;
- `sectors`, its own NEXT real estate with an `icon` and a `cap`.

A signal is LATCHED at the run as one entry, `{signal, source, vector, door,
sector, n}`:

- the source is the declarant;
- the door is the way out, when the signal has one;
- the count grows while the fact stands.

#### Sectors

The `protocol` sector is the commons every declarant may name. A named sector
belongs to the package that declares it:

- a colliding declaration refuses the registry read;
- a signal claiming a sector its provider does not declare refuses unowned.

What a package DOES with the bus — a counter, a threshold, a sink shaping what
the agent formulates — is that package's mechanism, described in its own
README. The engine only carries.

### A diagnostic is a signal with a level

A signal may declare `level: critical | warning | note`: the engine for its
own, a package under `contributes.events.signals`. Any other word refuses
`level-invalid` at every read of the registry, the build's included.

With a level, the engine RENDERS the signal itself, in the block where it
happens or the next one, under a `▌ DIAGNOSTIC` section — one line per
diagnostic:

```
<signal> · <level> · <fact> -- <way out>
```

- The fact is the push's evidence; the way out is the signal's door.
- The line is said ONCE per run and per fact (a second `repaired` on another
  document is a new fact), whether or not any package reads the bus. A
  kit-only instance sees its drifted card at boot.
- The section sits between `DEVIATION` and `OPTIONS`, near the instruction. A
  view (`-peek`) forms none.
- It is WEIGHED at the trace as the `diagnostic` part of the block's line, and
  counted by `-stats`.

The levels posed today:

| Signal | Level |
|---|---|
| `card-drift` · `repaired` | warning |
| `refused` · `serve-stale` · `serve-shadowed` · `mount-gone` · `material-unknown` · `material-missing` | note |

There is no `critical` yet: it is reserved for what keeps a run from holding
its word. The standing orders say what the agent does with one: say it to the
principal with its level, a `critical` before any work.

### The operator's hand

`./pp acquit <vector>` retires a treated signal vector: its counter and its
latch fall together, and the bus stops asking.

A package whose reflex reads the bus (a sink, a `NEXT` overlay) leaves with
`package.<name>: off` or `-disable`. The diagnostics stay: they are the
engine's.

## When an answer misses

Back to the [README](../../README.md)'s `REVIEW`: the verdict came back as a
line. `REVIEW` carries laws of production, so the engine appends the exit
checkpoint: `INFER proof => tool (heredoc)`, no brief — the catalog's `proof`
format defines the shape.

The agent proves its production against each constraint in force, and hands
down a proof whose `C1` cannot pass, because the production rewrote the draft:

> `./pp <key> -` … `{"code": "C1", "evidence": "I rewrote section 2 to show the fix", "verdict": "fail"}` …

The conductor does not argue. The document reopens from its first step: the
injected checkpoint is purged with the reopening, and its repair is counted on
the frame. The block comes back, one field heavier:

```
▌ pp · REVIEW{2/2} · REPAIR 1

▌ INFORMATION — draft.md
# Q3 report — draft

The introduction restates the abstract almost verbatim. Section 2 presents the
results before the method, and its lead paragraph buries the headline number.

▌ CONSTRAINTS
C1  you judge the draft; you never rewrite it.
C2  a finding without the line it comes from is no finding.

▌ DEVIATION
your own proof failed -- C1: I rewrote section 2 to show the fix

▌ INSTRUCTION
INFER line => words

▶ CONTINUE
./pp <key>
```

The whole document is replayed: the draft re-served to the very eye that
misjudged it, the miss **named with the proof's own words**, the same answer
re-asked in the same form. The rewrite has nowhere to land, and `C1` cannot
have faded — it never left the screen.

### What counts as a miss

- an answer outside `OPTIONS`;
- a list handed to a `PICK` that is not an array of scalars;
- an empty production the next step consumes;
- a `json` that does not parse;
- a proof that leaves a code the line asks unnamed;
- a proof with a failing verdict that declares no gap (no `blocked`).

Only a move the tool **watched** counts. A status call is where the run stands,
held against no one.

#### What counts against the bound

What counts against the bound is a replay or a miss:

- a bare `fail`;
- a code failing again at its mini-proof;
- an empty answer;
- a mini-proof that names other codes than the repaired ones.

A fix whose mini-proof holds counts nothing. A declared gap (`blocked`, see
[The checkpoint](language.md#prove--the-checkpoint)) is no miss at all: the
checkpoint closes on it. `-stats` counts the same repairs.

A fused output a repair opened says `· REPAIR n` on the heading of each step it
plays again.

#### At the bound, the run stops

The repair counts survive the reopening. At the bound (`work_repairs_allowed`),
the conductor refuses `repair-exhausted` and the run STOPS on the step:

- a mark at the slot holds the document, the step, the count and the miss;
- `awaits` says `message` on it;
- the stack stands as it was — nothing reopened, nothing rewound;
- the trace says `stopped`.

The next keyed call — the principal's message, or a bare call — takes the step
up. The mark leaves, the counts of the document re-arm, and the document
reopens on the miss the bound saw, the message served as
`the principal's word` (traced `taken-up`).

`-peek` on a stopped run renders the step with a fact and no closing.

`exec-refused` and `artifact-stale` stop nothing of the run: the document or
the environment is wrong, and the next call plays once it is mended.

#### A tool outside the scope is caught

A tool invoked outside the block's scope is **caught** instead. The pending
block answers, the ask named as not played. No repair is counted, the pending
step stands on screen, and the trace says `offer-absent` with the name.

#### Deviation and refusal

- A **deviation** is the agent's move missing: the document replays.
- A **refusal** is the document or the environment being wrong: exit 2, a named
  reason, nothing played.

## See also

- [The block and the channels](block.md) — where the `DEVIATION` and `DIAGNOSTIC` sections sit in a block.
- [The language](language.md) — `PICK`, `PROVE` and the checkpoint whose misses are repaired here.
- [The agent face](agent-face.md) — `-peek`, `-stats` and the other commands named here.
- [The operator's console](console.md) — `acquit`, switching a package off and the console's verbs.
