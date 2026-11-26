"""Scenario `team-budget-deferred` -- 1 case(s) (batch le-filet-complete, 2026-11-25; cut out of `team-budget-capped`
by rule 10: with this case beside its own, that scenario played 39 s alone):
- the rest held by a launch under way: under `budget: 1` and three members, o delegates to o1 and o2 (a third each);
  o1 reports 0.9 while o2 still plays -- o2 held at a gate the bench opens once the journal carries the `deferred` --,
  so o, due on o1's answer, has no part left -- `deferred {agent: o, task: T1, reserved}` the third o2 holds --; o2
  ends, o is launched on the rest and T1 is done
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gate_o = bench.temp() / "o2.gate"                  # o2 plays once the bench lays it
    h = T.House(bench, script={
        "o": [{"sleep": 0.1, "cost": 0, "body": {"do": ["o1", "o2"]}}, {"sleep": 0.1, "cost": 0, "body": {"done": "over"}}],
        "o1": [{"sleep": 0.1, "cost": 0.9, "body": {"done": True}}],
        "o2": [{"gate": str(gate_o), "cost": 0.01, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- the rest held by a launch under way ------------------------------------------------------------------
    h.declare("over", "---\nagents: |\n  o agents/o\n  o1 agents/o1\n  o2 agents/o2\nreports: |\n  o1 o2 -> o\n"
                      "root: o\nbudget: 1\nschedule: off\n---\nSpend within your share.\n")
    started_o = h.call("team", "start", "over", "--message", "price the DDR3", *h.harnessed)
    deferred_o = h.settled("over", lambda found: bool(by_kind(found, "deferred")), 90)   # o1's end read, o2 still held
    gate_o.write_text("", encoding="utf-8")
    done_o = h.settled("over", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found_o = h.events("over")
    held_o = [(one.get("agent"), one.get("task"), one.get("reserved")) for one in by_kind(found_o, "deferred")]
    o2_end = next((one["id"] for one in by_kind(found_o, "wake-ended", agent="o2")), 10 ** 9)
    if (started_o.returncode == 0 and deferred_o and done_o and held_o and set(held_o) == {("o", "T1", 0.333333)}
            and all(one["id"] < o2_end for one in by_kind(found_o, "deferred"))
            and T.result_of(found_o, "T1") == "over"):
        held("the rest held by a launch under way", f"o1 reports 0.9 while o2 holds 0.333333: o deferred {held_o}; "
             "o2 ends, o launched on the rest, T1 done")
    else:
        failures.append(f"  ✗ the rest held               rc={started_o.returncode} done={done_o} deferred={held_o} "
                        f"o2_end={o2_end} result={T.result_of(found_o, 'T1')!r} "
                        f"intents={[(one['agent'], one.get('allowance')) for one in by_kind(found_o, 'wake-intent')]}")
    return 0
