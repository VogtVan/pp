---
name: STEERING
kind: proc
description: >-
  The steering space -- open it (`-open STEERING`) to see the archived steps, have the agent reorganise steps and labels, review them, or recall archived ones; `-close` gives the turn back.
exec: sweep
provides: steering-archived
with: pp-steering list --archived
payloads: steering-archived
tools: |
  pp-steering
proc: |
  WORK
constraints.behavior: |
  ST1  drop a step only when its work no longer has to be done, and give the reason
  ST2  recall an archived step only when its work is due again
  ST3  say every change in one line, the step by its name
  ST4  never dissolve a label the principal named without the principal's word
---

# STEERING — the steps, all of them

The active steps still to do are the ones the ledger listed at the start of the run;
`steering-archived` lists the steps archived since -- left untouched too long, or beyond the
active maximum -- with their status.

Here the principal has you work on the steps as a whole: group them with labels (`label`,
`note`, `order`, `dissolve`), go through them with `review` and close what is done or no
longer due (`done`, `drop`), bring an archived step back with `recall` when its work is due
again. Do what the principal asks, then `-close`.
