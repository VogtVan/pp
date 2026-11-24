---
name: STAGE
kind: proc
output: any
description: the stage -- one line, then a successor chosen among two
next: LEFT.md RIGHT.md
choose: |
  LEFT when the number the message gives is odd, RIGHT when it is even.
proc: |
  INFER
---

# STAGE

Say ONE line: the number the message gives and whether it is odd or even.
