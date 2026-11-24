---
name: LOBBY
kind: proc
description: speak, call the porch, speak again -- one law for the whole way, no offer of its own.
constraints.behavior: |
  L1  the lobby speaks for the porch too.
proc: |
  INFER
  CALL PORCH.md
  INFER
---

Say who waits in the lobby.
