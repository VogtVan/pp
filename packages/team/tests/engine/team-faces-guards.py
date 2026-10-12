"""Scenario `team-faces-guards` -- 1 case(s) (batch les-faces-de-l-equipe, 2026-10-11: row 81 of the study § 18,
team 0.30.0): the guards of `waiting_on` a bound or a failure holds, in the order `woken_on` judges them, then
`owner` and `blocked`; the object and the team's line say the same. The state along a team is `team-faces-state`'s.
- (a) the guards of the bounds and of a failure (KFE7): `dear` (`budget-wakes: 1`): `waiting [budget, owner]`;
  `count` (`wakes: 1`): `waiting [wakes, owner]`; `fail` (`retries: 0`, its root dead, reaped by a tick at hand
  under `schedule: off`): `waiting [owner, blocked]`
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "k": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which day?"}}}, {"sleep": 0.1, "body": {"done": "x"}}],
        "w": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which week?"}}}, {"sleep": 0.1, "body": {"done": "y"}}],
        "f": [{"sleep": 0.1, "body": "crash"}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def said(name: str) -> tuple:
        alone = cli(h.engine, "--instance", str(h.house), "team", "status", name, "--json", cwd=h.ws, env=h.env)
        every = cli(h.engine, "--instance", str(h.house), "team", "status", "--json", cwd=h.ws, env=h.env)
        try:
            obj = json.loads(alone.stdout)
            line = next((one for one in (json.loads(x) for x in every.stdout.splitlines() if x.strip())
                         if one.get("team") == name), {})
        except ValueError:
            return ("unreadable",)
        if (obj.get("state"), obj.get("waiting_on")) != (line.get("state"), line.get("waiting_on")):
            return ("object and line differ", obj.get("state"), line.get("state"))
        return obj.get("state"), tuple(obj.get("waiting_on") or ())

    def reply(name: str, task: str = "T1") -> None:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        h.call("team", "post", name, "--task", task, "--reply", str(ask), "--message", "main")

    # --- (a) the guards of the bounds and of a failure ---------------------------------------------------
    seen = {}
    h.declare("dear", "---\nagents: |\n  k agents/k\nroot: k\nbudget-wakes: 1\nschedule: off\n---\nOne wake-up.\n")
    h.call("team", "start", "dear", "--message", "cut the branch", *h.harnessed)
    h.settled("dear", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    reply("dear")
    h.settled("dear", lambda found: bool(by_kind(found, "budget-spent")) and all_ended(found), 30)
    seen["budget"] = said("dear")
    h.declare("count", "---\nagents: |\n  w agents/w\nroot: w\nwakes: 1\nschedule: off\n---\nOne wake-up.\n")
    h.call("team", "start", "count", "--message", "date the release", *h.harnessed)
    h.settled("count", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found), 60)
    reply("count")
    h.settled("count", lambda found: bool(by_kind(found, "wakes-spent")) and all_ended(found), 30)
    seen["wakes"] = said("count")
    h.declare("fail", "---\nagents: |\n  f agents/f\nroot: f\nretries: 0\nschedule: off\n---\nIt dies.\n")
    h.call("team", "start", "fail", "--message", "do it", *h.harnessed)
    h.tick_until("fail", lambda found: bool(by_kind(found, "terminal", agent="f")))   # no schedule: the owner reaps
    seen["blocked"] = said("fail")
    wanted = {"budget": ("waiting", ("budget", "owner")), "wakes": ("waiting", ("wakes", "owner")),
              "blocked": ("waiting", ("owner", "blocked"))}
    if seen == wanted:
        held("(a) the guards of the bounds and of a failure", "[budget, owner], [wakes, owner], [owner, blocked] -- "
             "the object and the line alike, KFE7")
    else:
        failures.append("  ✗ (a) the guards             " + " ".join(f"{key}={seen.get(key)}" for key in wanted
                                                                    if seen.get(key) != wanted[key]))
    return 0
