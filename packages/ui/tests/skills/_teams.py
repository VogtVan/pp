"""_teams -- what the scenarios of the Teams tab share (rule 10): a house pinning `ui`, the witness
`pp-team` posed under PP_UI_FACES as `team` (and `pp-chat` as `agent`, its faces empty, so that the
Agents tab reads nothing real), the script of three declared teams -- `core-review` and `ops` started,
`veille` never --, the journal of the witness, the renders of the post, and the processes of the witness
still alive; the gestures the witness played and the remedy line of a render; a LONG thread of T3 and the post
played on it under Textual's pilot, in a subprocess (`piloted`), what a probe counts and compares there."""
from __future__ import annotations

import json
import re
import os
import shlex
import shutil
import subprocess
import time

from tests.harness import SOURCE, cli, support

D = support(__file__, "dialogue")   # the provider of fixture the post's faces name

WITNESSES = SOURCE / "packages" / "ui" / "tests" / "witness"

STARTED = {"at": "2026-10-10T09:00:00+00:00", "id": 1}
LAST = {"id": 47, "kind": "post", "at": "2026-10-10T09:12:51+00:00"}
REQUIRED = ["agent", "kit", "team"]          # what a member may not switch off, as `status --json` says it
# the SET of packages a season without `--package` gives every member: the packages the team requires on, every other
# pin off (team 0.52.0) -- what `declaration --json` says of each member and what a bare season plays
SILENT = {"plan": False, "steering": False, "team": True}


def set_of(packages: dict) -> list[str]:
    """-> a set of packages as the face says it, one `<name>=on|off` per pin beyond the base."""
    return [f"{name}={'on' if on else 'off'}" for name, on in packages.items()]


def switches_set(said: list[str]) -> dict[str, bool]:
    """-> a set the face says, `["plan=off", ...]`, as `{name: on}`."""
    return {name: state == "on" for name, _, state in (one.partition("=") for one in said)}


# the launch the first season of `core-review` gave: what its next wake-up gets, its whole set
LAUNCH = {"harness": None, "provider": D.PROVIDER, "model": "opus", "permissions": None, "effort": "high",
          "launches": None, "packages": set_of({"plan": True, "steering": True, "team": True})}
BARE = {key: None for key in LAUNCH} | {"packages": set_of(SILENT)}     # a season started without a flag

CORE = {
    "team": "core-review", "owner": "house", "principals": ["pm"], "root": "lead", "started": STARTED, "changed": False,
    "limits": {"budget": 2.0, "budget-launches": 40}, "schedule": {"seconds": 300, "timer": True, "relaunch": True, "reason": None},
    "cost": 1.84, "budget_spent": False, "budget": {"cap": 2.0, "spent": 1.84, "reserved": 0.1, "left": 0.06},
    "launches": {"launched": 7, "bound": 40}, "last": LAST, "required": REQUIRED,
    "state": "working", "waiting_on": [], "paused": None,
    "season": {"n": 1, "at": STARTED["at"], "budget": 2.0, "budget-launches": None}, "launch": LAUNCH,
    "tasks": [
        {"id": "T1", "name": None, "text": "review PR 87 and its migration notes",
         "at": "2026-10-10T08:40:00+00:00", "ended": "2026-10-10T09:00:30+00:00",
         "last": {"id": 12, "kind": "stopped", "at": "2026-10-10T09:00:30+00:00"},
         "state": "stopped", "from": "house", "to": "lead", "ceremony": None, "period": None,
         "messages": 2, "resumed": None, "holders": ["lead"], "dos": []},
        {"id": "T2", "name": "daily 2026-10-10 09:30", "text": "the ceremony `daily` of team core-review rings",
         "at": "2026-10-10T09:00:00+00:00", "ended": "2026-10-10T09:01:30+00:00",
         "last": {"id": 40, "kind": "done", "at": "2026-10-10T09:01:30+00:00"},
         "state": "resolved", "from": "core-review", "to": "lead", "ceremony": "daily",
         "period": "2026-10-10", "messages": 5, "resumed": None, "holders": [],
         "dos": [{"id": 1, "from": "lead", "to": "reviewer", "answered": 101}]},
        {"id": "T3", "name": "review PR 88", "text": "review PR 88 and its release notes", "cost": 0.42,
         "at": "2026-10-10T09:01:00+00:00", "ended": None,
         "last": {"id": 47, "kind": "wake-ended", "at": "2026-10-10T09:06:00+00:00"},
         "state": "open", "from": "house", "to": "lead", "ceremony": None, "period": None,
         "messages": 6, "resumed": 31, "holders": ["lead", "reviewer"],
         "dos": [{"id": 2, "from": "lead", "to": "reviewer", "answered": None}]}],
    "members": [
        {"member": "lead", "path": "agents/lead", "run": "a77f10", "how": "ended", "since": None,
         "tasks": ["T1", "T2", "T3"], "pending": [],
         "unseen": [{"member": "reviewer", "task": "T2", "id": 40}], "launch": LAUNCH,
         "context": {"tokens": 52000, "used": 0.26, "window": 200000},     # what its last wake-up left (team 0.54.0)
         "owes": [{"id": 42, "verb": "do", "from": "house", "task": "T3", "reminded": 1},
                  {"id": 48, "verb": "re", "from": "reviewer", "task": "T3", "reminded": 0}], "health": None},
        {"member": "reviewer", "path": "agents/reviewer", "run": "a01389", "how": "running",
         "since": "2026-10-10T09:12:10+00:00", "tasks": ["T2", "T3"],
         "pending": [{"id": 46, "verb": "re", "from": "lead", "task": "T3"}], "unseen": [],
         "launch": {**LAUNCH, "model": "sonnet", "packages": set_of({"plan": False, "steering": True, "team": True})},
         "context": None, "owes": [], "health": None}],
    "ceremonies": [
        {"name": "daily", "mode": "every", "when": {"kind": "weekday", "at": "09:30"}, "after": None,
         "participants": ["reviewer"], "facilitator": "lead", "quorum": None, "next_due": "2026-10-12T09:30",
         "due": False, "last": {"period": "2026-10-10", "task": "T2", "state": "resolved", "by": None},
         "progress": [{"member": "reviewer", "answered": True}]},
        {"name": "retro", "mode": "after", "when": None, "after": "daily", "participants": ["reviewer", "scribe"],
         "facilitator": "lead", "quorum": 1, "next_due": None, "due": True, "last": None, "progress": []}],
    "owner_inbox": [{"id": 45, "verb": "ask", "from": "reviewer", "task": "T3", "returned": False}],
    "waiting": {"questions": [{"id": 45, "verb": "ask", "from": "reviewer", "task": "T3"}], "done": ["T2"],
                "returned": []}}

# a team whose owner posted two recurrences (team 0.53.0): `R1` live, its occurrence T6 open; `R2` stopped, never sounded
T6 = {"id": "T6", "name": "revue 2026-10-10 09:30", "text": "review the open PRs", "at": "2026-10-10T09:30:00+00:00",
      "ended": None, "last": {"id": 61, "kind": "task", "at": "2026-10-10T09:30:00+00:00"}, "state": "open",
      "from": "house", "to": "lead", "ceremony": None, "period": "2026-10-10", "recurrence": "R1", "messages": 1,
      "resumed": None, "holders": ["lead"], "dos": []}
RECURRENCES = [{"id": "R1", "name": "revue", "text": "review the open PRs", "from": "house", "to": "lead",
                "when": {"kind": "weekday", "at": "09:30"}, "since": "2026-10-09T08:00:00", "next_due": "2026-10-12T09:30",
                "due": False, "stopped": None, "last": {"period": "2026-10-10", "task": "T6", "state": "open"}},
               {"id": "R2", "name": None, "text": "rotate the logs of the gateway", "from": "house", "to": "reviewer",
                "when": {"kind": "day", "at": "18:00"}, "since": "2026-10-09T08:00:00", "next_due": None, "due": False,
                "stopped": {"by": "house", "at": "2026-10-10T09:20:00+00:00", "id": 60}, "last": None}]

T4 = {"id": "T4", "at": "2026-10-10T09:13:30+00:00", "ended": None, "state": "open", "from": "pm", "to": "lead", "ceremony": None, "period": None, "messages": 1,
      "resumed": None, "holders": ["lead"], "dos": []}
RECURRING = {**CORE, "tasks": CORE["tasks"] + [T6], "recurrences": RECURRENCES}
CORE_NEXT = {**CORE, "tasks": CORE["tasks"] + [T4], "last": {"id": 48, "kind": "post", "at": "2026-10-10T09:13:30+00:00"}}

# a task of twelve `do`s, ten answered -- the two left to members of long names --, and a text in
# markdown taller than its frame: what the band of a task says in one line each (batch la-zone-tache-en-sous-zones)
LATE = ("integration-tester", "documentation-writer")
T7 = {"id": "T7", "name": "release 2.4", "at": "2026-10-10T09:14:00+00:00", "ended": None, "state": "open",
      "text": ("# Release 2.4\n\nShip **the gateway** fixes before friday.\n\n- rotate the certificates\n"
               "- bump the chart\n- tag the images\n\nThen tell the *owners* of each service.\n\nThe notes of the "
               "release go to the wiki."),
      "from": "house", "to": "lead", "ceremony": None, "period": None, "messages": 14, "resumed": None, "cost": 0.73,
      "last": {"id": 70, "kind": "post", "at": "2026-10-10T09:14:30+00:00"}, "holders": ["lead", *LATE],
      "dos": [{"id": 10 + n, "from": "lead", "to": f"dev{n}", "answered": 110 + n} for n in range(1, 11)]
             + [{"id": 21 + n, "from": "lead", "to": one, "answered": None} for n, one in enumerate(LATE)]}
CORE_BAND = {**CORE, "tasks": CORE["tasks"] + [T7]}

# a member at two open tasks, each in its own run, as the face says them (`members[].runs[]`, team 1.4.9): `reviewer`
# holds `a01389` for T15, parked, and `a00007` for T16, running -- its member's own run the last one launched --; `lead`
# holds no open task (T3 is not there): one line (batch les-runs-par-tache-au-poste, s.1402 s.1337)
def held(carrier: str, run: str, name: str, how: str, at: str, used: float | None) -> dict:
    """One run of `members[].runs[]` as the frozen contract of the face says it."""
    return {"carrier": carrier, "run": run, "name": name, "how": how, "since": f"2026-10-10T{at}+00:00",
            "context": {"tokens": int(used * 200000), "used": used, "window": 200000} if used is not None else None}


def opened(task: str, name: str, at: str) -> dict:
    return {"id": task, "name": name, "text": name, "at": f"2026-10-10T{at}+00:00", "ended": None, "state": "open",
            "last": {"id": 80, "kind": "post", "at": f"2026-10-10T{at}+00:00"}, "from": "house", "to": "reviewer",
            "ceremony": None, "period": None, "messages": 2, "resumed": None, "holders": ["reviewer"], "dos": []}


