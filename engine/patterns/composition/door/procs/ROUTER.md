---
name: ROUTER
kind: proc
description: speak, call the inner step, speak again -- offering DOOR all along.
constraints.behavior: |
  O1  the router speaks for the whole route.
tools: |
  DOOR
proc: |
  INFER
  CALL RINNER.md
  INFER
---

Say where the route goes.
