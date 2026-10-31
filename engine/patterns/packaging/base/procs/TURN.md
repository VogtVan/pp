---
name: TURN
kind: proc
description: >-
  The base's turn: one exchange from the ask to its result, with a socket before and after the work.
output: any
proc: |
  HOOK turn.begin
  WORK
  §
  HOOK turn.end
  PROVE
---

# TURN

The message is the ask: serve its result in this exchange.