T15, T16 = opened("T15", "audit the gateway", "09:10:00"), opened("T16", "rotate the certificates", "09:11:00")
BY_TASK = {**CORE, "tasks": CORE["tasks"][:2] + [T16, T15], "members": [
    {**CORE["members"][0], "tasks": ["T1", "T2"], "runs": [held("T1", "a77f10", "core-review T1", "ended", "09:00:30", 0.26)]},
    {**CORE["members"][1], "run": "a00007", "tasks": ["T2", "T16", "T15"],
     "runs": [held("daily", "a00009", "daily", "parked", "09:01:30", None),
              held("T16", "a00007", "rotate the certificates", "running", "09:11:05", 0.44),
              held("T15", "a01389", "audit the gateway", "parked", "09:10:30", 0.31)]}]}

# a team at three ceremonies: `daily` rung and closed (T2), `retro` after it under `any 2` rung and open -- one of
# its three participants has answered, its task T5 carries the facilitator's wait --, `review` never rung
T5 = {"id": "T5", "at": "2026-10-10T09:11:00+00:00", "ended": None, "state": "open", "from": "core-review", "to": "lead", "ceremony": "retro", "period": "2026-10-10",
      "messages": 4, "resumed": None, "holders": ["lead", "scribe", "dev2"],
      "dos": [{"id": 3, "from": "lead", "to": "reviewer", "answered": 103}, {"id": 4, "from": "lead", "to": "scribe", "answered": None},
                      {"id": 5, "from": "lead", "to": "dev2", "answered": None}]}
CEREMONIAL = {**CORE, "tasks": CORE["tasks"] + [T5], "ceremonies": [
    {"name": "daily", "mode": "every", "when": {"kind": "weekday", "at": "09:30"}, "after": None,
     "participants": ["reviewer"], "facilitator": "lead", "quorum": None, "next_due": "2026-10-12T09:30",
     "due": False, "last": {"period": "2026-10-10", "task": "T2", "state": "resolved", "by": None},
     "progress": [{"member": "reviewer", "answered": True}]},
    {"name": "retro", "mode": "after", "when": None, "after": "daily", "participants": ["reviewer", "scribe", "dev2"],
     "facilitator": "lead", "quorum": 2, "next_due": None, "due": False,
     "last": {"period": "2026-10-10", "task": "T5", "state": "open", "by": None},
     "progress": [{"member": "reviewer", "answered": True}, {"member": "scribe", "answered": False},
                  {"member": "dev2", "answered": False}]},
    {"name": "review", "mode": "every", "when": {"kind": "mon", "at": "10:00"}, "after": None,
     "participants": ["scribe"], "facilitator": "lead", "quorum": None, "next_due": "2026-10-12T10:00",
     "due": False, "last": None, "progress": []}]}

# a second team started: one task open -- no name, its text long, one delegation of two answered for good --,
# one resolved and not seen yet
OPS = {
    "team": "ops", "owner": "house", "principals": [], "started": STARTED, "changed": False, "limits": {},
    "schedule": {"seconds": None, "timer": None, "relaunch": None, "reason": None}, "cost": 0.4, "budget_spent": False, "budget": None,
    "launches": {"launched": 2, "bound": None}, "last": {"id": 9, "kind": "wake-launched", "at": "2026-10-10T09:10:00+00:00"},
    "required": REQUIRED, "state": "working", "waiting_on": [], "paused": None,
    "season": {"n": 1, "at": STARTED["at"], "budget": None, "budget-launches": None}, "launch": BARE,
    "tasks": [
        {"id": "T1", "name": None, "text": "rotate the certificates of the gateway before friday",
         "at": "2026-10-10T08:50:00+00:00", "ended": None,
         "last": {"id": 9, "kind": "wake-launched", "at": "2026-10-10T09:10:00+00:00"},
         "state": "open", "from": "house", "to": "sre", "ceremony": None, "period": None, "messages": 3,
         "resumed": None, "holders": ["sre", "dba"],
         "dos": [{"id": 6, "from": "sre", "to": "dba", "answered": 106}, {"id": 7, "from": "sre", "to": "net", "answered": None}]},
        {"id": "T2", "name": "weekly report", "text": "write the weekly report",
         "at": "2026-10-10T08:20:00+00:00", "ended": "2026-10-10T08:30:00+00:00",
         "last": {"id": 5, "kind": "done", "at": "2026-10-10T08:30:00+00:00"},
         "state": "resolved", "from": "house", "to": "sre", "ceremony": None, "period": None, "messages": 2,
         "resumed": None, "holders": [], "dos": []}],
    "members": [{"member": "sre", "path": "agents/sre", "run": "b11111", "how": "running",
                 "since": "2026-10-10T09:10:00+00:00", "tasks": ["T1", "T2"], "pending": [], "unseen": [],
                 "launch": BARE},
                {"member": "dba", "path": "agents/dba", "run": "b22222", "how": "ended", "since": None, "tasks": ["T1"],
                 "pending": [], "unseen": [], "launch": BARE}],
    "ceremonies": [], "owner_inbox": [], "waiting": {"questions": [], "done": ["T2"], "returned": []}}

NEVER = {"state": "never", "waiting_on": [], "paused": None}    # what the face says of a team never started
BADGES = [{"team": "core-review", "started": STARTED, "state": "working", "waiting_on": [], "paused": None,
           "tasks": {"open": 1, "stopped": 1, "resolved": 1}, "running": 1, "asks": 1, "done": 1, "last": LAST},
          {"team": "ops", "started": STARTED, "state": "working", "waiting_on": [], "paused": None,
           "tasks": {"open": 1, "stopped": 0, "resolved": 1}, "running": 1, "asks": 0, "done": 1, "last": OPS["last"]},
          {"team": "veille", "started": None, **NEVER}]

# the teams of a house, one per state the face says (team 0.30.0, 0.32.0): `alpha` and `zeta` working, `beta` waiting
# on its members, `gamma` waiting on the owner and its budget -- the face of `test` on 10/10: no wake-up under way, an
# escalation and four tasks done not seen --, `delta` paused by the owner, `epsilon` idle, `veille` never started
PAUSED_AT = {"by": "house", "at": "2026-10-10T09:20:00+00:00"}


def badge_of(team: str, state: str, waiting_on: tuple = (), running: int = 0, asks: int = 0, done: int = 0,
             paused: dict | None = None) -> dict:
    """A line of `team status --json` without a name, for a team started."""
    return {"team": team, "started": STARTED, "state": state, "waiting_on": list(waiting_on), "paused": paused,
            "tasks": {"open": 1, "stopped": 0, "resolved": done}, "running": running, "asks": asks, "done": done,
            "last": LAST}


def state_of(team: str, state: str, waiting_on: tuple = (), paused: dict | None = None) -> dict:
    """`team status <team> --json` for a team started: core-review's object under another name and state."""
    return {**CORE, "team": team, "state": state, "waiting_on": list(waiting_on), "paused": paused}


SHADES = [("alpha", "working", (), 1, 0, 0, None), ("beta", "waiting", ("due",), 0, 0, 0, None),
          ("gamma", "waiting", ("owner", "budget"), 0, 1, 4, None), ("delta", "paused", (), 0, 0, 0, PAUSED_AT),
          ("epsilon", "idle", (), 0, 0, 2, None), ("zeta", "working", (), 2, 0, 0, None)]


def shades_script() -> dict:
    """The seven teams of SHADES and `veille`, each read whole by `status <team> --json`."""
    badges = [badge_of(*one) for one in SHADES] + [{"team": "veille", "started": None, **NEVER}]
    states = {name: [state_of(name, state, waits, paused)] for name, state, waits, _, _, _, paused in SHADES}
    return script(badges=badges, states={**states, "veille": [{"team": "veille", "started": None, **NEVER,
                                                                "required": REQUIRED}]})


def event(at: str, kind: str, number: int, **fields) -> dict:
    """An event of `core-review`'s journal as `log --json` and `watch --json` give it."""
    return {"at": f"2026-10-10T{at}+00:00", "team": "core-review", "event": kind, "id": number, **fields}


T3_LOG = [event("09:01:00", "task", 41, task="T3", **{"from": "house"}, to="lead", text="review PR 88"),
          event("09:01:00", "post", 42, task="T3", **{"from": "house"}, to="lead", verb="do", text="review PR 88"),
          event("09:02:00", "post", 44, task="T3", **{"from": "lead"}, to="reviewer", verb="do", text="read the PR"),
          event("09:05:00", "post", 45, task="T3", **{"from": "reviewer"}, to="house", verb="ask", text="tests green?"),
          event("09:06:00", "wake-ended", 47, tag="reviewer-T3-2", agent="reviewer", run="a01389", launch=2, cost=0.03)]
TEAM_LOG = [event("09:00:00", "team-started", 1, root="lead")] + T3_LOG
T2_LOG = [event("09:00:00", "task", 30, task="T2", **{"from": "core-review"}, to="lead", text="the daily"),
          event("09:00:10", "post", 31, task="T2", **{"from": "lead"}, to="reviewer", verb="do", text="your daily"),
          event("09:01:20", "post", 32, task="T2", **{"from": "reviewer"}, to="lead", verb="re", re=31, text="nothing")]
# the threads of T15 and T16 of `BY_TASK`
T15_LOG = [event("09:10:00", "task", 81, task="T15", **{"from": "house"}, to="reviewer", text="audit the gateway"),
           event("09:10:00", "post", 82, task="T15", **{"from": "house"}, to="reviewer", verb="do", text="audit it"),
           event("09:10:20", "post", 83, task="T15", **{"from": "reviewer"}, to="house", verb="ask", text="which port?")]
T16_LOG = [event("09:11:00", "task", 84, task="T16", **{"from": "house"}, to="reviewer", text="rotate the certificates"),
           event("09:11:00", "post", 85, task="T16", **{"from": "house"}, to="reviewer", verb="do", text="rotate them")]
WRITTEN = event("09:05:30", "post", 46, task="T3", **{"from": "house"}, to="reviewer", verb="re", re=45, text="yes, 412")
T3_READS = [T3_LOG, sorted(T3_LOG + [WRITTEN], key=lambda one: one["id"])]   # #46 written while the watch started
DEBT_LOG = [T3_LOG[0], T3_LOG[1], T3_LOG[2], T3_LOG[3], WRITTEN,
            event("09:06:00", "wake-ended", 47, tag="reviewer-T3-2", agent="reviewer", run="a01389", launch=2, cost=0.03),
            event("09:07:00", "post", 48, task="T3", **{"from": "reviewer"}, to="lead", verb="re", re=44, was="done",
                  text="LGTM"),
            event("09:08:00", "wake-intent", 49, tag="lead-T3-3", agent="lead", path="agents/lead", task="T3",
                  run="a77f10", messages=[48], relance="owed"),
            event("09:09:00", "post", 50, task="T3", **{"from": "lead"}, to="reviewer", verb="re", re=45, by="tick",
                  preempted=True, text="no answer in time"),
            event("09:10:00", "post", 51, task="T3", **{"from": "core-review"}, to="house", verb="notice", about="lead",
                  suspected=True, text="lead is not answering; tried again at 09:30"),
            event("09:11:00", "post", 52, task="T3", **{"from": "lead"}, to="scribe", verb="re", re=44, by="tick",
                  suspected=True, text="lead is not answering")]
