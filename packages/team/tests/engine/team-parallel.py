"""Scenario `team-parallel` -- 1 case(s) (batch les-limites-du-tick, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the parallel bound of the tick.
- `parallel: 1` holds: p delegates to p1 p2 p3, the journal read in order never shows two intents
  without an end, `deferred` is written for the agents held back, the team ends
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "p": [{"sleep": 0.2, "body": {"do": ["p1", "p2", "p3"]}}, {"sleep": 0.2, "body": {"done": "all three"}}],
        "p1": [{"sleep": 0.3, "body": {"done": True}}],
        "p2": [{"sleep": 0.3, "body": {"done": True}}],
        "p3": [{"sleep": 0.3, "body": {"done": True}}]})
    by_kind, lines, all_ended = T.by_kind, T.lines, T.all_ended

    # --- parallel: 1 holds: never two intents without an end, the rest deferred ---------------------
    h.declare("limited", "---\nagents: |\n  p p\n  p1 p1\n  p2 p2\n  p3 p3\n"
                         "reports: |\n  p1 p2 p3 -> p\nroot: p\nparallel: 1\n---\nOne at a time.\n")
    limited = h.call("team", "start", "limited", "--message", "review in turn", *h.harnessed)
    done_l = h.settled("limited", lambda found: any(one.get("kind") == "done" for one in found) and all_ended(found))
    time.sleep(1.0)
    found = h.events("limited")
    open_intents, peak = set(), 0
    for one in found:
        if one.get("kind") == "wake-intent":
            open_intents.add(one["tag"])
        elif one.get("kind") in ("wake-ended", "wake-failed"):
            open_intents.discard(one["tag"])
        peak = max(peak, len(open_intents))
    deferred = [one for one in found if one.get("kind") == "deferred"]
    started_l = next((one for one in found if one.get("kind") == "team-started"), {})
    if (limited.returncode == 0 and done_l and peak == 1 and len(deferred) >= 2
            and {one.get("agent") for one in deferred} <= {"p1", "p2", "p3"}
            and started_l.get("limits") == {"parallel": 1}
            and sum(1 for one in found if one.get("kind") == "wake-intent") == 5):
        held("parallel: 1 holds", f"peak of intents without an end {peak}, {len(deferred)} deferred, 5 wake-ups, done")
    else:
        failures.append(f"  ✗ parallel                    rc={limited.returncode} done={done_l} peak={peak} "
                        f"deferred={[(one.get('agent'), one.get('task')) for one in deferred]} limits={started_l.get('limits')} "
                        f"{limited.stderr[-200:]!r}")

    return 0
