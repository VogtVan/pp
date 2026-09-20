---
name: PP-RULES
kind: proc
description: >-
  Rules find their words and scope: distinguish body from constraint, arm rules against model biases, and place each in member, proc frame, overlay, kit, or dead. An instance door, opened on the operator's GO.
output: free
constraints.production: |
  PR1  one rule, one holder.
  PR2  what the kit already holds is consumed as it is.
  PR3  a dead rule is said dead, with the mechanism that replaced it.
  PR4  the member carries no work laws -- short, load-bearing first.
  PR5  a proposed constraint is imperative, meta and provable -- the descriptive stays in the body.
  PR7  a proposal is grounded in what was observed, and that alone.
constraints.behavior: |
  PR6  a rule is proposed -- it is placed on the operator's GO alone.
serve: |
  MEMBER.md
  PP_CHEATSHEET.md
proc: |
  SERVE
  WORK
---
# PP-RULES — rules find their words and their scope

The member was served above; every code already in force is the script's to say — `pp-authoring section constrain` inventories them and derives the free ones, a collision impossible by construction. Express what the operator needs as constraints WORTH their per-block cost, and place each where it belongs. Deliver an inventory table (rule · statement · scope · holder) and proposed constraints as ready lines, each naming its holder.

## What a constraint is

A constraint is IMPERATIVE and META: it governs every answer while its frame lives, and proof must cover it answer after answer. The BODY is descriptive — brief, material, steps. Test before writing a line:

    must this hold -- and be proven -- of EVERY answer while the frame lives?
        -> a constraint.
    does it describe the work, the material, the sequence?
        -> the body.

The same intent, both ways:

    body-worded (fades):    Please make sure to be honest about failures.
    constraint (holds):     R1  a failing check is reported before any fix is attempted.

Write a constraint POSITIVE, as one imperative line. It lives in ONE of two sections: `constraints.production` governs what the agent MAKES and is proven at checkpoints; `constraints.behavior` governs what it does, says or reads, is served every block and never proven. A production law names its rendering coverage: WHOLE (e.g. grep/count over all bound material), SAMPLE (the sites it names), or TRACE FACT (a run event). If proof cannot name coverage, it belongs in behavior or the body.

## The rule against the bias

A constraint earns its cost when it leans AGAINST a strong model pull. Proven set:

    the pull                    the rule that held
    ------------------------    --------------------------------------------
    flattering the material     verdicts are yours alone -- the draft's own
                                claims prove nothing.
    over-helpfulness            you judge the draft; you never rewrite it.
    inventing what fits         a proposal is grounded in what was observed,
                                never invented.
    scope creep                 you act within your own member alone.
    silent accommodation        what does not conform is said before the work.
    running ahead on an ask     new material is framed first, then played on
                                the GO that NAMES its lot.
    reading a GO wide           a GO reads at its NARROWEST: what it names,
                                nothing beyond.
    pushing through a surprise  the STOP when the architecture surprises:
                                said, reframed on its GO.

When the operator names recurring drift, oppose it in ONE imperative line, then place it below.

## Where a rule lives

OUTPUT softens per-block cost, never erases it: within one output a law's text appears once (later scopes use codes; new scopes print only their delta), and `verbatim_constraints: false` says a law's text once per RUN (first emission), codes after. Still judge a law's WORTH as if repeated: fusion thins the bill, not the debt.

Full scale, costliest first — MEMBER › plan › phase › lot › proc › overlay › kit › dead; plan rungs come with the plan package:

- **MEMBER** — EVERY block, proven every turn: identity and house invariants only; short, load-bearing first, never work laws.
- **a plan** — every mount of its nodes, phases and lots below; write only what EVERY lot below holds. Thesis, decision or provenance belongs in the body, one dated line.
- **a phase** — every mount of its lots; same test. What only one lot holds descends to that lot.
- **a lot** — its own mount only: its laws are the PROOF MODE, what the checkpoint judges of THIS work; a lot without laws is a framing defect.
- **a proc's `constraints.production` / `constraints.behavior`** — ITS frame only: rules of that work, free elsewhere; production proven, behavior served.
- **an overlay** — adjust a bundled proc's set at home: add yours, remove one.
- **already the kit's** — consume, never restate: member perimeter, said-before-work rule, no narration, recall, turn discipline, proof itself.
- **dead** — superseded by a mechanism; say so and name it.

A rule YOU write never blocks your build. A law defect in a document of this instance — a code declared twice, a line out of form `CODE  what it demands`, an `attach:` no proc hooks — comes back as `pp: WARNING -- …` naming the document, and `-build` passes; a malformed line is simply not in force, the rest of the document is. The same defect in a PACKAGE's document refuses by name: the product answers for itself, the author is told. The one exception is the bare `constraints:` key, which refuses on both sides — it is the migration gate, not a law defect.

Workspace shape matters: in a PROJECT, most rules fit the member or one working proc. In a SOLUTION, a sub-project rule belongs to THAT sub-project's proc or overlay; the member keeps only the map and cross-cutting invariants. Scoping `atelier` (solution, plan package installed):

    rule                                 scope      holder
    -----------------------------------  ---------  --------------------------
    the chat speaks French               member     MEMBER.md (M3)
    a test migrates red, never dropped   plan       plans/atelier/PLAN.md (KAT1)
    the parser lot proves by its bench   lot        plans/atelier/2-engine/3-parser/BATCH.md (KAP1)
    engine stays dependency-free         proc       procs/ENGINE-WORK.md
    an API change updates server/README  overlay    procs/TURN.md (+S1)
    be nice                              dead       character: already carries it
    re-read everything before answering  dead       the serve proves each reading

## The step toward proc design

When a rule cluster outgrows the member — a workflow with laws of its own — a proc is emerging: this door decides WHERE rules live; PP-DESIGN shapes HOW the proc is written. Hand over and say so.
