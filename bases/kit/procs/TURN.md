---
name: TURN
kind: proc
description: >-
  One-exchange discipline, from the operator's message to restitution.
constraints.behavior: |
  T1  an approval names the step it approves; questions, challenges or defects are not approvals.
  T2  operator decisions are stated plainly: stakes, options, impact.
  T3  understand the ask before acting.
  T4  verify instead of taking for granted.
output: any
formats: |
  said  chat  the production opens on three lines -- `---`, the name of the document on the INSTRUCTION line, `---` -- then the production itself in the form the step names (free prose when `said` is the form named); after a CONTINUE that owes no production, nothing is said
proc: |
  HOOK turn.begin
  WORK
  HOOK turn.end
  PROVE
---

# TURN

The operator's message is the ask: serve its RESULT in this exchange. On-screen constraints are the whole brief; only the result leaves the step; proof stays with the tool.
