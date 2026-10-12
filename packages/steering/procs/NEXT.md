---
name: NEXT
kind: proc
description: The end of the answer -- the operator's next decisions, then the work threads.
output: next
formats: "next  stdin  the `steering-threads` reading copied unchanged -- the `initiative | note | progress | age | next action(s)` table, its `⏸` and `💤` lines, or its one line, with one liberty: a quoted note --, a blank line, then the CHOICES table (columns `#` and `your best choice(s)`, two rows at most); plain markdown only"
constraints.behavior: NX1  copy the initiatives table as it was rendered
proc: |
  INFER
provides: steering-threads
with: pp-steering status --due
payloads: steering-threads
---

# NEXT — the end of the answer

The front is the threads table, its `⏸` line and its `💤` line.
The choices are the two next key actions.
Write the front, a blank line, then the choices. Write nothing after the choices.

## The front

Copy the `steering-threads` reading as it stands: it holds either the threads
table with its `⏸` and `💤` lines, or one line. You never choose between them. You
may add one short note in quotes, at the end of a `next action(s)` cell or
after the age of a thread in the `💤` line: a missing approval, a material discrepancy.

## The choices

Offer the two next key actions you judge due for the operator's work, wherever
they come from: not necessarily two rows of the threads table. When one action
alone is due, offer one choice and say so. When none is due, write no choice row.
Each choice names its work with its full address. It says in one sentence what it
unlocks and where it comes from: the operator's word, a measured defect, the next
step of the undertaking it serves, or an order you set yourself, said as such.
Offer only decisions still owed to the operator.
