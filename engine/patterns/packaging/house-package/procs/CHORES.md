---
name: CHORES
kind: proc
description: offers the house's list of chores -- every chore goes through its script.
tools: |
  pp-chores
proc: |
  WORK
---

Add each chore of the message to the house's list with `pp-chores add <chore>`, one call per
chore; read the list back with `pp-chores list`.
