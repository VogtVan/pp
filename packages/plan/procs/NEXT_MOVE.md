---
name: NEXT_MOVE
kind: proc
description: >-
  The plan's next move: what each open plan asks for next, read where NEXT chooses when the package next is there -- described, never played.
mount: next.next.begin
provides: plan-next-move
with: pp-plan next-move
payloads: plan-next-move
---

# NEXT_MOVE — what the plans ask for next

After every `pp-plan` call that writes, the script computes the plan's NEXT MOVE — the deepest node that waits for something, and the GO it waits for — and pushes it: one line held per plan, the newest replacing the one before, cleared when the plan is done. These lines come here under `INFORMATION — plan-next-move`, in NEXT's block at the end of the answer. They are computed after the work of the exchange, so they say what the plans ask for NOW.

A line DESCRIBES what the plan asks for next; the GO it names is the PRINCIPAL's. It ENDS with the vector of the node it names — `(plan:<address>)`, at every depth — the address a steering step takes as its key when steering is there. No `plan-next-move` section means that no plan is open, or that every open plan is done.
