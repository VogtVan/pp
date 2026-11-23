---
name: NEAR
kind: proc
description: a called document that declares `alt` again -- its own declaration wins; `side` comes from its caller.
materials: |
  alt: ../../other
serve: |
  @alt engine/x.py
  @side engine/z.py
proc: |
  SERVE
  INFER
---

Say what the two modules hold.
