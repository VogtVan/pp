---
name: SYSTEM.COMMON
kind: doc
description: >-
  Steering's word in the standing orders -- what a step and a label are, what you do with
  them in every exchange, and what pp does with them.
---

## Steering — the steps of work

Steering keeps the work owed in this workspace as STEPS, through the skill `pp-steering`.
Use it as you use your shell: whenever the work calls for it, at any moment of an exchange,
without waiting for a procedure to ask.

**Words.**

- *Step*: one unit of work owed, from one exchange of real work up to a few exchanges: a
  defect to fix, an idea to explore, a piece of work sketched, a question to settle. A single gesture -- merging a pull request, running
  an upgrade, one command, one reply -- is never a step. A step has a name, a date, a
  WORK text and a COMMENT.
- *Label*: a name and a short note that groups steps -- work too large for one step,
  broken into steps of that size; steps to treat together; or a line of thought that
  produces steps. A step may carry several labels. A label can be dissolved; its steps
  stay.

**What you do.**

1. Work of a step's size that you undertake is carried by an open step. Before you start
   such work and no open step carries it, add one. Work larger than a step gets a label
   and its steps.
2. Whatever of a step's size you notice that is owed and not done now -- a defect, an
   idea, a follow-up -- becomes a step at once, unasked. The test: it would be lost if
   the exchange ended now.
3. When the work of a step is done, close it with `done` in the same exchange. When it no
   longer has to be done, `drop` it with the reason.
4. A step's name and work are fixed when it is added: write the work so that it is
   understood alone, months later -- what to do, where and why. What happens to the step
   afterwards goes into its comment. When the work itself changes, drop the step and add
   a new one.
5. Take step ids from the ledger served at the start of the run and from the output of
   your calls. When you speak to the principal, name a step by its name, and say every
   change in one line, in the principal's language.
6. A key (`<family>:<id>`) ties a step to work another package tracks. Never change it.
7. At any moment, `review` lists the active steps, the least recently touched first:
   close what is done, drop what no longer has to be done, comment what moved.

**What pp does.** At the start of every run, pp archives the steps left untouched too long
or beyond the active maximum, then serves the active steps still to do, one line each, as
`steering-ledger`. At the end of every exchange, NEXT asks you for the principal's two best
next choices. The whole view -- labels, comments, archived steps -- opens with
`-open STEERING`, where the principal has you reorganise steps and recall archived ones.
