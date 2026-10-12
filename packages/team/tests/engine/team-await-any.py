"""Scenario `team-await-any` -- 1 case(s) (batch l-attente, 2026-10-01; split out of `team-review`
by les-scenarios-par-maison, 2026-10-07): an agent that departs from its delegation.
- `await any 1` departs from the delegation: a delegates to a1 a2 a3 with `{"await": {"any": 1}}`
  and is woken a second time before the terminals of a2 and a3 -- `wait {any: 1}`, one `wait-met`,
  done T1; `{"await": {"any": 0}}` is `response-unreadable`
"""
from __future__ import annotations

import os
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "a": [{"sleep": 0.2, "body": {"do": ["a1", "a2", "a3"], "await": {"any": 1}}},
              {"sleep": 0.2, "body": {"done": "the first answer"}}],
        "a1": [{"sleep": 0.3, "body": {"done": True}}],
        "a2": [{"sleep": 2.5, "body": {"done": True}}],
        "a3": [{"sleep": 2.5, "body": {"done": True}}],
        "w": [{"sleep": 0.1, "body": {"do": ["w1"], "await": {"any": 0}}}]})
    by_kind, lines, all_ended = T.by_kind, T.lines, T.all_ended

    # --- an agent departs from the delegation: await any 1 -----------------------------------------
    h.declare("any", "---\nagents: |\n  a a\n  a1 a1\n  a2 a2\n  a3 a3\n"
                     "reports: |\n  a1 a2 a3 -> a\nroot: a\n---\nThe first answer will do.\n")
    h.declare("badwait", "---\nagents: |\n  w w\n  w1 w1\nreports: |\n  w1 -> w\nroot: w\nretries: 0\n---\n")
    anyteam = h.call("team", "start", "any", "--message", "one answer is enough", *h.harnessed)
    badwait = h.call("team", "start", "badwait", "--message", "wait for none", *h.harnessed)
    done_a = h.settled("any", lambda found: any(one.get("kind") == "done" for one in found) and all_ended(found)
                       and len(by_kind(found, "terminal")) >= 4)
    failed_w = h.settled("badwait", lambda found: bool(by_kind(found, "wake-failed", final=True)), timeout=60)
    time.sleep(0.5)
    found = h.events("any")
    intents_a = by_kind(found, "wake-intent", agent="a")
    waits_a = by_kind(found, "wait", agent="a")
    met_a = by_kind(found, "wait-met", agent="a")
    late = [one["id"] for one in by_kind(found, "terminal") if one.get("agent") in ("a2", "a3")]
    fails_w = [(one.get("final"), str(one.get("reason"))) for one in by_kind(h.events("badwait"), "wake-failed")]
    if (anyteam.returncode == 0 and badwait.returncode == 0 and done_a and failed_w
            and len(intents_a) == 2 and len(waits_a) == 1 and waits_a[0].get("any") == 1
            and sorted(waits_a[0].get("to") or []) == ["a1", "a2", "a3"]
            and len(met_a) == 1 and len(late) == 2 and intents_a[1]["id"] < min(late)
            and by_kind(found, "done", task="T1") and by_kind(found, "done", task="T1")[0].get("result") == "the first answer"
            and len(fails_w) == 1 and fails_w[0][0] is True and fails_w[0][1].startswith("response-unreadable")
            and "await" in fails_w[0][1]):
        held("await any 1 departs from the delegation", f"a woken 2 times, the second (#{intents_a[1]['id']}) before the "
             f"terminals of a2 a3 ({late}); wait any 1, one wait-met; done T1; await any 0: response-unreadable")
    else:
        failures.append(f"  ✗ await any                   {anyteam.returncode}/{badwait.returncode} done={done_a} "
                        f"intents={[one['id'] for one in intents_a]} waits={waits_a} met={len(met_a)} late={late} "
                        f"fails_w={fails_w} {anyteam.stderr[-200:]!r}")

    return 0
