"""Scenario `team-await-by-task` -- 1 case(s) (batch le-tick, rework, pass A, team 0.12.0; split
out of `team-review` by les-scenarios-par-maison, 2026-10-07): the witness scripted per task.
- (b) the await by task [34] (I14): aw answers on T1 `{"do": ["aw1", "aw2"], "await": {"any": 1}}`,
  then on T2 `{"do": ["aw3"]}`; aw woken on T1 at aw1's terminal, before aw2's and aw3's; its wait on
  T2 whole -- woken on T2 after aw3's terminal alone; the await on T1 never held T2
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "aw": {"T1": [{"sleep": 0.2, "body": {"do": ["aw1", "aw2"], "await": {"any": 1}}},
                      {"sleep": 0.2, "body": {"done": "T1 by the first"}}],
               "T2": [{"sleep": 0.2, "body": {"do": ["aw3"]}},
                      {"sleep": 0.2, "body": {"done": "T2 by aw3"}}]},
        "aw1": [{"sleep": 3.0, "body": {"done": True}}],
        "aw2": [{"sleep": 9.0, "body": {"done": True}}],
        "aw3": [{"sleep": 5.0, "body": {"done": True}}]})
    by_kind, all_ended, intents_on, terminal_of, result_of = T.by_kind, T.all_ended, T.intents_on, T.terminal_of, T.result_of

    # --- (b) the await by task [34] -- I14 ------------------------------------------------------------
    h.declare("awaits", "---\nagents: |\n  aw aw\n  aw1 aw1\n  aw2 aw2\n  aw3 aw3\n"
                        "reports: |\n  aw1 aw2 aw3 -> aw\nroot: aw\nschedule: off\n---\nTwo waits, one per task.\n")
    awaits = h.call("team", "start", "awaits", "--message", "review PR 9", *h.harnessed)
    aw_ended = h.settled("awaits", lambda found: bool(by_kind(found, "wake-ended", agent="aw")), timeout=60)
    aw_second = h.call("team", "post", "awaits", "--to", "aw", "--message", "review PR 10")
    aw_done = h.settled("awaits", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=120)
    time.sleep(0.5)
    found_a = h.events("awaits")
    aw_t1, aw_t2 = intents_on(found_a, "aw", "T1"), intents_on(found_a, "aw", "T2")
    term = {one: terminal_of(found_a, one) for one in ("aw1", "aw2", "aw3")}
    met = sorted(str(one.get("task")) for one in by_kind(found_a, "wait-met", agent="aw"))
    waits_a = by_kind(found_a, "wait", agent="aw")
    if (awaits.returncode == 0 and aw_ended and aw_second.returncode == 0 and aw_done
            and len(aw_t1) == 2 and len(aw_t2) == 2
            and aw_t2[0]["id"] < term["aw1"]
            and term["aw1"] < aw_t1[1]["id"] < min(term["aw2"], term["aw3"])
            and aw_t2[1]["id"] > term["aw3"]
            and len(waits_a) == 1 and waits_a[0].get("task") == "T1" and waits_a[0].get("any") == 1
            and met == ["T1", "T2"]
            and result_of(found_a, "T1") == "T1 by the first" and result_of(found_a, "T2") == "T2 by aw3"):
        held("(b) the await by task", f"aw opened T2 (#{aw_t2[0]['id']}) under T1's await; woken on T1 "
             f"(#{aw_t1[1]['id']}) at aw1's terminal, before aw2's and aw3's; on T2 (#{aw_t2[1]['id']}) after "
             f"aw3's alone; wait-met {met} -- I14")
    else:
        failures.append(f"  ✗ (b) the await by task       {awaits.returncode}/{aw_second.returncode} ended={aw_ended} "
                        f"done={aw_done} t1={[one['id'] for one in aw_t1]} t2={[one['id'] for one in aw_t2]} "
                        f"term={term} met={met} waits={waits_a} results={result_of(found_a, 'T1')!r}/"
                        f"{result_of(found_a, 'T2')!r}")
    return 0
