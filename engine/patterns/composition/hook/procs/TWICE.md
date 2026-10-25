---
name: TWICE
kind: proc
description: the same socket written twice -- the build refuses it.
proc: |
  HOOK twice.open
  INFER
  HOOK twice.open
---

Nothing here plays: a socket names one place in the flow.
