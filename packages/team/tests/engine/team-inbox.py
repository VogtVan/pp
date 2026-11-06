"""Scenario `team-inbox` -- 3 case(s): what reaches the owner's inbox from a team -- a root speaks to its principal by
its own elements alone, the team's notice says what the tick saw, and an ask to the owner is answered, never returned.
- (c) a root that falls: the team's notice to its principal `about` the root (`awaits: true`), never a post from the
  root; it stays after `--seen`; `post --reply` writes `re`, the notice leaves the inbox, and the root, tried past its
  interval, answers its opening
- (d) a root that asks: its `ask` to the owner is a `question`; the owner's `--reply` is a `re`, and the root's answer to
  its opening closes the task
- (i) an ask to the owner is never returned: iq asks the owner on T1, the owner replies, iq answers done; no `returned`
  of the ask, the face lists it in the owner's inbox as iq's ask on T1, and the inbox holds T1 done
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f": [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}],
        "q": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which budget?"}}},
              {"sleep": 0.1, "body": {"re": "DO", "text": "answered"}}],
        "iq": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "scope?"}}},
               {"sleep": 0.1, "body": {"done": "answered"}}]})
    by_kind, all_ended, asks_to, result_of = T.by_kind, T.all_ended, T.asks_to, T.result_of

    def inbox(name: str) -> dict:
        said = h.call("team", "inbox", name, "--json").stdout.strip()
        try:
            return json.loads(said) if said else {}
        except ValueError:
            return {"unreadable": said}

    # --- every team declared and started before the first wait -----------------------------------------------------
    h.declare("frail", "---\nagents: |\n  f agents/f\nroot: f\nretries: 0\nschedule: off\n---\nIt may fall.\n")
    h.declare("asks", "---\nagents: |\n  q agents/q\nroot: q\nschedule: off\n---\nAsk when unsure.\n")
    h.declare("ownerq", "---\nagents: |\n  iq iq\nroot: iq\nschedule: off\n---\nAsk the owner.\n")
    started_c = h.call("team", "start", "frail", "--message", "try it", *h.harnessed)
    started_d = h.call("team", "start", "asks", "--message", "price it", *h.harnessed)
    started_i = h.call("team", "start", "ownerq", "--message", "scope it", *h.harnessed)

    # --- (c) a root that falls: the team's notice about it ---------------------------------------------------------
    h.tick_until("frail", lambda found: bool(T.finals_of(found, "f")) and all_ended(found), timeout=40)
    found = h.events("frail")
    told = by_kind(found, "post", to="house")
    h.call("team", "inbox", "frail", "--seen")
    kept = inbox("frail")
    fell = T.finals_of(found, "f")
    later = T.local_after(fell[0]["at"], 6).isoformat(timespec="seconds") if fell else None
    notice = told[0]["id"] if told else -1
    replied = h.call("team", "post", "frail", "--task", "T1", "--reply", str(notice), "--message", "go on", now=later)
    h.tick_until("frail", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40, now=later)
    found = h.events("frail")
    answer = [one for one in by_kind(found, "post", **{"from": "house"}) if one.get("re") == notice]
    gone = inbox("frail")
    if (started_c.returncode == 0 and replied.returncode == 0
            and [(one.get("from"), one.get("verb"), one.get("about")) for one in told] == [("frail", "notice", "f")]
            and [one.get("verb") for one in by_kind(found, "post", **{"from": "f"})] == ["re"]
            and [(one.get("id"), one.get("awaits")) for one in kept.get("notices") or []] == [(notice, True)]
            and [one.get("verb") for one in answer] == ["re"] and "reply" not in answer[0]
            and not gone.get("notices") and result_of(found, "T1") == "recovered"):
        held("(c) the team's notice about a fallen root", f"#{notice} notice from frail about f, kept after --seen "
             f"(awaits); --reply wrote re #{answer[0]['id']}, the notice gone, T1 'recovered'")
    else:
        failures.append(f"  ✗ (c) a fallen root          told={[(one.get('from'), one.get('verb'), one.get('about')) for one in told]} "
                        f"kept={kept} answer={answer} gone={gone} result={result_of(found, 'T1')!r} "
                        f"{replied.stderr.strip()[-200:]!r}")

    # --- (d) a root that asks: a question, its answer a re ---------------------------------------------------------
    h.settled("asks", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 40)
    box = inbox("asks")
    ask = next((one["id"] for one in by_kind(h.events("asks"), "post", verb="ask")), -1)
    replied = h.call("team", "post", "asks", "--task", "T1", "--reply", str(ask), "--message", "100 USD")
    h.settled("asks", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 40)
    found = h.events("asks")
    answer = [one for one in by_kind(found, "post", **{"from": "house"}) if one.get("re") == ask]
    after = inbox("asks")
    if (started_d.returncode == 0 and replied.returncode == 0
            and [(one.get("id"), one.get("verb"), one.get("from")) for one in box.get("questions") or []] == [(ask, "ask", "q")]
            and not box.get("notices") and [one.get("verb") for one in answer] == ["re"]
            and result_of(found, "T1") == "answered" and not after.get("questions")):
        held("(d) a root that asks", f"#{ask} a question of q; --reply wrote re, the root's re to the opening closed T1 "
             "'answered'")
    else:
        failures.append(f"  ✗ (d) a root that asks       box={box} answer={answer} result={result_of(found, 'T1')!r} "
                        f"after={after} {replied.stderr.strip()[-200:]!r}")

    # --- (i) the post to a principal: an ask to the owner is never returned ----------------------------------------
    asked_iq = h.settled("ownerq", lambda found: bool(asks_to(found, "iq", "house")) and all_ended(found), timeout=40)
    ask_iq = next((one["id"] for one in asks_to(h.events("ownerq"), "iq", "house")), -1)
    replied_iq = h.call("team", "post", "ownerq", "--task", "T1", "--reply", str(ask_iq), "--message", "all of it")
    done_iq = h.settled("ownerq", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=40)
    found_i = h.events("ownerq")
    face_i = h.face("ownerq")
    listed = [(one.get("id"), one.get("verb"), one.get("from"), one.get("task"), one.get("returned"))
              for one in face_i.get("owner_inbox") or [] if one.get("id") == ask_iq]
    box_i = inbox("ownerq")
    if (started_i.returncode == 0 and asked_iq and replied_iq.returncode == 0 and done_iq
            and not [one for one in by_kind(found_i, "returned") if one.get("message") == ask_iq]
            and listed == [(ask_iq, "ask", "iq", "T1", False)]
            and [one.get("task") for one in box_i.get("done") or []] == ["T1"] and not box_i.get("returned")
            and not box_i.get("questions") and result_of(found_i, "T1") == "answered"):
        held("(i) a post to the owner is never returned", f"iq's ask #{ask_iq} to the owner, the owner's reply, T1 "
             "done: no returned; the face lists it in the owner's inbox (ask from iq on T1, not returned); the inbox "
             "holds T1 done, nothing returned")
    else:
        failures.append(f"  ✗ (i) the post to the owner    {started_i.returncode}/{replied_iq.returncode} asked={asked_iq} "
                        f"done={done_iq} returned={by_kind(found_i, 'returned')} listed={listed} inbox={box_i}")
    return 0
