---
name: MARKED
kind: proc
description: compare a module on the branch `alt` with the repository's.
serve: |
  @alt engine/x.py
  engine/x.py
  code: @alt engine/t.py[def alpha..def beta]
  @alt TURN.md
proc: |
  SERVE
  INFER
---

Say what the branch changes in the module, and what `alpha` does there.
