"""Scenario `team-silence-mute` -- 1 case (batches le-silence-au-detecteur, team 0.48.0, and le-battement-du-reveil; study
§ 19, row 115): a mute debtor is relanced, then suspected, then tried without a gesture of the principal.
- (b) a root that says nothing is woken, then relanced `owed` twice -- no other kind of relance, the head of each
  opening on the module's RELANCED, the beats 3, 2, 1 --, then `silence {passages: 3}` at its third silent passage --
  suspected (`health.cause: silence`), the team's notice about it to the owner, which holds
  no wait (`waiting_on` says `suspected`, never `owner`) --; a tick within the interval wakes nobody; past it the root is
  TRIED (`relance: tried`, the beat 1) while the owner never answered; a silent try is one more fall (`wake-ended` alone
  lifts nothing);
  the try that answers resolves T1 and lifts the suspicion -- J9
"""
from __future__ import annotations

import json

from tests.harness import support

T = support(__file__, "team")

AT = "2026-11-03T21:00:00+00:00"
STARTED = {"kind": "team-started", "agents": {"m": "agents/m"}, "reports": [], "root": "m", "principals": [],
           "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None, "digest": "000000000000"}


def exchange(tag: str, task: str, messages: list, state: str) -> list[dict]:
    """-> one exchange of m on the task as the journal keeps it: its intent, its launch, its end in `state`."""
    return [{"kind": "wake-intent", "tag": tag, "agent": "m", "path": "agents/m", "task": task, "run": "k1", "index": 1,
             "messages": messages},
            {"kind": "wake-launched", "tag": tag, "agent": "m", "run": "k1", "pid": 1, "launch": 1},
            {"kind": "wake-ended", "tag": tag, "agent": "m", "run": "k1", "launch": 1, "state": state, "cost": 0.01}]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "mute": [{"sleep": 0.1, "body": []}] * 4 + [{"sleep": 0.1, "body": {"re": "DO", "text": "at last"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    module = h.module()

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    def member_face(name: str, member: str, now: str | None = None) -> dict:
        return next((one for one in h.face(name, now=now).get("members") or [] if one.get("member") == member), {})

    h.declare("mutetask", "---\nagents: |\n  mute agents/mute\nroot: mute\nschedule: off\n---\nSay nothing.\n")
    started = {"mutetask": h.call("team", "start", "mutetask", "--message", "do it", *h.harnessed)}

    # --- (b) a mute debtor: relanced, suspected, tried -------------------------------------------------------------
    fell = h.settled("mutetask", lambda found: bool(by_kind(found, "silence")) and all_ended(found), timeout=90)
    found = h.events("mutetask")
    relances_m = [one.get("relance") for one in T.intents_of(found, "mute")]
    silence = next((one for one in by_kind(found, "silence")), {})
    told = [one for one in by_kind(found, "post", verb="notice") if one.get("about") == "mute"]
    prompts = h.prompts_of("mute")
    relanced_heads = [module.RELANCED in one.split("▌ pp · run", 1)[0] for one in prompts[:3]]
    beats_m = [(one.get("continued"), one.get("beat")) for one in T.intents_of(found, "mute")]
    face_b = h.face("mutetask")
    health_b = member_face("mutetask", "mute").get("health") or {}
    quiet = h.call("team", "tick", "mutetask")                       # within the interval: nobody woken
    unmoved = len(h.events("mutetask")) == len(found)
    later = T.local_after(silence["at"], 6).isoformat(timespec="seconds") if silence else None
    h.tick_until("mutetask", lambda found: len(by_kind(found, "silence")) >= 2 and all_ended(found), timeout=60, now=later)
    found = h.events("mutetask")
    tries = [one.get("relance") for one in T.intents_of(found, "mute") if one.get("relance") == "tried"]
    second = by_kind(found, "silence")
    health_try = member_face("mutetask", "mute", now=later).get("health") or {}
    later2 = T.local_after(second[-1]["at"], 11).isoformat(timespec="seconds") if len(second) > 1 else later
    h.tick_until("mutetask", ended, timeout=60, now=later2)
    found = h.events("mutetask")
    health_end = member_face("mutetask", "mute", now=later2).get("health") or {}
    tries = [one.get("relance") for one in T.intents_of(found, "mute") if one.get("relance") == "tried"]
    kinds = {one.get("relance") for one in T.intents_of(found, "mute")}
    if (started["mutetask"].returncode == 0 and fell and relances_m[:3] == [None, "owed", "owed"]
            and relanced_heads == [False, True, True] and beats_m[:3] == [(False, 3), (False, 2), (False, 1)]
            and kinds <= {None, "owed", "tried"}
            and [one.get("beat") for one in T.intents_of(found, "mute") if one.get("relance") == "tried"] == [1, 1]
            and (silence.get("agent"), silence.get("task"), silence.get("passages")) == ("mute", "T1", 3)
            and len(told) == 1 and told[0].get("to") == "house" and told[0].get("cause") == "silence"
            and health_b.get("suspected") is True and health_b.get("cause") == "silence" and health_b.get("falls") == 1
            and "suspected" in (face_b.get("waiting_on") or []) and "owner" not in (face_b.get("waiting_on") or [])
            and quiet.returncode == 0 and unmoved
            and tries == ["tried", "tried"] and len(second) == 2 and second[1].get("passages") == 1
            and health_try.get("suspected") is True and health_try.get("falls") == 2
            and not [one for one in by_kind(found, "post", **{"from": "house"}) if one.get("re") is not None]
            and result_of(found, "T1") == "at last" and health_end.get("falls") == 0 and health_end.get("suspected") is False):
        held("(b) a mute debtor: relanced, suspected, tried", f"relances {relances_m[:3]}, their heads on RELANCED, the "
             f"beats 3, 2, 1; silence "
             f"#{silence['id']} (3 passages), notice about mute to house (cause silence), health {health_b}; a tick within the "
             "interval writes nothing; past it: tried, silent -> one more fall (falls 2, the wake-ended lifts nothing); tried "
             "again: 'at last', falls 0 -- the owner never answered -- J9")
    else:
        failures.append(f"  ✗ (b) a mute debtor            rc={started['mutetask'].returncode} fell={fell} relances={relances_m} "
                        f"heads={relanced_heads} beats={beats_m} silence={silence} "
                        f"told={[(one.get('to'), one.get('cause')) for one in told]} "
                        f"health={health_b} waiting_on={face_b.get('waiting_on')} quiet={quiet.returncode}/{unmoved} "
                        f"tries={tries} second={[one.get('passages') for one in second]} health_try={health_try} "
                        f"health_end={health_end} result={result_of(found, 'T1')!r} "
                        f"all={[(one.get('relance'), one['id']) for one in T.intents_of(found, 'mute')]} "
                        f"silences={[(one['id'], one.get('passages')) for one in by_kind(found, 'silence')]}")

    return 0
