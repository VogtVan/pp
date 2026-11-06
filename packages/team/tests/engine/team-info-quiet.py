"""Scenario `team-info-quiet` -- 2 case(s) (batch le-message-info, team 0.47.0; study § 19, row 114): a MEMBER's
info launches nobody -- it waits in its recipient's box and rides the head of its next launch, whatever its cause.
- (b1) p1 informs its idle peer p2, which is never launched: the info stays in p2's box (`pending`, verb `info`) and
  comes back to p1 at the close (`returned`)
- (b2) w1 informs a supervisor that waits on w1 and w2: no intent of sup is written for it, and sup's next launch --
  at the answers -- carries the info in its `[inbox]`
"""
from __future__ import annotations

import json
import time

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "lead": [{"sleep": 0.1, "body": {"do": {"p1": "the part"}}},
                 {"sleep": 0.1, "body": {"re": "DO", "text": "lead closes"}}],
        "p1": [{"sleep": 0.1, "body": [{"info": {"to": "p2", "text": "fyi, I took the part"}}]},
               {"sleep": 3.0, "body": {"re": "DO", "text": "p1 done"}}],
        "p2": [{"sleep": 0.1, "body": {"re": "DO", "text": "never"}}],
        "sup": [{"sleep": 0.1, "body": {"do": ["w1", "w2"]}},
                {"sleep": 0.1, "body": {"re": "DO", "text": "both in"}}],
        "w1": [{"sleep": 0.1, "body": [{"info": {"to": "sup", "text": "halfway"}}]},
               {"sleep": 0.1, "body": {"re": "DO", "text": "w1 done"}}],
        "w2": [{"sleep": 2.5, "body": {"re": "DO", "text": "w2 done"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    h.declare("peers", "---\nagents: |\n  lead agents/lead\n  p1 agents/p1\n  p2 agents/p2\nreports: |\n  p1 p2 -> lead\n"
                       "root: lead\nschedule: off\n---\nOne part.\n")
    h.declare("waiting", "---\nagents: |\n  sup agents/sup\n  w1 agents/w1\n  w2 agents/w2\nreports: |\n  w1 w2 -> sup\n"
                         "root: sup\nschedule: off\n---\nTwo parts.\n")

    # --- (b1) an info to an idle peer: never launched for it -------------------------------------------------------
    peers = h.call("team", "start", "peers", "--message", "do it", *h.harnessed)
    waiting = h.call("team", "start", "waiting", "--message", "do it", *h.harnessed)
    pending_p2, seen_at = [], time.monotonic() + 40
    while time.monotonic() < seen_at:
        face_p = h.face("peers")
        pending_p2 = [(one.get("verb"), one.get("from")) for member in face_p.get("members") or []
                      if member.get("member") == "p2" for one in member.get("pending") or []]
        if pending_p2 or by_kind(h.events("peers"), "done", task="T1"):
            break
        time.sleep(0.2)
    done_p = h.settled("peers", ended, timeout=60)
    found_p = h.events("peers")
    info_p = next((one for one in by_kind(found_p, "post", verb="info")), {})
    returned_p = [(one.get("message"), one.get("to")) for one in by_kind(found_p, "returned")]
    if (peers.returncode == 0 and done_p and (info_p.get("from"), info_p.get("to")) == ("p1", "p2")
            and pending_p2 == [("info", "p1")] and not T.intents_of(found_p, "p2")
            and returned_p == [(info_p["id"], "p1")] and result_of(found_p, "T1") == "lead closes"):
        held("(b1) an info to an idle peer", f"p1's info #{info_p['id']} to p2: p2 never launched, the info pending "
             "(verb info) then returned to p1 at the close; T1 'lead closes'")
    else:
        failures.append(f"  ✗ (b1) an info to a peer        rc={peers.returncode} done={done_p} info={info_p} "
                        f"pending={pending_p2} p2={len(T.intents_of(found_p, 'p2'))} returned={returned_p} "
                        f"result={result_of(found_p, 'T1')!r}")

    # --- (b2) an info to a waiting supervisor: no launch, the head of the next one -----------------------------------
    done_w = h.settled("waiting", ended, timeout=60)
    found_w = h.events("waiting")
    info_w = next((one for one in by_kind(found_w, "post", verb="info")), {})
    sup = T.intents_of(found_w, "sup")
    answers_w = [one["id"] for one in by_kind(found_w, "post", verb="re") if one.get("from") in ("w1", "w2")]
    prompts_sup = h.prompts_of("sup")
    head_line = f"#{info_w.get('id')} INFO from w1 on T1"
    if (waiting.returncode == 0 and done_w and (info_w.get("from"), info_w.get("to")) == ("w1", "sup")
            and len(sup) == 2 and sup[1]["id"] > max(answers_w) and info_w["id"] in (sup[1].get("messages") or [])
            and len(prompts_sup) == 2 and head_line in prompts_sup[1] and "halfway" in prompts_sup[1]
            and head_line not in prompts_sup[0] and result_of(found_w, "T1") == "both in"):
        held("(b2) an info to a waiting supervisor", f"w1's info #{info_w['id']} to sup: no intent of sup for it (2 "
             f"intents, the second #{sup[1]['id']} after both answers), its head carries '{head_line}'; T1 'both in'")
    else:
        failures.append(f"  ✗ (b2) an info to a supervisor  rc={waiting.returncode} done={done_w} info={info_w} "
                        f"sup={[(one['id'], one.get('messages')) for one in sup]} answers={answers_w} "
                        f"prompts={len(prompts_sup)} head={[head_line in one for one in prompts_sup]} "
                        f"result={result_of(found_w, 'T1')!r}")
    return 0
