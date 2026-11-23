---
name: LEDGER
kind: proc
description: a space whose last step calls REPORT -- every message replays it from its first step.
output: any
proc: |
  INFER
  CALL REPORT.md
---

Read what the message asks of the ledger; REPORT says it.
