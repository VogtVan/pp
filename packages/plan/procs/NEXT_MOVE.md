---
name: NEXT_MOVE
kind: proc
description: >-
  The plan's next move: what each open plan asks for next arrives with this block, before the steering surface that carries it -- described, carried, never played.
mount: turn.end
order: |
  turn.end before steering
provides: plan-next-move
with: pp-plan next-move
payloads: plan-next-move
---

# NEXT_MOVE — what the plans ask for next

After every mutating `pp-plan` call the script computes the plan's NEXT MOVE — the deepest node that awaits something, and the GO it awaits — and pushes it to the bus: one held line per plan, the newest replacing the previous, cleared when the plan is done. Those lines arrive here under `INFORMATION — plan-next-move`.

A line DESCRIBES what the plan asks for next; the GO it names is the OPERATOR's. It is CARRIED into the steering surface at the thread already holding that plan's work — never its own row, never a line beside the threads, and NEVER PLAYED in the turn. The line ENDS with the vector of the node it names — `(plan-lot:<plan>/<phase>/<batch>)`, `(plan-phase:…)` or `(plan:…)` — and that vector is the KEY of the thread's step: the first time, `pp-steering attach <thread> --key <vector> <text>`; a later line on the same node finds the step that carries it — `done` when the node delivered, `renext` when it is the next move — and never adds one. Word the move in prose, with node slugs carrying all ancestors. No `plan-next-move` section means no plan is open, or all open plans are done.