DEBT_WAITING = {"questions": [], "done": [],
                "notices": [{"id": 51, "from": "core-review", "about": "lead", "task": "T3", "awaits": True}],
                "returned": []}
STEP = {"agent": "reviewer", "run": "a01389", "event": "block", "stack": "BOOT ▸ MEMBER ▸ TURN{4/4}", "wait": True,
        "task": "T3", "tag": "reviewer-T3-3", "launch": 3}       # a step names its task, its tag, its launch (team 0.40.0-alpha)
T3_WATCH = [T3_LOG[2],                                   # #44 again: the history read it already
            {"sleep": 0.4},
            event("09:13:00", "post", 48, task="T3", **{"from": "lead"}, to="reviewer", verb="re", re=47, text="412 held"),
            STEP,
            {"sleep": 0.3},
            event("09:14:00", "wake-ended", 49, tag="reviewer-T3-3", agent="reviewer", run="a01389", launch=3, cost=0.02)]
PROVIDERS = [{"provider": D.PROVIDER, "spells": ["model", "max_budget_usd", "effort", "permissions"],
              "models": list(D.MODELS)}]                                  # what `agent providers --json` says
# a result in markdown, taller than the band: its frame scrolls
REPORT = ("# Weekly report\n\n| item | state |\n|---|---|\n| certificates | rotated |\n"
          + "".join(f"| check {n} | done |\n" for n in range(1, 41)))
RESULTS = {"core-review/T2": {"verdict": "LGTM", "remarks": 2}, "ops/T2": REPORT}
# what `team delete <t> --json` says without `--yes`: what it would remove, the agents it keeps
DELETES = {"ops": {"team": "ops", "name": "ops", "dry": True, "directory": "teams/ops", "journal": ".pp/teams/ops",
                   "calendar": False, "timer": True, "runs": [{"path": "agents/sre", "run": "b11111"}],
                   "agents": ["agents/dba", "agents/sre"]}}


# the run of `reviewer`, as `agent exchanges agents/reviewer a01389 --json` gives it: two exchanges at the
# opening of its tab, a third once a wake-up launched (its answer to come), the third answered once it ended
def exchange(index: int, message: str, response: str | None, cost: float | None = None) -> dict:
    return {"agent": "agents/reviewer", "run": "a01389", "index": index, "at": f"2026-10-10T09:0{index}:00+00:00",
            "message": message, "response": response, "cost_usd": cost, "launches": 1 if response else None,
            "error": None, "harness_rc": 0 if response else None, "conducted": True}


EX1 = exchange(1, "[team core-review · you are reviewer]\n#44 do from lead on T3: read the PR", '{"ask": "tests green?"}', 0.02)
EX2 = exchange(2, "[team core-review · you are reviewer]\n#46 reply from house on T3: yes, 412", '{"done": "LGTM"}', 0.03)
EX3 = "[team core-review · you are reviewer]\n#48 reply from lead on T3: 412 held"
MEMBER_EXCHANGES = [[EX1, EX2], [EX1, EX2, exchange(3, EX3, None)], [EX1, EX2, exchange(3, EX3, '{"done": "merged"}', 0.04)]]
MEMBER_STATUS = [{"agent": "agents/reviewer", "run": "a01389", "name": "", "exchanges": 3, "state": "parked", "stack": "",
                  "session": "s-r", "provider": D.PROVIDER, "cost_usd": 0.09, "launches": 3, "responses": 3,
                  "first_message": "[team core-review · you are reviewer]", "first_at": "2026-10-10T09:01:00+00:00",
                  "last_at": "2026-10-10T09:03:00+00:00", "context": None},
                 {"agent": "agents/reviewer", "run": "a00007", "name": "", "exchanges": 1, "state": "parked", "stack": "",
                  "session": "s-o", "provider": D.PROVIDER, "cost_usd": 0.01, "launches": 1, "responses": 1,
                  "first_message": "a run of its own", "first_at": "2026-10-09T09:00:00+00:00",
                  "last_at": "2026-10-09T09:01:00+00:00", "context": None},
                 {"agent": "agents/reviewer", "providers": [D.PROVIDER], "last": None}]
def kept(index: int, message: str, answer: str | None, stack: str = "BOOT ▸ MEMBER ▸ TURN{2/4}") -> list[dict]:
    """The kept flow of one exchange of `reviewer`'s run, as `agent flow --json` gives it: its opening, the message,
    a launch -- its conduction, a call of `WebSearch` and its result, a thought --, then, answered, the agent's
    words, the step that parks, the response and the verdict."""
    at = f"2026-10-10T09:0{index}:00+00:00"

    def said(kind: str, **fields) -> dict:
        return {"kind": kind, "at": at, "run": "a01389", **fields}
    flow = [said("opened", agent="agents/reviewer", exchange=index, resumed=index > 1, standing=False),
            said("principal", exchange=index, text=message),
            said("step", event="launch", launch=1, chars=900),
            said("conduction", exchange=index, launch=1, text=f"▌ pp · run a01389\n▌ {stack}", chars=40,
                 blocks=[{"stack": stack, "command": "./pp a01389", "wait": False}]),
            said("tool", exchange=index, launch=1, id=f"c{index}", name="WebSearch", title='"DDR4 spot"', shell=None,
                 input={"query": "DDR4 spot"}, pp=False),
            said("tool-result", exchange=index, launch=1, id=f"c{index}", content="3 results", error=False),
            said("thinking", exchange=index, launch=1, text="the price first")]
    if answer is not None:
        flow += [said("agent", exchange=index, launch=1, text=answer, cost_usd=0.02),
                 said("step", event="block", stack="BOOT ▸ MEMBER ▸ TURN{4/4}", wait=True),
                 said("response", index=index, response=answer, state="parked"),
                 said("verdict", exchange=index, state="parked", cost_usd=0.02, launches=1)]
    return flow


# `reviewer`'s kept flow: its two exchanges at the opening of its tab, then the third -- read again by its exchange,
# under way at a step, answered at its end
KEPT = {"all": kept(1, EX1["message"], EX1["response"]) + kept(2, EX2["message"], EX2["response"]),
        "3": [kept(3, EX3, None), kept(3, EX3, '{"done": "merged"}')]}
# `lead`'s run keeps no flow (a run older than agent 0.22.0): its exchanges stand in
LEAD_EXCHANGES = [{**exchange(1, "[team core-review · you are lead]\n#42 do from house on T3: review PR 88",
                              '{"do": ["reviewer"]}', 0.01), "agent": "agents/lead", "run": "a77f10"}]
# `lead`'s kept flow of its exchange 4: a call of `Read`
LEAD_KEPT = {"4": [{"kind": "opened", "at": "2026-10-10T09:13:00+00:00", "run": "a77f10", "agent": "agents/lead",
                    "exchange": 4, "resumed": True, "standing": False},
                   {"kind": "tool", "at": "2026-10-10T09:13:01+00:00", "run": "a77f10", "exchange": 4, "launch": 1,
                    "id": "l4", "name": "Read", "title": "PR 88 diff", "shell": None, "input": {}, "pp": False}]}
MEMBER_FACES = {"list": [{"agent": "agents/reviewer", "runs": 2, "running": 0, "responses": 4}],
                "status": {"agents/reviewer": MEMBER_STATUS},
                "exchanges": {"agents/reviewer": {"a01389": MEMBER_EXCHANGES}, "agents/lead": {"a77f10": LEAD_EXCHANGES}},
                "flow": {"agents/reviewer": {"a01389": KEPT}, "agents/lead": {"a77f10": LEAD_KEPT}}}
# the team's watch while `reviewer` plays a wake-up and `lead` another: what the tab of `reviewer` keeps is its own --
# the first step once the tab of `reviewer` has subscribed to the watch and read its kept flow, whatever the time the
# keys that open it took
MEMBER_WATCH = [{"until": "flow agents/reviewer a01389 --json"},
                event("09:10:00", "wake-launched", 50, tag="reviewer-T3-3", agent="reviewer", run="a01389", pid=4242),
                {"agent": "reviewer", "run": "a01389", "event": "block", "stack": "BOOT ▸ MEMBER ▸ TURN{4/4}", "wait": True,
                 "task": "T3", "tag": "reviewer-T3-3", "launch": 3},
                event("09:10:01", "wake-launched", 51, tag="lead-T3-4", agent="lead", run="a77f10", pid=4243),
                {"agent": "lead", "run": "a77f10", "event": "refused", "code": "lead-only", "task": "T3", "tag": "lead-T3-4",
                 "launch": 4},
                {"sleep": 0.4},
                event("09:11:00", "wake-ended", 52, tag="reviewer-T3-3", agent="reviewer", run="a01389", launch=3, cost=0.04)]
RESPONSES = [{"id": 40, "member": "reviewer", "path": "agents/reviewer", "task": "T2", "run": "a01389", "launch": 1,
              "at": "2026-10-10T09:01:30+00:00", "cost_usd": 0.02, "response": '{"done": "the daily: nothing to say"}'},
             {"id": 47, "member": "lead", "path": "agents/lead", "task": "T3", "run": "a77f10", "launch": 4,
              "at": "2026-10-10T09:06:00+00:00", "cost_usd": 0.03, "response": '{"ask": "lead asks"}'},
             {"id": 49, "member": "reviewer", "path": "agents/reviewer", "task": "T3", "run": "a01389", "launch": 2,
              "at": "2026-10-10T09:02:30+00:00", "cost_usd": 0.03, "response": '{"done": "LGTM"}'}]


# the wake-ups under way, as the face says them (`tasks[].running`, team 0.30.0): `reviewer` on core-review's T3,
# `sre` on ops' T1
def running(task: dict, *wakes: tuple, relance: str | None = None) -> dict:
    """The wake-ups under way on a task: `(member, run, at)` each, `at` an hour of 10/10 or a whole ISO instant;
    `relance` what the face says of a wake-up that is a reminder (`owed`, `cycle`, `tried`), None otherwise."""
    return {**task, "running": [{"member": member, "tag": f"{member}-{task['id']}", "run": run,
                                 "since": at if "T" in at else f"2026-10-10T{at}+00:00", "allowance": None,
                                 "relance": relance} for member, run, at in wakes]}


