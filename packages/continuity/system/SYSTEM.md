---
name: SYSTEM
kind: doc
description: >-
  Continuity's word in the standing orders -- what an operation is, when you record one,
  and what pp gives back from the record.
---

## Continuity — the operations

Continuity keeps a record of the work done in this workspace, so that a later run starts
from it. You write to it through the skill `pp-continuity`, whenever a fact is worth
keeping, at any moment of an exchange, without waiting for a procedure to ask.

**Words.**

- *Operation*: one fact a later run will need -- work delivered, a regression found, a
  decision taken on the work, a measure with its figure. It stands alone for a reader who
  was absent: what, where, and why it matters. It holds on one line; the skill dates it,
  and refuses it over `continuity_entry_budget` characters.

**What you do.**

1. When such a fact is established, record it with `register` in the same exchange, one
   fact per call.
2. A single gesture, a reply, or a fact already recorded is not an operation.
3. An entry is never edited: when one is wrong, record a new entry that corrects it and
   names the entry it corrects.
4. When the work needs facts older than the recall, find them by their words:
   `./pp records search '"<exact words>"' --records operations`, narrowed with `--since` and
   `--until` (a date, or a span such as `7d`). Words between double quotes match that exact
   text; words without quotes must each appear somewhere in the entry. To read a whole
   period, use `recall last <days>`: it prints one page, the 40 latest operations, and when
   its last line says older ones are left, type the `--skip` call that line gives.

**What pp does.** At the start of every run, pp serves the operations of the last
`continuity_recall_days` days as `continuity-recall`. On the chosen day of the week, it
asks you for a short summary of the week, which HISTORY records.
