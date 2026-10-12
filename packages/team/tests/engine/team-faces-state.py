"""Scenario `team-faces-state` -- 3 case(s) (batch les-faces-de-l-equipe, 2026-10-11: row 81 of the study § 18,
team 0.30.0): `team status --json` says the team's `state` -- derived from the replay, never written -- and, while
it waits, `waiting_on`: every guard that holds, in the order `woken_on` judges them (`members`, `wakes`, `budget`),
then `owner`, `blocked`, `due`; the object and the team's line say the same. The badge and the season are
`team-faces`'s.
- (a) the state and its guards (KFE7): `flow` -- `never` before its start; `waiting [due]` after a start without
  a tick; `working` while m plays; `waiting [members, owner]` once r1 asked the owner and r2 answered; `idle` once
  T1 is resolved; the guards of the bounds and of a failure are `team-faces-guards`'s
- (b) the wake-ups of a task: while r1 and r2 play on T1, `tasks[T1].running` carries both -- member, tag, run,
  since, allowance --, then `[]` at their end
- (c) a team paused (batch la-pause-de-l-equipe, row 83, team 0.32.0): `team pause` on a team waiting [due] -- the
  object and the line say `paused`, `waiting_on []`, `paused {by, at}`; the text says `paused since`; `team resume
  --no-tick` -- `waiting [due]` again, no `paused`
"""
from __future__ import annotations

import json
import time

from tests.harness import cli, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 1.0, "body": {"do": ["r1", "r2"]}}, {"sleep": 0.1, "body": {"done": "both"}}],
        "r1": [{"sleep": 1.5, "body": {"ask": {"to": "house", "text": "which branch?"}}},
               {"sleep": 0.1, "body": {"done": True}}],
        "r2": [{"sleep": 1.5, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def both(name: str) -> tuple[dict, dict]:
        """-> (the object, the team's line) of `team status --json`."""
        alone = cli(h.engine, "--instance", str(h.house), "team", "status", name, "--json", cwd=h.ws, env=h.env)
        every = cli(h.engine, "--instance", str(h.house), "team", "status", "--json", cwd=h.ws, env=h.env)
        try:
            obj = json.loads(alone.stdout)
            lines = [json.loads(one) for one in every.stdout.splitlines() if one.strip()]
        except ValueError:
            return {}, {}
        return obj, next((one for one in lines if one.get("team") == name), {})

    def said(name: str) -> tuple:
        obj, line = both(name)
        if (obj.get("state"), obj.get("waiting_on")) != (line.get("state"), line.get("waiting_on")):
            return ("object and line differ", obj.get("state"), line.get("state"))
        return obj.get("state"), tuple(obj.get("waiting_on") or ())

    def reply(name: str, task: str = "T1") -> None:
        ask = next((one["id"] for one in by_kind(h.events(name), "post", verb="ask")), -1)
        h.call("team", "post", name, "--task", task, "--reply", str(ask), "--message", "main")

    def under_way(found: list[dict]) -> int:
        ended = {one.get("tag") for one in found if one.get("kind") in ("wake-ended", "wake-failed", "wake-killed")}
        return sum(1 for one in found if one.get("kind") == "wake-intent" and one.get("tag") not in ended)

    def watch(name: str, predicate, timeout: float = 30.0) -> dict:
        """-> the first object of `status <name> --json` that satisfies `predicate`, {} past the bound."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            obj, _ = both(name)
            if predicate(obj):
                return obj
            time.sleep(0.1)
        return {}

    # --- (a) the state and its guards ---------------------------------------------------------------------
    h.declare("flow", "---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\n"
                      "root: m\nschedule: off\n---\nFlow.\n")
    seen = {"never": said("flow")}
    h.call("team", "start", "flow", "--message", "review PR 13", *h.harnessed, "--no-tick")
    seen["due"] = said("flow")
    h.call("team", "tick", "flow")
    seen["working"] = said("flow") if under_way(h.events("flow")) else ("not caught",)
    running = watch("flow", lambda obj: len(next((t.get("running") or [] for t in obj.get("tasks") or []
                                                  if t.get("id") == "T1"), [])) == 2
                    and all(one.get("run") for t in obj.get("tasks") or [] for one in t.get("running") or []))
    asked = h.settled("flow", lambda found: bool(by_kind(found, "post", verb="ask")) and all_ended(found)
                      and bool(by_kind(found, "terminal", agent="r2")), 60)
    seen["members"] = said("flow")
    t1_ended = next((t.get("running") for t in both("flow")[0].get("tasks") or [] if t.get("id") == "T1"), None)
    reply("flow")
    h.settled("flow", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    seen["idle"] = said("flow")
    wanted = {"never": ("never", ()), "due": ("waiting", ("due",)), "working": ("working", ()),
              "members": ("waiting", ("members", "owner")), "idle": ("idle", ())}
    if seen == wanted:
        held("(a) the state and its guards", "never, waiting [due], working, waiting [members, owner], idle -- "
             "the object and the line alike, KFE7")
    else:
        failures.append(f"  ✗ (a) the state              " + " ".join(f"{key}={seen.get(key)}" for key in wanted
                                                                     if seen.get(key) != wanted[key]))

    # --- (b) the wake-ups of a task -----------------------------------------------------------------------
    on_t1 = next((t.get("running") for t in running.get("tasks") or [] if t.get("id") == "T1"), [])
    if (asked and sorted(one.get("member") for one in on_t1) == ["r1", "r2"]
            and all(one.get("tag") and one.get("run") and one.get("since") and "allowance" in one for one in on_t1)
            and t1_ended == []):
        held("(b) the wake-ups of a task", f"T1 running {[(one['member'], one['run']) for one in on_t1]}, then []")
    else:
        failures.append(f"  ✗ (b) running                asked={asked} running={on_t1} after={t1_ended}")

    # --- (c) a team paused ------------------------------------------------------------------------------
    h.declare("rest", "---\nagents: |\n  m agents/m\nroot: m\nschedule: off\n---\nRest.\n")
    h.call("team", "start", "rest", "--message", "later", *h.harnessed, "--no-tick")
    due = said("rest")
    paused = h.call("team", "pause", "rest")
    stood = said("rest")
    obj, line = both("rest")
    text = h.call("team", "status", "rest").stdout
    resumed = h.call("team", "resume", "rest", "--no-tick")
    back = said("rest")
    lifted = both("rest")[0]
    if (due == ("waiting", ("due",)) and paused.returncode == 0 and stood == ("paused", ())
            and (obj.get("paused") or {}).get("by") == "house" and (obj.get("paused") or {}).get("at")
            and (line.get("paused") or {}).get("by") == "house" and "paused since " in text
            and resumed.returncode == 0 and back == ("waiting", ("due",)) and not lifted.get("paused")):
        held("(c) a team paused", "waiting [due], then paused (object and line, paused {by, at}, the text), "
             "then waiting [due] again")
    else:
        failures.append(f"  ✗ (c) paused                 due={due} rc={paused.returncode}/{resumed.returncode} stood={stood} "
                        f"paused={obj.get('paused')}/{line.get('paused')} back={back} {paused.stderr.strip()[-160:]!r}")
    return 0
