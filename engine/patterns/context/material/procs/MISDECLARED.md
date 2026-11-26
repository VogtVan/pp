---
name: MISDECLARED
kind: proc
description: a declaration that takes one of the engine's names -- it refuses.
materials: |
  repo: ../../alt
serve: |
  engine/x.py
proc: |
  SERVE
  INFER
---

This document cannot declare `repo`.
