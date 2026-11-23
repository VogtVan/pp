---
name: OWNED
kind: proc
description: review the branch `alt` -- every row reads it unless it says otherwise.
material: alt
materials: |
  alt: ../../alt
  other: ../../other
serve: |
  engine/x.py
  @other engine/x.py
proc: |
  SERVE
  CALL HEIR.md
  INFER
---

Say how the module differs between the two trees.
