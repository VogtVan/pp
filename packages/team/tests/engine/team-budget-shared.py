"""Scenario `team-budget-shared` -- 1 case(s) (batch le-budget-de-l-equipe, 2026-10-11: row 75 of the study § 18,
team 0.22.0; realigned by la-part-calculee, team 0.29.0): the team's rest is SHARED between the wake-ups under way --
each intent's allowance, its part of the rest, reserved until its end; the allowance composed is `team-budget`'s, the
parts `team-budget-parallel`'s. The case names the invariant of `team-sim-reframe.py` it replays.
- (b) the rest shared (I10r, I10p): `budget: 1`, `parallel: 2`, l delegates to r1 and r2 after spending 0.4 --
  r1 and r2 launched together, 0.3 each (the rest 0.6 over k = 2), neither `deferred`; at every intent the cost
  kept plus the allowances under way stays within the budget
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "l": [{"sleep": 0.1, "cost": 0.4, "body": {"do": ["r1", "r2"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "r1": [{"sleep": 1.5, "body": {"done": True}}],
        "r2": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def within(found: list[dict], budget: float) -> bool:
        """-> whether, at every intent, the cost kept plus the allowances of the intents without an end
        (this one included) stays within the budget -- I10r replayed on the journal."""
        cost, open_ = 0.0, {}
        for one in found:
            if one["kind"] in ("wake-ended", "wake-failed"):
                cost += float(one.get("cost") or 0)
            if one["kind"] in ("wake-ended", "wake-failed", "wake-killed"):
                open_.pop(one.get("tag"), None)
            if one["kind"] == "wake-intent":
                open_[one["tag"]] = float(one.get("allowance") or 0)
                if cost + sum(open_.values()) > budget + 1e-9:
                    return False
        return True

    # --- (b) the rest shared: r1 and r2 each their part, launched together -- I10r, I10p ---------------------
    h.declare("pair", "---\nagents: |\n  l agents/l\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> l\n"
                      "root: l\nparallel: 2\nbudget: 1\nschedule: off\n---\nShare the rest.\n")
    paired = h.call("team", "start", "pair", "--message", "review PR 10", *h.harnessed)
    done_p = h.settled("pair", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("pair")
    by_tag = {one["tag"]: one for one in by_kind(found, "wake-intent")}
    r1 = next((one for one in by_tag.values() if one["agent"] == "r1"), {})
    r2 = next((one for one in by_tag.values() if one["agent"] == "r2"), {})
    r1_end = next((one["id"] for one in found if one["kind"] == "wake-ended" and one.get("tag") == r1.get("tag")), -1)
    if (paired.returncode == 0 and done_p and r1.get("allowance") == 0.3 and r2.get("allowance") == 0.3
            and not by_kind(found, "deferred") and r2.get("id", 10 ** 9) < r1_end and within(found, 1.0)):
        held("(b) the rest shared", "l spent 0.4: r1 and r2 launched together, 0.3 each, neither deferred; "
             "cost + allowances within 1 at every intent -- I10r, I10p")
    else:
        failures.append(f"  ✗ (b) the rest shared        rc={paired.returncode} done={done_p} r1={r1.get('allowance')} "
                        f"r2={r2.get('allowance')} deferred={by_kind(found, 'deferred')} r1_end={r1_end} "
                        f"r2_at={r2.get('id')} within={within(found, 1.0)}")

    return 0
