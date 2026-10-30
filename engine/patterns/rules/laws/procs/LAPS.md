---
name: LAPS
kind: proc
description: a door that turns on the elements its prose describes, one line each.
output: any
field: |
  The three names alpha, beta, gamma -- one lap each, in that order.
constraints.production: |
  LP1  the lap's line names its element and nothing else.
proc: |
  INFER
  PROVE
---

One lap per element: say ONE line about it.
