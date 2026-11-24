"""Scenario `team-member-relaunch-vector-parked` -- 1 case(s): the PARKED run of a member relaunched with its vectors,
on the house of `_relaunch.py` (cut from `team-member-relaunch-vector`):
- (c) the parked run relaunched (s.1600): `agent run --run <key>` with the node and the member's vector, as the tick
  passes them, launches -- rc 0, the run's flow says no `refused`; the relaunch's first prompt carries the law TM5
  the member's vector mounts, asked at its proof
"""
from __future__ import annotations

import re

from tests.harness import support

L = support(__file__, "relaunch")
NODE, MEMBER = L.NODE, L.MEMBER


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    r = L.Relaunched(bench)
    h, key, flow, relaunch = r.h, r.key, r.flow, r.relaunch

    # --- (c) the parked run relaunched -- s.1600 -------------------------------------------------------------
    seen = len(h.prompts_of("mi"))
    again = relaunch(NODE, MEMBER)
    refused = [one.get("detail") for one in flow() if one.get("kind") == "refused"]
    first = (h.prompts_of("mi")[seen:] or [""])[0]
    asks = re.search(r"^INFER proof \[[^\]]*\bTM5\b", first, re.M)
    if r.settled and again.returncode == 0 and not refused and asks:
        held("(c) the parked run relaunched", f"run {key} parked, `agent run --run` with {NODE} and {MEMBER}: rc 0, "
             "the vectors mounted on the exchange the message opens, TM5 asked at the first prompt's proof (s.1600)")
    else:
        failures.append(f"  ✗ (c) the parked run          rc={again.returncode} refused={refused} "
                        f"TM5 asked={bool(asks)} {again.stderr.strip()[-300:]!r}")
    return 0
