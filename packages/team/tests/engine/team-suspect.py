"""Scenario `team-suspect` -- 5 case(s): a member whose final failure stands is SUSPECTED -- the tick's failure
detector ◇P --, and a suspected member that answers its try REPENTS. Two teams play side by side in one house, each
on its own clock: `pair` (r1, r2) and `repent` (p1, p2), both under `retries: 1`.
- (a) answered at once: r2 dies twice on r1's `do` (T1), the tick answers in its place; on T2 r1 asks r2 during
  r2's interval -- the tick answers the ask at once (`re` to the ask, `by: tick`, `suspected`), the face's
  `health.tried_at` the hour of r2's final failure plus the calendar's base, 5 min; no wake-up of r2; r1 closes T2
- (b) the try and the interval doubled: `PP_NOW` past the interval, T3's `do` to r2 wakes it -- its try --, it dies
  once and its failure is final at once (no silent retry for a suspected member); the next interval is the double
- (c) the health view: while r2 is suspected, the head of r1's wake-ups says `[not answering at the moment: r2 --
  tried again at HH:MM]` -- the first interval's hour on T1 and T2, the doubled one on T3
- (a) the try answers, it repents: p2 dies twice on T1 and is suspected; `PP_NOW` past its interval, T2's `do`
  wakes it -- its try -- and it answers; the suspicion ends: p1's head says the health line while p2 is suspected,
  and nothing once p2 answered
- (b) one silent retry more: on T3 p2 dies three times -- under `retries: 1` its tolerance is now two silent
  retries, the third failure alone is final
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")

DEATH = {"sleep": 0.1, "body": "crash"}
DECLARED = ("---\nagents: |\n  {a} agents/{a}\n  {b} agents/{b}\nreports: |\n  {b} -> {a}\nroot: {a}\nretries: 1\n"
            "schedule: off\n---\nSplit the work, report.\n")


def ticked(h, waits: list[tuple], timeout: float = 40.0) -> None:
    """Ticks every team named, side by side, until its journal satisfies its predicate -- `waits` as (team,
    predicate, now), each team on its own clock."""
    deadline = time.monotonic() + timeout
    pending = list(waits)
    with ThreadPoolExecutor(max_workers=len(waits)) as pool:
        while time.monotonic() < deadline:
            pending = [one for one in pending if not one[1](h.events(one[0]))]
            if not pending:
                return
            time.sleep(0.3)
            list(pool.map(lambda one: h.call("team", "tick", one[0], now=one[2]), pending))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "r1": {"T1": [{"sleep": 0.1, "body": {"do": ["r2"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": "t1 done"}}],
               "T2": [{"sleep": 0.1, "body": {"ask": {"to": "r2", "text": "your part?"}}},
                      {"sleep": 0.1, "body": {"re": "DO", "text": "t2 done"}}],
               "T3": [{"sleep": 0.1, "body": {"do": ["r2"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": "t3 done"}}]},
        "r2": {"T1": [DEATH, DEATH], "T3": [DEATH]},
        "p1": {task: [{"sleep": 0.1, "body": {"do": ["p2"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": f"{task} done"}}]
               for task in ("T1", "T2", "T3")},
        "p2": {"T1": [DEATH, DEATH], "T2": [{"sleep": 0.1, "body": {"re": "DO", "text": "back"}}],
               "T3": [DEATH, DEATH, DEATH]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    closed = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)

    # --- both teams started at once, then each task played on both, each team on its own clock -----------------
    health_line = T.health_pattern(h.module())
    h.declare("pair", DECLARED.format(a="r1", b="r2"))
    h.declare("repent", DECLARED.format(a="p1", b="p2"))
    started = h.call("team", "start", "pair", "--message", "build it", *h.harnessed)
    started_r = h.call("team", "start", "repent", "--message", "build it", *h.harnessed)
    ticked(h, [("pair", closed("T1"), None), ("repent", closed("T1"), None)])
    first = T.finals_of(h.events("pair"), "r2")
    hour = T.local_after(first[0]["at"], 5).strftime("%H:%M") if first else "?"
    later = T.local_after(first[0]["at"], 6).isoformat(timespec="seconds") if first else None
    first_r = T.finals_of(h.events("repent"), "p2")
    later_r = T.local_after(first_r[0]["at"], 6).isoformat(timespec="seconds") if first_r else None

    posted = h.call("team", "post", "pair", "--message", "second part")
    posted_r = h.call("team", "post", "repent", "--message", "second part", now=later_r)
    ticked(h, [("pair", closed("T2"), None), ("repent", closed("T2"), later_r)])
    found_t2 = h.events("pair")
    face_t2 = h.face("pair")
    found_r_t2 = h.events("repent")
    heads_r_t2 = [health_line.findall(one) for one in h.prompts_of("p1")]

    posted_3 = h.call("team", "post", "pair", "--message", "third part", now=later)
    posted_r3 = h.call("team", "post", "repent", "--message", "third part", now=later_r)
    ticked(h, [("pair", closed("T3"), later), ("repent", closed("T3"), later_r)])
    found = h.events("pair")
    found_r = h.events("repent")

    # --- (a) a message to a suspected member answered at once, no wake-up -------------------------------------
    ask = next((one for one in by_kind(found_t2, "post", verb="ask") if one.get("task") == "T2"), {})
    at_once = [one for one in by_kind(found_t2, "post", verb="re", **{"from": "r2"}) if one.get("task") == "T2"]
    r2_on_t2 = T.intents_on(found_t2, "r2", "T2")
    health = next((one.get("health") for one in face_t2.get("members") or [] if one.get("member") == "r2"), None) or {}
    if (started.returncode == 0 and posted.returncode == 0 and len(first) == 1 and len(at_once) == 1
            and at_once[0].get("re") == ask.get("id") and at_once[0].get("by") == "tick"
            and at_once[0].get("suspected") is True and at_once[0].get("to") == "r1"
            and health.get("suspected") is True and str(health.get("tried_at"))[-5:] == hour
            and not r2_on_t2 and result_of(found_t2, "T2") == "t2 done"):
        held("(a) answered at once", f"r2 fell on T1; r1's ask #{ask.get('id')} on T2 answered by the tick at once "
             f"(suspected, tried again at {health.get('tried_at')}), no wake-up of r2; T2 't2 done'")
    else:
        failures.append(f"  ✗ (a) answered at once         rc={started.returncode}/{posted.returncode} finals={len(first)} "
                        f"ask={ask.get('id')} at_once={[(one.get('re'), one.get('by'), one.get('suspected'), one.get('to')) for one in at_once]} "
                        f"health={health} r2_on_t2={len(r2_on_t2)} result={result_of(found_t2, 'T2')!r} hour={hour}")

    # --- (b) the try after the interval, final at once, the interval doubled ----------------------------------
    tried = T.intents_on(found, "r2", "T3")
    second = [one for one in T.finals_of(found, "r2") if one.get("task") == "T3"]
    doubled = T.local_after(second[0]["at"], 10).strftime("%H:%M") if second else "?"
    if (posted_3.returncode == 0 and len(tried) == 1 and len(second) == 1
            and not [one for one in by_kind(found, "wake-failed", agent="r2", task="T3") if not one.get("final")]
            and result_of(found, "T3") == "t3 done"):
        held("(b) the try, the interval doubled", f"PP_NOW past {hour}: T3's do wakes r2 once -- its try --, it dies and "
             f"its failure is final at once; tried again at {doubled} (2 x 5 min); T3 't3 done'")
    else:
        failures.append(f"  ✗ (b) the try                  rc={posted_3.returncode} tried={len(tried)} second={len(second)} "
                        f"result={result_of(found, 'T3')!r} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found]}")

    # --- (c) the health view in r1's heads ---------------------------------------------------------------------
    heads = [health_line.findall(one) for one in h.prompts_of("r1")]
    expected = [[], [("r2", hour)], [("r2", hour)], [("r2", hour)], [("r2", hour)], [("r2", doubled)]]
    if heads == expected:
        held("(c) the health view", f"r1's heads: none before r2 fell, then 'r2 -- tried again at {hour}' on T1 and T2 "
             f"and T3's opening, 'at {doubled}' after its try failed")
    else:
        failures.append(f"  ✗ (c) the health view          heads={heads} expected={expected}")

    # --- (a) the try answers: the suspicion ends --------------------------------------------------------------
    answered = [one for one in by_kind(found_r_t2, "post", verb="re", **{"from": "p2"}) if one.get("task") == "T2"]
    if (started_r.returncode == 0 and posted_r.returncode == 0 and len(first_r) == 1 and len(answered) == 1
            and answered[0].get("by") is None and answered[0].get("text") == "back"
            and result_of(found_r_t2, "T2") == "T2 done" and len(heads_r_t2) == 4
            and heads_r_t2[1] and heads_r_t2[2] and heads_r_t2[0] == [] and heads_r_t2[3] == []):
        held("(a) the try answers, it repents", "p2 fell on T1; past its interval T2's do is its try, it answers 'back'; "
             "p1's heads: the health line while p2 is suspected, none once it answered")
    else:
        failures.append(f"  ✗ (a) the try answers         rc={started_r.returncode}/{posted_r.returncode} finals={len(first_r)} "
                        f"answered={[(one.get('by'), one.get('text')) for one in answered]} "
                        f"result={result_of(found_r_t2, 'T2')!r} heads={heads_r_t2}")

    # --- (b) its tolerance: one silent retry more ---------------------------------------------------------------
    deaths = [one.get("final") for one in by_kind(found_r, "wake-failed", agent="p2") if one.get("task") == "T3"]
    if posted_r3.returncode == 0 and deaths == [False, False, True] and result_of(found_r, "T3") == "T3 done":
        held("(b) one silent retry more", "on T3 p2 dies three times: two silent retries (retries: 1 + one repentance), "
             "the third failure final; T3 'T3 done'")
    else:
        failures.append(f"  ✗ (b) one silent retry more    rc={posted_r3.returncode} deaths={deaths} "
                        f"result={result_of(found_r, 'T3')!r}")
    return 0
