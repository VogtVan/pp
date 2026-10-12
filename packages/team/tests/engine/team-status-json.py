"""Scenario `team-status-json` -- 3 case(s) (batch le-status-des-equipes of plan ui, 2026-10-10: team
0.20.0; realigned by les-faces-de-l-equipe, team 0.30.0): `team status --json` is the face a program reads -- ONE
object for a team named, one line per team declared without a name; the text keeps its bytes. A team `crew` (m
root, r1 r2 reporting to m, the mandator pm; `daily every weekday 09:30 with r1 r2 -> m any 1`, `retro after daily
with r1 -> m`) and a team `idle` declared, never started; the clock frozen by `PP_NOW` on Thursday 2026-10-01. The
ceremonies' rhythm is `team-status-rhythm`'s; the state, the season and the launch are `team-faces`'s.
- the team: after `start --no-tick`, the object carries every key, T1 held by m, m's `do` pending;
  after T1 (m delegates to r1, r1 answers, m concludes), T1 resolved with its delegation terminal,
  r2 -- never woken -- has m's and r1's answers unseen, the owner's waiting box says T1 done
- every team: without a name, one line per team declared -- `idle` as `{team, started: null, state: never,
  waiting_on: [], required}` (the packages a member may not switch off, team 0.32.1), which `status idle --json` says
  too; crew's line counts what waits for the owner
- refused: a flag of no verb's, and a team nobody declared
"""
from __future__ import annotations

import json

from tests.harness import cli, support

T = support(__file__, "team")

CREW = ("---\nagents: |\n  m agents/m\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> m\nroot: m\n"
        "principals: |\n  pm\nceremonies: |\n  daily every weekday 09:30 with r1 r2 -> m any 1\n"
        "  retro after daily with r1 -> m\n---\nKeep the beat.\n")
KEYS = {"team", "owner", "principals", "started", "changed", "limits", "schedule", "cost", "budget_spent", "budget",
        "wakes", "last", "tasks", "members", "ceremonies", "owner_inbox", "waiting", "state", "waiting_on", "season",
        "launch", "paused", "required"}