def ago(seconds: float) -> str:
    """An instant that many seconds before now, as a face dates it (ISO 8601, UTC)."""
    from datetime import datetime, timedelta, timezone
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).replace(microsecond=0).isoformat()


def age_said(iso: str) -> str:
    """The age of an instant as the post says it (`palette.age_of`): `now` under 5 s, then `s`, `min`, `h`, `d` --
    the bench's own copy, so that a scenario expects a face of 10/10 in days."""
    from datetime import datetime, timezone
    seconds = max(0.0, (datetime.now(timezone.utc) - datetime.fromisoformat(iso)).total_seconds())
    if seconds < 5:
        return "now"
    for bound, unit, size in ((60, "s", 1), (3600, "min", 60), (86400, "h", 3600)):
        if seconds < bound:
            return f"{int(seconds // size)} {unit}"
    return f"{int(seconds // 86400)} d"


def aged(face: dict, last: float, since: float, paused: float | None = None) -> dict:
    """A team's face whose instants are posed at the reading: its `last` event and every task's `last` that many
    seconds ago, each wake-up under way and each running member launched `since` seconds ago, the pause `paused`
    seconds ago when given -- what `age_of` renders against the post's clock."""
    tasks = [{**task, "last": {**task["last"], "at": ago(last)} if task.get("last") else None,
              "running": [{**one, "since": ago(since)} for one in task.get("running") or []]} for task in face["tasks"]]
    members = [{**one, "since": ago(since) if one.get("since") else None} for one in face["members"]]
    aged_face = {**face, "last": {**face["last"], "at": ago(last)}, "tasks": tasks, "members": members}
    if paused is not None:
        aged_face = {**aged_face, "state": "paused", "waiting_on": [],
                     "paused": {"by": "house", "at": ago(paused)}}
    return aged_face


# the debts of a task (team 0.36.0): T3 with a `do` answered by #46 and one still running, a wait counted 1 of 3,
# `lead` woken again without a new message -- a relance the face says `owed`
DEBTS = {**CORE, "tasks": [
    running({**one, "dos": [{"id": 1, "from": "lead", "to": "reviewer", "answered": 46},
                            {"id": 2, "from": "lead", "to": "scribe", "answered": None}]},
            ("lead", "a77f10", "09:12:10"), relance="owed") if one["id"] == "T3" else one for one in CORE["tasks"]]}
# a member that does not answer (team 0.35.0): `reviewer` suspected, tried again at 09:30; `lead` fallen once and
# back, its run ended
SUSPECTED = {**CORE, "state": "waiting", "waiting_on": ["suspected"], "members": [
    {**CORE["members"][0], "health": {"suspected": False, "falls": 0, "tried_at": None, "repents": 1}},
    {**CORE["members"][1], "how": "dead", "since": None,
     "health": {"suspected": True, "falls": 2, "tried_at": "2026-10-10T09:30", "repents": 0}}]}
# members stopped by their provider's usage limit (team 1.25.0, `members[].quota {until, said, at}`): `lead` until 15:00,
# `scribe` with no hour said -- until the house resumes it --, beside `reviewer` suspected
QUOTED = {**SUSPECTED, "members": [
    {**CORE["members"][0], "quota": {"until": "2026-10-10T15:00:00+00:00", "said": "usage limit reached, resets 3pm",
                                     "at": "2026-10-10T09:10:00+00:00"}},
    SUSPECTED["members"][1],
    {"member": "scribe", "path": "agents/scribe", "run": "c55e01", "how": "parked", "since": None, "tasks": ["T3"],
     "pending": [], "unseen": [], "launch": LAUNCH, "context": None, "owes": [], "health": None,
     "quota": {"until": None, "said": "weekly limit reached", "at": "2026-10-10T09:11:00+00:00"}}]}


def crowded(count: int = 100, opened: tuple = (42, 47, 97)) -> dict:
    """core-review whose `reviewer` holds `count` tasks born a minute apart, those of `opened` open, the others
    resolved -- what the band of a member's tasks pages through."""
    tasks = [{**CORE["tasks"][2], "id": f"T{n}", "name": None, "text": f"task {n} of the reviewer",
              "at": f"2026-10-10T{6 + n // 60:02d}:{n % 60:02d}:00+00:00", "state": "open" if n in opened else "resolved",
              "ended": None if n in opened else f"2026-10-10T{6 + n // 60:02d}:{n % 60:02d}:30+00:00", "dos": [],
              "holders": ["reviewer"] if n in opened else []} for n in range(1, count + 1)]
    members = [CORE["members"][0], {**CORE["members"][1], "tasks": [one["id"] for one in tasks]}]
    return {**CORE, "tasks": tasks, "members": members}


LIVE_CORE = {**CORE, "tasks": [running(one, ("reviewer", "a01389", "09:12:10")) if one["id"] == "T3" else one
                               for one in CORE["tasks"]]}
LIVE_OPS = {**OPS, "tasks": [running(one, ("sre", "b11111", "09:10:00")) if one["id"] == "T1" else one
                             for one in OPS["tasks"]]}
# two members on T3: a step of `lead` (its exchange 4), one of `reviewer` (its exchange 3), then `lead`'s wake-up ends
LEAD_STEP = {"agent": "lead", "run": "a77f10", "event": "block", "stack": "BOOT ▸ MEMBER ▸ TURN{3/4}", "wait": False,
             "task": "T3", "tag": "lead-T3-4", "launch": 4}
TWO_WATCH = [{"sleep": 0.3}, LEAD_STEP, {"sleep": 0.2}, STEP, {"sleep": 0.3},
             event("09:13:30", "wake-ended", 53, tag="lead-T3-4", agent="lead", run="a77f10", launch=4, cost=0.01)]


# the ACTIVITY of `reviewer`'s wake-up on T3, as the team's watch relays it from the run's flow (team 0.50.0): a call
# of a tool, its result, a thought, the context a call measured -- each with the task, the tag and the launch
def activity(kind: str, **fields) -> dict:
    return {"agent": "reviewer", "run": "a01389", "event": "activity", "kind": kind, "task": "T3", "tag": "reviewer-T3-3",
            "launch": 3, **fields}


ACT_TOOL = activity("tool", name="Read", title="pp.py", pp=False)
ACT_RESULT = activity("tool-result", error=False, size=1234)
ACT_THOUGHT = activity("thinking", text="the price first, then the rest")
ACT_CONTEXT = activity("context", tokens=34000, used=0.17, window=200000)
STEP_LAST = {**STEP, "stack": "BOOT ▸ MEMBER ▸ TURN{5/5}", "wait": False}
# a block, three activities, a block: the live line of `reviewer` changes at each -- the first once the post has read
# its tasks and the thread, so that a render waits for each in turn
LIVE_WATCH = [{"sleep": 2.0}, STEP, {"sleep": 0.8}, ACT_TOOL, {"sleep": 0.8}, ACT_RESULT, {"sleep": 0.8}, ACT_THOUGHT,
              {"sleep": 0.8}, STEP_LAST]
def template(name: str, description: str, members: list[str], ceremony: str | None, values: tuple = ()) -> dict:
    """A preset of a team as `team templates --json` says it (team 1.26.0), `teams/<name>`, for its default members: the
    values it declares, each `(name, description, default)`."""
    return {"template": f"teams/{name}", "kind": "preset", "description": description, "origin": "package",
            "values": [{"name": one, "description": said, "default": default} for one, said, default in values],
            "documents": [], "form": "star", "members": members, "root": members[0],
            "reports": [{"from": members[1:], "to": members[0]}] if len(members) > 1 else [],
            "ceremony": ceremony, "limits": {"budget": 5, "launches": 8, "timeout": 900},
            "intention": f"The root `{members[0]}` answers every task."}


DAILY = "every weekday 09:30"
PRESETS = [template("supervisor-workers", "the root splits each task, one part per worker",
                    ["supervisor", "worker-1", "worker-2"], f"daily {DAILY} with worker-1 worker-2 -> supervisor",
                    (("daily", "the daily's rhythm; left empty, no daily", DAILY),
                     ("focus", "what the workers look at first", "tests"))),
           template("lead-reviewers", "the root does the work, each reviewer checks its draft", ["lead", "reviewer"], None),
           template("chain", "each member hands the next step to the next one", ["first", "second", "third"], None),
           template("solo", "one member does every task", ["solo"], None),
           template("empty", "the smallest declaration", ["root"], None)]
# the documents a team names by key, and the presets of a season: its documents and its values
DOCUMENTS = [{"template": "git/branches", "kind": "document", "description": "one branch per piece of work",
              "origin": "house", "values": []},
             {"template": "git/trunk", "kind": "document", "description": "every change lands on the main branch",
              "origin": "house", "values": []}]
SEASONS = [{"template": "seasons/files", "kind": "preset", "description": "members write files, a reader checks them",
            "origin": "package", "values": [{"name": "readers", "description": "the role key of who reads",
                                             "default": "readers"}],
            "documents": [{"key": "all", "documents": ["git/trunk"]}]},
           {"template": "seasons/plan-branch", "kind": "preset", "description": "one branch per plan, a request per batch",
            "origin": "package", "values": [{"name": "base", "description": "the branch work starts from",
                                             "default": "main"}],
            "documents": [{"key": "all", "documents": ["git/branches"]}]}]
TEMPLATES = DOCUMENTS + SEASONS + PRESETS     # what `team templates --json` says, one object per line


def season_written(launch: dict | None = None, packages: dict | None = None, profiles: dict | None = None,
                   limits: dict | None = None) -> dict:
    """The season a start without a flag opens, as `declared.season` of `team declaration --json` says it -- what
    SEASON.md writes: its launch, its limits, its whole set of packages (`SILENT` without one), each member's
    profile -- its keys and its own whole set."""
    return {"launch": dict(launch or {}), "limits": dict(limits or {}), "packages": set_of(packages or SILENT),
            "profiles": dict(profiles or {}), "work": None}


def text_of(front: list[tuple[str, object]], body: str = "") -> str:
    """-> a values file: its keys in order -- a scalar, or a block given as a list of lines --, then its body."""
    lines = ["---"]
    for key, said in front:
        if isinstance(said, list):
            lines += [f"{key}: |", *(f"  {one}" for one in said)] if said else []
        elif said not in (None, ""):
            lines.append(f"{key}: {said}")
    return "\n".join(lines + ["---", ""]) + body


