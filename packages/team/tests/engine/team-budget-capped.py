"""Scenario `team-budget-capped` -- 1 case(s) (batch la-part-calculee, 2026-10-11, row 75 of the study § 18; rewritten
by le-lanceur-et-la-lecture, 2026-10-23: a wake-up is ONE launch, so no cap falls between two launches any more --
the share of a launch is the cap the house passes to the harness, and what the launch reports is charged whole):
- the share is the launch's cap (I10r): under `budget: 1` and two members, l's first launch gets the cap 0.5 (its
  share: the rest over the members that may play together) at the house's record of the launch; it reports 0.8,
  charged whole at `wake-ended`, no failure; f, the root of a second team at `budget: 1`, delegates to g at 0.8:
  g's launch gets the cap 0.1 -- min((1 - 0.8) / 2, the rest no launch holds) --, the team's cost 0.81, T1 done
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "l": [{"sleep": 0.1, "cost": 0.8, "body": {"done": "too dear"}}],
        "f": [{"sleep": 0.1, "cost": 0.8, "body": {"do": ["g"]}}, {"sleep": 0.1, "cost": 0.01, "body": {"done": "paid"}}],
        "g": [{"sleep": 0.1, "cost": 0.01, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def cap_of(path: str, nth: int):
        sent = [one for one in T.lines(h.records / "messages.jsonl") if one.get("to") == path]
        return ((sent[nth].get("policy") or {}).get("max_budget_usd") if len(sent) > nth else None)

    h.declare("dear", "---\nagents: |\n  l agents/l\n  r agents/r\nreports: |\n  r -> l\nroot: l\nbudget: 1\n"
                      "schedule: off\n---\nSpend within your share.\n")
    h.declare("last", "---\nagents: |\n  f agents/f\n  g agents/g\nreports: |\n  g -> f\nroot: f\nbudget: 1\n"
                      "schedule: off\n---\nSpend within your share.\n")
    started = h.call("team", "start", "dear", "--message", "price the DDR4", *h.harnessed)
    started_b = h.call("team", "start", "last", "--message", "price the DDR5", *h.harnessed)
    done = h.settled("dear", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    done_b = h.settled("last", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    found = h.events("dear")
    found_b = h.events("last")
    ends_l = [(one.get("cost"), one.get("state")) for one in by_kind(found, "wake-ended", agent="l")]
    face_b = h.face("last")
    if (started.returncode == 0 and done and ends_l == [(0.8, "parked")] and not by_kind(found, "wake-failed")
            and cap_of("agents/l", 0) == 0.5 and abs(float(h.face("dear").get("cost") or 0) - 0.8) < 1e-9
            and started_b.returncode == 0 and done_b and not by_kind(found_b, "wake-failed")
            and cap_of("agents/f", 0) == 0.5 and abs(float(cap_of("agents/g", 0) or 0) - 0.1) < 1e-5
            and abs(float(face_b.get("cost") or 0) - 0.82) < 1e-9 and T.result_of(found_b, "T1") == "paid"):
        held("the share is the launch's cap", "l's launch capped at 0.5, reports 0.8: charged whole, no failure, "
             "T1 done; f at 0.8 then g capped at 0.1 -- the rest over two --, the team's cost 0.82 -- I10r")
    else:
        failures.append(f"  ✗ the share is the cap        rc={started.returncode}/{started_b.returncode} done={done}/{done_b} "
                        f"ends={ends_l} caps={cap_of('agents/l', 0)}/{cap_of('agents/f', 0)}/{cap_of('agents/g', 0)} "
                        f"cost={h.face('dear').get('cost')}/{face_b.get('cost')} fails={by_kind(found, 'wake-failed')}"
                        f"/{by_kind(found_b, 'wake-failed')} result={T.result_of(found_b, 'T1')!r} {started.stderr[-200:]!r}")
    return 0
