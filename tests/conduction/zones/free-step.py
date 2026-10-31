"""Scenario `zones/free-step` -- the zone `free-step` of the conduction (an output that ends on a free step (`WORK`, `INFER => words`) and waits the agent's words), played under the
modelled LLM by the fewest roots that cross it, on every channel the zone exists on (`semantics.ZONES`), and
read on the sheet of that play: the zone crossed on each of those channels, every exchange played at cost 0
without a hole, parked unless its root expects otherwise, no `rouge-conduction` and no `trou` on its lines
(tests/README.md, rule 11; `zone_case` in the support).
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")
ZONE = "free-step"
ROOTS = ('read-lines', 'stray')


def scenario(bench) -> int:
    return C.zone_case(bench, ZONE, ROOTS)
