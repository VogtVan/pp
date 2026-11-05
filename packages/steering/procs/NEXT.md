---
name: NEXT
kind: proc
description: The end of the answer -- the principal's two best next choices.
attach: turn.end
output: choices
formats: "choices  stdin  the CHOICES table alone -- columns `#` and `your best choice(s)`, two rows at most, each naming its work and what it unlocks; plain markdown only"
proc: |
  HOOK next.begin
  INFER
---

# NEXT — the end of the answer

Offer the two next key actions you judge due for the principal's work. Take them from the
steps of the ledger, from the readings this block carries, and from the exchange -- not
necessarily from the steps. When one action alone is due, offer one choice. When none is
due, write the table with no row.

Each choice names its work with its full address -- a step by its name, a plan node by its
path. It says in one sentence what it unlocks and where it comes from: the principal's word,
a measured defect, the next step of the work it serves, or an order you set yourself, said
as such. Offer only decisions still owed to the principal.
