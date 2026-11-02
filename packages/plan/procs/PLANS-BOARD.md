---
name: PLANS-BOARD
kind: proc
description: >-
  The welcome of the plans space -- played once when the space opens: the open plans and the work under way in them said to the principal as tables, with the steps the run already holds that are tied to them.
attach: plan.plans.initialize
provides: plan-board
with: pp-plan status --all --engaged --json
payloads: plan-board
formats: |
  plan-board  words  the board as titled markdown tables -- the open plans (plan, status, progress, next move), the phases and batches under way (doing, redo, blocked), the steps of this run tied to them by their key when the run holds any, the closed plans in one line; nothing the board and those steps do not say
output: plan-board
proc: |
  INFER
---

# PLANS-BOARD — the welcome of the plans space

`plan-board` is what `pp-plan status --all --engaged --json` says of the plans, read from
their documents: one object per plan, and under each open plan one object per phase or batch
under way. Each object gives its `address`, its `kind`, its `status`, its progress
(`children`: done, open and prepared; `todos` for a batch) and, for an open plan, its `next`
move. A plan whose `status` is `done` is closed.

The steps tied to the plans are already in this run, if any: the steps served at the start
(`steering-ledger`), the tables of the steering space when it was opened, archived steps
included, and the steps added since. A step belongs to a plan, a phase or a batch when its
key names it: `plan:<slug>`, `plan-phase:<slug>/<phase>`, `plan-lot:<slug>/<phase>/<batch>`.
Use the steps you hold; call nothing to find more. When you hold none, leave their table out.

Say the board to the principal as tables, one per part, each with its title.
