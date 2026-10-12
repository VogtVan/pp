"""Scenario `team-ask-members` -- 2 case(s) (batch le-tick, rework of 2026-10-09: decision 62 of the
phase, team 0.16.0): an `ask` goes to ANY member of the team or to a principal; each case names the
invariant of `team-sim-reframe.py` it replays.
- (a) T19 by the witness (I11a restated): `a1 a2 -> lead`; lead delegates T1 to both; a1 asks a2, a2 asks
  a1, each replies to the ask it received, then each answers `done`; lead closes T1 -- no `wake-failed`,
  each ask posted between the two helpers, each reply citing the ask it answers
- (b) a name nobody declared (I11a): x1 asks `zz`: `response-unreadable` naming a member nobody declared,
  retried; the retry answers `done`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "lead": [{"sleep": 0.1, "body": {"do": ["a1", "a2"]}},
                 {"sleep": 0.1, "body": {"done": "T19 closed"}}],
        "a1": [{"sleep": 0.2, "body": {"ask": {"to": "a2", "text": "which half is yours?"}}},
               {"sleep": 0.1, "body": {"reply": {"to": "a2", "text": "the tests"}}},
               {"sleep": 0.1, "body": {"done": "a1 done"}}],
        "a2": [{"sleep": 0.4, "body": {"ask": {"to": "a1", "text": "and yours?"}}},
               {"sleep": 0.1, "body": {"reply": {"to": "a1", "text": "the code"}}},
               {"sleep": 0.1, "body": {"done": "a2 done"}}],
        "x1": [{"sleep": 0.1, "body": {"ask": {"to": "zz", "text": "anyone?"}}},
               {"sleep": 0.1, "body": {"done": "alone"}}]})
    by_kind, all_ended, asks_to, result_of = T.by_kind, T.all_ended, T.asks_to, T.result_of

    # --- (a) two helpers ask each other, reply, then close -- I11a restated ---------------------------
    h.declare("pair", "---\nagents: |\n  lead agents/lead\n  a1 agents/aide\n  a2 agents/aide\nreports: |\n"
                      "  a1 a2 -> lead\nroot: lead\nschedule: off\n---\nSplit the work and agree.\n")
    pair = h.call("team", "start", "pair", "--message", "T19: split the change", *h.harnessed)
    done = h.settled("pair", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=90)
    found = h.events("pair")
    fails = [(one.get("agent"), str(one.get("reason"))) for one in by_kind(found, "wake-failed")]
    ask12, ask21 = asks_to(found, "a1", "a2"), asks_to(found, "a2", "a1")
    replies = [(one.get("from"), one.get("to"), one.get("reply")) for one in by_kind(found, "post", verb="reply")]
    owed = {("a1", "a2", ask21[0]["id"] if ask21 else None), ("a2", "a1", ask12[0]["id"] if ask12 else None)}
    if (pair.returncode == 0 and done and fails == [] and len(ask12) == 1 and len(ask21) == 1
            and set(replies) == owed and len(replies) == 2
            and len(by_kind(found, "terminal", agent="a1")) == 1 and len(by_kind(found, "terminal", agent="a2")) == 1
            and result_of(found, "T1") == "T19 closed"):
        held("(a) two members ask each other", f"a1 asks a2 (#{ask12[0]['id']}), a2 asks a1 (#{ask21[0]['id']}), each "
             "replies citing the ask it received, each answers done; T1 closed by lead, no wake-failed -- I11a restated")
    else:
        failures.append(f"  ✗ (a) two members ask each other  rc={pair.returncode} done={done} fails={fails} "
                        f"asks={len(ask12)}/{len(ask21)} replies={replies} owed={sorted(owed, key=str)} "
                        f"result={result_of(found, 'T1')!r}")

    # --- (b) an ask to a name nobody declared stays unreadable -- I11a ---------------------------------
    h.declare("alone", "---\nagents: |\n  x1 agents/x1\nroot: x1\nretries: 1\nschedule: off\n---\nWork alone.\n")
    alone = h.call("team", "start", "alone", "--message", "do it", *h.harnessed)
    done_b = h.settled("alone", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_b = h.events("alone")
    fails_b = [(one.get("final"), str(one.get("reason"))) for one in by_kind(found_b, "wake-failed", agent="x1")]
    if (alone.returncode == 0 and done_b and len(fails_b) == 1 and not fails_b[0][0]
            and fails_b[0][1].startswith("response-unreadable") and "zz" in fails_b[0][1]
            and "nobody declared" in fails_b[0][1] and not by_kind(found_b, "post", verb="ask")
            and result_of(found_b, "T1") == "alone"):
        held("(b) an ask to nobody", f"x1's ask to zz: {fails_b[0][1]!r}, retried; the retry answers done -- I11a")
    else:
        failures.append(f"  ✗ (b) an ask to nobody            rc={alone.returncode} done={done_b} fails={fails_b} "
                        f"result={result_of(found_b, 'T1')!r}")
    return 0
