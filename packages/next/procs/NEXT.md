---
name: NEXT
kind: proc
description: The end of the answer -- the principal's two best next choices.
attach: turn.end
output: choices
formats: "choices  stdin  the CHOICES table alone -- columns `#` and `your best choice(s)`, two rows at most, each naming its work and what it unlocks; plain markdown only; use icons to illustrate each choice."
proc: |
  HOOK next.begin
  INFER
---

# NEXT — the end of the answer

Offer the two next key actions you judge due for the principal's work. Take them from the
exchange, from the readings this block carries, and from the steps of work when the run
keeps any. When one action alone is due, offer one choice. When none is due, write the
table with no row.

Each choice present its work by its full name and description. It says in one sentence what it unlocks and where it comes from: the principal's word,
a measured defect, the next step of the work it serves, or an order you set yourself, said
as such. Offer only decisions still owed to the principal.
