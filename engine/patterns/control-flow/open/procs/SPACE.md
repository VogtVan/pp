---
name: SPACE
kind: proc
description: a space -- every message replays its two steps, until the agent closes it.
constraints.production: |
  S1  every answer in the space names the topic it serves.
proc: |
  INFER
  WORK
---

Name the topic the message brings, then work on it.
