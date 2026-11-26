"""Scenario `team-inbox` -- 5 case(s): what reaches the owner's inbox from a team -- a root speaks to its principal by
its own elements alone, the team's notice says what the tick saw, and an ask to the owner is answered, never returned.
- (c) a root that falls: the team's notice to its principal `about` the root (`awaits: true`), never a post from the
  root, dated by its event's `at` (s.1706); it stays after `--seen`; `post --reply` writes `re`, the notice leaves the
  inbox, and the root, tried past its interval, answers its opening
- (d) a root that asks: its `ask` to the owner is a `question`; the owner's `--reply` is a `re`, and the root's answer to
  its opening closes the task
- (i) an ask to the owner is never returned: iq asks the owner on T1, the owner replies, iq answers done; no `returned`
  of the ask, the face lists it in the owner's inbox as iq's ask on T1, and the inbox holds T1 done
- (j) one message marked read: `--seen --id` takes one info out, a question and an unknown id refuse
- (k) an ask of a closed task (s.1587), on a journal written by hand: lead's asks to the owner on T1 (resolved), T2
  (open) and T3 (stopped) -- T2's alone is a question (`inbox --json`, `status --json`, the inbox's line and the
  team's `asks`); T1's and T3's are infos said `closed: true` until read; a reply to T1's refuses `task-closed`;
  `--seen --id 4` marks T1's read alone -- `inbox-read`, `--json` without #4, #11 still there (s.1704) --, then
  `--seen` takes the rest; each question, info and task done of `inbox --json` carries the `at` of its event, and
  house's note #13 on T2, returned to it (#14), stands under `returned` with the `at` of its own post (s.1706)
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

AT = "2026-10-01T09:00:00+00:00"
CLOSED = [
    {"kind": "team-started", "agents": {"lead": "agents/lead"}, "reports": [], "root": "lead", "principals": [],
     "owner": "house", "ceremonies": [], "entries": {}, "work": None, "launch": {}, "limits": {}, "schedule": None,
     "digest": "000000000000"},
    {"kind": "task", "task": "T1", "from": "house", "to": "lead", "text": "scope it"},                           # 2
    {"kind": "post", "task": "T1", "from": "house", "to": "lead", "verb": "do", "text": "scope it"},              # 3
    {"kind": "post", "task": "T1", "from": "lead", "to": "house", "verb": "ask", "text": "scope?"},               # 4
    {"kind": "done", "task": "T1", "result": "scoped"},                                                          # 5
    {"kind": "task", "task": "T2", "from": "house", "to": "lead", "text": "price it"},                           # 6
    {"kind": "post", "task": "T2", "from": "house", "to": "lead", "verb": "do", "text": "price it"},              # 7
    {"kind": "post", "task": "T2", "from": "lead", "to": "house", "verb": "ask", "text": "budget?"},              # 8
    {"kind": "task", "task": "T3", "from": "house", "to": "lead", "text": "name it"},                            # 9
    {"kind": "post", "task": "T3", "from": "house", "to": "lead", "verb": "do", "text": "name it"},               # 10
    {"kind": "post", "task": "T3", "from": "lead", "to": "house", "verb": "ask", "text": "which?"},               # 11
    {"kind": "stopped", "task": "T3", "by": "house"},                                                            # 12
    {"kind": "post", "task": "T2", "from": "house", "to": "lead", "verb": "note", "text": "the deadline moved",
     "at": "2026-10-01T09:05:00+00:00"},                                                                         # 13
    {"kind": "returned", "message": 13, "to": "house"},                                                          # 14
]
RETURNED_AT = CLOSED[12]["at"]                       # the moment of the post returned, its own


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "f": [{"sleep": 0.1, "body": "crash"}, {"sleep": 0.1, "body": {"re": "DO", "text": "recovered"}}],
        "q": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which budget?"}}},
              {"sleep": 0.1, "body": {"re": "DO", "text": "answered"}}],
        "iq": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "scope?"}}},
               {"sleep": 0.1, "body": {"done": "answered"}}],
        "rd": [{"sleep": 0.1, "body": [{"info": {"to": "house", "text": "first"}},
                                       {"info": {"to": "house", "text": "second"}},
                                       {"ask": {"to": "house", "text": "which one?"}}]}]})
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
    h.declare("reads", "---\nagents: |\n  rd agents/rd\nroot: rd\nschedule: off\n---\nTell the owner.\n")
    started_j = h.call("team", "start", "reads", "--message", "tell me", *h.harnessed)

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
            and [(one.get("id"), one.get("awaits"), one.get("at")) for one in kept.get("notices") or []]
            == [(notice, True, told[0].get("at"))]
            and [one.get("verb") for one in answer] == ["re"] and "reply" not in answer[0]
            and not gone.get("notices") and result_of(found, "T1") == "recovered"):
        held("(c) the team's notice about a fallen root", f"#{notice} notice from frail about f, dated, kept after "
             f"--seen (awaits); --reply wrote re #{answer[0]['id']}, the notice gone, T1 'recovered'")
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

    # --- (j) one message marked read: an info leaves, a question and an unknown id refuse --------------------------
    h.settled("reads", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 40)
    found_j = h.events("reads")
    told_j = [one["id"] for one in by_kind(found_j, "post", verb="info")]
    ask_j = next((one["id"] for one in by_kind(found_j, "post", verb="ask")), -1)
    first, second = (told_j + [-1, -1])[:2]
    read = h.call("team", "inbox", "reads", "--seen", "--id", str(first))
    box_j = inbox("reads")
    before = len(h.events("reads"))
    asked = h.call("team", "inbox", "reads", "--seen", "--id", str(ask_j))
    unknown = h.call("team", "inbox", "reads", "--seen", "--id", "9999")
    after_j = len(h.events("reads"))
    logged = h.call("team", "log", "reads").stdout
    marks = [one.get("message") for one in by_kind(h.events("reads"), "inbox-read")]
    if (started_j.returncode == 0 and read.returncode == 0 and marks == [first]
            and [one.get("id") for one in box_j.get("infos") or []] == [second]
            and [one.get("id") for one in box_j.get("questions") or []] == [ask_j]
            and asked.returncode != 0 and "inbox-question" in asked.stderr
            and unknown.returncode != 0 and "inbox-id-unknown" in unknown.stderr
            and before == after_j and f"inbox-read #{first}" in logged):
        held("(j) one message marked read", f"--seen --id {first} wrote inbox-read, info #{second} and question "
             f"#{ask_j} stay; --id {ask_j} refused inbox-question, --id 9999 inbox-id-unknown, nothing written; log "
             "says it")
    else:
        failures.append(f"  ✗ (j) one message marked read  {started_j.returncode}/{read.returncode} infos={told_j} "
                        f"ask={ask_j} marks={marks} box={box_j} asked={asked.returncode}:{asked.stderr.strip()[-160:]!r} "
                        f"unknown={unknown.returncode}:{unknown.stderr.strip()[-160:]!r} events={before}->{after_j} "
                        f"read={read.stderr.strip()[-160:]!r}")
    # --- (k) an ask of a closed task: an info said closed, never a question -- s.1587 ----------------------------
    h.declare("closed", "---\nagents: |\n  lead agents/lead\nroot: lead\nschedule: off\n---\nAsk the owner.\n")
    h.written("closed", CLOSED, AT)
    box_k = inbox("closed")
    line_k = h.call("team", "inbox", "closed").stdout.strip()
    face_k = h.face("closed").get("waiting") or {}
    listed_k = h.call("team", "status", "--json").stdout.splitlines()
    asks_k = next((json.loads(one).get("asks") for one in listed_k if one.startswith("{")
                   and json.loads(one).get("team") == "closed"), None)
    reply_k = h.call("team", "post", "closed", "--task", "T1", "--reply", "4", "--message", "late")
    read_k = h.call("team", "inbox", "closed", "--seen", "--id", "4")
    one_k = inbox("closed")
    seen_k = h.call("team", "inbox", "closed", "--seen")
    after_k = inbox("closed")
    if ([one.get("id") for one in box_k.get("questions") or []] == [8]
            and [(one.get("id"), one.get("task"), one.get("closed")) for one in box_k.get("infos") or []]
            == [(4, "T1", True), (11, "T3", True)]
            and len(line_k.split(" · ")) == 4                  # T1 done, the question, two infos, one returned
            and [one.get("at") for sort in ("questions", "infos", "done") for one in box_k.get(sort) or []] == [AT] * 4
            and [(one.get("id"), one.get("at")) for one in box_k.get("returned") or []] == [(13, RETURNED_AT)]
            and [one.get("id") for one in face_k.get("questions") or []] == [8] and asks_k == 1
            and reply_k.returncode == 2 and "task-closed" in reply_k.stderr
            and read_k.returncode == 0 and [one.get("message") for one in h.events("closed")
                                            if one.get("kind") == "inbox-read"] == [4]
            and [(one.get("id"), one.get("closed")) for one in one_k.get("infos") or []] == [(11, True)]
            and seen_k.returncode == 0
            and [one.get("id") for one in after_k.get("questions") or []] == [8] and not after_k.get("infos")
            and not after_k.get("returned")):
        held("(k) an ask of a closed task", "T2's ask #8 alone a question -- inbox, status --json, asks 1, the line in 4 parts; "
             "T1's #4 and T3's #11 infos said closed; a reply to #4 refused task-closed (s.1587); --seen --id 4 wrote "
             "inbox-read, --json without #4, #11 kept (s.1704); --seen took the rest; each dated by its event's "
             f"at, the post #13 returned by its own {RETURNED_AT} (s.1706)")
    else:
        failures.append(f"  ✗ (k) an ask of a closed task  box={box_k} line={line_k!r} face={face_k} asks={asks_k} "
                        f"reply={reply_k.returncode}:{reply_k.stderr.strip()[-120:]!r} "
                        f"read={read_k.returncode}:{read_k.stderr.strip()[-120:]!r} one={one_k} after={after_k}")
    return 0
