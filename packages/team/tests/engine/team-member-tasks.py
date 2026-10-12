"""Scenario `team-member-tasks` -- 2 case(s) (batch le-tick, rework, pass A: the run and the
parallel, team 0.12.0; split out of `team-review` by les-scenarios-par-maison, 2026-10-07): the
witness gains a script PER TASK (the task its inbox names); each case names the invariant of
`team-sim-reframe.py` it replays.
- (a) two members of one agent, a member's two tasks [49] (I8a, I10, I20): d delegates T1 to d1
  (asleep) and d2, both played by agents/dd and launched together, two runs; T2 posted to d once d2
  answered: d woken on T2 before d1's terminal, in its ONE run; `parallel: 2` never exceeded
- (c) the cursor of the member's run [34] (I8b): d's wake-up on T2 names d2's answer since its run's
  opening; its resume on T1 names d1 alone, since its wake-up on T2 -- what its run read is never
  named twice
"""
from __future__ import annotations

import re
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "d": {"T1": [{"sleep": 0.2, "body": {"do": ["d1", "d2"]}},
                     {"sleep": 0.2, "body": {"done": "first"}}],
              "T2": [{"sleep": 0.2, "body": {"done": "second"}}]},
        "d1": [{"sleep": 4.0, "body": {"done": True}}],
        "d2": [{"sleep": 0.2, "body": {"done": True}}]})
    by_kind, all_ended, intents_on, terminal_of, peak, result_of = (
        T.by_kind, T.all_ended, T.intents_on, T.terminal_of, T.peak, T.result_of)

    # --- (a) two members of one agent in parallel, a member's two tasks in its run [49] -- I8a, I10, I20 ----
    h.declare("duo", "---\nagents: |\n  d d\n  d1 agents/dd\n  d2 agents/dd\nreports: |\n  d1 d2 -> d\n"
                     "root: d\nparallel: 2\nschedule: off\n---\nTwo tasks for one manager.\n")
    duo = h.call("team", "start", "duo", "--message", "review PR 7", *h.harnessed)
    d2_done = h.settled("duo", lambda found: bool(by_kind(found, "terminal", agent="d2")), timeout=60)
    second_task = h.call("team", "post", "duo", "--to", "d", "--message", "review PR 8")
    both = h.settled("duo", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=90)
    time.sleep(0.5)
    found_d = h.events("duo")
    d_t1, d_t2 = intents_on(found_d, "d", "T1"), intents_on(found_d, "d", "T2")
    runs_d = {one["tag"]: one.get("run") for one in by_kind(found_d, "wake-launched", agent="d")}
    keys_d = set(runs_d.values())
    devs_d = {one.get("agent"): one for one in by_kind(found_d, "wake-launched") if one.get("agent") in ("d1", "d2")}
    first_dev_end = min((one["id"] for one in by_kind(found_d, "wake-ended") if one.get("agent") in ("d1", "d2")),
                        default=0)
    if (duo.returncode == 0 and d2_done and second_task.returncode == 0 and both
            and len(d_t1) == 2 and len(d_t2) == 1 and d_t2[0]["id"] < terminal_of(found_d, "d1")
            and len(keys_d) == 1 and d_t2[0].get("run") in keys_d
            and set(devs_d) == {"d1", "d2"} and devs_d["d1"].get("run") != devs_d["d2"].get("run")
            and all(one["id"] < first_dev_end for one in devs_d.values())
            and peak(found_d) <= 2
            and result_of(found_d, "T1") == "first" and result_of(found_d, "T2") == "second"):
        held("(a) two members of one agent in parallel", f"d1 and d2 of agents/dd launched together, two runs; d "
             f"woken on T2 (#{d_t2[0]['id']}) before d1's terminal (#{terminal_of(found_d, 'd1')}), in its ONE run "
             f"{sorted(keys_d)[0]}; parallel 2 never exceeded (peak {peak(found_d)}); T1 first, T2 second -- I8a, I10, I20")
    else:
        failures.append(f"  ✗ (a) two members, a member's two tasks  {duo.returncode}/{second_task.returncode} "
                        f"d2={d2_done} both={both} t1={[one['id'] for one in d_t1]} "
                        f"t2={[(one['id'], one.get('run')) for one in d_t2]} d1_term={terminal_of(found_d, 'd1')} "
                        f"keys={keys_d} devs={ {k: (v['id'], v.get('run')) for k, v in devs_d.items()} } "
                        f"first_dev_end={first_dev_end} peak={peak(found_d)} "
                        f"results={result_of(found_d, 'T1')!r}/{result_of(found_d, 'T2')!r} {second_task.stderr[-200:]!r}")

    # --- (c) the cursor of the run [34] -- I8b ----------------------------------------------------------
    d_prompts = h.prompts_of("d")
    wake_t2 = next((one for one in d_prompts if re.search(r"^#\d+ do from house on T2:", one, re.M)), "")
    resume_t1 = next((one for one in d_prompts if "done from d1 on T1" in one), "")
    items_t2, _, since_t2, _ = T.shared_in(wake_t2)
    items_t1, _, since_t1, _ = T.shared_in(resume_t1)
    named_t2, named_t1 = [one[0] for one in items_t2], [one[0] for one in items_t1]
    if (wake_t2 and resume_t1 and d_t1 and d_t2
            and named_t2 == ["d2"] and since_t2 == d_t1[0]["id"]
            and named_t1 == ["d1"] and since_t1 == d_t2[0]["id"]):
        held("(c) the cursor of the member's run", f"d's wake-up on T2 names {named_t2} since its run's opening "
             f"(#{since_t2}); its resume on T1 names {named_t1} alone since its wake-up on T2 (#{since_t1}): "
             "what its run already read is never named twice -- I8b")
    else:
        failures.append(f"  ✗ (c) cursor of the run       t2={named_t2}/{since_t2} t1={named_t1}/{since_t1} "
                        f"intents={[one['id'] for one in d_t1]}/{[one['id'] for one in d_t2]} "
                        f"{wake_t2[-300:]!r} {resume_t1[-300:]!r}")
    return 0
