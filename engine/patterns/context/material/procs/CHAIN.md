---
name: CHAIN
kind: proc
description: a proc that declares two trees, reads one and calls a document that declares one of them again.
materials: |
  alt: ../../alt
  side: ../../other
serve: |
  @alt engine/x.py
proc: |
  SERVE
  CALL NEAR.md
  INFER
---

Say which tree each module came from.
