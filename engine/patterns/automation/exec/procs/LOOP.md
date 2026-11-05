---
name: LOOP
kind: proc
description: a floor that opens its own point at every passage -- its own exec never plays.
exec: pp-stamp stamp floor
proc: |
  HOOK loop.open
  WORK
---

Serve the message.
