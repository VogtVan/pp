"""Scenario `team-kill` -- 1 case(s) (batch l-attente, 2026-10-01; split out of `team-review` by
les-scenarios-par-maison, 2026-10-07): the kill of a wake-up under way.
- a stop --kill kills: k delegates to k1, which sleeps 5 s; `team stop kill --task T1 --kill` -- the
  launcher's pid gone, `wake-killed` with its tag, run and pid, no response of k1 at the house's
  record, no retry, k not woken for its stop (team 0.10.0), `status` says `killed`
"""
from __future__ import annotations

import os
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "k": [{"sleep": 0.2, "body": {"do": ["k1"]}}, {"sleep": 0.1, "body": {"done": "stopped"}}],
        "k1": [{"sleep": 5.0, "body": {"done": True}}]})
    by_kind, lines, all_ended = T.by_kind, T.lines, T.all_ended

    # --- a stop --kill kills: the pid gone, nothing kept, no retry -----------------------------------
    h.declare("kill", "---\nagents: |\n  k k\n  k1 k1\nreports: |\n  k1 -> k\nroot: k\n---\nKill on demand.\n")
    killing = h.call("team", "start", "kill", "--message", "review very slowly", *h.harnessed)
    running_k = h.settled("kill", lambda found: bool(by_kind(found, "wake-launched", agent="k1")), timeout=60)
    launch_k = next(iter(by_kind(h.events("kill"), "wake-launched", agent="k1")), {})
    time.sleep(0.5)                                          # the witness sleeps its 5 s
    killed_k = h.call("team", "stop", "kill", "--task", "T1", "--kill")
    gone, deadline = False, time.monotonic() + 5
    while time.monotonic() < deadline and launch_k.get("pid"):
        try:
            os.kill(int(launch_k["pid"]), 0)
        except ProcessLookupError:
            gone = True
            break
        time.sleep(0.1)
    quiet_k = h.settled("kill", all_ended)
    time.sleep(5.5)                                          # past the witness's own end, had it lived
    found = h.events("kill")
    killed_events = by_kind(found, "wake-killed")
    answers_k1 = [one for one in lines(h.records / "responses.jsonl") if one.get("agent") == "k1"]
    k1_line = h.status_line("kill", "k1 · ")
    if (killing.returncode == 0 and running_k and killed_k.returncode == 0 and gone and quiet_k
            and len(killed_events) == 1 and killed_events[0].get("agent") == "k1"
            and killed_events[0].get("pid") == launch_k.get("pid") and killed_events[0].get("run") == launch_k.get("run")
            and killed_events[0].get("tag") == launch_k.get("tag")
            and answers_k1 == [] and len(by_kind(found, "wake-intent", agent="k1")) == 1
            and not by_kind(found, "wake-failed") and len(by_kind(found, "wake-intent", agent="k")) == 1
            and "killed" in killed_k.stdout and "· killed" in k1_line):
        held("a stop --kill kills", f"pid {launch_k.get('pid')} gone, wake-killed {killed_events[0].get('tag')}, no response of k1 "
             f"at the record, no retry; k not woken for its stop; status: {k1_line!r}")
    else:
        failures.append(f"  ✗ kill                        {killing.returncode}/{killed_k.returncode} running={running_k} "
                        f"gone={gone} quiet={quiet_k} killed={killed_events} launch={launch_k} answers={len(answers_k1)} "
                        f"k1={k1_line!r} {killed_k.stdout[-200:]!r} {killed_k.stderr[-200:]!r}")
    return 0
