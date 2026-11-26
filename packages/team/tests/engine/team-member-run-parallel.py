"""Scenario `team-member-run-parallel` -- 2 cases: one wake-up at a time per member, the members of one agent in
parallel, each task of a member in its own run.
- (o) one wake-up at a time per member: tv1 tv2 tv3 of agents/trio launch together, three runs, three sessions;
  tl's `do` on T2 to tv1 while tv1 plays T1 waits, and OPENS tv1's run for T2 once T1's wake-up ended; never two
  wake-ups of tv1 at once, no `run-busy`
- (p) a run stands per (member, task) (batch la-continuation-par-tache, s.1401): tw, whose entry cuts two acts by a
  `§`, opens T1 then T2 and stands on both, one run each; its run on T1 is continued first (the tasks' order,
  `[nothing new]`, `messages: []`), answers and parks -- (tw, T2) still stands, and the tick after continues T2
  the same way: four launches, both tasks done, no relance
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    gate_three, gate_tv1 = bench.temp() / "three-launched", bench.temp() / "t2-routed"
    h = T.House(bench, script={
        # (o) three members on one agent; tv1 still plays T1 when T2 comes
        "tl": {"T1": [{"sleep": 0.2, "body": {"do": ["tv1", "tv2", "tv3"]}},
                      {"sleep": 0.1, "body": {"done": "T1 by three"}}],
               "T2": [{"sleep": 0.1, "body": {"do": ["tv1"]}},
                      {"sleep": 0.1, "body": {"done": "T2 by tv1"}}]},
        "tv1": {"T1": [{"words": [{"gate": str(gate_tv1)}, {"done": True}]}],   # playing T1 until T2's do is routed
                "T2": [{"sleep": 0.2, "body": {"done": True}}]},
        "tv2": [{"words": [{"gate": str(gate_three)}, {"done": True}]}],        # playing until the three are launched
        "tv3": [{"words": [{"gate": str(gate_three)}, {"done": True}]}],
        # (p) tw says an info and stands on each task, then answers it on its continuation
        "tw": {"T1": [{"sleep": 0.1, "body": {"info": {"to": "house", "text": "T1 under way"}}},
                      {"sleep": 0.1, "body": {"re": "DO", "text": "T1 by tw"}}],
               "T2": [{"sleep": 0.1, "body": {"info": {"to": "house", "text": "T2 under way"}}},
                      {"sleep": 0.1, "body": {"re": "DO", "text": "T2 by tw"}}]}})
    by_kind, all_ended, intents_on, result_of, runs_launched = (
        T.by_kind, T.all_ended, T.intents_on, T.result_of, T.runs_launched)

    h.declare("trio", "---\nagents: |\n  tl agents/lead3\n  tv1 agents/trio\n  tv2 agents/trio\n  tv3 agents/trio\n"
                      "reports: |\n  tv1 tv2 tv3 -> tl\nroot: tl\nschedule: off\n---\nThree members on one agent.\n")
    trio = h.call("team", "start", "trio", "--message", "review PR 60", *h.harnessed)
    three = h.settled("trio", lambda found: len([one for one in by_kind(found, "wake-launched")
                                                 if one.get("agent") in ("tv1", "tv2", "tv3")]) == 3, timeout=60)
    gate_three.write_text("open", encoding="utf-8")
    trio2 = h.call("team", "post", "trio", "--to", "tl", "--message", "review PR 61")
    # (p) both openings stand before the first tick: tw opens T1, then T2
    h.declare("twice", "---\nagents: |\n  tw agents/tw\nroot: tw\nentries: |\n  do -> ACTS.md\nschedule: off\n---\n"
                       "One member, two tasks, each in its own run.\n")
    (h.teams / "twice" / "ACTS.md").write_text("---\nproc: |\n  INFER\n  §\n  INFER\noutput: team-act\n---\n"
                                              "# ACTS\n\nSay one act at each step.\n", encoding="utf-8")
    two_tasks = [h.call("team", "start", "twice", "--message", "part one", *h.harnessed, "--no-tick"),
                 h.call("team", "post", "twice", "--to", "tw", "--message", "part two", "--no-tick"),
                 h.call("team", "tick", "twice")]
    routed = h.settled("trio", lambda found: any(one.get("task") == "T2" and one.get("to") == "tv1"
                                                 for one in by_kind(found, "post", verb="do")), timeout=90)
    gate_tv1.write_text("open", encoding="utf-8")           # tv1 played T1 through the opening of `twice`
    # --- (o) one wake-up at a time per member, the parallel between members ------------------------------
    done_o = h.settled("trio", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=90)
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
    if (trio.returncode == 0 and three and trio2.returncode == 0 and routed and done_o
            and set(tv_launched) == {"tv1", "tv2", "tv3"} and all(one["id"] < first_tv_end for one in tv_launched.values())
            and len(keys_o["tv1"]) == 2 and len(keys_o["tv2"]) == len(keys_o["tv3"]) == 1
            and len(set().union(*keys_o.values())) == 4
            and len({session for _, session in h.sessions_at("agents/trio")}) == 4
            and do_t2 < tv1_t1_end and len(tv1_t2) == 1 and tv1_t2[0]["id"] > tv1_t1_end
            and tv1_t2[0].get("run") is None and not twice and not busy_o
            and result_of(found_o, "T1") == "T1 by three" and result_of(found_o, "T2") == "T2 by tv1"):
        held("(o) one wake-up at a time per member", "tv1 tv2 tv3 of agents/trio launched together, three runs, "
             f"three sessions; tl's do on T2 to tv1 (#{do_t2}) while tv1 plays T1 waits, and opens tv1's run for T2 "
             f"after its end (#{tv1_t1_end}); never two wake-ups of tv1, no run-busy")
    else:
        failures.append(f"  ✗ (o) one wake-up per member  {trio.returncode}/{trio2.returncode} three={three} "
                        f"routed={routed} done={done_o} "
                        f"launched={ {k: v['id'] for k, v in tv_launched.items()} } first_end={first_tv_end} "
                        f"keys={keys_o} sessions={h.sessions_at('agents/trio')} do_t2={do_t2} tv1_end={tv1_t1_end} "
                        f"tv1_t2={[(one['id'], one.get('run')) for one in tv1_t2]} twice={twice} busy={len(busy_o)} "
                        f"results={result_of(found_o, 'T1')!r}/{result_of(found_o, 'T2')!r}")

    # --- (p) a run stands per (member, task): the park of T1 leaves T2 standing ------------------------------
    done_p = h.settled("twice", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=40)
    found_p = h.events("twice")
    tw = [(one.get("task"), one.get("messages"), one.get("relance")) for one in T.intents_of(found_p, "tw")]
    ends_p = [(intent.get("task"), one.get("state")) for one in by_kind(found_p, "wake-ended", agent="tw")
              for intent in by_kind(found_p, "wake-intent") if intent.get("tag") == one.get("tag")]
    end_t1 = next((one["id"] for one in by_kind(found_p, "wake-ended", agent="tw")
                   if one.get("state") == "parked"), 10 ** 9)
    t2_on = [one["id"] for one in intents_on(found_p, "tw", "T2")]
    if (all(one.returncode == 0 for one in two_tasks) and done_p and len(tw) == 4
            and [(task, bool(box), why) for task, box, why in tw]
            == [("T1", True, None), ("T2", True, None), ("T1", False, None), ("T2", False, None)]
            and ends_p == [("T1", "standing"), ("T2", "standing"), ("T1", "parked"), ("T2", "parked")]
            and len(t2_on) == 2 and t2_on[1] > end_t1 and len(runs_launched(found_p, "tw")) == 2
            and result_of(found_p, "T1") == "T1 by tw" and result_of(found_p, "T2") == "T2 by tw"):
        held("(p) a run stands per (member, task)", "tw stands on T1 and on T2, one run each; T1 continued first "
             f"(nothing delivered), it answers and parks (#{end_t1}); (tw, T2) still stands and is continued at the "
             "tick after: four launches, both tasks done, no relance")
    else:
        failures.append(f"  ✗ (p) a run per (member, task)  rc={[one.returncode for one in two_tasks]} done={done_p} "
                        f"intents={tw} ends={ends_p} parked={end_t1} t2={t2_on} runs={runs_launched(found_p, 'tw')} "
                        f"results={result_of(found_p, 'T1')!r}/{result_of(found_p, 'T2')!r}")
    return 0
