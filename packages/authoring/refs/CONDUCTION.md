# CONDUCTION — why a reading goes where it goes

`PP-DESIGN` says HOW a form is written, `PP_CHEATSHEET` what each mechanism does; this
page says WHY conduction exists and WHEN to choose each form. Read it before you decide
where a piece of knowledge or work goes.

## Why conduction

The documents of an instance exist to give the agent a knowledge. Enough general
knowledge must reach it to play the right proc at the right moment; the rest reaches it
when the moment comes. Conduction is the art of that transport: move a line or a
paragraph and something stops working. Serving everything at the turn is brute force: it works, slows production
and costs at every run. A door costs a call: the agent must open it to
receive the teaching. The balance is delicate; here are its measures.

## What conduction carries

Conduction brings one piece of knowledge to the agent, by one channel, at one moment.
The readings found both the proof and the production: an `ok` cites a served text; without it the
proof is an opinion on a law known by its code alone. A model's training and a session's
prompts do not replace a well-scaffolded context: without it the production drifts from
its target. The boot is paid once: what a run has seen is spared in its later exchanges. The ratio of served mass to answers is a figure of COST, never of return.

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

Mass has a grain and a place. A register served whole for one id is a reading without
grain; a row that serves a whole file for one range costs the file. The middle of a long block weighs less than its edge: a context has a diminishing return, and "well-scaffolded" means
the grain and the place, not the presence alone.

## What a reading founds

The context precedes the ask. At boot nobody knows what the operator will ask, so the
scaffolding is laid before: the method served for nothing tonight would have held the
law had the ask been "frame X". The right distinction is not LESS context but
the reading that matches the inference asked of it, in grain and in moment.
Served is not applied: the context founds the inference, it does not guarantee it — that
is why the proof and the refusals exist.

## Two laws of knowledge

1. The reflex — when to open, what to name — comes before the ask, and it is small.
2. The know-how — how — comes behind the door the reflex opens, and it is large.

A reading placed on an overlay of TURN is paid by every run. The same reading behind a
door is paid by the runs that need it, and a run pays a mounted reading once. The boot keeps what founds EVERY ask — the standing
orders, MEMBER, the recall, the catalog — and loses what founds a particular one. A
placement fails in two directions: upward, a reference put on the document that is always
open; downward, a row at the gesture that serves the whole file.
The second is the author's grain, written at framing.

## The offer

At the turn the packages must tell the agent that something exists. The offer of the
skills, with their descriptions, suffices on three conditions: the description says WHEN,
not only what; the overlay of TURN carries the reflex and the offer in one paragraph; the
reference lives behind the door or the mount. A tool must not arrive without its rules:
the first turn can carry work, and after a summary of the conversation the rules of an
attached document do not come back, its body being served once per run. So the overlay stays,
three useful sentences — when to act during the work, what the
attached step takes up, where to read the ids — and no internals.
Model, whole: `continuity/overlays/TURN.md`

    tools: |
      +pp-continuity

    Read earlier operations whenever the work needs them with
    `pp-continuity recall last <days>`; recall is available throughout the exchange.

Model, a package with steps of its own: `steering/overlays/TURN.md`

    `pp-steering` organises the operator's initiatives into threads and steps of work.
    Manage these initiatives proactively, in the steps dedicated to them.

## Where work comes from

- **Direct** work is what the operator's message asks for.
- **Induced** work is what the direct work makes due: a thread to update, a plan step to check off, an operation to log.
- **Background** work is due on a date or at every turn, whatever the message says: a weekly digest, a reading of the message, the choices that close the exchange.

## Where work is played

**1. Direct work plays in the turn's `WORK` step.** Offer the skill it needs from an
overlay of TURN, with the short rule that lets the agent use it at once. Figure:
*The overlay*. Model: the continuity overlay above.

**2. When direct work changes its method, it still plays in `WORK`,** under a door
or a document mounted by a skill call, which brings the laws. The overlay keeps the
reflex alone: when to open it. Figures: *The door*, *The mounted step*. Models: the plan
methods, the authoring doors.

**3. Induced and background work play in a document attached to a socket,** with a
scope of its own: a `WORK` step when it plays a skill, an `INFER` step when it only
produces a reading. A guard keeps it silent when nothing is due. An attached `WORK`
was feared to cost a call; observed, it fuses with the steps that close the turn.
Figure: *The conducted step*.
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

## The law of inference

Orchestration is probabilistic, execution is deterministic. Everything that can be
scripted is scripted, and is never asked of the agent: reading, writing, parsing,
validating, counting belong to the skills. Inference is
for constrained judgment — classifying, composing, arbitrating, refusing — bounded by the conduction that frames it. The agent chains scripts by its
`WORK` steps; it does not replace them; inference is not spent on what a script would render. A skill is played on its contract — its nominal reading — never by reading its
code. In a conducted document, the skill does, the proc judges: a `WORK` step chains
scripts, an `INFER` step produces one judgment.

## The test of a document

A document that tells the agent to play a skill has a `WORK` step, or lives in the
view of one. An `INFER` step produces: one production, no skill call. A mounted
document serves: it gives no order. When a mounted document or an `INFER` brief
says "play this skill", move that order to a `WORK` step and leave the data behind.
A body that asks the agent to compute, parse or validate what a script would render is
misplaced: the operation goes to a skill, the judgment stays.

This test has to be mechanical. A gesture played under an `INFER` was never reported:
the agent obeyed the nearest and most precise instruction — the document
ordered the gesture and the block offered the tool — while the card that forbade it
had been served once, at boot, twenty thousand characters away. Two served texts that
contradict are settled by proximity, not rank; a rule that counts is held by the engine.

## Judging a placement

Usage is never declared by the agent. An operation is a fact the agent produced; a usage
is a causality between what was served and what was produced, and the agent is badly
placed to judge it — "the most used reading" was a judgment, not a measure.
Three signals come from the trace: **cited** — a proof names a rendering of the reading;
**taken up** — a phrase, a path or a verb of a served text reappears in a call or a
production; **ablation** — the same task played without the reading. A reading served on
thirty runs, never cited nor taken up, is a candidate to leave its channel: "live" and
"beside" become columns, not opinions.

## The author's three documents

`CONDUCTION`, this page, is the theory: why and when. `PP_CHEATSHEET` is the catalog:
every mechanism, its primitives and its detail — how the theory is applied.
`PP-DESIGN` is the door: it asks the agent to analyse the operator's ask and make the
instance evolve to answer it, with the mechanisms of the catalog. A conducted document
divides the same way: its body says what is expected of the agent while it plays; its
laws frame that expectation and add the policy; its `serve:` rows give the reference.

## A checklist for the author

1. Where does this work come from: direct, induced or background?
2. Does it need a skill? Then it needs a `WORK` step.
3. At what moment does the agent need this knowledge: before the ask, or after it?
4. What does it cost every turn, and every run?
5. What keeps it silent when nothing is due?
6. Is any of it scriptable? Then it is a skill's, and the agent judges its result.
7. What shows this reading was used: a proof that cites it, a call that takes it up?
