---
name: RESERVED
kind: proc
description: writes its implicit socket as a HOOK -- the build refuses it.
proc: |
  HOOK reserved.initialize
  INFER
---

Nothing here plays: the entry socket is never written.
