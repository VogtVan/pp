---
name: PLANS
kind: proc
description: >-
  The plans space -- open it (`-open PLANS`) to see the open plans at a glance, the work under way in them and the steps tied to them, then frame, mount and deliver from there; `-close` gives the turn back.
serve: |
  PLAN_CHEATSHEET.md
tools: |
  pp-plan
proc: |
  SERVE
  WORK
  PROVE
constraints.behavior: |
  PS1  a view you build yourself names the `pp-plan status` calls it comes from and keeps the address of each plan, phase and batch
  PS2  work on a plan, a phase or a batch only once it is mounted, as at the turn
  PS3  close the space only on the principal's word
---

# PLANS — the plans, at a glance

This space is where the principal looks at the plans as a whole and works on them.

**What the principal sees when it opens.** The board, said as tables: the open plans with
their progress and their next move, the phases and batches under way (`doing`, `redo`,
`blocked`), the steps of this run tied to them, and the closed plans in one line.

**What the principal can ask for next.** Any view of the plans, with `pp-plan status`:

- the open plans, or all of them with `--all`;
- the work under way in every open plan: `--engaged`;
- one plan whole, its phases and its batches, the todos counted: `status <slug>`;
- the same as data: `--json`.

**How the work goes here.** Exactly as at the turn: a plan, a phase or a batch is mounted
before anything is written about it, framed on the principal's « frame », implemented on the
GO that names it. A deeper node mounted later in the same message extends the chain: what is
already in view stays, the deeper documents are added. The plan's reference (the cheat sheet)
arrives with the opening of the space, or with the first mount of the run. The steps tied to a plan are the ones the run already holds -- the steps
served at the start, the tables of the steering space when it was opened, the steps added
since; use them, and change them with `pp-steering` when it is offered.

**How it ends.** Each message worked here ends on the proof of the laws in force. When the
principal is done, `-close` gives the turn back.