def declaration(team: str, members: list[tuple], limits: dict, started: bool = True, template: str | None = None,
                values: tuple = (), roles: tuple = (), season: dict | None = None, views: list | None = None,
                season_file: dict | None = None, description: str | None = None, documents: tuple = (),
                running: bool = False, reports: tuple = (), body: str = "",
                principals: tuple = (), root: str | None = None) -> dict:
    """The declaration of `team` as `team declaration --json` says it (team 1.26.0): TEAM.md's TEXT -- its description,
    its preset, its values (`(name, value, from)`, those `from` `team` written), its members `(name, path)` or `(name,
    path, born)`, its role keys `(key, [members])`, its documents `(key, [documents])`, its root when written, its
    principals, its edges (`reports`), its limits, its body --, its start `running` (in season) or stopped (off
    season, what a declare needs), and `declared`: what the next start writes -- the members in their order, the first the
    root, each born by default with the set a season without `--package` gives (`SILENT`), the limits, the preset and
    its values, the role keys, the documents by key (the team's and the season's), the values applied, the season
    written (`season_written`), each member's view; `season_file` SEASON.md: its preset `{template, values: [(name,
    value)], documents: [(key, [documents])]}`, written to SEASON.md's text."""
    keys = {key: list(names) for key, names in roles}
    owned = [(name, value) for name, value, source in values if source == "team"]
    text = text_of([("description", None if description is None else f'"{description}"'), ("template", template),
                    ("agents", [f"{one[0]} {one[1]}" for one in members]),
                    ("roles", [" ".join([key, *names]) for key, names in roles]),
                    ("documents", [" ".join([key, *named]) for key, named in documents]),
                    ("values", [f"{name} = {value}" for name, value in owned]), ("root", root),
                    ("reports", list(reports)),
                    ("principals", list(principals)),
                    *((key, limits[key]) for key in ("budget", "launches", "timeout") if key in limits)], body)
    season_text = None if season_file is None else text_of(
        [("template", season_file.get("template")), ("values", [f"{name} = {value}" for name, value in
                                                             season_file.get("values") or ()]),
         ("documents", [" ".join([key, *named]) for key, named in season_file.get("documents") or ()])])
    lines = [{"key": key, "team": list(named), "season": []} for key, named in documents]
    lines += [{"key": key, "team": [], "season": list(named)} for key, named in (season_file or {}).get("documents") or ()]
    return {"team": team, "path": f"teams/{team}/TEAM.md", "text": text, "digest": "abc123abc123",
            "description": description, "verdict": {"ok": True, "refusal": None},
            "started": ({**STARTED, "digest": "abc123abc123", "state": "running" if running else "stopped"}
                        if started else None),
            "changed": False, "pending": [],
            "season": ({"path": f"teams/{team}/SEASON.md", "text": season_text, "digest": "def456def456"}
                       if season_text is not None else None),
            "declared": {"agents": [{"member": one[0], "path": one[1], "born": one[2] if len(one) > 2 else True,
                                     "packages": [{"name": name, "on": on} for name, on in SILENT.items()],
                                     "description": None, "roles": [key for key, names in keys.items() if one[0] in names]}
                                    for one in members], "root": root or members[0][0],
                         "reports": list(reports), "principals": list(principals), "limits": limits, "schedule": None,
                         "ceremonies": [], "entries": {}, "work": None,
                         "season": season if season is not None else season_written(),
                         "roles": [{"role": key, "members": names} for key, names in keys.items()],
                         "documents": lines,
                         "values": [{"name": name, "value": value, "from": source} for name, value, source in values]
                                   + [{"name": name, "value": value, "from": "season"}
                                      for name, value in (season_file or {}).get("values") or ()],
                         "views": views if views is not None else [{"member": one[0], "roles": [], "documents": []}
                                                                   for one in members],
                         "template": None if template is None else {
                             "template": template, "origin": "package",
                             "values": [{"name": name, "value": value, "from": source} for name, value, source in values]}}}


def document(name: str, effect: str, roles: tuple = ()) -> dict:
    """A document of a member's view as `declared.views[].documents` says it."""
    return {"document": name, "template": "git/trunk", "roles": list(roles), "effect": effect,
            "by": "vector" if roles else "file"}


# `core-review` declares a member more than it started with (`scribe`) and a budget below the season's own; its preset
# `teams/supervisor-workers`, its value `daily` the preset's; its role `make` held by `lead`, whose view adds a document
# of the role; the document `git/trunk` for every member; its season's preset `seasons/files`; its season written as its
# first season launched it -- `reviewer` on its own model and set
CORE_SEASON = season_written({"provider": D.PROVIDER, "model": "opus", "effort": "high"},
                             {"plan": True, "steering": True, "team": True},
                             {"reviewer": {"model": "sonnet", "packages": set_of({"plan": False, "steering": True,
                                                                                    "team": True})}},
                             {"budget": 2.0})
CORE_VIEWS = [{"member": "lead", "roles": ["make"],
               "documents": [document("TEAM-core-review-trunk.md", "served"),
                             document("roles/TEAM-core-review-review.md", "mounted", ("make",))]},
              {"member": "reviewer", "roles": [], "documents": [document("TEAM-core-review-trunk.md", "served")]},
              {"member": "scribe", "roles": [], "documents": [document("TEAM-core-review-trunk.md", "served")]}]
FILES = {"template": "seasons/files", "values": [("readers", "readers")]}
DECLARATIONS = {
    "core-review": declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer"),
                                               ("scribe", "agents/scribe")],
                               {"budget": 1.0, "budget-launches": 40}, template="teams/supervisor-workers",
                               values=(("daily", DAILY, "default"), ("focus", "tests", "default")),
                               roles=(("make", ["lead"]),), season=CORE_SEASON, views=CORE_VIEWS, season_file=FILES,
                               documents=(("all", ["git/trunk"]),)),
    "ops": declaration("ops", [("sre", "agents/sre"), ("dba", "agents/dba")], {}),
    "veille": declaration("veille", [("scout", "agents/scout"), ("writer", "agents/writer")], {"budget": 3.0},
                          started=False)}
# `core-review` as an owner who wrote more of it: two principals, and a SEASON.md that writes no season --
# `declared.season` none: the lines open on the season under way
OWNED = declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer"),
                                    ("scribe", "agents/scribe")], {"budget": 1.0, "budget-launches": 40},
                    template="teams/supervisor-workers", roles=(("make", ["lead"]),), views=CORE_VIEWS,
                    documents=(("all", ["git/trunk"]),), principals=("pm", "qa"))
OWNED = {**OWNED, "declared": {**OWNED["declared"], "season": None}}
# the same, its TEAM.md writing `root:` -- a root its owner chose, not the one a preset's form makes
ROOTED = declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer"),
                                     ("scribe", "agents/scribe")], {"budget": 1.0, "budget-launches": 40},
                     template="teams/supervisor-workers", roles=(("make", ["lead"]),), views=CORE_VIEWS,
                     documents=(("all", ["git/trunk"]),), principals=("pm", "qa"), root="lead")
REFUSED = {**DECLARATIONS["ops"], "verdict": {"ok": False, "refusal": "team-invalid -- `parallel: 0` is no whole "
                                                                      "number of 1 or more"},
           "pending": None, "declared": None}


def tail(last: dict | None) -> list[dict]:
    """An agent's `status --json` without a run: the providers and what it last played."""
    return [{"agent": "?", "providers": [D.PROVIDER], "last": last}]


# the agents of the members as a season reads them: `scout` and `writer` played before, the others never
SEASON_AGENTS = {"agents/scout": tail({"provider": D.PROVIDER, "policy": {"model": "opus", "effort": "high"}}),
                 "agents/writer": tail({"provider": D.PROVIDER, "policy": {"model": "sonnet"}}),
                 "agents/lead": tail(None), "agents/reviewer": tail(None), "agents/scribe": tail(None)}


def _three(usd, launches, tokens, estimated: bool = False) -> dict:
    return {"usd": usd, "launches": launches, "tokens": tokens, "tokens_estimated": estimated}


def _against(median, ratio, over: int = 3) -> dict:
    return {"median": median, "ratio": ratio, "over": over}


def task_line(task: str, state: str, usd: float, launches: int, do: int, share: float, per: tuple, ratios: tuple,
              failures: int, context: float, season: int = 3, hour: tuple = (19.4, 0.88)) -> dict:
    """A line of `by_task` of a season, as the socle's face says it: its share, its cost per delegation and per hour
    of effort (`hour`, the cost and its ratio; team 1.36.64, D8), and those costs against the median -- figures
    written, never derived from one another."""
    return {"task": task, "name": f"the task {task}", "season": season, "state": state,
            "cost": _three(usd, launches, launches * 118_000), "do": do, "re": do, "failures": failures,
            "time": {"elapsed": 3600, "active": 2400, "effort": 3000}, "first": "2026-10-10T09:00:00+00:00",
            "last": "2026-10-10T10:00:00+00:00", "context_max": context,
            "share": {"usd": share, "launches": round(share + 0.03, 2), "tokens": round(share - 0.02, 2)},
            "per_delegation": {"usd": per[0], "launches": per[1], "tokens": 97_000},
            "per_effort_hour": {"usd": hour[0], "tokens": 2_310_000},
            "against": {"per_delegation": {"usd": _against(2.18, ratios[0]), "launches": _against(4.4, ratios[1]),
                                           "tokens": _against(150_000, 0.71)},
                        "per_effort_hour": {"usd": _against(22.1, hour[1]), "tokens": _against(2_100_000, 1.07)}}}


def member_line(member: str, role: str | None, usd: float, launches: int, per_usd: float, do: int, wait: int | None,
                failures: int, context: float, share: float, models: tuple = ("opus-x",),
                hour: tuple = (21.3, 0.96)) -> dict:
    """A line of `by_member` of a season: its cost, its cost per launch, its share; its models, the most launched
    first, and its cost per hour of effort against the median of the season (`hour`, the cost and its ratio; team
    1.36.64, D8)."""
    return {"member": member, "roles": [role] if role else [], "cost": _three(usd, launches, launches * 121_000),
            "models": list(models), "per_effort_hour": {"usd": hour[0], "tokens": 2_420_000},
            "against": {"per_effort_hour": {"usd": _against(22.1, hour[1]), "tokens": _against(2_100_000, 1.12)}},
            "per_launch": {"usd": per_usd, "tokens": 121_000}, "do": do, "re": do, "failures": failures,
            "time": {"elapsed": 6000, "active": 2000, "effort": 2000}, "context_max": context, "do_re_median": wait,
            "share": {"usd": share, "launches": round(share + 0.04, 2), "tokens": round(share - 0.03, 2)}}


def model_line(model: str | None, provider: str | None, launches: int, usd: float, share: float, effort: int,
               per_usd: float, hour: float) -> dict:
    """A line of `by_model` (team 1.36.64): a model and its provider, its launches, its cost, its share, its effort,
    its cost per launch and per hour of effort -- `None` the launches without a model written."""
    return {"model": model, "provider": provider, "launches": launches, "cost": _three(usd, launches, launches * 117_000),
            "share": {"usd": share, "launches": round(share + 0.02, 2), "tokens": round(share - 0.01, 2)},
            "effort": effort, "per_launch": {"usd": per_usd, "tokens": 117_000},
            "per_effort_hour": {"usd": hour, "tokens": 2_700_000}}


