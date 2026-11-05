---
name: STAGE
kind: proc
description: a stage that leaves to one of two successors.
output: any
next: LEFT.md RIGHT.md
choose: |
  LEFT when the line is odd, RIGHT when it is even.
proc: |
  INFER
---

Say ONE line.
