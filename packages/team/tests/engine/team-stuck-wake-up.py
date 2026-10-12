"""Scenario `team-stuck-wake-up` -- 1 case(s) (batch les-garde-fous, 2026-10-01; split out of
`team-review` by les-scenarios-par-maison, 2026-10-07): the timeout of a wake-up.
- a stuck wake-up is freed: under `timeout: 2`, a witness sleeping 30 s is killed by a tick
  played ~3 s after the launch (`wake-failed wake-timeout`, the pid gone), the retry (a sane
  witness at the second wake-up) resolves the task; under `retries: 0` the first timeout is
  final and the escalate rises
"""
from __future__ import annotations

import os
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "x": [{"sleep": 0.1, "body": {"do": ["x1"]}},
              {"sleep": 0.1, "body": {"done": "freed"}}],
        "x1": [{"sleep": 30, "body": {"done": True}},
               {"sleep": 0.1, "body": {"done": True}}],
        "x0": [{"sleep": 0.1, "body": {"do": ["x01"]}},
               {"sleep": 0.1, "body": {"done": "gave up"}}],
        "x01": [{"sleep": 30, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    # --- a stuck wake-up is freed ----------------------------------------------------------------
    h.declare("stuck", "---\nagents: |\n  x x\n  x1 x1\nreports: |\n  x1 -> x\nroot: x\ntimeout: 2\n---\nFree the stuck.\n")
    h.declare("stuck0", "---\nagents: |\n  x0 x0\n  x01 x01\nreports: |\n  x01 -> x0\nroot: x0\ntimeout: 2\nretries: 0\n---\nGive up fast.\n")
    stuck = h.call("team", "start", "stuck", "--message", "review slowly", *h.harnessed)
    stuck0 = h.call("team", "start", "stuck0", "--message", "review slowly", *h.harnessed)
    running_x = h.settled("stuck", lambda found: bool(by_kind(found, "wake-launched", agent="x1")), timeout=60)
    launch_x1 = next(iter(by_kind(h.events("stuck"), "wake-launched", agent="x1")), {})
    time.sleep(3.0)                                          # past the 2 s bound, the witness still asleep
    freed = h.call("team", "tick", "stuck")
    freed0 = h.call("team", "tick", "stuck0")
    done_x = h.settled("stuck", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    final_x0 = h.settled("stuck0", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)
    found_x = h.events("stuck")
    found_x0 = h.events("stuck0")
    timeouts = [(one.get("final"), one.get("reason")) for one in by_kind(found_x, "wake-failed", agent="x1")]
    gone_x1 = True
    if launch_x1.get("pid"):
        try:
            os.kill(int(launch_x1["pid"]), 0)
            gone_x1 = False
        except ProcessLookupError:
            gone_x1 = True
    timeouts0 = [(one.get("final"), one.get("reason")) for one in by_kind(found_x0, "wake-failed", agent="x01")]
    esc_x0 = [one for one in by_kind(found_x0, "post", verb="escalate") if one.get("to") == "x0"]
    if (stuck.returncode == 0 and stuck0.returncode == 0 and running_x and freed.returncode == 0
            and freed0.returncode == 0 and done_x and final_x0
            and timeouts == [(False, "wake-timeout")] and gone_x1
            and len(by_kind(found_x, "wake-intent", agent="x1")) == 2
            and by_kind(found_x, "done", task="T1")[0].get("result") == "freed"
            and timeouts0 == [(True, "wake-timeout")] and len(esc_x0) == 1
            and len(by_kind(found_x0, "wake-intent", agent="x01")) == 1):
        held("a stuck wake-up is freed", f"timeout 2: x1 killed ~3 s after its launch (pid {launch_x1.get('pid')} "
             "gone), wake-failed wake-timeout, the retry resolves T1 (freed); retries 0: the first timeout is "
             "final, the escalate rises to x0 (gave up)")
    else:
        failures.append(f"  ✗ wake-timeout                {stuck.returncode}/{stuck0.returncode} run={running_x} "
                        f"done={done_x}/{final_x0} t={timeouts} t0={timeouts0} gone={gone_x1} "
                        f"esc={len(esc_x0)} intents={len(by_kind(found_x, 'wake-intent', agent='x1'))} "
                        f"{freed.stderr[-150:]!r}")

    return 0
