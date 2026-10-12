"""Scenario `team-guards` -- 2 case(s) (batch les-garde-fous, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the guards of a team, each on a team of
its own under the witness.
- a ping-pong stops: under `wakes: 3`, two witnesses trading `ask`/`reply` stop at the task's
  third wake-up -- `wakes-spent` once, the escalate from the team to the owner, no further
  `wake-intent` on the task
- a costless provider is bounded: under `budget-wakes: 2`, two wake-ups play, the third due is
  never launched -- `budget-spent {unit: wakes}` once, the escalate; `status` says it
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f2": [{"sleep": 0.1, "body": {"do": ["c"]}},
               {"sleep": 0.1, "body": {"reply": {"to": "c", "text": "again"}}},
               {"sleep": 0.1, "body": {"reply": {"to": "c", "text": "and again"}}}],
        "c": [{"sleep": 0.1, "body": {"ask": {"to": "f2", "text": "q1"}}},
              {"sleep": 0.1, "body": {"ask": {"to": "f2", "text": "q2"}}},
              {"sleep": 0.1, "body": {"ask": {"to": "f2", "text": "q3"}}}],
        "n": [{"sleep": 0.1, "body": {"do": ["n1"]}},
              {"sleep": 0.1, "body": {"done": "never reached"}}],
        "n1": [{"sleep": 0.1, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- a ping-pong stops -------------------------------------------------------------------------
    h.declare("pong", "---\nagents: |\n  f2 f2\n  c c\nreports: |\n  c -> f2\nroot: f2\nwakes: 3\n---\nStop the rally.\n")
    pong = h.call("team", "start", "pong", "--message", "talk it over", *h.harnessed)
    spent_p = h.settled("pong", lambda found: bool(by_kind(found, "wakes-spent")) and all_ended(found), timeout=60)
    time.sleep(1.5)
    found_p = h.events("pong")
    intents_p = by_kind(found_p, "wake-intent")
    spent_events = by_kind(found_p, "wakes-spent")
    esc_p = [one for one in by_kind(found_p, "post", verb="escalate") if one.get("from") == "pong"]
    more = h.call("team", "tick", "pong")
    after_more = by_kind(h.events("pong"), "wake-intent")
    if (pong.returncode == 0 and spent_p and len(intents_p) == 3
            and all(one.get("task") == "T1" for one in intents_p)
            and len(spent_events) == 1 and spent_events[0].get("task") == "T1"
            and spent_events[0].get("spent") == 3 and spent_events[0].get("wakes") == 3
            and len(esc_p) == 1 and esc_p[0].get("to") == "house"
            and more.returncode == 0 and len(after_more) == 3):
        held("a ping-pong stops", "wakes 3: f2 and c trade ask/reply, the task's third wake-up is the last -- "
             "wakes-spent once, the escalate pong -> house, a later tick launches nothing more")
    else:
        failures.append(f"  ✗ wakes bound                 rc={pong.returncode} spent={spent_p} "
                        f"intents={len(intents_p)}/{len(after_more)} events={spent_events} esc={len(esc_p)} "
                        f"{pong.stderr[-150:]!r}")

    # --- a costless provider is bounded --------------------------------------------------------------
    h.declare("nocost", "---\nagents: |\n  n n\n  n1 n1\nreports: |\n  n1 -> n\nroot: n\nbudget-wakes: 2\n---\nCount the wake-ups.\n")
    nocost = h.call("team", "start", "nocost", "--message", "spend nothing", *h.harnessed)
    spent_n = h.settled("nocost", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found_n = h.events("nocost")
    bspent = by_kind(found_n, "budget-spent")
    status_n = h.call("team", "status", "nocost")
    if (nocost.returncode == 0 and spent_n and len(by_kind(found_n, "wake-intent")) == 2
            and len(bspent) == 1 and bspent[0].get("unit") == "wakes"
            and bspent[0].get("spent") == 2 and bspent[0].get("budget") == 2
            and status_n.returncode == 0 and "budget spent" in status_n.stdout
            and "owner inbox 1" in status_n.stdout):
        held("a costless provider is bounded", "budget-wakes 2: two wake-ups play, the third due is never "
             "launched -- budget-spent {unit: wakes} once, the escalate in the owner's inbox, status says it")
    else:
        failures.append(f"  ✗ budget-wakes                rc={nocost.returncode} spent={spent_n} "
                        f"intents={len(by_kind(found_n, 'wake-intent'))} bspent={bspent} "
                        f"{status_n.stdout[-200:]!r} {nocost.stderr[-150:]!r}")
    return 0
