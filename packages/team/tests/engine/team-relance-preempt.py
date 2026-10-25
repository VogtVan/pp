"""Scenario `team-relance-preempt` -- 3 case(s): a relance asks a debtor to answer and guarantees nothing; two
relances on a debt still owed, and the tick answers it in the member's place -- never a principal's opening; a
relance that fails for good is answered in place at once, and the member is suspected.
- (a) a stubborn worker: w puts its `do` off and gives nothing back on two relances; the tick answers the `do`
  in w's place (`preempted`, `by: tick`, on T1), sup is woken and closes T1; no third relance
- (b) a stubborn root: r puts its principal's opening off and gives nothing back on two relances; the opening is
  never answered in its place -- the team's notice about r to house, and no relance follows
- (a) fallen: b puts its `do` off, its relance dies twice -- the tick answers the `do` in b's place, a is woken; a
  asks b within b's interval -- the tick answers the ask at once (`suspected`), b is woken no more, and a closes T1
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "sup": [{"sleep": 0.1, "body": {"do": ["w"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": "closed without w"}}],
        "w": [{"sleep": 0.1, "body": []}] * 5,
        "r": [{"sleep": 0.1, "body": []}] * 5,
        "a": [{"sleep": 0.1, "body": {"do": ["b"]}},
              {"sleep": 0.1, "body": {"ask": {"to": "b", "text": "anything left?"}}},
              {"sleep": 0.1, "body": {"re": "DO", "text": "closed after b"}}],
        "b": [{"sleep": 0.1, "body": []}, {"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": "crash"}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    reminded = h.module().REMINDED

    # --- every team declared and started before the first wait ------------------------------------------------------
    h.declare("stub", "---\nagents: |\n  sup agents/sup\n  w agents/w\nreports: |\n  w -> sup\nroot: sup\nschedule: off\n---\n"
                      "Delegate, then conclude.\n")
    h.declare("lone", "---\nagents: |\n  r agents/r\nroot: r\nschedule: off\n---\nDo it alone.\n")
    h.declare("fall", "---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nretries: 1\n"
                      "schedule: off\n---\nDelegate, then conclude.\n")
    started = h.call("team", "start", "stub", "--message", "do it", *h.harnessed)
    lone = h.call("team", "start", "lone", "--message", "do it alone", *h.harnessed)
    fallen = h.call("team", "start", "fall", "--message", "try it", *h.harnessed)

    stub_done = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
    lone_told = lambda found: bool(by_kind(found, "post", verb="notice")) and all_ended(found)
    fall_ended = lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found)
    # stub and lone move by their wake-ups' ends alone; fall, whose dead wake-ups fire no on-end, is ticked meanwhile
    deadline = time.monotonic() + 40
    done = told = ended = False
    while time.monotonic() < deadline:
        done, told, ended = stub_done(h.events("stub")), lone_told(h.events("lone")), fall_ended(h.events("fall"))
        if done and told and ended:
            break
        time.sleep(0.5)
        if not ended:
            h.call("team", "tick", "fall")
    ticks = [h.call("team", "tick", name) for _ in range(2) for name in ("stub", "lone")]
    stub_ticks, lone_ticks = ticks[0::2], ticks[1::2]

    # --- (a) a stubborn worker is preempted -----------------------------------------------------------------------
    found = h.events("stub")
    to_w = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "sup"})), None)
    preempted = [one for one in by_kind(found, "post", verb="re") if one.get("preempted")]
    w = [one.get("relance") for one in T.intents_of(found, "w")]
    shape = [(one.get("from"), one.get("to"), one.get("re"), one.get("by"), one.get("task")) for one in preempted]
    if (started.returncode == 0 and done and all(one.returncode == 0 for one in stub_ticks) and w == [None, "owed", "owed"]
            and shape == [("w", "sup", to_w, "tick", "T1")] and reminded in str(preempted[0].get("text"))
            and result_of(found, "T1") == "closed without w"):
        held("(a) a stubborn worker, preempted", f"w relanced twice ({w[1:]}), nothing back; the tick answers #{to_w} in its "
             "place (preempted), sup closes T1; no third relance")
    else:
        failures.append(f"  ✗ (a) a stubborn worker       rc={started.returncode} done={done} w={w} preempted={shape} "
                        f"texts={[one.get('text') for one in preempted]} result={result_of(found, 'T1')!r}\n"
                        f"{started.stderr[-300:]}")

    # --- (b) a stubborn root: the team's notice, its opening never preempted ---------------------------------------
    found = h.events("lone")
    r = [one.get("relance") for one in T.intents_of(found, "r")]
    up = by_kind(found, "post", verb="notice")
    if (lone.returncode == 0 and told and all(one.returncode == 0 for one in lone_ticks) and r == [None, "owed", "owed"]
            and [(one.get("from"), one.get("to"), one.get("about"), one.get("preempted")) for one in up] == [("lone", "house", "r", True)]
            and not by_kind(found, "post", verb="re") and not by_kind(found, "done")):
        held("(b) a stubborn root, the team tells", f"r relanced twice ({r[1:]}), nothing back: the team's notice about r to house, the "
             "opening never answered in its place, no relance after")
    else:
        failures.append(f"  ✗ (b) a stubborn root         rc={lone.returncode} told={told} r={r} "
                        f"up={[(one.get('from'), one.get('to'), one.get('about'), one.get('preempted')) for one in up]} "
                        f"re={[(one.get('from'), one.get('re')) for one in by_kind(found, 'post', verb='re')]}")

    # --- (a) fallen: answered in place, then suspected ---------------------------------------------------------
    found = h.events("fall")
    to_b = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "a"})), None)
    in_place = [one for one in by_kind(found, "post", verb="re", **{"from": "b"}) if one.get("by") == "tick"]
    finals = [one for one in by_kind(found, "wake-failed", agent="b") if one.get("final")]
    final_at = finals[0]["id"] if finals else 10 ** 9
    later = [one.get("relance") for one in T.intents_of(found, "b") if one["id"] > final_at]
    ask = next((one["id"] for one in by_kind(found, "post", verb="ask", **{"from": "a"})), None)
    if (fallen.returncode == 0 and fall_ended(found) and len(finals) == 1 and len(in_place) == 2
            and in_place[0].get("re") == to_b and not in_place[0].get("suspected")
            and in_place[1].get("re") == ask and in_place[1].get("suspected") is True
            and later == [] and result_of(found, "T1") == "closed after b"):
        held("(a) fallen, answered, suspected", f"b's relance dies twice: the tick answers #{to_b} in its place; "
             f"a's ask #{ask} answered at once ({in_place[1]['text']!r}), b woken no more; T1 'closed after b'")
    else:
        failures.append(f"  ✗ (a) fallen, suspected        rc={fallen.returncode} ended={fall_ended(found)} finals={len(finals)} "
                        f"in_place={[(one.get('re'), one.get('suspected')) for one in in_place]} later={later} "
                        f"result={result_of(found, 'T1')!r} "
                        f"journal={[T.shape(one) + ((one.get('reason'), one.get('final')) if one.get('kind') == 'wake-failed' else ()) for one in found]}")
    return 0
