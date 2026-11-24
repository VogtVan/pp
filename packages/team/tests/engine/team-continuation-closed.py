"""Scenario `team-continuation-closed` -- 1 case(s): the old runs that stand on closed tasks (s.1409, the loop of
2026-11-08: twelve runs continued without end, an open task starved); cut from `team-continuation` by rule 10.
- (d) old runs standing on closed tasks get ONE continuation each (s.1409, the loop of 2026-11-08): oa's entry cuts
  FIVE acts; it closes T1 in its first, then T2 in another run, and stands on both; each run is continued once
  under CLOSED_HEAD, stands still, and is held as parked -- no launch more; T3, posted to ob under `parallel: 1`
  while they stand, is served after two continuations at most
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")

FIVE = ("---\nproc: |\n  INFER\n  §\n  INFER\n  §\n  INFER\n  §\n  INFER\n  §\n  INFER\noutput: team-act\n---\n"
        "# FIVE\n\nSay one act at each step.\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # oa closes T1 then T2 in its first act of each and stands, four acts left; ob closes T3 the same way
        "oa": {"T1": [{"sleep": 0.1, "body": {"re": "DO", "text": "T1 closed"}}] + [{"sleep": 0.1, "body": "prose"}] * 4,
               "T2": [{"sleep": 0.1, "body": {"re": "DO", "text": "T2 closed"}}] + [{"sleep": 0.1, "body": "prose"}] * 4},
        "ob": [{"sleep": 0.1, "body": {"re": "DO", "text": "T3 closed"}}] + [{"sleep": 0.1, "body": "prose"}] * 4})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    h.declare("olds", "---\nagents: |\n  oa agents/oa\n  ob agents/ob\nreports: |\n  ob -> oa\nroot: oa\n"
                      "entries: |\n  do -> FIVE.md\nparallel: 1\nschedule: off\n---\nClose first, then go on.\n")
    (h.teams / "olds" / "FIVE.md").write_text(FIVE, encoding="utf-8")
    olds = h.call("team", "start", "olds", "--message", "close the first", *h.harnessed)

    # --- old runs standing on closed tasks get one continuation each -------------------------------------------
    closed_1 = h.settled("olds", lambda found: bool(by_kind(found, "done", task="T1")), timeout=40)
    second = h.call("team", "post", "olds", "--to", "oa", "--message", "close the second")
    closed_2 = h.settled("olds", lambda found: bool(by_kind(found, "done", task="T2")), timeout=40)
    third = h.call("team", "post", "olds", "--to", "ob", "--message", "close the third")
    served = h.settled("olds", lambda found: bool(by_kind(found, "done", task="T3")) and all_ended(found)
                       and len(T.intents_of(found, "ob")) >= 2, timeout=90)
    ticks_d = [h.call("team", "tick", "olds") for _ in range(2)]
    h.settled("olds", all_ended, timeout=30)
    found_d = h.events("olds")
    done_at = {task: next((one["id"] for one in by_kind(found_d, "done", task=task)), 10 ** 9) for task in ("T1", "T2", "T3")}
    after = {(agent, task): [one for one in T.intents_of(found_d, agent)
                             if one.get("task") == task and one["id"] > done_at[task]]
             for agent, task in (("oa", "T1"), ("oa", "T2"), ("ob", "T3"))}
    ends_d = {one.get("tag"): one.get("state") for one in by_kind(found_d, "wake-ended")}
    posted_3 = next((one["id"] for one in found_d if one.get("kind") == "task" and one.get("task") == "T3"), 10 ** 9)
    first_ob = next((one["id"] for one in T.intents_of(found_d, "ob")), 10 ** 9)
    late = [one["id"] for one in T.intents_of(found_d, "oa") if posted_3 < one["id"] < first_ob]
    if (olds.returncode == 0 and closed_1 and second.returncode == 0 and closed_2 and third.returncode == 0 and served
            and all(one.returncode == 0 for one in ticks_d)
            and [len(one) for one in after.values()] == [1, 1, 1]
            and all(not one[0].get("messages") and ends_d.get(one[0]["tag"]) == "standing" for one in after.values())
            and len(late) <= 2 and result_of(found_d, "T3") == "T3 closed"):
        held("(d) old runs on closed tasks get one continuation", "oa stands on T1 and on T2, both closed: one "
             f"continuation each (#{after[('oa', 'T1')][0]['id']}, #{after[('oa', 'T2')][0]['id']}), each standing "
             f"still and held as parked; T3 served after {len(late)} launch(es) of oa; ob's run the same; no launch "
             "more through 2 ticks")
    else:
        failures.append(f"  ✗ (d) old runs on closed tasks  rc={olds.returncode}/{second.returncode}/{third.returncode} "
                        f"closed={closed_1}/{closed_2} served={served} "
                        f"continuations={ {key: [(one['id'], ends_d.get(one['tag'])) for one in value] for key, value in after.items()} } "
                        f"late={late} result={result_of(found_d, 'T3')!r}")
    return 0
