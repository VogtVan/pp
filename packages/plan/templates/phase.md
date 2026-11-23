---
name: phase
description: a phase of a plan -- its ground, its choices and the batches it prepares
next: batch
sections: |
  Ground
  Expected
  Choices
  Items
  Delivery
statuses: |
  doing  Choices
  redo  Ground Expected Choices Items
shown: |
  Expected
  Choices
constraints.production: |
  PH5  a phase law MAY exist: it is written only when it applies to EVERY batch of the phase -- what does not apply to all descends to its batch; a decision goes to the body, one dated line (principal's word 2026-08-27)
  PH3  the proof is a RENDERING (bench, dry-run, grep, diff); a live RUN is the OPERATOR's gate alone.
  PH4  what a batch touches carries its DEPENDENTS -- spotted at the zoom-out, they enter the perimeter.
constraints.behavior: |
  PH1  a batch CLOSES IN THE TURN that opens it -- sized at the framing, neither trivial nor unclosable; an overflowing batch is a framing defect: said, reframed on its GO.
  PH2  breaking is allowed and the change arrives whole: the new form alone; the node that carries a whole component closes on its clean convergence.
  PH6  the phase's laws and readings are posed LAST at the framing -- after the zoom-out and the batches proposed, from what the framing read; a law written before is a guess.
---

# PHASE `{slug}` — plan `{plan}`

A phase is where one part of the plan comes together: one component, or the whole plan when the plan has one phase. Code, interfaces or tests may break inside it; the phase ends clean. Its batches do the work. The script `pp-plan` writes every section and every status.

## The framing, in order

The principal's « frame » on a phase gives it its birth: write its Ground. Its line in the plan's Items is not copied into it, so say in Ground what the phase works on.

1. **Ground** — read the ground whole before you split the work: the sources, the code the phase touches, then, in a last paragraph, what DEPENDS on that code. Everything a change here would break enters the phase. Date what you read and name its commit. *e.g. `memo/storage.py` (54 lines: `add`, `list`) at `a1b2c3d`; depends on it: `memo/cli.py` calls `list`.*
2. **Expected** — first what is true when the phase closes, each line with what shows it; then what stays outside. *e.g. `pytest tests/test_storage.py` green, 6 cases; the CLI stays as it is.*
3. **Choices** — each choice the phase makes: the choice, its reason, its strongest objection. Writing Choices makes the phase `doing`. *e.g. a linear scan, because a notebook is small; objection: slow past ten thousand notes.*
4. **Items** — the batches, one line each, `- <slug> -- <brief>`: the work, the exit one can see, how it is proved. Make each batch the largest piece one turn can open, do, prove and close: neither trivial nor too big to close. Say whether it builds something new or changes what stands. A change carries the alignment of everything that depends on it, as a batch of its own or as todos of the batch that breaks it. *e.g. `- search -- a word looked up in every note; exit: `memo search x` prints the matching notes; proof: the test named`*
5. **The laws and the readings**, last (below).

Then stop. Each batch gets its birth and its framing on the GO that names it.

## The laws and the readings of the phase

Write them last, from what the Ground has read; a law written before is a guess.

- Write a phase law only when every batch of the phase can break it. A law that holds for fewer goes down to its batch.
- A law says what must hold while the work is done, and how that is seen. It never says what the work is: Expected says that. A law carries no figure: a figure goes to Expected.
- Give each law its section: `constraints.production` for what you make, judged at every proof; `constraints.behavior` for how you work, never proven.
- The phase's readings (`serve`) are references every batch of the phase needs: specs, designs, contracts, maps. Never code.

## The work, on the GO

- « frame X/p/b » gives a prepared batch its birth by its Ground, and frames it in the same turn.
- A question, a challenge or a defect is answered, never coded.
- New work on what a closed batch established goes to that batch: rewrite its framing (a new todo, a new Expected) and it reopens (`redo`, its ancestors with it). Never create a twin.
- Keep the state as it is now: of the past, keep the reasons alone, one dated line in Choices. Delivery is the phase's journal: appended, it moves no status.
- The phase closes by the script when its last batch closes. Before that, the node that carries a whole component runs, once, the suite of that component and of the components that depend on it: the phase, by its last batch; or the batch itself when the plan has one batch per component. When the plan has one phase, its last batch runs the project's whole suite once. A red there is fixed before the closing.
