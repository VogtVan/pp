---
name: TURN
kind: proc
description: >-
  The witness base's turn: one exchange from the ask to its result, the two sockets
  around the WORK, and nothing a scenario does not write itself.
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
