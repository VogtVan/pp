---
name: CHECKED
kind: proc
description: a line of its own, a line of another document, then the proof.
constraints.production: |
  FU1  each line says one fact
proc: |
  INFER
  CALL LEFT.md
  PROVE
---

Say one fact, let LEFT say another, then prove both.
