---
name: RUNNER
kind: proc
description: the root -- it calls ASK at every passage and offers the script as a gesture.
tools: |
  pp-alpha
proc: |
  CALL ASK.md
  HOOK runner.end
---

Answer the message.