def band(start, end, launches: int, usd: float, share: float, per_usd: float | None, hour: float | None) -> dict:
    """A band of `by_duration` or of `context.by_band` (team 1.36.64): its bounds as the face gives them -- `to` None
    for the last --, its launches, its cost and share, its cost per launch and per hour; an empty band costs 0, its
    rates none (D11)."""
    return {"from": start, "to": end, "launches": launches, "cost": _three(usd, launches, launches * 116_000),
            "share": {"usd": share, "launches": share, "tokens": share},
            "per_launch": {"usd": per_usd, "tokens": None if per_usd is None else 116_000},
            "per_effort_hour": {"usd": hour, "tokens": None if hour is None else 2_650_000}}


def season_stats(n: int, state: str, started: str, ended: str | None = None, **said) -> dict:
    """A season of `core-review` as `team stats --json` says it under `season`, in the face of the socle (team
    1.36.62): its delegations, their price, the root's share, its stopped tasks, its budget in time, each measure
    judged against the median of the seasons (`against.<group>.<key>`), its tasks and its members -- the figures given
    in `said`, written one by one: none is the quotient of two others, so that a post that computes draws another
    figure than the face's. A season without a launch is `empty`, its measures none."""
    empty = not said
    none3 = _three(None, None, None)
    zero3 = _three(0.0, 0, 0)
    return {"season": n, "started": started, "ended": ended, "stopped": ended, "state": state, "empty": empty,
            "tasks": said.get("tasks", {"born": 0, "closed": 0, "stopped": 0, "open": 0}),
            "cost": said.get("cost", zero3), "delegations": said.get("delegations", 0),
            "per_delegation": said.get("per_delegation", none3),
            "per_launch": said.get("per_launch", {"usd": None, "tokens": None}),
            "per_effort_hour": said.get("per_effort_hour", {"usd": None, "tokens": None}),
            "root": said.get("root", {"member": "lead", "cost": zero3, "share": none3}),
            "stopped_tasks": said.get("stopped_tasks", {"tasks": 0, "cost": zero3, "share": none3}),
            "budget": said.get("budget"),
            "time": said.get("time", {"elapsed": 82800, "active": 0, "effort": 0, "active_share": 0.0,
                                      "parallelism": None, "slot": 7200, "effort_by_slot": [0] * 12}),
            "opening": {"count": 0, "median": None, "p90": None},
            "principal": said.get("principal", {"asked": 0, "answered": 0, "wait_median": None, "wait_max": None,
                                                "from_principal": {"asked": 0, "answered": 0, "wait_median": None,
                                                                   "wait_max": None}}),
            "context": said.get("context", {"median": None, "p90": None, "max": None, "renewals": 0}),
            "losses": said.get("losses", {"failed": 0, "cost": zero3, "reasons": {}, "silences": 0}),
            "by_task": said.get("by_task", []), "by_member": said.get("by_member", []),
            "by_model": said.get("by_model", []), "by_duration": said.get("by_duration", []),
            "against": said.get("against", {"per_delegation": {base: _against(None, None) for base in
                                                               ("usd", "launches", "tokens")},
                                            "per_effort_hour": {base: _against(None, None) for base in ("usd", "tokens")},
                                            "losses": {"failed": _against(1, None)},
                                            "context": {"p90": _against(0.52, None)}})}


SEASON_STATS = [
    season_stats(1, "stopped", "2026-10-08T09:00:00+00:00", "2026-10-09T09:00:00+00:00",
                 tasks={"born": 4, "closed": 4, "stopped": 0, "open": 0}, cost=_three(12.4, 20, 2_400_000, True),
                 delegations=6, per_delegation=_three(1.93, 3.07, 380_000), per_launch={"usd": 0.66, "tokens": 117_000},
                 per_effort_hour={"usd": 9.8, "tokens": 1_700_000},
                 root={"member": "lead", "cost": _three(4.1, 7, 820_000), "share": _three(0.31, 0.36, 0.33)},
                 stopped_tasks={"tasks": 0, "cost": _three(0.0, 0, 0), "share": _three(0.0, 0.0, 0.0)},
                 budget={"usd": {"cap": 20.0, "spent": 12.4, "share": 0.62, "per_active_hour": 14.3,
                                 "hours_left": None}, "launches": None},
                 time={"elapsed": 86400, "active": 3120, "effort": 4860, "active_share": 0.0361, "parallelism": 1.56,
                       "slot": 7200, "effort_by_slot": [1200, 3660] + [0] * 10},
                 context={"median": 0.19, "p90": 0.41, "max": 0.47, "renewals": 0},
                 losses={"failed": 0, "cost": _three(0.0, 0, 0), "reasons": {}, "silences": 1},
                 by_task=[task_line("T1", "resolved", 7.3, 11, 4, 0.59, (1.71, 2.6), (0.79, 0.61), 0, 0.41, 1),
                          task_line("T0", "resolved", 5.1, 9, 2, 0.41, (2.38, 4.1), (1.09, 0.93), 0, 0.33, 1)],
                 by_member=[member_line("lead", "make", 4.1, 7, 0.59, 1, None, 0, 0.41, 0.31),
                            member_line("reviewer", None, 8.3, 13, 0.62, 5, 420, 0, 0.47, 0.69)],
                 against={"per_delegation": {"usd": _against(2.18, 0.89), "launches": _against(4.4, 0.7),
                                             "tokens": _against(150_000, 2.4)},
                          "per_effort_hour": {"usd": _against(22.1, 0.44), "tokens": _against(2_100_000, 0.81)},
                          "losses": {"failed": _against(1, 0.0)}, "context": {"p90": _against(0.52, 0.79)}}),
    season_stats(2, "stopped", "2026-10-09T09:00:00+00:00", "2026-10-10T08:00:00+00:00"),
    season_stats(3, "running", "2026-10-10T08:58:00+00:00",
                 tasks={"born": 3, "closed": 1, "stopped": 1, "open": 1}, cost=_three(41.2, 38, 4_560_000),
                 delegations=11, per_delegation=_three(3.47, 3.21, 401_000),
                 per_launch={"usd": 1.12, "tokens": 118_000}, per_effort_hour={"usd": 27.31, "tokens": 3_020_000},
                 root={"member": "lead", "cost": _three(15.2, 16, 1_610_000), "share": _three(0.37, 0.42, 0.33)},
                 stopped_tasks={"tasks": 1, "cost": _three(17.3, 15, 1_900_000), "share": _three(0.42, 0.39, 0.41)},
                 budget={"usd": {"cap": 60.0, "spent": 41.2, "share": 0.69, "per_active_hour": 47.5,
                                 "hours_left": 0.4},
                         "launches": {"cap": 80, "spent": 38, "share": 0.475, "per_active_hour": 43.8,
                                      "hours_left": 0.96}},
                 time={"elapsed": 6540, "active": 3120, "effort": 4860, "active_share": 0.48, "parallelism": 1.56,
                       "slot": 7200, "effort_by_slot": [4860],
                       "cost_by_slot": {"usd": [41.2], "launches": [38], "tokens": [4_560_000]}},
                 principal={"asked": 2, "answered": 1, "wait_median": 600, "wait_max": 600,
                            "from_principal": {"asked": 0, "answered": 0, "wait_median": None, "wait_max": None}},
                 context={"median": 0.22, "p90": 0.74, "max": 0.81, "renewals": 1, "by_band": [
                     band(0.0, 0.25, 9, 8.6, 0.21, 0.96, 19.8), band(0.25, 0.5, 14, 13.9, 0.34, 0.99, 24.6),
                     band(0.5, 0.75, 8, 10.2, 0.25, 1.27, 26.1), band(0.75, 0.9, 5, 7.1, 0.17, 1.42, 31.4),
                     band(0.9, None, 0, 0.0, 0.0, None, None)]},
                 by_model=[model_line("opus-x", "claude", 20, 24.9, 0.6, 3100, 1.24, 28.6),
                           model_line("fable-y", "claude", 16, 15.0, 0.36, 1500, 0.94, 37.3),
                           model_line(None, None, 2, 1.3, 0.04, 260, 0.65, 18.4)],
                 by_duration=[band(0, 60, 9, 3.1, 0.08, 0.34, 61.9), band(60, 180, 14, 9.8, 0.24, 0.7, 34.2),
                              band(180, 600, 10, 14.2, 0.34, 1.42, 23.8), band(600, 1800, 4, 12.6, 0.31, 3.15, 16.7),
                              band(1800, None, 1, 1.5, 0.03, 1.5, 2.9)],
                 losses={"failed": 2, "cost": _three(1.3, 2, 240_000), "reasons": {"launch-refused": 2},
                         "silences": 0},
                 by_task=[task_line("T1", "resolved", 9.4, 9, 3, 0.23, (2.91, 2.84), (1.33, 0.65), 0, 0.52),
                          task_line("T2", "stopped", 17.3, 15, 5, 0.42, (3.62, 3.07), (1.66, 0.7), 2, 0.81),
                          task_line("T3", "open", 14.5, 14, 3, 0.35, (4.47, 4.9), (2.05, 1.11), 0, 0.64)],
                 by_member=[member_line("lead", "make", 15.2, 16, 0.97, 2, None, 1, 0.66, 0.37, ("fable-y",),
                                        (19.7, 0.89)),
                            member_line("reviewer", None, 18.6, 15, 1.31, 6, 540, 1, 0.81, 0.45, ("opus-x", "fable-y"),
                                        (33.4, 1.62)),
                            member_line("scribe", None, 7.4, 7, 1.03, 3, 180, 0, 0.38, 0.18, ("opus-x",),
                                        (24.1, 1.09))],
                 against={"per_delegation": {"usd": _against(2.18, 1.71), "launches": _against(4.4, 0.66),
                                             "tokens": _against(150_000, 2.71)},
                          "per_effort_hour": {"usd": _against(22.1, 1.31), "tokens": _against(2_100_000, 1.38)},
                          "losses": {"failed": _against(1, 2.0)}, "context": {"p90": _against(0.81, 0.93)}})]


def all_task(task: str, seasons: list[int], state: str, usd: float, launches: int, do: int, per_usd: float) -> dict:
    """A line of `by_task` under `--all`: a task over all its seasons -- its `seasons`, its cost per delegation."""
    return {"task": task, "name": f"the task {task}", "state": state, "cost": _three(usd, launches, launches * 118_000),
            "do": do, "re": do, "failures": 0, "time": {"elapsed": 3600, "active": 2400, "effort": 3000},
            "first": "2026-10-08T10:00:00+00:00", "last": "2026-10-10T10:00:00+00:00", "context_max": 0.5,
            "per_delegation": {"usd": per_usd, "launches": 2.7, "tokens": 99_000}, "seasons": seasons}


