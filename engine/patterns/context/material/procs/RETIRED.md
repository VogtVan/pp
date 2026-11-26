---
name: RETIRED
kind: proc
description: a row marked `@repo` -- no tree is called `repo` or `work`, so it refuses.
serve: |
  @repo engine/x.py
proc: |
  SERVE
  INFER
---

This row names a tree that does not exist.
