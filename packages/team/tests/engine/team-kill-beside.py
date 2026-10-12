"""Scenario `team-kill-beside` -- 1 case(s) (batch le-tick, rework: the members, team 0.13.1; split
out of `team-review` by les-scenarios-par-maison, 2026-10-07): a kill beside another task of the
same member.
- (q) the kill beside another task [57] (I9, I18): km plays T2 while it holds T1; `stop --kill --task T2`
  ends that wake-up alone; kd's answer on T1 resumes km's same key and session, T1 done
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "km": {"T1": [{"sleep": 0.1, "body": {"do": ["kd"]}},
                      {"sleep": 0.1, "body": {"done": "after the kill"}}],
               "T2": [{"sleep": 30.0, "body": {"done": "never"}}]},
        "kd": [{"sleep": 6.0, "body": {"done": True}}]})
    by_kind, all_ended, result_of, runs_launched = T.by_kind, T.all_ended, T.result_of, T.runs_launched

    # --- (q) the kill beside another task [57] -- I9, I18 ------------------------------------------------
    h.declare("beside", "---\nagents: |\n  km agents/km\n  kd agents/kd\nreports: |\n  kd -> km\nroot: km\n"
                        "schedule: off\n---\nA kill beside.\n")
    beside = h.call("team", "start", "beside", "--message", "delegate it", *h.harnessed)
    out_q = h.settled("beside", lambda found: bool(by_kind(found, "wake-launched", agent="kd")), timeout=60)
    beside2 = h.call("team", "post", "beside", "--to", "km", "--message", "a long one")
    plays_t2 = h.settled("beside", lambda found: any(one.get("task") == "T2" and one["tag"] in
                                                      {l.get("tag") for l in by_kind(found, "wake-launched", agent="km")}
                                                      for one in by_kind(found, "wake-intent", agent="km")), timeout=60)
    time.sleep(1.0)                                   # km's witness asleep on T2
    killed_q = h.call("team", "stop", "beside", "--task", "T2", "--kill")
    done_q = h.settled("beside", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_q = h.events("beside")
    kills_q = by_kind(found_q, "wake-killed")
    key_q = next((one.get("run") for one in by_kind(found_q, "wake-ended", agent="km")), "")
    after_kill = [one for one in by_kind(found_q, "wake-intent", agent="km") if kills_q and one["id"] > kills_q[0]["id"]]
    if (beside.returncode == 0 and out_q and beside2.returncode == 0 and plays_t2 and killed_q.returncode == 0
            and done_q and len(kills_q) == 1 and kills_q[0].get("agent") == "km" and kills_q[0].get("task") == "T2"
            and kills_q[0].get("run") == key_q and runs_launched(found_q, "km") == {key_q}
            and len(after_kill) == 1 and after_kill[0].get("task") == "T1" and after_kill[0].get("run") == key_q
            and len({session for _, session in h.sessions_at("agents/km")}) == 1
            and by_kind(found_q, "stopped", task="T2") and result_of(found_q, "T1") == "after the kill"):
        held("(q) the kill beside another task", f"km plays T2 in its run {key_q} while it holds T1: stop --kill "
             "T2 ends that wake-up alone (wake-killed on T2); kd's answer on T1 resumes km's same key and session, "
             "T1 done -- I9, I18")
    else:
        failures.append(f"  ✗ (q) the kill beside         {beside.returncode}/{beside2.returncode}/{killed_q.returncode} "
                        f"out={out_q} plays={plays_t2} done={done_q} kills={[(one.get('agent'), one.get('task'), one.get('run')) for one in kills_q]} "
                        f"key={key_q} runs={runs_launched(found_q, 'km')} after={[(one['task'], one.get('run')) for one in after_kill]} "
                        f"sessions={h.sessions_at('agents/km')} {killed_q.stdout[-200:]!r} {killed_q.stderr[-200:]!r}")
    return 0
