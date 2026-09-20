---
name: CONDUCTION
kind: doc
description: When to choose each form -- what conduction carries to the agent, where work comes from, and where it is played. PP-DESIGN says how each form is written.
---

# CONDUCTION — when to choose each form

`PP-DESIGN` says HOW a form is written. This page says WHEN to choose it. Read it
before you decide where a piece of knowledge or a piece of work goes.

## What conduction carries

Conduction brings one piece of knowledge to the agent, by one channel, at one
moment. A good placement brings it just before the agent needs it, and no earlier.

## The five channels

| channel | what lives there | the agent gets it | it costs |
|---|---|---|---|
| the standing orders | the protocol | at boot | every run |
| MEMBER and its readings | the role, its references | at boot | every run |
| an overlay of TURN | a package's reflex and its offers | before every ask | every run, whatever is asked |
| a document at a socket | a moment's brief, its data | at that moment of the turn | once per run while unchanged |
| a door, or a mount behind a skill call | a method, its readings | after the agent opens it | only in the runs that open it |

## Three measures

- **Reach** — does it arrive before the ask, or after it?
- **Mass** — the characters it costs each time it is served.
- **Latency** — the calls the agent makes to get it: none, one for a door, several for a staircase.

## Two laws of knowledge

1. The reflex comes before the ask, and it is small: when to open, what to name.
2. The know-how comes behind the door the reflex opens, and it is large.

A reading placed on an overlay of TURN is paid by every run. The same reading
behind a door is paid by the runs that need it.

## Where work comes from

- **Direct** work is what the operator's message asks for.
- **Induced** work is what the direct work makes due: a thread to update, a plan step to check off, an operation to log.
- **Background** work is due on a date or at every turn, whatever the message says: a weekly digest, a reading of the message, the choices that close the exchange.

## Where work is played

**1. Direct work plays in the turn's `WORK` step.** Offer the skill it needs from an
overlay of TURN, with the short rule that lets the agent use it at once. Figure:
*The overlay*.
Model, whole: `continuity/overlays/TURN.md`

    tools: |
      +pp-continuity

    Read earlier operations whenever the work needs them with
    `pp-continuity recall last <days>`; recall is available throughout the exchange.

**2. When direct work changes its method, it still plays in `WORK`,** under a door
or a document mounted by a skill call, which brings the laws. The overlay keeps the
reflex alone: when to open it. Figures: *The door*, *The mounted step*. Models: the
plan package's methods, the authoring doors.

**3. Induced and background work play in a document attached to a socket,** with a
scope of its own: a `WORK` step when it plays a skill, an `INFER` step when it only
produces a reading. A guard keeps it silent when nothing is due. Figure: *The
conducted step*.
Model, induced: `continuity/procs/OPERATIONS.md`

    proc: |
      WORK
    attach: turn.end
    when: "@SETTINGS.continuity_memory_frequency"

Model, background: `improvement/procs/IMPROVE.md`

    proc: |
      INFER
    attach: turn.end
    sink: pp-improvement

**4. Data another document consumes enters by a mount or a payload.** It serves,
it asks for nothing, and it orders nothing. Figures: *The contributor*, *The payload*.
Model: `continuity/procs/RECALL.md`

    mount: boot.ready
    provides: continuity-recall

## The test of a document

A document that tells the agent to play a skill has a `WORK` step, or lives in the
view of one. An `INFER` step produces: one production, no skill call. A mounted
document serves: it gives no order. When a mounted document or an `INFER` brief
says "play this skill", move that order to a `WORK` step and leave the data behind.

## A checklist for the author

1. Where does this work come from: direct, induced or background?
2. Does it need a skill? Then it needs a `WORK` step.
3. At what moment does the agent need this knowledge: before the ask, or after it?
4. What does it cost every turn, and every run?
5. What keeps it silent when nothing is due?
