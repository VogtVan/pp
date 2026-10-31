---
name: SAME
kind: proc
description: one module the same in two trees, one module that differs.
serve: |
  engine/same.py
  @alt engine/same.py
  engine/x.py
  @alt engine/x.py
proc: |
  SERVE
  INFER
---

Say which module the branch changes.
