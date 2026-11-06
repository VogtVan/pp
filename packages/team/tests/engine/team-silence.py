"""Scenario `team-silence` -- 3 case(s) (batch le-silence-au-detecteur, team 0.48.0; study § 19, row 115): the silence
as the detector's second input -- its count, its limit, a mute worker. `team-silence-long` (a long task informed) and
`team-silence-mute` (a mute root reminded, suspected, tried) carry the other cases.
- (c) a mute worker unblocks its supervisor: under `silence: 1` w is reminded then suspected; the `do` it owes is answered
  in its place (`suspected: true`), sup is woken and closes T1; no `preempted` anywhere -- KSD13
- (d) the count is right, read from the journal alone: parked exchanges count, a standing relaunch does not, an act of the
  member, a `resume` and a season set it to zero; `status --json` read twice without a tick is the same bytes -- KSD12
- (e) the limit: `silence: 0` refuses `team-invalid`; `team start --silence 5` is the season's, `--member s --silence 2`
  the member's, over it
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
        "sup": [{"sleep": 0.1, "body": {"do": ["w"]}}, {"sleep": 0.1, "body": {"re": "DO", "text": "closed without w"}}],
        "w": [{"sleep": 0.1, "body": []}] * 5,
        "r": [{"sleep": 0.1, "body": {"do": ["s"]}}],
        "s": [{"sleep": 4.0, "body": []}] * 3})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    module = h.module()

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    def member_face(name: str, member: str, now: str | None = None) -> dict:
        return next((one for one in h.face(name, now=now).get("members") or [] if one.get("member") == member), {})

    h.declare("stuck", "---\nagents: |\n  sup agents/sup\n  w agents/w\nreports: |\n  w -> sup\nroot: sup\nschedule: off\n"
                       "silence: 1\n---\nDelegate, then conclude.\n")
    started = {"stuck": h.call("team", "start", "stuck", "--message", "do it", *h.harnessed)}

    # --- (c) a mute worker unblocks its supervisor ---------------------------------------------------------------
    done_c = h.settled("stuck", ended, timeout=90)
    found = h.events("stuck")
    to_w = next((one["id"] for one in by_kind(found, "post", verb="do", **{"from": "sup"})), None)
    relances_w = [one.get("relance") for one in T.intents_of(found, "w")]
    in_place = [one for one in by_kind(found, "post", verb="re", **{"from": "w"}) if one.get("by") == "tick"]
    preempted = [one for one in found if one.get("preempted")]
    if (started["stuck"].returncode == 0 and done_c and relances_w == [None, "reminder"]
            and [(one.get("agent"), one.get("exchanges")) for one in by_kind(found, "silence")] == [("w", 2)]
            and [(one.get("re"), one.get("suspected"), one.get("to")) for one in in_place] == [(to_w, True, "sup")]
            and not preempted and not by_kind(found, "post", verb="notice") and result_of(found, "T1") == "closed without w"):
        held("(c) a mute worker unblocks its supervisor", f"w reminded after one silent exchange, silence at the second; its do "
             f"#{to_w} answered in its place (suspected), sup closes T1; nothing preempted, no notice")
    else:
        failures.append(f"  ✗ (c) a mute worker            rc={started['stuck'].returncode} done={done_c} relances={relances_w} "
                        f"silences={[(one.get('agent'), one.get('exchanges')) for one in by_kind(found, 'silence')]} "
                        f"in_place={[(one.get('re'), one.get('suspected'), one.get('to')) for one in in_place]} "
                        f"preempted={len(preempted)} result={result_of(found, 'T1')!r}")

    # --- (d) the count, read from the journal alone ---------------------------------------------------------------
    opening = [{"kind": "task", "task": "T1", "from": "house", "to": "m", "text": "count it"},
               {"kind": "post", "task": "T1", "from": "house", "to": "m", "verb": "do", "text": "count it"}]
    parked = exchange("a", "T1", [3], "parked") + exchange("b", "T1", [], "standing") + exchange("c", "T1", [], "parked")
    counts = {}
    h.declare("count", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\nCount.\n")
    h.written("count", [STARTED] + opening + parked, AT)
    counts["parked"] = member_face("count", "m").get("silence")
    first = h.call("team", "status", "count", "--json").stdout
    second_read = h.call("team", "status", "count", "--json").stdout
    acted = parked + [{"kind": "post", "task": "T1", "from": "m", "to": "house", "verb": "info", "text": "at work"}] \
        + exchange("d", "T1", [], "parked")
    h.written("count", [STARTED] + opening + acted, AT)
    counts["acted"] = member_face("count", "m").get("silence")
    h.written("count", [STARTED] + opening + parked + [{"kind": "resumed", "task": "T1", "by": "house", "from": ["stopped"]}], AT)
    counts["resumed"] = member_face("count", "m").get("silence")
    h.written("count", [STARTED] + opening + parked + [STARTED], AT)
    counts["season"] = member_face("count", "m").get("silence")
    wanted = {"parked": [{"task": "T1", "exchanges": 2, "limit": getattr(module, "DEFAULT_SILENCE", 3)}],
              "acted": [{"task": "T1", "exchanges": 1, "limit": getattr(module, "DEFAULT_SILENCE", 3)}],
              "resumed": [{"task": "T1", "exchanges": 0, "limit": getattr(module, "DEFAULT_SILENCE", 3)}],
              "season": [{"task": "T1", "exchanges": 0, "limit": getattr(module, "DEFAULT_SILENCE", 3)}]}
    if counts == wanted and first and first == second_read:
        held("(d) the count is right", "two parked exchanges count 2 (the standing relaunch not); an info of m then one parked "
             "counts 1; a resume, a season count 0; status --json twice the same bytes -- KSD12")
    else:
        failures.append(f"  ✗ (d) the count                counts={counts} same={first == second_read}")

    # --- (e) the limit: TEAM.md, the season, the profile -----------------------------------------------------------
    h.declare("bad", "---\nagents: |\n  b agents/b\nroot: b\nschedule: off\nsilence: 0\n---\nBad.\n")
    refused = h.call("team", "start", "bad", "--message", "x", *h.harnessed)
    h.declare("lim", "---\nagents: |\n  r agents/r\n  s agents/s\nreports: |\n  s -> r\nroot: r\nschedule: off\n---\nLimits.\n")
    seasoned = h.call("team", "start", "lim", "--message", "do it", "--silence", "5", *h.harnessed,
                      "--member", "s", "--silence", "2")
    h.settled("lim", lambda found: bool(T.by_kind(found, "wake-launched", agent="s")), timeout=60)   # s plays: it owes
    face_e = h.face("lim")
    limits_e = {one.get("member"): [(s.get("task"), s.get("limit")) for s in one.get("silence") or []]
                for one in face_e.get("members") or []}
    if (refused.returncode == 2 and "team-invalid" in refused.stderr and "silence" in refused.stderr
            and seasoned.returncode == 0 and (face_e.get("limits") or {}).get("silence") == 5
            and limits_e.get("r") == [("T1", 5)] and limits_e.get("s") == [("T1", 2)]):
        held("(e) the limit", "silence: 0 refuses team-invalid; --silence 5 is the season's limit (r), --member s --silence 1 "
             "the member's (s, 2)")
    else:
        failures.append(f"  ✗ (e) the limit                rc={refused.returncode}/{seasoned.returncode} "
                        f"{refused.stderr.strip()[-120:]!r} limits={face_e.get('limits')} per_member={limits_e} "
                        f"owes={[(one.get('member'), one.get('owes')) for one in face_e.get('members') or []]} "
                        f"intents={[(one.get('agent'), one.get('relance')) for one in T.by_kind(h.events('lim'), 'wake-intent')]} "
                        f"refused={[one.get('why') for one in T.by_kind(h.events('lim'), 'wake-refused')]} "
                        f"{seasoned.stderr.strip()[-160:]!r}")
    return 0
