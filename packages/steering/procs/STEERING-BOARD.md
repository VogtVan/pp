---
name: STEERING-BOARD
kind: proc
description: >-
  The welcome of the steering space -- played once when the space opens: the old steps archived, then the board of the steps said to the principal as tables.
attach: steering.steering.initialize
exec: sweep
provides: steering-board
with: pp-steering board
payloads: steering-board
formats: |
  steering-board  words  each part of the board pp-steering rendered, as one titled markdown table -- the counts by status, the last 7 days, the durations, the least touched steps, the labels with their freshest steps; nothing the board does not say
output: steering-board
proc: |
  INFER
---

# STEERING-BOARD — the welcome of the steering space

`steering-board` is what `pp-steering board` says of the steps, read from their fields:
how many steps there are by status, active and archived; what happened in the last 7 days;
how long steps take from birth to closure and how old the steps still to do are; the five
least recently touched; each label with its counts and its most recently touched steps;
the steps without a label.

Say it to the principal as tables, one per part, each with its title.
