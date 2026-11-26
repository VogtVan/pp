"""Scenario `team-suspect` -- 3 case(s): a member whose final failure stands is SUSPECTED -- the tick's failure
detector ◇P --, and what reaches it within its interval is answered in its place. Two teams play side by side in one
house: `pair` (r1, r2) under `retries: 1` and `late` (l1, l2) under `retries: 0`; a third, `kept`, is a journal
written by hand. `team-suspect-try` carries the try
and the health view, `team-suspect-repent` the repentance and its tolerance.
- (a) answered at once: r2 dies twice on r1's `do` (T1), the tick answers in its place -- r1's head hands the `do`
  back, its text the one r1 wrote, said carried by a launch that failed; on T2 r1 asks r2 during
  r2's interval -- the tick answers the ask at once (`re` to the ask, `by: tick`, `returned`, no `suspected`: no
  launch of r2 delivered it), `log --json` says `returned` on that post, r1's head hands the ask back, said never
  delivered, its text the one r1 wrote; the face's
  `health.tried_at` the hour of r2's final failure plus the calendar's base, 5 min, to the second; no wake-up of r2; r1 closes T2
- (d) a `do` posted during the member's last launch: l1 hands l2 a first `do`, then, l2's launch under way, a
  second one; l2 dies, its failure final at once -- the first `do` answered in its place as a launch that failed,
  the second `returned`: no `wake-intent` of l2 carries it, and l1's head hands both back, each with the text l1 wrote
- (e) a `do` a dead launch carried is a debt delivered, on a journal written by hand: kb's first launch carries
  ka's `do` and dies while its run stands -- a retry is left, the `do` is back in kb's inbox --; its continuation,
  which carries nothing, dies for good and kb is suspected: what the tick answers within the interval
  (`suspected_answers`) is `suspected`, never `returned` -- a `wake-intent` of kb carried the `do` --, and ka's head
  hands it back, said delivered without an answer
"""
from __future__ import annotations

import json
import threading
import time

from tests.harness import support

T = support(__file__, "team")