STATS = {"core-review": {                                             # what `team stats core-review --json` says
    "seasons": SEASON_STATS,
    "median": {"tasks": {"closed": 2, "stopped": 0}, "cost": {"usd": 26.8, "launches": 29, "tokens": 3_480_000},
               "time": {"elapsed": 46000, "active": 3120, "effort": 4860, "active_share": 0.26, "parallelism": 1.56},
               "opening": {"median": 5}, "principal": {"wait_median": 600},
               "context": {"median": 0.2, "p90": 0.52}, "losses": {"failed": 1},
               "per_delegation": {"usd": 2.18, "launches": 4.4, "tokens": 150_000},
               "per_effort_hour": {"usd": 22.1, "tokens": 2_100_000}},
    "by_task": [all_task("T0", [1], "resolved", 5.1, 9, 2, 2.38), all_task("T1", [1, 3], "resolved", 16.7, 20, 7, 2.21),
                all_task("T2", [3], "stopped", 17.3, 15, 5, 3.62), all_task("T3", [3], "open", 14.5, 14, 3, 4.47),
                all_task("T4", [1], "resolved", 0.6, 1, 1, 0.55), all_task("T5", [3], "resolved", 0.3, 1, 1, 0.29)],
    "total": {"seasons": 2, "cost": _three(53.6, 58, 6_960_000, True), "delegations": 17,
              "per_delegation": _three(2.88, 3.29, 377_000), "per_launch": {"usd": 0.97, "tokens": 116_000},
              "per_effort_hour": {"usd": 21.7, "tokens": 2_500_000}, "tasks": {"closed": 5, "stopped": 1, "open": 1},
              "stopped_tasks": {"tasks": 1, "cost": _three(17.3, 15, 1_900_000), "share": _three(0.32, 0.26, 0.27)},
              "failed": 2},
    "task_cost": {"usd": {"median": 9.4, "p90": 17.3, "concentration": {"tasks": 3, "of": 6}},
                  "launches": {"median": 9, "p90": 20, "concentration": {"tasks": 3, "of": 6}},
                  "tokens": {"median": 1_060_000, "p90": 2_360_000, "concentration": {"tasks": 3, "of": 6}}}}}


def many_seasons(count: int = 14) -> dict:
    """`core-review` after `count` seasons -- the first, the empty second, then the first played again under each
    number, the one under way last: more tabs of seasons than the title of a narrow dashboard holds."""
    first, empty, now = SEASON_STATS
    seasons = [first, empty] + [{**first, "season": n} for n in range(3, count)] + [{**now, "season": count}]
    return {"core-review": {**STATS["core-review"], "seasons": seasons}}


def script(**extra) -> dict:
    """The two teams, `core-review` read the same at every call unless `states` says otherwise; its
    journal and T3's history for `log`, T2's result for `result`; the declaration of each team."""
    return {"badges": BADGES, "states": {"core-review": [CORE], "ops": [OPS],
                                         "veille": [{"team": "veille", "started": None, "state": "never",
                                                     "waiting_on": [], "required": REQUIRED}]},
            "log": {"core-review": TEAM_LOG, "core-review/T3": T3_LOG, "core-review/T2": T2_LOG}, "results": RESULTS,
            "deletes": DELETES,
            "responses": {"core-review": RESPONSES}, "templates": TEMPLATES, "declarations": DECLARATIONS, **extra}


class Teams:
    """A throwaway house pinning `ui`, the witnesses and their scripts, the journal of `team`: `render`
    plays `./pp ui …` there; `alive` names the witness processes that outlived the post. `agents` gives the
    `status --json` of more agents -- what a season reads of the members' agents."""

    def __init__(self, bench, name: str, team_script: dict | None = None, agents: dict | None = None) -> None:
        env = bench.env(name, packages=("ui",))
        self.made = env.made
        self.ws, self.engine = env.made.parent, env.engine
        self.faces = bench.temp() / f"faces-{name}"
        self.faces.mkdir(exist_ok=True)
        shutil.copy(WITNESSES / "pp-team", self.faces / "team")
        shutil.copy(WITNESSES / "pp-chat", self.faces / "agent")
        for one in ("team", "agent"):
            (self.faces / one).chmod(0o755)
        team_file = bench.temp() / f"{name}-team.json"
        self.team_file = team_file
        self.use(team_script or script())
        chat_file = bench.temp() / f"{name}-chat.json"
        self.chat_file = chat_file
        self.chat_faces = {**MEMBER_FACES, "status": {**MEMBER_FACES["status"], **(agents or {})}, "providers": PROVIDERS}
        self.use_chat()
        self.journal = bench.temp() / f"{name}-team.log"
        self.chat_journal = bench.temp() / f"{name}-chat.log"
        self.env = {"PP_UI_FACES": str(self.faces), "PP_UI_TEAM_SCRIPT": str(team_file),
                    "PP_UI_TEAM_LOG": str(self.journal), "PP_UI_CHAT_SCRIPT": str(chat_file),
                    "PP_UI_CHAT_LOG": str(self.chat_journal)}

    def use(self, team_script: dict) -> None:
        """The witness replays this script from the next call on."""
        self.team_file.write_text(json.dumps(team_script), encoding="utf-8")

    def use_chat(self, statuses: dict | None = None, **script) -> None:
        """The witness of `agent` replays these faces from the next call on -- `statuses`, the `status --json` of more
        agents --, and `script` for every `agent chat` (its `opening`, its `exchanges`...)."""
        faces = {**self.chat_faces, "status": {**self.chat_faces["status"], **(statuses or {})}}
        self.chat_file.write_text(json.dumps({"faces": faces, **script}), encoding="utf-8")

    def render(self, *args: str):
        return D.rendered(cli(self.engine, "ui", *args, cwd=self.ws, env=self.env))

    def journal_lines(self) -> list[str]:
        return self.journal.read_text(encoding="utf-8").splitlines() if self.journal.is_file() else []

    def chat_lines(self) -> list[str]:
        """-> what the witness of `agent` was asked: its faces, and an `open` for any `agent chat`."""
        return self.chat_journal.read_text(encoding="utf-8").splitlines() if self.chat_journal.is_file() else []

    def clear_journal(self) -> None:
        for one in (self.journal, self.journal.with_name(self.journal.name + ".seen.json"),
                    self.journal.with_name(self.journal.name + ".deleted.json"),
                    self.journal.with_name(self.journal.name + ".stopped.json"),
                    self.journal.with_name(self.journal.name + ".documents.json"), self.chat_journal,
                    self.chat_journal.with_name(self.chat_journal.name + ".calls.json")):
            if one.is_file():
                one.unlink()

    def gestures(self, wait: float = 10.0, ticks: tuple[str, ...] = ()) -> list[str]:
        """-> the gestures the witness played, each `team <argv>` as a shell would quote it -- without the tick the
        post plays APART after each gesture played `--no-tick` (ui 1.3.4): waited for (`wait` seconds at most), one
        `team tick <team>` taken out per such gesture -- none owed by a gesture the witness's script refuses (its
        verb's `answers` rc not 0): the post ticks after a verb that answered --; a tick that never came is said in
        the list (`(no tick apart after …)`), so that the list differs from what the case expects. `ticks` names the
        teams whose bare `team tick` the post started apart (`T`): their lines waited for the same way, and kept."""
        answers = json.loads(self.team_file.read_text(encoding="utf-8")).get("answers") or {}
        refused = {verb for verb, answer in answers.items() if int((answer or {}).get("rc") or 0) != 0}
        deadline = time.monotonic() + wait
        while True:
            found = [one for one in self.journal_lines() if one.startswith("team ")]
            kept, owed = [], []
            for one in found:
                words = shlex.split(one)
                if words[1:2] == ["tick"] and len(words) == 3 and words[2] in [team for team, _ in owed]:
                    owed.remove(next(entry for entry in owed if entry[0] == words[2]))
                    continue
                kept.append(one)
                if "--no-tick" in words and len(words) > 2 and words[1] not in refused:
                    owed.append((words[2], one))
            if (not owed and all(f"team tick {team}" in kept for team in ticks)) or time.monotonic() >= deadline:
                return kept + [f"(no tick apart after {one})" for _, one in owed]
            time.sleep(0.1)

    def alive(self) -> list[str]:
        """-> the processes of this house's witness of `team` still running."""
        found = subprocess.run(["pgrep", "-af", str(self.faces / "team")], capture_output=True, text=True)
        return [one for one in found.stdout.splitlines() if "pgrep" not in one]


def cells_of(row: str) -> list[str]:
    """-> the cells of a table's row: what two blanks or more part."""
    import re
    return [one for one in re.split(r"\s{2,}", row.strip(" │┃")) if one]


cells_by_name = D.cells_by_name      # the cells of a table's row by the name of their column (rule 10: one home)


def edge_of(text: str) -> int | None:
    """-> the column right after the MENU's edge in a capture of the Teams or Tasks tab: after the menu's frame in
    ample size (the leftmost frame, found by its corners), after the thin `│` between the menu and its centre in
    compact size; None when the capture shows neither (a menu folded, another tab)."""
    frames = D.frames_of(text)
    if frames:
        x, _, w, _ = min(frames, key=lambda one: (one[0], one[1]))
        return x + w
    rows = [one for one in text.split("\n") if "│" in one]
    return min(one.index("│") for one in rows) + 1 if rows else None


def sides_of(text: str) -> tuple[list[str], list[str]]:
    """-> the menu's side of the pane and the centre's, row by row: what stands left and right of the menu's edge
    (`edge_of`), on the rows of the menu -- the rows of its frame in ample size, the rows carrying the `│` in
    compact size."""
    edge = edge_of(text)
    if edge is None:
        return [], []
    frames = D.frames_of(text)
    rows = text.split("\n")
    if frames:
        x = min(one[0] for one in frames)
        menu = [one for one in frames if one[0] == x]         # the menu's frames, stacked (Show and Team on Tasks)
        top, bottom = min(one[1] for one in menu), max(one[1] + one[3] for one in menu)
        kept = rows[top:bottom]
    else:
        kept = [one for one in rows if "│" in one]
    return [one[:edge - 1] for one in kept], [one[edge:] for one in kept]


def _edge_row(row: str) -> bool:
    """-> whether a row of the centre is an EDGE: the top or the bottom of a frame, or a thin rule."""
    said = row.strip()
    return bool(said) and (said[0] in "╭╰" or set(said) == {"─"})


def head_rows(centre: list[str]) -> list[str]:
    """-> the rows of the head of the team chosen: the centre's rows above its first band's bottom edge, the frame's
    top left out, those with text."""
    bottom = next((n for n, one in enumerate(centre) if _edge_row(one) and not one.strip().startswith("╭")),
                  len(centre))
    return [one.strip() for one in centre[:bottom] if one.strip() and not _edge_row(one)]


