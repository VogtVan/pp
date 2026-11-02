---
name: NEXT_MOVE
kind: proc
description: >-
  The plan's next move: what each open plan asks for next, read where NEXT chooses when steering is there -- described, never played.
mount: steering.next.begin
provides: plan-next-move
with: pp-plan next-move
payloads: plan-next-move
---

# NEXT_MOVE — what the plans ask for next

After every mutating `pp-plan` call the script computes the plan's NEXT MOVE — the deepest node that awaits something, and the GO it awaits — and pushes it to the bus: one held line per plan, the newest replacing the previous, cleared when the plan is done. Those lines arrive here under `INFORMATION — plan-next-move`, with the steering pass: computed after the work of the exchange, so they say what the plans ask for NOW.

A line DESCRIBES what the plan asks for next; the GO it names is the OPERATOR's. It ENDS with the vector of the node it names — `(plan-lot:<plan>/<phase>/<batch>)`, `(plan-phase:…)` or `(plan:…)` — the address a steering step takes as its key. No `plan-next-move` section means no plan is open, or all open plans are done.
