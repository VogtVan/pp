---
name: OWNED
kind: proc
description: review the branch `alt` -- every row reads it unless it says otherwise.
material: alt
serve: |
  engine/x.py
  @repo engine/x.py
proc: |
  SERVE
  CALL HEIR.md
  INFER
---

Say how the branch's module differs from the repository's.
