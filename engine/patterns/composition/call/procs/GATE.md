---
name: GATE
kind: proc
description: open the review, then decide on its verdict.
constraints.behavior: |
  G1  you decide on the verdict alone; you never review the draft yourself.
proc: |
  CALL REVIEW.md
  INFER
---

Say what the verdict decides.