HALF, PART = "build the second half", "your part?"          # what r1 writes to r2: its do on T1, its ask on T2
FIRST, LATE = "frame the first node", "frame the second node"   # what l1 writes to l2: before its launch, during it
KEPT = "weigh the third crate"                              # what ka writes to kb
AT = "2026-11-13T21:00:00+00:00"                            # the hour of every event of the journal written by hand
# kb's first launch carries ka's do #4 and dies standing, a retry left; its continuation carries nothing and dies for good
CARRIED = [{"kind": "team-started", "agents": {"ka": "agents/ka", "kb": "agents/kb"}, "reports": [{"from": ["kb"], "to": "ka"}],
            "root": "ka", "principals": [], "owner": "house", "ceremonies": [], "launch": {}, "limits": {"retries": 1},
            "schedule": None, "digest": "000000000000"},
           {"kind": "task", "task": "T1", "from": "house", "to": "ka", "text": "weigh the crates"},
           {"kind": "post", "task": "T1", "from": "house", "to": "ka", "verb": "do", "text": "weigh the crates"},
           {"kind": "post", "task": "T1", "from": "ka", "to": "kb", "verb": "do", "text": KEPT},
           {"kind": "wake-intent", "tag": "kb-T1-1", "agent": "kb", "path": "agents/kb", "task": "T1", "run": "k1",
            "index": 1, "messages": [4]},
           {"kind": "wake-launched", "tag": "kb-T1-1", "agent": "kb", "run": "k1", "pid": 1, "launch": 1},
           {"kind": "wake-failed", "tag": "kb-T1-1", "agent": "kb", "task": "T1", "final": False, "reason": "wake-dead",
            "state": "standing", "run": "k1"},
           {"kind": "wake-intent", "tag": "kb-T1-2", "agent": "kb", "path": "agents/kb", "task": "T1", "run": "k1",
            "index": 2, "messages": []},
           {"kind": "wake-launched", "tag": "kb-T1-2", "agent": "kb", "run": "k1", "pid": 2, "launch": 2},
           {"kind": "wake-failed", "tag": "kb-T1-2", "agent": "kb", "task": "T1", "final": True, "reason": "wake-dead",
            "state": "standing", "run": "k1"}]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "r1": {"T1": [{"sleep": 0.1, "body": {"do": {"r2": HALF}}}, {"sleep": 0.1, "body": {"re": "DO", "text": "t1 done"}}],
               "T2": [{"sleep": 0.1, "body": {"ask": {"to": "r2", "text": PART}}},
                      {"sleep": 0.1, "body": {"re": "DO", "text": "t2 done"}}]},
        "r2": {"T1": [T.DEATH, T.DEATH]}})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    closed = lambda task: lambda found: bool(by_kind(found, "done", task=task)) and all_ended(found)
    module = h.module()
    gate = h.out / "late.gate"                        # l1 says its second do once the scenario opens it
    h.scripted(l1={"T1": [{"sleep": 0.1, "words": [{"do": {"l2": FIRST}}, {"gate": str(gate)}, {"do": {"l2": LATE}}]},
                          {"sleep": 0.1, "body": {"re": "DO", "text": "late done"}}]},
               l2={"T1": [{"sleep": 3.0, "body": "crash"}]})

    def opened_once_launched() -> None:
        """Opens l1's gate once l2's launch is under way: the second do is posted during l2's last launch."""
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline and not by_kind(h.events("late"), "wake-launched", agent="l2"):
            time.sleep(0.1)
        gate.write_text("open", encoding="utf-8")

    # --- the teams started at once, then each task played ------------------------------------------------------
    h.declare("pair", T.SUSPECT_PAIR.format(a="r1", b="r2"))
    h.declare("late", T.SUSPECT_PAIR.format(a="l1", b="l2").replace("retries: 1", "retries: 0"))
    started = h.call("team", "start", "pair", "--message", "build it", *h.harnessed)
    h.speaks("agents/l1")                             # its work is said to pp: its first do is handed by its print call
    started_l = h.call("team", "start", "late", "--message", "build it", *h.harnessed)
    opener = threading.Thread(target=opened_once_launched)
    opener.start()
    T.ticked(h, [("pair", closed("T1"), None), ("late", closed("T1"), None)])
    opener.join()
    first = T.finals_of(h.events("pair"), "r2")
    hour = T.local_after(first[0]["at"], 5).strftime("%H:%M:%S") if first else "?"

    posted = h.call("team", "post", "pair", "--message", "second part")
    T.ticked(h, [("pair", closed("T2"), None)])
    found_t2 = h.events("pair")
    face_t2 = h.face("pair")

    # --- (a) a message to a suspected member answered at once, no wake-up -------------------------------------
    ask = next((one for one in by_kind(found_t2, "post", verb="ask") if one.get("task") == "T2"), {})
    at_once = [one for one in by_kind(found_t2, "post", verb="re", **{"from": "r2"}) if one.get("task") == "T2"]
    r2_on_t2 = T.intents_on(found_t2, "r2", "T2")
    health = next((one.get("health") for one in face_t2.get("members") or [] if one.get("member") == "r2"), None) or {}
    half = next((one for one in by_kind(found_t2, "post", verb="do", **{"from": "r1"}) if one.get("task") == "T1"), {})
    back = {}                                         # what r1's heads hand back to it, by the message's id
    for one in h.prompts_of("r1"):
        back.update(T.handed_back(module, one))
    logged = h.call("team", "log", "pair", "--task", "T2", "--json")
    said = [json.loads(one) for one in logged.stdout.splitlines() if one.strip()]
    faced = next((one for one in said if one.get("id") == (at_once[0].get("id") if at_once else None)), {})
    if (started.returncode == 0 and posted.returncode == 0 and len(first) == 1 and len(at_once) == 1
            and at_once[0].get("re") == ask.get("id") and at_once[0].get("by") == "tick"
            and at_once[0].get("returned") is True and at_once[0].get("suspected") is None
            and at_once[0].get("to") == "r1" and faced.get("returned") is True
            and (back.get(half.get("id")) or {}).get("how") == "failed" and back[half["id"]].get("text") == HALF
            and (back.get(ask.get("id")) or {}).get("how") == "returned" and back[ask["id"]].get("text") == PART
            and health.get("suspected") is True and str(health.get("tried_at"))[-8:] == hour
            and not r2_on_t2 and result_of(found_t2, "T2") == "t2 done"):
        held("(a) answered at once", f"r2 fell on T1: r1's head hands its do #{half.get('id')} back, a launch that "
             f"failed; r1's ask #{ask.get('id')} on T2 answered by the tick at once (returned, tried again at "
             f"{health.get('tried_at')}), no wake-up of r2, log --json says returned, r1's head hands the ask back, "
             "never delivered; T2 't2 done'")
    else:
        failures.append(f"  ✗ (a) answered at once         rc={started.returncode}/{posted.returncode} finals={len(first)} "
                        f"ask={ask.get('id')} at_once={[(one.get('re'), one.get('by'), one.get('suspected'), one.get('returned'), one.get('to')) for one in at_once]} "
                        f"log={faced.get('returned')!r} back={back} "
                        f"health={health} r2_on_t2={len(r2_on_t2)} result={result_of(found_t2, 'T2')!r} hour={hour}")

    # --- (d) a do posted during the member's last launch: returned, never delivered ----------------------------
    found_l = h.events("late")
    dos_l = [one["id"] for one in by_kind(found_l, "post", verb="do", **{"from": "l1"})]
    first_l, late_l = (dos_l + [None, None])[:2]
    in_place = {one.get("re"): one for one in by_kind(found_l, "post", verb="re", **{"from": "l2"}) if one.get("by") == "tick"}
    carried = [key for one in T.intents_of(found_l, "l2") for key in one.get("messages") or []]
    back_l = {}
    for one in h.prompts_of("l1"):
        back_l.update(T.handed_back(module, one))
    if (started_l.returncode == 0 and len(dos_l) == 2 and sorted(in_place) == [first_l, late_l]
            and in_place[first_l].get("returned") is None
            and in_place[late_l].get("returned") is True and in_place[late_l].get("suspected") is None
            and carried == [first_l] and len(T.finals_of(found_l, "l2")) == 1
            and (back_l.get(first_l) or {}).get("how") == "failed" and back_l[first_l].get("text") == FIRST
            and (back_l.get(late_l) or {}).get("how") == "returned" and back_l[late_l].get("text") == LATE
            and result_of(found_l, "T1") == "late done"):
        held("(d) a do posted during the last launch is returned", f"l1's do #{late_l} posted while l2 plays #{first_l}; "
             f"l2 dies, final at once: #{first_l} answered in its place, #{late_l} returned -- l2's intents carry "
             f"{carried} alone; l1's head hands both back with the text l1 wrote; T1 'late done'")
    else:
        failures.append(f"  ✗ (d) a do during the last launch rc={started_l.returncode} dos={dos_l} "
                        f"in_place={ {key: (one.get('suspected'), one.get('returned')) for key, one in in_place.items()} } "
                        f"carried={carried} finals={len(T.finals_of(found_l, 'l2'))} back={back_l} "
                        f"result={result_of(found_l, 'T1')!r}")

    # --- (e) a do a dead launch carried is a debt delivered, even back in the inbox ----------------------------
    h.written("kept", CARRIED, AT)
    events_k = T.lines(h.journal_of("kept"))
    state_k = module.replay(events_k)
    boxed = [one.id for one in module.inbox(state_k, "kb")]       # back in the inbox: the retry was left
    carried_k = [one.get("messages") or [] for one in T.intents_of(events_k, "kb")]
    answers = module.suspected_answers(state_k, T.local_after(AT, 1))   # one minute into kb's interval
    after_k = module.replay(events_k + [{"at": AT, "id": len(events_k) + n, "team": "kept", **one.json()}
                                         for n, one in enumerate(answers, 1)])
    back_k = {}
    for key, one in after_k.task.messages.items():
        if one.body.by == "tick":
            back_k.update(T.handed_back(module, module.message_of(after_k, "ka", one)))
    if (boxed == [4] and carried_k == [[4], []] and module.suspicion_of(state_k, "kb") is not None
            and [(one.re, one.suspected, one.returned, one.to) for one in answers]
            == [(4, True, None, "ka")]
            and not after_k.task.returned and not module.inbox(after_k, "kb")
            and back_k == {4: {"how": "suspected", "member": "kb", "vector": None, "text": KEPT}}):
        held("(e) a do a dead launch carried is a debt delivered", "kb's first launch carries #4 and dies standing, a "
             "retry left: #4 back in its inbox; its continuation carries nothing and dies for good, kb suspected: the "
             "tick answers #4 under suspected, not returned, nothing returned at the replay; ka's head hands it back, "
             "delivered without an answer")
    else:
        failures.append(f"  ✗ (e) a do a dead launch carried boxed={boxed} carried={carried_k} "
                        f"suspected={module.suspicion_of(state_k, 'kb')} "
                        f"answers={[(one.re, one.suspected, one.returned, one.to) for one in answers]} "
                        f"returned={sorted(after_k.task.returned)} back={back_k}")
    return 0
