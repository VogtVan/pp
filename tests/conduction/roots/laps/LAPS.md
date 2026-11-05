---
name: LAPS
kind: proc
output: any
description: the described door -- three laps on three names, one line each, proven at the exit by its own PROVE
field: |
  The three names alpha, beta, gamma -- one lap each, in that order.
constraints.production: |
  LP1  the lap's line names its element and nothing else.
proc: |
  INFER
  PROVE
---

# LAPS

One lap per element under `field`: say ONE line that names the element you were served
and what you make of it, in ten words at most.
