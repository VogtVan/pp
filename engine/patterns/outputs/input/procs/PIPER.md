---
name: PIPER
kind: proc
description: a proven JSON value handed to a called document.
output: json
constraints.production: |
  Q1  the payload is one json value.
proc: |
  INFER
  PROVE
  CALL SHIP.md
---

Make the payload.