NEVER = {"team": "idle", "started": None, "state": "never", "waiting_on": [], "required": ["agent", "kit", "team"]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "m": [{"sleep": 0.1, "body": {"do": ["r1"]}}, {"sleep": 0.1, "body": {"done": "ok"}},
              {"sleep": 0.1, "body": {"done": "standup"}}, {"sleep": 0.1, "body": {"done": "retro"}}],
        "r1": [{"sleep": 0.1, "body": {"done": True}}, {"sleep": 0.1, "body": {"done": True}},
               {"sleep": 0.1, "body": {"done": True}}],
        "r2": [{"sleep": 0.6, "body": {"done": True}}]})
    by_kind, all_ended = T.by_kind, T.all_ended

    def face(name: str | None = None, when: str = "2026-10-01T09:10") -> tuple:
        args = ("team", "status", *([name] if name else []), "--json")
        played = cli(h.engine, "--instance", str(h.house), *args, cwd=h.ws, env={**h.env, "PP_NOW": when})
        try:
            found = [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            found = []
        return played, found

    def ceremony(found: list, name: str) -> dict:
        return next((one for one in (found[0] if found else {}).get("ceremonies") or [] if one.get("name") == name), {})

    def member(found: list, name: str) -> dict:
        return next((one for one in (found[0] if found else {}).get("members") or [] if one.get("member") == name), {})

    h.declare("crew", CREW)
    h.declare("idle", "---\nagents: |\n  s s\nroot: s\n---\nNothing yet.\n")

    # --- the team ----------------------------------------------------------------------------------
    started = h.call("team", "start", "crew", "--message", "ship it", *h.harnessed, "--no-tick", now="09:10")
    first, first_obj = face("crew")
    one = first_obj[0] if first_obj else {}
    t1 = (one.get("tasks") or [{}])[0]
    pending_m = member(first_obj, "m").get("pending") or []
    ticked = h.call("team", "tick", "crew", now="09:15")
    done_t1 = h.settled("crew", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), 60)
    after, after_obj = face("crew", "2026-10-01T09:20")
    t1_after = next((task for task in (after_obj[0] if after_obj else {}).get("tasks") or [] if task.get("id") == "T1"), {})
    found = h.events("crew")
    ended = {(e.get("agent"), e["id"]) for e in by_kind(found, "wake-ended")}
    unseen = {(u.get("member"), u.get("task"), u.get("id")) for u in member(after_obj, "r2").get("unseen") or []}
    waiting = (after_obj[0] if after_obj else {}).get("waiting") or {}
    if (started.returncode == 0 and first.returncode == 0 and len(first_obj) == 1 and set(one) == KEYS
            and one.get("team") == "crew" and one.get("owner") == "house" and one.get("principals") == ["pm"]
            and one.get("schedule") == {"minutes": 5, "laid": True} and one.get("changed") is False
            and t1.get("id") == "T1" and t1.get("state") == "open" and t1.get("holders") == ["m"]
            and [(p.get("verb"), p.get("from"), p.get("task")) for p in pending_m] == [("do", "house", "T1")]
            and member(first_obj, "m").get("run") is None and member(first_obj, "m").get("path") == "agents/m"
            and ticked.returncode == 0 and done_t1 and after.returncode == 0
            and t1_after.get("state") == "resolved" and t1_after.get("holders") == []
            and t1_after.get("delegations") == [{"from": "m", "to": "r1", "terminal": True}]
            and unseen == {(agent, "T1", eid) for agent, eid in ended} and {u[0] for u in unseen} == {"m", "r1"}
            and member(after_obj, "m").get("how") == "ended" and member(after_obj, "m").get("tasks") == ["T1"]
            and waiting.get("done") == ["T1"] and (after_obj[0].get("wakes") or {}).get("launched") == 3):
        held("the team", f"one object, {len(KEYS)} keys; T1 held by m, its do pending; after T1: resolved, the "
             f"delegation m -> r1 terminal, r2's unseen {sorted(unseen)}, waiting done T1, 3 wake-ups launched")
    else:
        failures.append(f"  ✗ the team                    rc={started.returncode}/{first.returncode}/{ticked.returncode}/"
                        f"{after.returncode} keys={sorted(set(one) ^ KEYS)} t1={t1} pending={pending_m} done={done_t1} "
                        f"t1_after={t1_after} unseen={unseen} ended={ended} waiting={waiting} "
                        f"{first.stderr[-200:]!r} {first.stdout[:300]!r}")

    # --- every team --------------------------------------------------------------------------------
    every, every_obj = face(None, "2026-10-01T09:50")
    alone, alone_obj = face("idle", "2026-10-01T09:50")
    crew_line = next((one for one in every_obj if one.get("team") == "crew"), {})
    if (every.returncode == 0 and [one.get("team") for one in every_obj] == ["crew", "idle"]
            and every_obj[-1] == NEVER and alone.returncode == 0 and alone_obj == [NEVER]
            and crew_line.get("tasks", {}).get("open") == 0 and crew_line.get("tasks", {}).get("resolved") == 1
            and crew_line.get("running") == 0 and crew_line.get("asks") == 0 and crew_line.get("done") == 1
            and crew_line.get("state") == "idle" and crew_line.get("waiting_on") == []
            and set(crew_line) == {"team", "started", "state", "waiting_on", "paused", "tasks", "running", "asks", "done", "last",
                                   "required"}):
        held("every team", f"2 lines, idle {{team, started: null, state: never}} -- the same alone; crew "
             f"{crew_line.get('tasks')}, idle, done 1")
    else:
        failures.append(f"  ✗ every team                  rc={every.returncode}/{alone.returncode} every={every_obj} "
                        f"alone={alone_obj} {every.stderr[-200:]!r}")

    # --- refused -----------------------------------------------------------------------------------
    flagged = h.call("team", "status", "crew", "--json", "--task", "T1")
    unknown = h.call("team", "status", "nobody", "--json")
    if (flagged.returncode == 2 and "usage" in flagged.stderr and flagged.stdout == ""
            and unknown.returncode == 2 and "team-unknown" in unknown.stderr and unknown.stdout == ""):
        held("refused", "--task beside --json: the usage; a team nobody declared: team-unknown")
    else:
        failures.append(f"  ✗ refused                     rc={flagged.returncode}/{unknown.returncode} "
                        f"{flagged.stderr[-120:]!r} {unknown.stderr[-120:]!r}")
    return 0
