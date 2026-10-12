"""Scenario `team-member-parallel` -- 1 case(s) (batch le-tick, rework: the members, team 0.13.1;
split out of `team-review` by les-scenarios-par-maison, 2026-10-07): one wake-up at a time per
member, the parallel between members.
- (o) one wake-up at a time per member [49] (I19, I20): tv1 tv2 tv3 of agents/trio launched together, three
  runs, three sessions; tl's `do` on T2 to tv1 while tv1 plays T1 waits, and arrives in tv1's run at its
  next wake-up; never two wake-ups of tv1 at once, no `run-busy`
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "tl": {"T1": [{"sleep": 0.2, "body": {"do": ["tv1", "tv2", "tv3"]}},
                      {"sleep": 0.1, "body": {"done": "T1 by three"}}],
               "T2": [{"sleep": 0.1, "body": {"do": ["tv1"]}},
                      {"sleep": 0.1, "body": {"done": "T2 by tv1"}}]},
        "tv1": {"T1": [{"sleep": 6.0, "body": {"done": True}}],   # long enough to be playing when T2 comes
                "T2": [{"sleep": 0.2, "body": {"done": True}}]},
        "tv2": [{"sleep": 1.0, "body": {"done": True}}],
        "tv3": [{"sleep": 1.0, "body": {"done": True}}]})
    by_kind, all_ended, intents_on, result_of, runs_launched = (
        T.by_kind, T.all_ended, T.intents_on, T.result_of, T.runs_launched)

    # --- (o) one wake-up at a time per member, the parallel between members [49] -- I19, I20 ------------
    h.declare("trio", "---\nagents: |\n  tl agents/lead3\n  tv1 agents/trio\n  tv2 agents/trio\n  tv3 agents/trio\n"
                      "reports: |\n  tv1 tv2 tv3 -> tl\nroot: tl\nschedule: off\n---\nThree members on one agent.\n")
    trio = h.call("team", "start", "trio", "--message", "review PR 60", *h.harnessed)
    three = h.settled("trio", lambda found: len([one for one in by_kind(found, "wake-launched")
                                                 if one.get("agent") in ("tv1", "tv2", "tv3")]) == 3, timeout=60)
    trio2 = h.call("team", "post", "trio", "--to", "tl", "--message", "review PR 61")
    done_o = h.settled("trio", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=90)
    time.sleep(0.5)
    found_o = h.events("trio")
    tv_launched = {one.get("agent"): one for one in by_kind(found_o, "wake-launched")
                   if one.get("agent") in ("tv1", "tv2", "tv3") and one.get("tag") in
                   {i["tag"] for i in by_kind(found_o, "wake-intent") if i.get("task") == "T1"}}
    first_tv_end = min((one["id"] for one in by_kind(found_o, "wake-ended") if one.get("agent") in ("tv1", "tv2", "tv3")),
                       default=0)
    tv1_t1_end = next((one["id"] for one in by_kind(found_o, "wake-ended", agent="tv1")), 10 ** 9)
    tv1_t2 = intents_on(found_o, "tv1", "T2")
    do_t2 = next((one["id"] for one in by_kind(found_o, "post", verb="do") if one.get("task") == "T2"
                  and one.get("to") == "tv1"), 10 ** 9)
    open_tv1, twice = set(), False
    for one in found_o:                               # never two wake-ups of tv1 without an end
        if one.get("kind") == "wake-intent" and one.get("agent") == "tv1":
            twice = twice or bool(open_tv1)
            open_tv1.add(one["tag"])
        elif one.get("kind") in ("wake-ended", "wake-failed", "wake-killed"):
            open_tv1.discard(one.get("tag"))
    busy_o = [one for one in by_kind(found_o, "wake-failed") if "run-busy" in str(one.get("reason"))]
    keys_o = {member: runs_launched(found_o, member) for member in ("tv1", "tv2", "tv3")}
    if (trio.returncode == 0 and three and trio2.returncode == 0 and done_o
            and set(tv_launched) == {"tv1", "tv2", "tv3"} and all(one["id"] < first_tv_end for one in tv_launched.values())
            and all(len(keys) == 1 for keys in keys_o.values())
            and len(set().union(*keys_o.values())) == 3
            and len({session for _, session in h.sessions_at("agents/trio")}) == 3
            and do_t2 < tv1_t1_end and len(tv1_t2) == 1 and tv1_t2[0]["id"] > tv1_t1_end
            and tv1_t2[0].get("run") in keys_o["tv1"] and not twice and not busy_o
            and result_of(found_o, "T1") == "T1 by three" and result_of(found_o, "T2") == "T2 by tv1"):
        held("(o) one wake-up at a time per member", "tv1 tv2 tv3 of agents/trio launched together, three runs, "
             f"three sessions; tl's do on T2 to tv1 (#{do_t2}) while tv1 plays T1 waits, and arrives in tv1's run "
             f"after its end (#{tv1_t1_end}); never two wake-ups of tv1, no run-busy -- I19, I20")
    else:
        failures.append(f"  ✗ (o) one wake-up per member  {trio.returncode}/{trio2.returncode} three={three} done={done_o} "
                        f"launched={ {k: v['id'] for k, v in tv_launched.items()} } first_end={first_tv_end} "
                        f"keys={keys_o} sessions={h.sessions_at('agents/trio')} do_t2={do_t2} tv1_end={tv1_t1_end} "
                        f"tv1_t2={[(one['id'], one.get('run')) for one in tv1_t2]} twice={twice} busy={len(busy_o)} "
                        f"results={result_of(found_o, 'T1')!r}/{result_of(found_o, 'T2')!r}")
    return 0
