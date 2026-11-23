---
name: CYCLE
kind: proc
output: any
description: the iterated door -- a lap per element the witness provides, each production fed to the sink
cycle: cyclewit-items
sink: pp-cyclewit
constraints.production: |
  CY1  the lap's line names its element and nothing else.
proc: |
  INFER
---

# CYCLE

One lap per element under `cyclewit-items`: say ONE line that names the element you were
served, in ten words at most. The sink marks it done; the next lap serves the next one.
