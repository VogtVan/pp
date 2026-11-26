---
name: BEGIN
kind: proc
output: any
description: the contributor -- a producer at the turn's beginning, its law proven at the turn's checkpoint
attach: turn.begin
constraints.production: |
  BG1  the opening line says « begin » and the hour, nothing else.
proc: |
  INFER
---

# BEGIN

Before the work: say ONE line that opens on « begin » and gives the hour the block says.
