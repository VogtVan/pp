---
name: STAGE
kind: proc
description: one line and its proof, then a fork between two successors.
next: LEFT.md RIGHT.md
choose: |
  LEFT when the draft is @SHELF.state, RIGHT otherwise.
output: line
proc: |
  INFER
  PROVE
---

Say in one line how the draft stands.
