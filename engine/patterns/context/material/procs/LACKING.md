---
name: LACKING
kind: proc
description: rows whose tree cannot answer -- each is said missing in the block, nothing is read from another tree.
materials: |
  alt: ../../alt
  gone: ../../nowhere/at/all
serve: |
  @nope engine/x.py
  @gone engine/x.py
  @alt engine/absent.py
proc: |
  SERVE
  INFER
---

Say which rows were not served, and why.
