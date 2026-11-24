---
name: plan
description: a plan -- its context, its ground, its choices and the phases it prepares
next: phase
sections: |
  Context
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
  TPL1  a plan document is a BLUEPRINT, never a history manual: every framing and every reframing writes the state TRUE at the moment it speaks, and of the history it keeps the reasons and the justifications alone, one dated line
---

# PLAN `{slug}`

A plan carries one undertaking of the principal, from its first word to its delivery. On the product's templates it has three levels: the plan, its phases and their batches. A batch is the only unit of work. A phase is where one part of the plan comes together. The script `pp-plan` writes every section and every status: never edit a plan document by hand. The progress is read from the documents (`pp-plan status`), never kept by hand.

## Before the birth

Let the undertaking take shape in the exchange first. When it is clear enough, propose the plan to the principal. Write nothing before their GO. On that GO, write the Context: it gives the plan its birth (`section <slug> Context`).

## The framing, in order

1. **Context** — what the undertaking is and why, in the principal's terms. *e.g. a notebook kept on the command line, because the notes are scattered.*
2. **Ground** — what stands before the work, in titled parts, one whole component per bullet, and what depends on each one. On an existing project, read it before anything else: the phases come from it. *e.g. `memo/` holds `storage.py` and `cli.py`; `cli.py` depends on `storage.list`.*
3. **Expected** — first what is true when the plan closes, each line with what shows it; then what stays outside the plan. *e.g. `memo add` then `memo list` prints the note back, the bench scenario named; a web front stays outside.*
4. **Choices** — each choice the plan makes: the choice, its reason, and the strongest objection to it. Writing Choices makes the plan `doing`. *e.g. JSON lines, because one file needs no dependency; objection: a search reads every line.*
5. **Items** — the phases, one line each, `- <slug> -- <brief>`: what the phase does, how it ends, how that is proved. A line prepares a phase and gives no document. The principal amends the lines until their « frame » names one. *e.g. `- core -- the store and its two commands; exit: the store's bench green`*
6. **The laws and the readings**, last (below).

Lay the plan out one of two ways: one phase per component, each with its batches, for work that lasts; or one phase with one batch per component, for fixes or a short rework. The node that carries a whole component is born when it is first needed, and reopened for every later fix: never create a twin of it.

## The laws and the readings of the plan

Write them last, from what the framing has read; a law written before is a guess.

- Write a plan law only when every batch under the plan can break it. A law that holds for fewer goes down to its phase or its batch.
- A law says what must hold while the work is done, and how that is seen. It never says what the work is: Expected says that. A law carries no figure: a figure the work aims at goes to Expected.
- Give each law its section: `constraints.production` for what you make, judged at every proof; `constraints.behavior` for how you work, shown at every block and never proven.
- The plan's readings (`serve`) are references: specs, designs, contracts, maps. Never code: the code comes with the batch that touches it.

## Keep the document true

Write the state as it is when you write it. Of the past, keep the reasons alone, one dated line in Choices. What landed is said in Delivery, the plan's journal: it is appended and moves no status.

The plan closes by the script when its last phase closes: no word closes it. Do not let it close before the project's whole test suite is green: its last batch runs that suite once.
