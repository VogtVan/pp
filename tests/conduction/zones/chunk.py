"""Scenario `zones/chunk` -- the zone `chunk` of the conduction (an output cut under a cap and served in pieces), played under the
modelled LLM by the fewest roots that cross it, on every channel the zone exists on (`semantics.ZONES`), and
read on the sheet of that play: the zone crossed on each of those channels, every exchange played at cost 0
without a hole, parked unless its root expects otherwise, no `rouge-conduction` and no `trou` on its lines
(tests/README.md, rule 11; `zone_case` in the support).
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")
ZONE = "chunk"
ROOTS = ('long-read',)


def scenario(bench) -> int:
    return C.zone_case(bench, ZONE, ROOTS)
