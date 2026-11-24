"""Scenario `team-halted` -- 4 case(s) (batch l-echec-du-harness-borne, team 1.25.0; s.1458, s.1492): a launch that
ends on an ERROR of its harness without an act is a failure, never an answer, and the same failure three times in a
row on a task stops launching the member there -- `wake-halted`, ONE notice of the team to the owner -- until `team
resume --task` lifts it; a house that refuses the launch is held by the same guard. Two teams side by side in one house,
`schedule: off`, `retries: 5` so that the guard, not the retries, ends the series.
- (a) a harness error: e's harness ends three times on an error (`is_error`, exit 1) and says no act -- three
  `wake-failed {reason: harness-error…}`, no `wake-ended`, nothing in `team responses`; at the third, ONE `wake-halted
  {agent e, task T1, count 3}` and ONE notice to the owner; two ticks more launch nobody; `team resume --task T1` lifts
  it: e is launched again, answers, T1 resolved
- (b) a house that refuses: w plays under a provider the house is not wired with -- `agent start` refuses before any
  harness -- at the start's tick and at each tick after it: at the third `wake-failed {house: true}`, ONE `wake-halted
  {agent w, task T1, count 3}` and ONE notice of it; two ticks more launch nobody; `team resume --task T1` lifts it, w is
  launched again and refused again, its count afresh: no second halt
- (c) one code, two stderrs: s's harness ends three times on exit 1 without an act, each time with another text on
  stderr -- `harness rc 1` is the failure's identity, never what the harness said: ONE `wake-halted {count 3}`
- (d) a relance past a halted task: d owes the openings of T1 and of T2, delivered and unanswered, and the guard holds
  it on T1 -- the journal's tail written by hand while the team rests --: a tick RELANCES d on T2, the first debt of a
  task that does not halt it; nothing on T1
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from tests.harness import support

T = support(__file__, "team")

ERROR = {"sleep": 0.1, "body": "silent", "error": "error_during_execution", "rc": 1}   # the harness ends on an error
EXIT = lambda n: {"sleep": 0.1, "body": "silent", "rc": 1, "stderr": f"boom at step {n} of the build"}   # exit 1, another text


def tail_written(h, name: str, events: list[dict]) -> list[int]:
    """The events appended to the team's journal while it rests, each stamped now and numbered after the last one, the
    keys `{n}` of a text replaced by the ids of the events before it. -> their ids."""
    journal = h.journal_of(name)
    last = max(json.loads(line)["id"] for line in journal.read_text(encoding="utf-8").splitlines() if line.strip())
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    made = [{"at": at, "id": last + n, "team": name, **one} for n, one in enumerate(events, 1)]
    with journal.open("a", encoding="utf-8") as handle:
        handle.write("".join(json.dumps(one, ensure_ascii=False) + "\n" for one in made))
    return [one["id"] for one in made]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={"e": {"T1": [ERROR, ERROR, ERROR, {"sleep": 0.1, "body": {"done": "back"}}]},
                               "s": {"T1": [EXIT(1), EXIT(2), EXIT(3), {"sleep": 0.1, "body": {"done": "back"}}]},
                               "d": {"T2": [{"sleep": 0.1, "body": {"done": "t2"}}]}})
    by_kind, all_ended = T.by_kind, T.all_ended
    h.declare("err", "---\nagents: |\n  e agents/e\nroot: e\nretries: 5\nschedule: off\n---\nAnswer the task.\n")
    h.declare("hb", "---\nagents: |\n  w agents/w\nroot: w\nretries: 5\nschedule: off\n---\nThe house may refuse.\n")
    erring = h.call("team", "start", "err", "--message", "work T1", *h.harnessed)
    refusing = h.call("team", "start", "hb", "--message", "work T1", *h.harnessed, "--member", "w", "--provider", "nowhere")
    h.declare("sd", "---\nagents: |\n  s agents/s\nroot: s\nretries: 5\nschedule: off\n---\nAnswer the task.\n")
    exiting = h.call("team", "start", "sd", "--message", "work T1", *h.harnessed)
    h.declare("rel", "---\nagents: |\n  d agents/d\nroot: d\nschedule: off\n---\nAnswer the tasks.\n")
    resting = h.call("team", "start", "rel", "--no-tick", *h.harnessed)
    halted = lambda name: (lambda found: bool(by_kind(found, "wake-halted")) and all_ended(found)
                           or len(by_kind(found, "wake-failed")) > 3)

    # --- (b) a house that refuses: every tick launches w again until the guard holds it -------------------------
    ticks_b = []
    for _ in range(4):
        if halted("hb")(h.events("hb")):
            break
        ticks_b.append(h.call("team", "tick", "hb"))
    ticks_b += [h.call("team", "tick", "hb") for _ in range(2)]        # held: nobody launched
    found_b = h.events("hb")
    fails_b = by_kind(found_b, "wake-failed", agent="w")
    halts_b = by_kind(found_b, "wake-halted")
    notices_b = [one for one in by_kind(found_b, "post", verb="notice") if one.get("halted")]
    resumed_b = h.call("team", "resume", "hb", "--task", "T1")
    again_b = h.settled("hb", lambda found: len(by_kind(found, "wake-failed", agent="w")) >= 4 and all_ended(found), 20)
    after_b = h.events("hb")
    one_b = halts_b[0] if halts_b else {}
    if (refusing.returncode == 0 and all(one.returncode == 0 for one in (*ticks_b, resumed_b)) and len(fails_b) == 3
            and all(one.get("house") for one in fails_b) and len(halts_b) == 1 and one_b.get("agent") == "w"
            and one_b.get("task") == "T1" and one_b.get("count") == 3 and int(one_b["id"]) > int(fails_b[-1]["id"])
            and len(notices_b) == 1 and notices_b[0].get("to") == "house" and notices_b[0].get("about") is None
            and again_b and len(by_kind(after_b, "wake-failed", agent="w")) == 4
            and len(by_kind(after_b, "wake-halted")) == 1):
        held("(b) a house that refuses", f"w refused 3 times before any harness: wake-halted #{one_b.get('id')} count 3, "
             "one notice; two ticks more launch nobody; resume lifts it, w refused once more, no second halt")
    else:
        failures.append(f"  ✗ (b) a house that refuses     rc={refusing.returncode}/{[one.returncode for one in ticks_b]}/"
                        f"{resumed_b.returncode} fails={[(one['id'], one.get('house'), one.get('reason')) for one in fails_b]} "
                        f"halts={halts_b} notices={notices_b} again={again_b} "
                        f"after={len(by_kind(after_b, 'wake-failed', agent='w'))} {resumed_b.stderr[-200:]!r}")

    # --- (a) a harness error: three in a row, then the guard -----------------------------------------------------
    first_a = h.settled("err", halted("err"), 40)
    ticks_a = [h.call("team", "tick", "err") for _ in range(2)]        # held: nobody launched
    found_a = h.events("err")
    fails_a = by_kind(found_a, "wake-failed", agent="e")
    halts_a = by_kind(found_a, "wake-halted")
    notices_a = [one for one in by_kind(found_a, "post", verb="notice") if one.get("halted")]
    intents_a = len(T.intents_of(found_a, "e"))
    told = [json.loads(line) for line in h.call("team", "responses", "err", "--json").stdout.splitlines() if line.strip()]
    resumed_a = h.call("team", "resume", "err", "--task", "T1")
    done_a = h.settled("err", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 30)
    one_a = halts_a[0] if halts_a else {}
    if (erring.returncode == 0 and first_a and all(one.returncode == 0 for one in (*ticks_a, resumed_a))
            and len(fails_a) == 3 and all(str(one.get("reason")).startswith("harness-error") for one in fails_a)
            and not by_kind(found_a, "wake-ended", agent="e") and told == [] and intents_a == 3
            and len(halts_a) == 1 and one_a.get("agent") == "e" and one_a.get("task") == "T1" and one_a.get("count") == 3
            and len(notices_a) == 1 and notices_a[0].get("to") == "house" and done_a
            and T.result_of(h.events("err"), "T1") == "back"):
        held("(a) a harness error", f"e's harness ended 3 times on an error without an act: 3 wake-failed "
             f"{fails_a[0].get('reason')!r}, no wake-ended, no response; wake-halted #{one_a.get('id')} count 3, one "
             "notice; two ticks more launch nobody; resume lifts it, e answers, T1 done")
    else:
        failures.append(f"  ✗ (a) a harness error         rc={erring.returncode}/{[one.returncode for one in ticks_a]}/"
                        f"{resumed_a.returncode} first={first_a} intents={intents_a} "
                        f"fails={[(one['id'], one.get('reason')) for one in fails_a]} "
                        f"ended={[(one['id'], one.get('state')) for one in by_kind(found_a, 'wake-ended', agent='e')]} "
                        f"told={len(told)} halts={halts_a} notices={notices_a} done={done_a} "
                        f"{resumed_a.stderr[-200:]!r}")

    # --- (c) one code, two stderrs --------------------------------------------------------------------------------
    first_c = h.settled("sd", halted("sd"), 40)
    found_c = h.events("sd")
    fails_c = by_kind(found_c, "wake-failed", agent="s")
    halts_c = by_kind(found_c, "wake-halted")
    if (exiting.returncode == 0 and first_c and len(fails_c) == 3
            and all(str(one.get("reason")).startswith("harness-error: harness rc 1") for one in fails_c)
            and len({one.get("reason") for one in fails_c}) == 3 and len(halts_c) == 1
            and halts_c[0].get("count") == 3 and len(T.intents_of(found_c, "s")) == 3):
        held("(c) one code, two stderrs", "s's harness exits 1 three times, each with another stderr: three reasons "
             f"apart, one identity -- wake-halted #{halts_c[0].get('id')} count 3")
    else:
        failures.append(f"  ✗ (c) one code, two stderrs   rc={exiting.returncode} first={first_c} "
                        f"fails={[(one['id'], one.get('reason')) for one in fails_c]} halts={halts_c} "
                        f"intents={len(T.intents_of(found_c, 's'))}")

    # --- (d) a relance past a halted task -------------------------------------------------------------------------
    base = max(one["id"] for one in h.events("rel"))
    do1, do2 = base + 2, base + 4
    tail_written(h, "rel", [
        {"kind": "task", "task": "T1", "from": "house", "to": "d", "text": "work T1"},
        {"kind": "post", "task": "T1", "from": "house", "to": "d", "verb": "do", "text": "work T1"},
        {"kind": "task", "task": "T2", "from": "house", "to": "d", "text": "work T2"},
        {"kind": "post", "task": "T2", "from": "house", "to": "d", "verb": "do", "text": "work T2"},
        {"kind": "wake-intent", "tag": "d-T1-0a0a0a", "agent": "d", "path": "agents/d", "task": "T1", "run": None,
         "messages": [do1]},
        {"kind": "wake-ended", "tag": "d-T1-0a0a0a", "agent": "d", "run": None, "state": "parked", "cost": 0.0},
        {"kind": "wake-intent", "tag": "d-T2-0b0b0b", "agent": "d", "path": "agents/d", "task": "T2", "run": None,
         "messages": [do2]},
        {"kind": "wake-ended", "tag": "d-T2-0b0b0b", "agent": "d", "run": None, "state": "parked", "cost": 0.0},
        {"kind": "wake-halted", "agent": "d", "task": "T1", "reason": "harness-error: error_during_execution",
         "count": 3}])
    ticked_d = h.call("team", "tick", "rel")
    done_d = h.settled("rel", lambda found: len(T.intents_of(found, "d")) >= 3 and all_ended(found), 20)
    later = [one for one in T.intents_of(h.events("rel"), "d") if one["id"] > base + 9]
    if (resting.returncode == 0 and ticked_d.returncode == 0 and done_d and len(later) == 1
            and later[0].get("task") == "T2" and later[0].get("relance") and do2 in (later[0].get("messages") or [])):
        held("(d) a relance past a halted task", f"d owes #{do1} on T1, halted, and #{do2} on T2: the tick relances "
             f"it on T2 ({later[0].get('relance')}), nothing on T1")
    else:
        failures.append(f"  ✗ (d) relance past a halt     rc={resting.returncode}/{ticked_d.returncode} done={done_d} "
                        f"later={[(one['id'], one.get('task'), one.get('relance'), one.get('messages')) for one in later]} "
                        f"{ticked_d.stderr[-200:]!r}")
    return 0
