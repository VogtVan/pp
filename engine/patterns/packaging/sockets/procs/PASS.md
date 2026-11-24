---
name: PASS
kind: proc
description: the package's pass -- after the turn's work, it opens its own socket
attach: turn.end
proc: |
  HOOK pass.begin
  WORK
---

PASS: the pass.
