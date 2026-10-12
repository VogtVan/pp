"""Scenario `team-bounds` -- 2 case(s) (batch les-limites-du-tick, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the bounds of the tick, each on a
team of its own under the witness, which here gains `prose` (an answer that is no JSON object).
- `budget: 0.015` holds: two wake-ups paid (0.02), the third agent due is not launched --
  `budget-spent` once, an `escalate` post from the team to the owner; `status` says the cost spent
- a limit mis-written refuses `team-invalid` before anything is written
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "b": [{"sleep": 0.2, "body": {"do": ["b1", "b2"]}}],
        "b1": [{"sleep": 0.3, "body": {"done": True}}]})
    by_kind, lines, all_ended = T.by_kind, T.lines, T.all_ended

    # --- budget: 0.015 holds: two wake-ups paid, the third not launched, the owner told ---------------
    h.declare("budgeted", "---\nagents: |\n  b b\n  b1 b1\n  b2 b2\nreports: |\n  b1 b2 -> b\n"
                          "root: b\nparallel: 1\nbudget: 0.015\n---\nSpend little.\n")
    budgeted = h.call("team", "start", "budgeted", "--message", "review cheaply", *h.harnessed)
    spent = h.settled("budgeted", lambda found: any(one.get("kind") == "budget-spent" for one in found) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found = h.events("budgeted")
    spent_events = [one for one in found if one.get("kind") == "budget-spent"]
    escalated = [one for one in found if one.get("kind") == "post" and one.get("verb") == "escalate" and one.get("to") == "house"]
    intents_b = [one.get("agent") for one in found if one.get("kind") == "wake-intent"]
    status_b = h.call("team", "status", "budgeted")
    if (budgeted.returncode == 0 and spent and len(spent_events) == 1
            and abs(spent_events[0].get("spent", 0) - 0.02) < 1e-9 and spent_events[0].get("budget") == 0.015
            and len(escalated) == 1 and escalated[0].get("from") == "budgeted"
            and sorted(intents_b) == ["b", "b1"] and "b2" not in intents_b
            and status_b.returncode == 0 and "cost 0.02 USD · budget spent" in status_b.stdout
            and "owner inbox 1" in status_b.stdout and "escalate from budgeted on T1" in status_b.stdout):
        held("budget: 0.015 holds", "two wake-ups paid (0.02), b2 not launched: budget-spent once, escalate budgeted -> house; "
             "status says cost 0.02 USD · budget spent and the owner's inbox")
    else:
        failures.append(f"  ✗ budget                      rc={budgeted.returncode} spent={spent} events={spent_events} "
                        f"escalated={len(escalated)} intents={intents_b} {status_b.stdout[-300:]!r} {budgeted.stderr[-200:]!r}")

    # --- a limit mis-written refuses before anything is written ---------------------------------------
    h.declare("bad-par", "---\nagents: |\n  z1 z1\nroot: z1\nparallel: 0\n---\n")
    h.declare("bad-bud", "---\nagents: |\n  z2 z2\nroot: z2\nbudget: free\n---\n")
    h.declare("bad-ret", "---\nagents: |\n  z3 z3\nroot: z3\nretries: -1\n---\n")
    h.declare("bad-tmo", "---\nagents: |\n  z4 z4\nroot: z4\ntimeout: soon\n---\n")
    h.declare("bad-wak", "---\nagents: |\n  z5 z5\nroot: z5\nwakes: 0\n---\n")
    h.declare("bad-bwk", "---\nagents: |\n  z6 z6\nroot: z6\nbudget-wakes: -1\n---\n")
    bad = {name: h.call("team", "start", name, "--message", "x", *h.harnessed)
           for name in ("bad-par", "bad-bud", "bad-ret", "bad-tmo", "bad-wak", "bad-bwk")}
    if (all(one.returncode == 2 and "team-invalid" in one.stderr and one.stdout == "" for one in bad.values())
            and "parallel" in bad["bad-par"].stderr and "budget" in bad["bad-bud"].stderr and "retries" in bad["bad-ret"].stderr
            and "timeout" in bad["bad-tmo"].stderr and "wakes" in bad["bad-wak"].stderr and "budget-wakes" in bad["bad-bwk"].stderr
            and not any(h.agent_stands(name) for name in ("z1", "z2", "z3", "z4", "z5", "z6"))
            and not any(h.journal_of(name).exists() for name in bad)):
        held("a limit mis-written refuses", "parallel 0, budget free, retries -1, timeout soon, wakes 0, "
             "budget-wakes -1: team-invalid naming the key; no agent, no journal")
    else:
        failures.append("  ✗ limits invalid              " + " ".join(f"{name}={one.returncode}:{one.stderr[-100:]!r}" for name, one in bad.items()))
    return 0
