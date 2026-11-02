"""Scenario `zones/value-judged` -- the zone `value-judged` of the conduction (an output opened by the answer to a value handed (a proof, a field, a choice)), played under the
modelled LLM by the fewest roots that cross it, on every channel the zone exists on (`semantics.ZONES`), and
read on the sheet of that play: the zone crossed on each of those channels, every exchange played at cost 0
without a hole, parked unless its root expects otherwise, no `rouge-conduction` and no `trou` on its lines
(tests/README.md, rule 11; `zone_case` in the support).
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")
ZONE = "value-judged"
ROOTS = ('laps',)


def scenario(bench) -> int:
    return C.zone_case(bench, ZONE, ROOTS)