def band_rows(centre: list[str]) -> list[str]:
    """-> the rows of the band under the first table of the centre: those below its first bottom edge, the edges
    of the frames left out, those with text."""
    bottom = next((n for n, one in enumerate(centre) if _edge_row(one) and not one.strip().startswith("╭")),
                  len(centre))
    return [one.strip() for one in centre[bottom + 1:] if one.strip() and not _edge_row(one)]


def in_order(row: str, *words: str) -> bool:
    """-> whether the row holds each word, in that order."""
    import re
    return bool(re.search(r".*?".join(rf"(?<!\w){re.escape(one)}(?!\w)" for one in words), row))


def look_of(text: str, name: str, within: str = "") -> tuple[bool, str | None] | None:
    """-> how the first cell holding `name` as a word is drawn in a `--styles` capture -- on the first row holding
    `within`, when given --: (bold, foreground), the foreground as its SGR parameters say it, None when the cell
    carries none."""
    import re

    def codes(params: str) -> tuple[bool, str | None]:
        tokens, bold, fg, at = params.split(";"), False, None, 0
        while at < len(tokens):
            one = tokens[at]
            if one in ("38", "48") and at + 1 < len(tokens):
                width = 5 if tokens[at + 1] == "2" else 3
                if one == "38":
                    fg = ";".join(tokens[at + 2:at + width])
                at += width
                continue
            if one == "1":
                bold = True
            elif one.isdigit() and (30 <= int(one) <= 37 or 90 <= int(one) <= 97):
                fg = one
            at += 1
        return bold, fg

    for row in text.split("\n"):
        bare = D.ANSI.sub("", row)
        if within not in bare or not re.search(rf"\b{re.escape(name)}\b", bare):
            continue
        current = ""
        for part in re.split(r"(\x1b\[[0-9;]*m)", row):
            found = D.SGR.fullmatch(part)
            if found:
                current = found.group(1)
            elif re.search(rf"\b{re.escape(name)}\b", part):
                return codes(current)
    return None


def form_rows(text: str) -> list[str]:
    """-> the rows of a form a capture shows: those of its zone of fields when the keys noted where its zones stand
    (`boxes`) -- the side pane left out --, the overlay's rows otherwise."""
    line = next((one for one in text.splitlines() if one.startswith("boxes ")), "")
    found = dict(re.findall(r"([\w-]+)=(\d+,\d+,\d+,\d+)", line.split(" | ")[-1]))
    if "form-fields" not in found:
        return D.overlay_rows(text)
    x, y, w, h = map(int, found["form-fields"].split(","))
    rows = text.splitlines()
    return [rows[n][x:x + w].rstrip(" ▁▂▃▄▅▆▇█▔▀▕▏").strip(" │").strip() for n in range(y, min(y + h, len(rows)))]


def season_rows(text: str, declared: dict) -> list[list[str]]:
    """-> the cells of the season's table: the line above the first member's, then one per member of `declared`,
    each found by its name and its path; [] when a member's line is missing."""
    rows = [cells_of(one) for one in form_rows(text)]
    found = []
    for one in declared["declared"]["agents"]:
        at = next((n for n, cells in enumerate(rows) if cells[:2] == [one["member"], one["path"]]), None)
        if at is None:
            return []
        found.append(rows[at])
        if len(found) == 1:
            found.insert(0, rows[at - 1])
    return found


def remedy_of(done) -> str:
    """-> the remedy line of a render: the footer's second line -- the closing lines a word of the keys notes left out."""
    lines = [one for one in done.stdout.rstrip("\n").split("\n") if not one.startswith("boxes ")]
    return lines[-2].strip() if len(lines) >= 2 else ""


# ---------- the next season of `core-review` (`S`): what the scenarios `ui-team-season-*` of a team at work share ----------
SEASON_SIZE = ("--size", "140x60")     # the form of SEASON.md whole, its side pane tall enough
SEASON_SMALL = ("--size", "140x60")
TO_LINES = "ctrl+pagedown,ctrl+pagedown,ctrl+pagedown"    # from the preset `S` focuses: the documents, the launch, then
#                                        the members, its table of lines first and focused
TO_PACKAGES = "tab,tab,tab"            # in a profile, from the model down to the packages: effort, permissions, packages
NEXT = "team start core-review --no-tick"     # the season SEASON.md writes: a start without a flag of the season
NEXT_DECLARED = "team declare core-review --season --context 90 --json"   # nothing changed: the context at its default


def season_line(text: str, member: str, path: str) -> list[str]:
    """-> the cells of the season's line of `member`, found by its name and its path; [] when it is missing."""
    return next((cells for cells in map(cells_of, form_rows(text)) if cells[:2] == [member, path]), [])


# ---------- a long thread, the post played on it under the pilot ----------
CREW = ["lead", "reviewer"] + [f"dev{n}" for n in range(1, 8)]     # with `house`, ten columns
LONG = 425                                                         # the rows of banking-build T2, the step's measure


def clock(n: int) -> str:
    """-> the hour of 10/10 the `n`-th post of the long thread is dated at: seven seconds apart from 09:01:00."""
    seconds = 9 * 3600 + 60 + 7 * n
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def long_post(n: int, source: str, target: str) -> dict:
    return event(clock(n), "post", 42 + n, task="T3", **{"from": source}, to=target, verb="do",
                 text=f"part {n + 1} of the long review, said with words enough to reach the note")


def long_log(count: int = LONG) -> list[dict]:
    """-> T3's thread, long: its birth, then `count` posts of `lead` with each other participant in turn, to it then
    from it -- ten columns, and every row `lead`'s, so that the Teams tab centred on `lead` draws them all."""
    others = ["house"] + CREW[1:]
    found = [T3_LOG[0]]
    for n in range(count):
        other = others[n % len(others)]
        found.append(long_post(n, *(("lead", other) if n % 2 == 0 else (other, "lead"))))
    return found


def lead_act(n: int) -> dict:
    """An activity of `lead`'s wake-up on T3, as the watch relays it: a call of a tool, its title the `n`-th."""
    return {"agent": "lead", "run": "a77f10", "event": "activity", "kind": "tool", "name": "Read",
            "title": f"part-{n}.py", "pp": False, "task": "T3", "tag": "lead-T3-4", "launch": 4}


def long_script(watch: list[dict]) -> dict:
    """The two teams, T3 and ops' T1 played by a wake-up, T3's thread long, `core-review`'s watch saying `watch`."""
    found = script(log={"core-review": TEAM_LOG, "core-review/T3": long_log(), "core-review/T2": T2_LOG},
                   watch={"core-review": watch})
    found["states"].update({"core-review": [LIVE_CORE], "ops": [LIVE_OPS]})
    return found


SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
# what every probe starts with: the post opened on the house, its pane shown at the size asked; `palette.sequence_text`
# and `palette.sequence_head` counted in COUNTS; `TEXT` the drawing of reference, never counted; `probe(app, pilot,
# view, out)`, written by the scenario, fills `out`, printed as JSON
PILOT = """
import asyncio, json, sys, time
from dataclasses import replace
from pathlib import Path
sys.path.insert(0, sys.argv[1])
WS, PANE, ROWS = sys.argv[2], sys.argv[3], int(sys.argv[5])
SIZE = tuple(int(one) for one in sys.argv[4].split("x"))
from textual import events
from textual.strip import Strip
import palette
TEXT = palette.sequence_text
COUNTS = {"text": 0, "head": 0}


def counted(key, function):
    def call(*args, **kwargs):
        COUNTS[key] += 1
        return function(*args, **kwargs)
    return call


palette.sequence_text = counted("text", palette.sequence_text)
palette.sequence_head = counted("head", palette.sequence_head)
from model import House
from app import PostApp
from faces.team import close_all
from panes.sequence_body import SequenceBody


def body_of(view):
    found = list(view.query(SequenceBody))
    return found[0] if found else None


def drawn(view):
    body = body_of(view)
    return body.drawn if body is not None else None


async def until(pilot, test, seconds=12.0):
    deadline = time.monotonic() + seconds
    while not test():
        if time.monotonic() > deadline:
            return False
        await asyncio.sleep(0.02)
    await pilot.pause()
    return True


def cells(strips):
    return [[(seg.text, str(seg.style or "")) for seg in strip.simplify()] for strip in strips]


def as_palette(view):
    \"\"\"-> whether the lines the body shows and the head are those `palette.sequence_text` draws, in text and styles.\"\"\"
    body = body_of(view)
    if body is None:
        return False
    head, text = TEXT(replace(view.sequence, rows=tuple(view.shown)), max(40, view.size.width - 2), view.cursor,
                      view.activities)
    rows, (x, top) = text.split("\\n"), body.scroll_offset
    base, width, console = body.rich_style, body.size.width, body.app.console
    expected = [Strip(list(rows[top + y].render(console))).apply_style(base).crop_extend(x, x + width, base)
                if top + y < len(rows) else Strip.blank(width, base)
                for y in range(body.scrollable_content_region.height)]
    found = [body.render_line(y) for y in range(body.scrollable_content_region.height)]
    said = view.query_one(".sequence-head .sequence-lines").content
    return (cells(found) == cells(expected) and said.plain == head.plain and said.spans == head.spans
            and said.style == head.style)


async def main():
    app, out = PostApp(House.at(Path(WS))), {}
    try:
        async with app.run_test(size=SIZE) as pilot:
            await app.settled()
            await pilot.pause()
            app.show_pane(PANE)
            await app.pane_settled()
            await pilot.pause()
            await probe(app, pilot, app.query_one(f"#{PANE}-sequence"), out)
    finally:
        await close_all()
    print(json.dumps(out))
"""


def piloted(bench, house: Teams, name: str, probe: str, *panes: str, size: str = "180x50",
            rows: int = LONG) -> list[tuple[int, dict, str]]:
    """Plays `probe` -- the text of `async def probe(app, pilot, view, out)` -- in the post opened on `house` under
    Textual's pilot, at `size`, one subprocess per pane of `panes` shown, all at once: -> for each pane, its exit
    code, the `out` it printed, its stderr."""
    env = {**os.environ, **house.env, "PP_HOME": str(house.ws / ".pp")}
    started = []
    for pane in panes:
        path = bench.temp() / f"{name}-{pane}-probe.py"
        path.write_text(PILOT + probe + "\n\nasyncio.run(main())\n", encoding="utf-8")
        started.append(subprocess.Popen([*TEXTUAL, str(path), str(SKILL), str(house.ws), pane, size, str(rows)],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=house.ws,
                                        env=env))
    found = []
    for one in started:
        out, err = one.communicate(timeout=120)
        try:
            said = json.loads(out.strip().splitlines()[-1])
        except (ValueError, IndexError):
            said = {}
        found.append((one.returncode, said, err))
    return found
