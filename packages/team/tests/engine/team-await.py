"""Scenario `team-await` -- 2 case(s): the await of a delegation, met on its first answer and kept per task.
- `await any 1` departs from the delegation: a delegates to a1 a2 a3 with `{"await": {"any": 1}}`
  and is woken a second time before the answers of a2 and a3 -- `wait {any: 1}`, one `wait-met`,
  done T1, their answers posted after it (information); `{"await": {"any": 0}}` is
  `response-unreadable`
- (b) the await by task: aw answers on T1 `{"do": ["aw1", "aw2"], "await": {"any": 1}}`, then on
  T2 `{"do": ["aw3"]}`; aw is woken on T1 at aw1's terminal, before aw2's and aw3's; its wait on T2
  is whole -- woken on T2 after aw3's terminal alone; the await on T1 never holds T2
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "a": [{"sleep": 0.2, "body": {"do": ["a1", "a2", "a3"], "await": {"any": 1}}},
              {"sleep": 0.2, "body": {"done": "the first answer"}}],
        "a1": [{"sleep": 0.3, "body": {"done": True}}],
        "a2": [{"sleep": 2.5, "body": {"done": True}}],
        "a3": [{"sleep": 2.5, "body": {"done": True}}],
        "w": [{"sleep": 0.1, "body": {"do": ["w1"], "await": {"any": 0}}}],
        "aw": {"T1": [{"sleep": 0.2, "body": {"do": ["aw1", "aw2"], "await": {"any": 1}}},
                      {"sleep": 0.2, "body": {"done": "T1 by the first"}}],
               "T2": [{"sleep": 0.2, "body": {"do": ["aw3"]}},
                      {"sleep": 0.2, "body": {"done": "T2 by aw3"}}]},
        "aw1": [{"sleep": 6.0, "body": {"done": True}}],
        "aw2": [{"sleep": 12.0, "body": {"done": True}}],
        "aw3": [{"sleep": 8.0, "body": {"done": True}}]})
    by_kind, all_ended, intents_on, terminal_of, result_of = T.by_kind, T.all_ended, T.intents_on, T.terminal_of, T.result_of

    # --- every team declared and started at once: the longest (awaits) first ----------------------
    h.declare("awaits", "---\nagents: |\n  aw aw\n  aw1 aw1\n  aw2 aw2\n  aw3 aw3\n"
                        "reports: |\n  aw1 aw2 aw3 -> aw\nroot: aw\nschedule: off\n---\nTwo waits, one per task.\n")
    h.declare("any", "---\nagents: |\n  a a\n  a1 a1\n  a2 a2\n  a3 a3\n"
                     "reports: |\n  a1 a2 a3 -> a\nroot: a\n---\nThe first answer will do.\n")
    h.declare("badwait", "---\nagents: |\n  w w\n  w1 w1\nreports: |\n  w1 -> w\nroot: w\nretries: 0\n---\n")
    # aw's T2 must open under T1's await, before aw1 answers: both openings stand before the first tick, so the tick
    # that ends aw's T1 opening launches aw1, aw2 and aw on T2 together
    awaits = h.call("team", "start", "awaits", "--message", "review PR 9", *h.harnessed, "--no-tick")
    aw_second = h.call("team", "post", "awaits", "--to", "aw", "--message", "review PR 10", "--no-tick")
    aw_ended = h.call("team", "tick", "awaits").returncode == 0
    anyteam = h.call("team", "start", "any", "--message", "one answer is enough", *h.harnessed)
    badwait = h.call("team", "start", "badwait", "--message", "wait for none", *h.harnessed)

    # --- an agent departs from the delegation: await any 1 -----------------------------------------
    done_a = h.settled("any", lambda found: any(one.get("kind") == "done" for one in found) and all_ended(found)
                       and len(by_kind(found, "post", verb="re")) >= 4)
    failed_w = h.settled("badwait", lambda found: bool(by_kind(found, "wake-failed", final=True)), timeout=60)
    time.sleep(0.5)
    found = h.events("any")
    intents_a = by_kind(found, "wake-intent", agent="a")
    waits_a = by_kind(found, "wait", agent="a")
    met_a = by_kind(found, "wait-met", agent="a")
    late = [one["id"] for one in by_kind(found, "post", verb="re") if one.get("from") in ("a2", "a3")]
    fails_w = [(one.get("final"), str(one.get("reason"))) for one in by_kind(h.events("badwait"), "wake-failed")]
    if (anyteam.returncode == 0 and badwait.returncode == 0 and done_a and failed_w
            and len(intents_a) == 2 and len(waits_a) == 1 and waits_a[0].get("any") == 1
            and sorted(waits_a[0].get("to") or []) == ["a1", "a2", "a3"]
            and len(met_a) == 1 and len(late) == 2 and intents_a[1]["id"] < min(late)
            and by_kind(found, "done", task="T1") and by_kind(found, "done", task="T1")[0].get("result") == "the first answer"
            and len(fails_w) == 1 and fails_w[0][0] is True and fails_w[0][1].startswith("response-unreadable")
            and "await" in fails_w[0][1]):
        held("await any 1 departs from the delegation", f"a woken 2 times, the second (#{intents_a[1]['id']}) before the "
             f"answers of a2 a3 ({late}, information after the close); wait any 1, one wait-met; done T1; "
             "await any 0: response-unreadable")
    else:
        failures.append(f"  ✗ await any                   {anyteam.returncode}/{badwait.returncode} done={done_a} "
                        f"intents={[one['id'] for one in intents_a]} waits={waits_a} met={len(met_a)} late={late} "
                        f"fails_w={fails_w} {anyteam.stderr[-200:]!r}")

    # --- (b) the await by task -- I14 ------------------------------------------------------------------
    aw_done = h.settled("awaits", lambda found: len(by_kind(found, "done")) == 2 and all_ended(found), timeout=120)
    time.sleep(0.5)
    found_a = h.events("awaits")
    aw_t1, aw_t2 = intents_on(found_a, "aw", "T1"), intents_on(found_a, "aw", "T2")
    term = {one: terminal_of(found_a, one) for one in ("aw1", "aw2", "aw3")}
    met = sorted(str(one.get("task")) for one in by_kind(found_a, "wait-met", agent="aw"))
    waits_aw = by_kind(found_a, "wait", agent="aw")
    if (awaits.returncode == 0 and aw_ended and aw_second.returncode == 0 and aw_done
            and len(aw_t1) == 2 and len(aw_t2) == 2
            and aw_t2[0]["id"] < term["aw1"]
            and term["aw1"] < aw_t1[1]["id"] < min(term["aw2"], term["aw3"])
            and aw_t2[1]["id"] > term["aw3"]
            and len(waits_aw) == 1 and waits_aw[0].get("task") == "T1" and waits_aw[0].get("any") == 1
            and met == ["T1", "T2"]
            and result_of(found_a, "T1") == "T1 by the first" and result_of(found_a, "T2") == "T2 by aw3"):
        held("(b) the await by task", f"aw opened T2 (#{aw_t2[0]['id']}) under T1's await; woken on T1 "
             f"(#{aw_t1[1]['id']}) at aw1's answer, before aw2's and aw3's; on T2 (#{aw_t2[1]['id']}) after "
             f"aw3's alone; wait-met {met} -- I14")
    else:
        failures.append(f"  ✗ (b) the await by task       {awaits.returncode}/{aw_second.returncode} ended={aw_ended} "
                        f"done={aw_done} t1={[one['id'] for one in aw_t1]} t2={[one['id'] for one in aw_t2]} "
                        f"term={term} met={met} waits={waits_aw} results={result_of(found_a, 'T1')!r}/"
                        f"{result_of(found_a, 'T2')!r}")
    return 0
