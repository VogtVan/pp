"""Scenario `launcher/hybrid` -- 2 case(s) (plan moteur-0.2.0, phase le-banc-de-conduction, batch
la-campagne-au-banc, 2026-10-27): the six patterns of the engine played under the modelled LLM on the
RELAYED channel, `conduction: hybrid` -- the output whose closing asks a value comes back in the
model's tool result:
- six exchanges on a throwaway house, every one parked at cost 0, no hole, no refusal; the coverage
  written; the agent's `conduction` setting put back to `strict` after the play
- the zones each root crosses are in the table, and the channel's own: `inline` on the roots whose
  door asks a value at every lap (LAPS, CYCLE)
"""
from __future__ import annotations

from tests.harness import support

C = support(__file__, "conduction")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    done, coverage, folder, house = C.played(bench, *C.PATTERNS, "--channel", C.RELAYED, "--conduction", C.HYBRID)
    found = C.exchanges_of(coverage)
    names = [f"{root}-relayed-hybrid" for root in C.ROOTS]
    setting = C.setting_of(house, "agents/pat", "conduction")
    if done.returncode == 0 and set(found) == set(names) and C.all_parked(coverage) and setting == C.STRICT:
        held("six exchanges relayed hybrid, all parked", f"rc 0, {len(found)} exchanges at cost 0, no hole, no "
             f"refusal; {sum(one['launches'] for one in found.values())} launches, "
             f"{round(sum(one['seconds'] for one in found.values()), 1)} s; the agent's conduction back to strict")
    else:
        failures.append(f"  ✗ relayed hybrid             rc={done.returncode} {sorted(found)} setting={setting!r} "
                        f"{done.stderr[-300:]!r}")
    missing = {root: C.crossed(found.get(f"{root}-relayed-hybrid", {}), C.ZONES[root]) for root in C.ROOTS}
    no_inline = [root for root in ("laps", "cycle") if not found.get(f"{root}-relayed-hybrid", {}).get("zones", {}).get("inline")]
    if not any(missing.values()) and not no_inline:
        held("the zones of each root, and the channel's", "every root crosses its zones; inline on LAPS and CYCLE; "
             "never crossed: " + ", ".join(coverage.get("never", [])))
    else:
        failures.append(f"  ✗ the zones                  missing={missing} no_inline={no_inline}")
    return 0
