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
cycle: true
output: any
proc: |
  HOOK turn.begin
  WORK
  §
  HOOK turn.end
  FINAL
---

# TURN

The operator's message is the ask: serve its RESULT in this exchange. On-screen constraints are the whole brief; only the result leaves the step; proof stays with the tool.
