# The conduction

Why pp puts a conductor between you and the model, how it stages one step, and the
two ways a run can be conducted. The full mechanics are in the
[reference](../REFERENCE.md).

- [Context grows](#context-grows-monolithic-prompts-do-not-scale)
- [Why a conductor](#why-a-conductor)
- [A step, staged](#a-step-staged)
- [Two ways to conduct](#two-ways-to-conduct)
- [Core, kit, packages](#core-kit-packages)
- [What pp weighs in a session](#what-pp-weighs-in-a-session)

## Context grows. Monolithic prompts do not scale.

Agent instructions rarely stay small. A project begins with a few conventions,
then accumulates coding rules, review policies, document references, tool
restrictions, workflows and exceptions.

Placed in one permanent context file, these instructions gradually become
harder to maintain. Rules remain active outside the tasks they were written
for, obsolete guidance survives because removing it feels risky, and every new
requirement increases the burden placed on both the model and the person
maintaining the prompt.

Procedural Prompting turns that growing instruction block into a context
architecture. Instructions live in named documents. Constraints have an explicit
scope. Procedures decide when material enters the context, how it composes with
what is already active, and when it falls away. The result remains readable,
reviewable and extensible as the project grows.

## Why a conductor

A language model is excellent at judgment and poor at bookkeeping. Ask one to
follow a long procedure and you have handed it two jobs at once: the work, and
the management of the work — the current position, the rules in force, what
was already read, what comes next.

Procedural Prompting externalizes the bookkeeping. A small deterministic
**conductor** plays the procedure and hands the model **one output at a
time**. The model's freedom is untouched *inside* the step. The **limits**
around the step are not its concern anymore: it does not track them, so it
cannot lose them. And the limits are **yours to write**.

What the conductor does:

- **Stages the right context** — one block at a time: the documents the step
  needs, one instruction, the form of the answer and the exact call back.
- **Scopes constraints structurally** — a law is pushed with its frame, stays in
  force through nested work and disappears when that frame ends.
- **Proves work before it leaves** — a law of production is checked at the
  `PROVE` the author writes where the work can escape; a failed proof repairs
  before delivery, within an explicit bound.
- **Performs the readings** — pp reads and injects the source material itself;
  the model does not certify its own reading.
- **Composes without patching** — calls, sockets, overlays and mounts extend one
  procedure or package from another while each source stays intact.
- **Leaves a trace** — blocks, readings, proofs, refusals and timings are
  recorded per run, so the conduction can be inspected and measured.

## A step, staged

A procedure is a plain markdown document. This one stages a review: one reference
served by the tool, two production laws scoped to the work, one verdict, and the
proof of the laws before the verdict leaves:

```
---
name: REVIEW
kind: proc
description: review a draft against the house rules, then hand down a verdict
output: line
serve: |
  draft.md
constraints.production: |
  C1  you judge the draft; you never rewrite it.
  C2  a finding without the line it comes from is no finding.
proc: |
  SERVE
  INFER
  PROVE
---

Hand down ONE verdict — approve, revise or reject — and the findings that carry it.
```

The model receives the step fully staged:

```
▌ pp · run <key> · … · <time> · +<elapsed>

▌ REVIEW{2/3}

▌ INFORMATION — draft.md
(… the draft, served by the tool …)

▌ NEXT INSTRUCTION CONTEXT — REVIEW
Hand down ONE verdict — approve, revise or reject — and the findings that carry it.

▌ CONSTRAINTS
production:
C1  you judge the draft; you never rewrite it.
C2  a finding without the line it comes from is no finding.

▌ INSTRUCTION
INFER line => words
```

`C1` and `C2` travel with the frame and disappear when it ends. At the `PROVE`
step the model owes one verdict per law, with its evidence:

```
▌ INSTRUCTION
INFER proof [C1 C2] on all produced areas => tool

▶ CONTINUE
./pp <key> - <<'EOF'
<proof>
EOF
```

If the proof fails — a rewrite where a verdict was asked, for example — the same
document returns with the miss named in `DEVIATION`, and the repair happens before
anything reaches you. After the configured repair bound, pp hands control back
rather than pretending the step succeeded.

## Two ways to conduct

The same engine, the same procedures, the same rules — only the channel changes.

| | **agent mode** (recommended) | **editor mode** (the historical mode) |
|---|---|---|
| who advances the run | the house: it launches the coding agent, serves each step in its prompt and moves pp forward | the model itself, calling `./pp` from your editor session |
| where you work | the post (`./pp ui`), or the `agent` and `team` commands | Claude Code, Codex, Gemini or Cursor, as usual |
| what it enables | agents in the background, teams, budgets, one screen for all | one conducted conversation at a time |
| set up | [Quick start](../README.md#quick-start) | [the editor mode](editor-mode.md) |

In the agent mode the model never learns that someone else advances its run: it
answers the step in front of it, and the house does the rest. Under
`conduction: hybrid`, a step that only asks a value (a proof, a choice) comes
back in the tool result instead of costing a new launch: an exchange of three
laps takes 2 launches instead of 6.

## Core, kit, packages

| Layer | Where | Role |
|---|---|---|
| **Core** | `engine/` | The deterministic engine: it interprets procedures, holds runs and frame stacks, serves readings, scopes constraints and renders the next block. |
| **Kit** | `bases/kit/` | The default turn model: `BOOT` opens a session, `TURN` takes one message through its work and its proof. |
| **Packages** | `packages/<name>/` | Complete capabilities — the house, teams, plans, steering… — that plug into that model. |

The analogy is a kernel, a default session process, then applications. A package
extends the composition; it never patches the core or the package it depends on.

## What pp weighs in a session

pp weighs **5 % to 20 %** of a session, depending on the degree of conduction set
in the settings. The first exchange — the boot — carries the heaviest weight: pp
serves there what the rest of the session will not be served again. A high degree
of conduction asks for a comfortable context window.

## See also

- [The editor mode](editor-mode.md) — pp inside your editor, without the house
- [The reference](../REFERENCE.md) — every keyword, command and file
- [The language](reference/language.md) — the procedure keywords one by one
