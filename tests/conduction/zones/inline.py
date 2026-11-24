"""Scenario `zones/inline` -- the zone `inline` of the conduction (a replay that asks the agent a value -- a block it has read, its deviation said -- answered in its tool result under the principal's conduction), played under the
modelled LLM by the fewest roots that cross it, and read on the sheet of that play: the zone crossed, every
exchange played at cost 0
without a hole, parked unless its root expects otherwise, no `rouge-conduction` and no `trou` on its lines
(tests/README.md, rule 11; `zone_case` in the support).
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")
ZONE = "inline"
ROOTS = ('stubborn',)


def scenario(bench) -> int:
    return C.zone_case(bench, ZONE, ROOTS)
