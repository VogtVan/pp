---
name: METRICS
kind: doc
description: >-
  The frame of the metrics: what the ENGINE measures on its own -- the fields
  pp-monitoring exploits -- function by function, and the token estimator with its
  calibration. A reference, never played.
---

# METRICS — what the engine measures, and what an analysis reads

The SUPPORT lives in the core and is always on: every rendered block writes its
weight to the run's trace, part by part; the engine-run skills leave named
lines. This package adds nothing to the engine — it reads.

## The block line — volume, by function

Every `block` event carries `weight` and, when the block serves matter,
`payloads`:

| field | measures | function it discriminates |
|---|---|---|
| `weight.constraints` | the laws' characters as rendered (texts + held codes) | the LAW emission — graded by `verbatim_constraints` and the first-emission ledger |
| `weight.payload` | everything served under `INFORMATION` titles | the READINGS whole |
| `payloads` | `{subject: [chars, tokens≈]}`, per subject — two providers of one token add up | serve rows, CALLed bodies, mount bodies, provider tokens, the standing orders — each source apart |
| `weight.options` | a PICK's closed list | the elections |
| `weight.instruction` | the command and the output name | the asks |
| `weight.frame` | what remains: headings, titles, closings | the scaffolding |
| `weight.total` · `weight.tokens` | the block whole, characters exact and tokens estimated | — |

The block's `stack` names the document in flight: a block, and every interval
that ends on the agent's next move, is attributable to its STEP -- and through
the composition, to its package.

## The named lines — the engine's own effort

| event | fields | measures |
|---|---|---|
| `provider` | `name`, `token`, `package`, `rc`, `ms` | a payload provider the engine ran |
| `sink` | `skill`, `said`, `ms` | a document's production handed to its sink |
| `gesture` | `name`, `segment` | a skill the agent played through pp |
| `turn-end` | — | the turn's end, stamped by the harness hook or the operator's top (`./pp -et`) — the tail that makes AGENT TIME deducible |

## The token estimator — part of the metrics

`metrics.tokens` estimates the tokens a text costs: a pure function of the
standard library — no tiktoken, no dependency, no network — calibrated once
against the o200k encoding on rendered blocks (2026-08-28): **1.7 % median
error, 4.5 % at p90, 9.1 % at worst** over 21 blocks of about six thousand
characters; a text of one nature alone drifts up to 6-7 % (French prose under,
code over). Every analysis renders its token figures with the `~` sign — the
characters beside them are exact.

## Agent time — the deduction

Within a turn, the intervals between a rendered block and the agent's next
call are agent work, owned by the pending step. The tail — after the last
block, while the agent delivers its chat answer — is closed by the `turn-end`
stamp. Agent time of a turn = first pp call to `turn-end`, minus the engine's
traced milliseconds; the operator's wait (turn-end to the next prompt) never
enters. Without a stamp the analysis says the tail is unknown — it never
guesses.

## Resolution — what a regime lets you see

**Volume by package.** `report` maps each served subject to its OWNING package from the
repo's composition -- a served body (`NEXT`, `RECALL`, the kit's own) has no provider line,
yet belongs to its package. A provider line is added only for a skill the engine RUNS
(a consumed `payloads:` token); in a composition where nothing consumes a token, its
provider never runs -- that is not a gap, and the volume is still attributed by owner.

**Time granularity follows the fusion.** Under `instructions_fusion: max` a turn renders in
ONE output: the agent works it as a whole, so the time is per TURN, not per step -- the
report says so (`fusion=0, time is per TURN`). For per-STEP time (WORK vs NEXT vs proof),
measure a `pp-monitoring derive <dir> --fusion none` pass: one output per step, one interval
per step. The report always names the regime; it never feigns a granularity the trace
cannot carry.

## The levers — what a setting governed, by the figure

`report` closes on one line per setting: the value the source's `SETTINGS.md`
spells (`?` when an archive kept none) and what the traces charge to it. The
subjects are classed by their NAME alone — the rule an archive can still
apply: a subject a `provider` line named is a TOKEN (its owning package rides
that line), `standing orders`, `constraints` and `tools.md` are the protocol's
own, a subject with an extension is a READING (a serve row, a SERVEd file),
the rest are BODIES (a CALLed or mounted document, served by its name).

| lever | the figure |
|---|---|
| `proc_body_serve` | the bodies served AGAIN within one run (chars, count, the names) — what `once` spares |
| readings (no key: a row always serves) | the readings served (chars, count, the names), and the chars a repair re-served on traces older than 2026-09-05 — a repair re-serves nothing since |
| `verbatim_constraints` | the laws' chars and their share of the total; the standing orders' chars beside (the marble channel) |
| proofs (no key: the checkpoint stands) | the proofs, their seconds and their share of the agent time — one regime since 2026-09-05, no skip to count |
| `work_repairs_allowed` | the repairs and the refusals |
| `max_harness_tool_output` | the cuts and the turns they fell in — one more bare call each |
| `instructions_fusion` | the blocks over the stamped turns and the runs — the blocks per turn |
| `<package>_*` | each token the package regenerated (count, chars), named by its provider lines |
| `conduction_effort` | the preset of the four weight keys and of every fragment's `effort:` block |
