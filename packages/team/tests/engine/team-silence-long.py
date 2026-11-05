"""Scenario `team-silence-long` -- 1 case (batch le-silence-au-detecteur, team 0.48.0; study § 19, row 115; KSD11): a long
task informed is never stopped -- a case apart, eleven launches of the witness.
- (a) the root keeps its opening ten exchanges, an `info` to the owner at each one: ten relances `owed`, no reminder, no
  `silence`, no notice, `waiting_on` never `owner`; then it answers and T1 resolves -- J10
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
        "long": [{"sleep": 0.1, "body": {"info": {"to": "house", "text": f"step {n}"}}} for n in range(1, 11)]
                + [{"sleep": 0.1, "body": {"re": "DO", "text": "all done"}}]})
    by_kind, all_ended, result_of = T.by_kind, T.all_ended, T.result_of
    module = h.module()

    def ended(found: list[dict]) -> bool:
        return bool(by_kind(found, "done", task="T1")) and all_ended(found)

    def member_face(name: str, member: str, now: str | None = None) -> dict:
        return next((one for one in h.face(name, now=now).get("members") or [] if one.get("member") == member), {})

    h.declare("longtask", "---\nagents: |\n  long agents/long\nroot: long\nschedule: off\n---\nA long task.\n")
    started = {"longtask": h.call("team", "start", "longtask", "--message", "do it", *h.harnessed)}

    # --- (a) a long task informed is never stopped ----------------------------------------------------------------
    done_a = h.settled("longtask", ended, timeout=120)
    found = h.events("longtask")
    relances = [one.get("relance") for one in T.intents_of(found, "long")]
    infos = [one for one in by_kind(found, "post", verb="info", **{"from": "long"})]
    if (started["longtask"].returncode == 0 and done_a and relances == [None] + ["owed"] * 10 and len(infos) == 10
            and not by_kind(found, "silence") and not by_kind(found, "post", verb="notice")
            and not [one for one in by_kind(found, "wake-intent") if one.get("relance") == "reminder"]
            and result_of(found, "T1") == "all done"):
        held("(a) a long task informed is never stopped", "long keeps the opening ten exchanges, an info at each: ten relances "
             "owed, no reminder, no silence, no notice; then 'all done' -- J10")
    else:
        failures.append(f"  ✗ (a) a long task informed     rc={started['longtask'].returncode} done={done_a} relances={relances} "
                        f"infos={len(infos)} silences={by_kind(found, 'silence')} notices={by_kind(found, 'post', verb='notice')} "
                        f"result={result_of(found, 'T1')!r}")

    return 0
