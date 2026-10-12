"""Scenario `team-prose-answer` -- 1 case(s) (batch les-limites-du-tick, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the witness gains `prose` (an answer that
is no JSON object).
- a prose answer is a dead wake-up: `wake-failed response-unreadable`, retried `retries` times
  (1, then 0 on a second team), then `final`, `terminal` and an `escalate` to the owner
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "q": [{"sleep": 0.1, "body": "prose"}, {"sleep": 0.1, "body": "prose"}],
        "q0": [{"sleep": 0.1, "body": "prose"}, {"sleep": 0.1, "body": "prose"}]})

    # --- a prose answer is a dead wake-up: retried `retries` times, then final ----------------------
    h.declare("prosy", "---\nagents: |\n  q q\nroot: q\nretries: 1\n---\nAnswer in JSON.\n")
    h.declare("prosy0", "---\nagents: |\n  q0 q0\nroot: q0\nretries: 0\n---\nAnswer in JSON.\n")
    prosy = h.call("team", "start", "prosy", "--message", "say something", *h.harnessed)
    prosy0 = h.call("team", "start", "prosy0", "--message", "say something", *h.harnessed)
    final_p = h.settled("prosy", lambda found: any(one.get("kind") == "wake-failed" and one.get("final") for one in found), timeout=60)
    final_p0 = h.settled("prosy0", lambda found: any(one.get("kind") == "wake-failed" and one.get("final") for one in found), timeout=60)
    time.sleep(0.5)
    found_p = h.events("prosy")
    found_p0 = h.events("prosy0")
    fails_p = [(one.get("final"), one.get("reason")) for one in found_p if one.get("kind") == "wake-failed"]
    fails_p0 = [(one.get("final"), one.get("reason")) for one in found_p0 if one.get("kind") == "wake-failed"]
    tail_p = [(one.get("kind"), one.get("verb"), one.get("to")) for one in found_p[-3:]]
    if (prosy.returncode == 0 and prosy0.returncode == 0 and final_p and final_p0
            and fails_p == [(False, "response-unreadable"), (True, "response-unreadable")]
            and fails_p0 == [(True, "response-unreadable")]
            and ("terminal", None, None) in tail_p and ("post", "escalate", "house") in tail_p):
        held("a prose answer is a dead wake-up", "retries 1: response-unreadable, then final + terminal + escalate q -> house; "
             "retries 0: final at the first")
    else:
        failures.append(f"  ✗ prose                       {prosy.returncode}/{prosy0.returncode} {final_p}/{final_p0} "
                        f"{fails_p} {fails_p0} {tail_p} {prosy.stderr[-200:]!r}")

    return 0
