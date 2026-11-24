---
name: WELCOME
kind: proc
output: said
description: the welcome of the space ROOM -- played once when the principal opens it, fused with ROOM's own step
attach: room.initialize
constraints.behavior: |
  W1  greet the principal by the name of the room
proc: |
  INFER
---

# WELCOME

Say ONE line: « welcome to the room ».
