---
name: PATHS
kind: proc
description: one path read twice -- from the repository, and from the machine's copy.
serve: |
  code: engine/x.py .sys/engine/x.py
proc: |
  SERVE
  INFER
---

Say where each copy came from.
