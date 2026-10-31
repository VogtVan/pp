---
name: HALL
kind: proc
description: open the hall, with the notes it names at its own socket.
mounts:
  hall.open: NOTES.md
proc: |
  HOOK hall.open
  INFER
---

Say what the hall is ready for.
