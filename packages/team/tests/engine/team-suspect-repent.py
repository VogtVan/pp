"""Scenario `team-suspect-repent` -- 2 case(s) (cut out of `team-suspect`, rule 10): a suspected member that answers
its try REPENTS, and is tolerated one silent retry more. Two teams play side by side in one house, each on its own
clock, both under `retries: 1`: `repent` (p1, p2) and `lone` (q alone, its root, the owner's tasks its own).
- (a) the try answers, it repents: p2 dies twice on T1 and is suspected; `PP_NOW` past its interval, T2's `do`
  wakes it -- its try -- and it answers; the suspicion ends: p1's head says the health line while p2 is suspected,
  and nothing once p2 answered
- (b) one silent retry more: q dies twice on T1 and is suspected; past its interval the tick tries it on the
  opening it owes, it answers and repents (`repents` 1 at the face); on T2 q dies three times -- under `retries: 1`
  its tolerance is now two silent retries, the third failure alone is final
"""
from __future__ import annotations

import threading

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "p1": {task: [{"sleep": 0.1, "body": {"do": ["p2"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": f"{task} done"}}]
               for task in ("T1", "T2")},
        "p2": {"T1": [T.DEATH, T.DEATH], "T2": [{"sleep": 0.1, "body": {"re": "DO", "text": "back"}}]},
        "q": {"T1": [T.DEATH, T.DEATH, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}],
              "T2": [T.DEATH, T.DEATH, T.DEATH]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    closed = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)
    fallen = lambda member, task: lambda found: (any(one.get("task") == task for one in T.finals_of(found, member))
                                                 and all_ended(found))
    health_line = T.health_pattern(h.module())

    # --- both teams started at once, then each plays its own chain on its own clock, side by side ----------------
    h.declare("repent", T.SUSPECT_PAIR.format(a="p1", b="p2"))
    h.declare("lone", "---\nagents: |\n  q agents/q\nroot: q\nretries: 1\nschedule: off\n---\nHold the task.\n")
    started = h.call("team", "start", "repent", "--message", "build it", *h.harnessed)
    started_q = h.call("team", "start", "lone", "--message", "build it", *h.harnessed)
    seen: dict = {}

    def repent_played() -> None:
        """p2 falls on T1; past its interval T2's do is its try, which answers."""
        T.ticked(h, [("repent", closed("T1"), None)])
        seen["first"] = T.finals_of(h.events("repent"), "p2")
        later = T.local_after(seen["first"][0]["at"], 6).isoformat(timespec="seconds") if seen["first"] else None
        seen["posted"] = h.call("team", "post", "repent", "--message", "second part", now=later)
        T.ticked(h, [("repent", closed("T2"), later)])

    def lone_played() -> None:
        """q falls on T1; past its interval the tick tries it on its opening, which it answers; then T2, three deaths."""
        T.ticked(h, [("lone", fallen("q", "T1"), None)])
        seen["first_q"] = T.finals_of(h.events("lone"), "q")
        later = T.local_after(seen["first_q"][0]["at"], 6).isoformat(timespec="seconds") if seen["first_q"] else None
        T.ticked(h, [("lone", closed("T1"), later)])
        seen["repented"] = next((one.get("health") for one in h.face("lone", now=later).get("members") or []
                                 if one.get("member") == "q"), None) or {}
        seen["posted_q"] = h.call("team", "post", "lone", "--message", "second part", now=later)
        T.ticked(h, [("lone", fallen("q", "T2"), later)])

    chains = [threading.Thread(target=one) for one in (repent_played, lone_played)]
    for one in chains:
        one.start()
    for one in chains:
        one.join()
    first, posted = seen.get("first") or [], seen.get("posted")
    first_q, posted_q, repented = seen.get("first_q") or [], seen.get("posted_q"), seen.get("repented") or {}
    found = h.events("repent")
    heads = [health_line.findall(one) for one in h.prompts_of("p1")]
    found_q = h.events("lone")

    # --- (a) the try answers: the suspicion ends --------------------------------------------------------------
    answered = [one for one in by_kind(found, "post", verb="re", **{"from": "p2"}) if one.get("task") == "T2"]
    if (started.returncode == 0 and posted is not None and posted.returncode == 0 and len(first) == 1
            and len(answered) == 1
            and answered[0].get("by") is None and answered[0].get("text") == "back"
            and result_of(found, "T2") == "T2 done" and len(heads) == 4
            and heads[1] and heads[2] and heads[0] == [] and heads[3] == []):
        held("(a) the try answers, it repents", "p2 fell on T1; past its interval T2's do is its try, it answers 'back'; "
             "p1's heads: the health line while p2 is suspected, none once it answered")
    else:
        failures.append(f"  ✗ (a) the try answers         rc={started.returncode}/{posted and posted.returncode} finals={len(first)} "
                        f"answered={[(one.get('by'), one.get('text')) for one in answered]} "
                        f"result={result_of(found, 'T2')!r} heads={heads}")

    # --- (b) its tolerance: one silent retry more ---------------------------------------------------------------
    deaths = [one.get("final") for one in by_kind(found_q, "wake-failed", agent="q") if one.get("task") == "T2"]
    if (started_q.returncode == 0 and posted_q is not None and posted_q.returncode == 0 and len(first_q) == 1
            and result_of(found_q, "T1") == "recovered" and repented.get("repents") == 1
            and repented.get("suspected") is False and deaths == [False, False, True]):
        held("(b) one silent retry more", "q fell on T1, answered its try and repented (repents 1); on T2 q dies three "
             "times: two silent retries (retries: 1 + one repentance), the third failure final")
    else:
        failures.append(f"  ✗ (b) one silent retry more    rc={started_q.returncode}/{posted_q and posted_q.returncode} "
                        f"finals={len(first_q)} t1={result_of(found_q, 'T1')!r} health={repented} deaths={deaths}")
    return 0
