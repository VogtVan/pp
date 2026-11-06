"""Scenario `team-info` -- 4 case(s) (batch le-message-info, team 0.47.0; study § 19, row 114): the INFO, an act
without debt -- `{"info": {"to": <member|principal>, "text"}}` of any member or principal to any member or principal.
- (a) the root informs its principal and keeps the opening: the info is routed (no `wake-refused`), it posts no
  question, the team keeps working -- the root is RELANCED on its opening (a relance proves it waits on nobody: the
  info put no arc toward the owner), `waiting_on` never says `owner`, and the task resolves at the relance
- (e) the owner's box says the infos: `inbox --json` `infos [{id, from, task, text}]`, the line `1 info`, `--seen`
  clears it, the team never waits on the owner for it
- (f) `status --json` says the verb: `owner_inbox` and `waiting.infos` carry the info
- (g) a journal written before team 0.47.0 reads: its `note` is said `info` (`was: note`) by `log --json`, `pending`
  and the inbox count, and it opens no debt (`owes` empty before any delivery); the marble of the house measured
`team-info-quiet` (a member's info launches nobody) and `team-info-wakes` (a principal's, a refused act, a re to an
info) carry the other cases.
"""
from __future__ import annotations

import json
import time

from tests.harness import support

T = support(__file__, "team")

AT = "2026-11-03T20:00:00+00:00"
BEFORE = [                                                   # a journal team 0.46.4 wrote: the principal's note
    {"kind": "team-started", "agents": {"vet": "agents/vet"}, "reports": [], "root": "vet", "principals": [],
     "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None, "digest": "000000000000"},
    {"kind": "task", "task": "T1", "from": "house", "to": "vet", "text": "price it"},
    {"kind": "post", "task": "T1", "from": "house", "to": "vet", "verb": "do", "text": "price it"},
    {"kind": "post", "task": "T1", "from": "house", "to": "vet", "verb": "note", "text": "the deadline moved"},
]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "boss": [{"sleep": 0.1, "body": {"info": {"to": "house", "text": "started: ten exchanges ahead"}}},
                 {"sleep": 0.1, "body": {"re": "DO", "text": "all done"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of

    def inbox(name: str) -> dict:
        said = h.call("team", "inbox", name, "--json").stdout.strip()
        try:
            return json.loads(said) if said else {}
        except ValueError:
            return {"unreadable": said}

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    h.declare("progress", "---\nagents: |\n  boss agents/boss\nroot: boss\nschedule: off\n---\nSay where you stand.\n")
    h.declare("old", "---\nagents: |\n  vet agents/vet\nroot: vet\nschedule: off\n---\nOf before.\n")
    started = h.call("team", "start", "progress", "--message", "do it", *h.harnessed)

    # --- (a) the root informs its principal and keeps the opening ------------------------------------------
    done_a = h.settled("progress", ended, timeout=60)
    found = h.events("progress")
    opening = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "house"})), None)
    infos = [(one.get("from"), one.get("to"), one.get("task"), one.get("text")) for one in by_kind(found, "post", verb="info")]
    intents = [(one.get("agent"), one.get("relance"), one.get("messages")) for one in by_kind(found, "wake-intent")]
    face = h.face("progress")
    if (started.returncode == 0 and done_a and opening is not None
            and infos == [("boss", "house", "T1", "started: ten exchanges ahead")]
            and not by_kind(found, "wake-refused") and not by_kind(found, "post", verb="ask")
            and not by_kind(found, "post", verb="notice")
            and intents == [("boss", None, [opening]), ("boss", "owed", [opening])]
            and result_of(found, "T1") == "all done" and face.get("state") == "idle"):
        held("(a) the root informs and keeps the opening", f"info boss -> house on T1 routed (no wake-refused, no ask, no "
             f"notice); boss relanced on #{opening} (relance owed: it waits on nobody, no arc to the owner), T1 'all done'")
    else:
        failures.append(f"  ✗ (a) the root informs         rc={started.returncode} done={done_a} infos={infos} "
                        f"refused={[one.get('why') for one in by_kind(found, 'wake-refused')]} intents={intents} "
                        f"result={result_of(found, 'T1')!r} state={face.get('state')}")

    # --- (e) the owner's box says the info, holds nobody -----------------------------------------------------
    box = inbox("progress")
    line = h.call("team", "inbox", "progress").stdout.strip()
    seen = h.call("team", "inbox", "progress", "--seen")
    after = inbox("progress")
    info_id = next((one["id"] for one in by_kind(found, "post", verb="info")), -1)
    if ([(one.get("id"), one.get("from"), one.get("task"), one.get("text")) for one in box.get("infos") or []]
            == [(info_id, "boss", "T1", "started: ten exchanges ahead")]
            and not box.get("questions") and not box.get("notices") and "1 info" in line and "T1 done" in line
            and seen.returncode == 0 and not after.get("infos")
            and "owner" not in (face.get("waiting_on") or [])):
        held("(e) the owner's box says the info", f"inbox --json infos [#{info_id} from boss on T1], the line says "
             f"'1 info'; --seen clears it; waiting_on {face.get('waiting_on')}")
    else:
        failures.append(f"  ✗ (e) the owner's box          box={box} line={line!r} after={after} "
                        f"waiting_on={face.get('waiting_on')} {seen.stderr.strip()[-120:]!r}")

    # --- (f) status --json says the verb --------------------------------------------------------------------------
    owner_box = [(one.get("id"), one.get("verb"), one.get("from")) for one in face.get("owner_inbox") or []
                 if one.get("verb") == "info"]
    waits = face.get("waiting") or {}
    if (owner_box == [(info_id, "info", "boss")]
            and [(one.get("id"), one.get("from"), one.get("task")) for one in waits.get("infos") or []] == [(info_id, "boss", "T1")]):
        held("(f) status --json says the verb", f"owner_inbox #{info_id} info from boss; waiting.infos [#{info_id}]")
    else:
        failures.append(f"  ✗ (f) status --json            owner_inbox={owner_box} waiting={waits}")

    # --- (g) a journal written before reads its note as an info ------------------------------------------------
    h.written("old", BEFORE, AT)
    logged = h.call("team", "log", "old", "--json")
    said = {}
    for raw in logged.stdout.splitlines():
        try:
            one = json.loads(raw)
        except ValueError:
            continue
        if one.get("event") == "post":
            said[one.get("id")] = (one.get("verb"), one.get("was"))
    face_o = h.face("old")
    member_o = next((one for one in face_o.get("members") or [] if one.get("member") == "vet"), {})
    text_o = h.call("team", "status", "old").stdout
    marble = h.house / ".sys" / "system.common.md"
    weight = len(marble.read_bytes()) if marble.is_file() else -1
    if (logged.returncode == 0 and said.get(4) == ("info", "note") and said.get(3) == ("do", None)
            and [(one.get("id"), one.get("verb")) for one in member_o.get("pending") or []] == [(3, "do"), (4, "info")]
            and member_o.get("owes") == []
            and "inbox 2 (do 1, info 1)" in text_o):
        held("(g) a journal of before reads", "its note #4 said info (was note) by log --json, pending and the count "
             f"'inbox 2 (do 1, info 1)'; nothing delivered yet, nothing owed; the house's marble "
             f"{weight} bytes")
    else:
        failures.append(f"  ✗ (g) a journal of before      rc={logged.returncode} said={said} "
                        f"pending={member_o.get('pending')} owes={member_o.get('owes')} text={text_o[-200:]!r}")
    return 0
