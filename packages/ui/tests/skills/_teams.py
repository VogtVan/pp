"""_teams -- what the scenarios of the Teams tab share (rule 10): a house pinning `ui`, the witness
`pp-team` posed under PP_UI_FACES as `team` (and `pp-chat` as `agent`, its faces empty, so that the
Agents tab reads nothing real), the script of three declared teams -- `core-review` and `ops` started,
`veille` never --, the journal of the witness, the renders of the post, and the processes of the witness
still alive; the gestures the witness played, the preview a render shows and its remedy line."""
from __future__ import annotations

import json
import shutil
import subprocess

from tests.harness import SOURCE, cli, support

D = support(__file__, "dialogue")   # the provider of fixture the post's faces name

WITNESSES = SOURCE / "packages" / "ui" / "tests" / "witness"

STARTED = {"at": "2026-10-10T09:00:00+00:00", "id": 1}
LAST = {"id": 47, "kind": "post", "at": "2026-10-10T09:12:51+00:00"}
REQUIRED = ["agent", "kit", "team"]          # what a member may not switch off, as `status --json` says it
# the launch the first season of `core-review` gave: what its next wake-up gets
LAUNCH = {"harness": None, "provider": D.PROVIDER, "model": "opus", "permissions": None, "effort": "high",
          "launches": None, "packages": []}
BARE = {key: None for key in LAUNCH} | {"packages": []}     # a season started without a flag

CORE = {
    "team": "core-review", "owner": "house", "principals": ["pm"], "started": STARTED, "changed": False,
    "limits": {"budget": 2.0, "budget-wakes": 40}, "schedule": {"minutes": 5, "laid": True},
    "cost": 1.84, "budget_spent": False, "budget": {"cap": 2.0, "spent": 1.84, "reserved": 0.1, "left": 0.06},
    "wakes": {"launched": 7, "bound": 40}, "last": LAST, "required": REQUIRED,
    "state": "working", "waiting_on": [], "paused": None,
    "season": {"n": 1, "at": STARTED["at"], "budget": 2.0, "budget-wakes": None}, "launch": LAUNCH,
    "tasks": [
        {"id": "T1", "name": None, "text": "review PR 87 and its migration notes",
         "last": {"id": 12, "kind": "stopped", "at": "2026-10-10T09:00:30+00:00"},
         "state": "stopped", "from": "house", "to": "lead", "ceremony": None, "period": None,
         "messages": 2, "resumed": None, "holders": ["lead"], "dos": [], "waits": []},
        {"id": "T2", "name": "daily 2026-10-10 09:30", "text": "the ceremony `daily` of team core-review rings",
         "last": {"id": 40, "kind": "done", "at": "2026-10-10T09:01:30+00:00"},
         "state": "resolved", "from": "core-review", "to": "lead", "ceremony": "daily",
         "period": "2026-10-10", "messages": 5, "resumed": None, "holders": [],
         "dos": [{"id": 1, "from": "lead", "to": "reviewer", "answered": 101}],
         "waits": [{"member": "lead", "any": 1, "answered": 1, "of": 1, "open": False}]},
        {"id": "T3", "name": "review PR 88", "text": "review PR 88 and its release notes", "cost": 0.42,
         "last": {"id": 47, "kind": "wake-ended", "at": "2026-10-10T09:06:00+00:00"},
         "state": "open", "from": "house", "to": "lead", "ceremony": None, "period": None,
         "messages": 6, "resumed": 31, "holders": ["lead", "reviewer"],
         "dos": [{"id": 2, "from": "lead", "to": "reviewer", "answered": None}], "waits": []}],
    "members": [
        {"member": "lead", "path": "agents/lead", "run": "a77f10", "how": "ended", "since": None,
         "tasks": ["T1", "T2", "T3"], "waits": ["reviewer"], "pending": [],
         "unseen": [{"member": "reviewer", "task": "T2", "id": 40}], "launch": LAUNCH,
         "owes": [{"id": 42, "verb": "do", "from": "house", "task": "T3", "reminded": 1},
                  {"id": 48, "verb": "re", "from": "reviewer", "task": "T3", "reminded": 0}], "health": None},
        {"member": "reviewer", "path": "agents/reviewer", "run": "a01389", "how": "running",
         "since": "2026-10-10T09:12:10+00:00", "tasks": ["T2", "T3"], "waits": [],
         "pending": [{"id": 46, "verb": "re", "from": "lead", "task": "T3"}], "unseen": [],
         "launch": {**LAUNCH, "model": "sonnet", "packages": ["plan=off"]}, "owes": [], "health": None}],
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

T4 = {"id": "T4", "state": "open", "from": "pm", "to": "lead", "ceremony": None, "period": None, "messages": 1,
      "resumed": None, "holders": ["lead"], "dos": [], "waits": []}
CORE_NEXT = {**CORE, "tasks": CORE["tasks"] + [T4], "last": {"id": 48, "kind": "post", "at": "2026-10-10T09:13:30+00:00"}}

# a team at three ceremonies: `daily` rung and closed (T2), `retro` after it under `any 2` rung and open -- one of
# its three participants has answered, its task T5 carries the facilitator's wait --, `review` never rung
T5 = {"id": "T5", "state": "open", "from": "core-review", "to": "lead", "ceremony": "retro", "period": "2026-10-10",
      "messages": 4, "resumed": None, "holders": ["lead", "scribe", "dev2"],
      "dos": [{"id": 3, "from": "lead", "to": "reviewer", "answered": 103}, {"id": 4, "from": "lead", "to": "scribe", "answered": None},
                      {"id": 5, "from": "lead", "to": "dev2", "answered": None}],
      "waits": [{"member": "lead", "any": 2, "open": True}]}
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
    "schedule": {"minutes": None, "laid": None}, "cost": 0.4, "budget_spent": False, "budget": None,
    "wakes": {"launched": 2, "bound": None}, "last": {"id": 9, "kind": "wake-launched", "at": "2026-10-10T09:10:00+00:00"},
    "required": REQUIRED, "state": "working", "waiting_on": [], "paused": None,
    "season": {"n": 1, "at": STARTED["at"], "budget": None, "budget-wakes": None}, "launch": BARE,
    "tasks": [
        {"id": "T1", "name": None, "text": "rotate the certificates of the gateway before friday",
         "last": {"id": 9, "kind": "wake-launched", "at": "2026-10-10T09:10:00+00:00"},
         "state": "open", "from": "house", "to": "sre", "ceremony": None, "period": None, "messages": 3,
         "resumed": None, "holders": ["sre", "dba"],
         "dos": [{"id": 6, "from": "sre", "to": "dba", "answered": 106}, {"id": 7, "from": "sre", "to": "net", "answered": None}],
         "waits": []},
        {"id": "T2", "name": "weekly report", "text": "write the weekly report",
         "last": {"id": 5, "kind": "done", "at": "2026-10-10T08:30:00+00:00"},
         "state": "resolved", "from": "house", "to": "sre", "ceremony": None, "period": None, "messages": 2,
         "resumed": None, "holders": [], "dos": [], "waits": []}],
    "members": [{"member": "sre", "path": "agents/sre", "run": "b11111", "how": "running",
                 "since": "2026-10-10T09:10:00+00:00", "tasks": ["T1", "T2"], "waits": ["net"], "pending": [], "unseen": [],
                 "launch": BARE},
                {"member": "dba", "path": "agents/dba", "run": "b22222", "how": "ended", "since": None, "tasks": ["T1"],
                 "waits": [], "pending": [], "unseen": [], "launch": BARE}],
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


SHADES = [("alpha", "working", (), 1, 0, 0, None), ("beta", "waiting", ("members",), 0, 0, 0, None),
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
          event("09:06:00", "wake-ended", 47, tag="reviewer-T3-2", agent="reviewer", run="a01389", index=2, cost=0.03)]
TEAM_LOG = [event("09:00:00", "team-started", 1, root="lead")] + T3_LOG
WRITTEN = event("09:05:30", "post", 46, task="T3", **{"from": "house"}, to="reviewer", verb="re", re=45, text="yes, 412")
T3_READS = [T3_LOG, sorted(T3_LOG + [WRITTEN], key=lambda one: one["id"])]   # #46 written while the watch started
DEBT_LOG = [T3_LOG[0], T3_LOG[1], T3_LOG[2], T3_LOG[3], WRITTEN,
            event("09:06:00", "wake-ended", 47, tag="reviewer-T3-2", agent="reviewer", run="a01389", index=2, cost=0.03),
            event("09:07:00", "post", 48, task="T3", **{"from": "reviewer"}, to="lead", verb="re", re=44, was="done",
                  text="LGTM"),
            event("09:08:00", "wake-intent", 49, tag="lead-T3-3", agent="lead", path="agents/lead", task="T3",
                  run="a77f10", index=3, messages=[48], relance="owed"),
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
        "task": "T3", "tag": "reviewer-T3-3", "index": 3}       # a step names its task, its tag, its exchange (team 0.28.0)
T3_WATCH = [T3_LOG[2],                                   # #44 again: the history read it already
            {"sleep": 0.4},
            event("09:13:00", "post", 48, task="T3", **{"from": "lead"}, to="reviewer", verb="re", re=47, text="412 held"),
            STEP,
            {"sleep": 0.3},
            event("09:14:00", "wake-ended", 49, tag="reviewer-T3-3", agent="reviewer", run="a01389", index=3, cost=0.02)]
PROVIDERS = [{"provider": D.PROVIDER, "spells": ["model", "max_budget_usd", "effort", "permissions"],
              "models": list(D.MODELS)}]                                  # what `agent providers --json` says
RESULTS = {"core-review/T2": {"verdict": "LGTM", "remarks": 2}}


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
# the team's watch while `reviewer` plays a wake-up and `lead` another: what the tab of `reviewer` keeps is its own
MEMBER_WATCH = [{"sleep": 0.6},
                event("09:10:00", "wake-launched", 50, tag="reviewer-T3-3", agent="reviewer", run="a01389", pid=4242),
                {"agent": "reviewer", "run": "a01389", "event": "block", "stack": "BOOT ▸ MEMBER ▸ TURN{4/4}", "wait": True,
                 "task": "T3", "tag": "reviewer-T3-3", "index": 3},
                event("09:10:01", "wake-launched", 51, tag="lead-T3-4", agent="lead", run="a77f10", pid=4243),
                {"agent": "lead", "run": "a77f10", "event": "refused", "code": "lead-only", "task": "T3", "tag": "lead-T3-4",
                 "index": 4},
                {"sleep": 0.4},
                event("09:11:00", "wake-ended", 52, tag="reviewer-T3-3", agent="reviewer", run="a01389", index=3, cost=0.04)]
RESPONSES = [{"id": 40, "member": "reviewer", "path": "agents/reviewer", "task": "T2", "run": "a01389", "index": 1,
              "at": "2026-10-10T09:01:30+00:00", "cost_usd": 0.02, "response": '{"done": "the daily: nothing to say"}'},
             {"id": 47, "member": "lead", "path": "agents/lead", "task": "T3", "run": "a77f10", "index": 4,
              "at": "2026-10-10T09:06:00+00:00", "cost_usd": 0.03, "response": '{"ask": "lead asks"}'},
             {"id": 49, "member": "reviewer", "path": "agents/reviewer", "task": "T3", "run": "a01389", "index": 2,
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
                            {"id": 2, "from": "lead", "to": "scribe", "answered": None}],
             "waits": [{"member": "lead", "any": 2, "answered": 1, "of": 3, "open": True}]},
            ("lead", "a77f10", "09:12:10"), relance="owed") if one["id"] == "T3" else one for one in CORE["tasks"]]}
# a member that does not answer (team 0.35.0): `reviewer` suspected, tried again at 09:30; `lead` fallen once and
# back, its run ended
SUSPECTED = {**CORE, "state": "waiting", "waiting_on": ["suspected"], "members": [
    {**CORE["members"][0], "health": {"suspected": False, "falls": 0, "tried_at": None, "repents": 1}},
    {**CORE["members"][1], "how": "dead", "since": None,
     "health": {"suspected": True, "falls": 2, "tried_at": "2026-10-10T09:30", "repents": 0}}]}


LIVE_CORE = {**CORE, "tasks": [running(one, ("reviewer", "a01389", "09:12:10")) if one["id"] == "T3" else one
                               for one in CORE["tasks"]]}
LIVE_OPS = {**OPS, "tasks": [running(one, ("sre", "b11111", "09:10:00")) if one["id"] == "T1" else one
                             for one in OPS["tasks"]]}
# two members on T3: a step of `lead` (its exchange 4), one of `reviewer` (its exchange 3), then `lead`'s wake-up ends
LEAD_STEP = {"agent": "lead", "run": "a77f10", "event": "block", "stack": "BOOT ▸ MEMBER ▸ TURN{3/4}", "wait": False,
             "task": "T3", "tag": "lead-T3-4", "index": 4}
TWO_WATCH = [{"sleep": 0.3}, LEAD_STEP, {"sleep": 0.2}, STEP, {"sleep": 0.3},
             event("09:13:30", "wake-ended", 53, tag="lead-T3-4", agent="lead", run="a77f10", index=4, cost=0.01)]
def template(name: str, description: str, members: list[str], ceremony: str | None) -> dict:
    """A template as `team templates --json` says it, for its default members."""
    return {"template": name, "description": description, "members": members, "root": members[0],
            "reports": [{"from": members[1:], "to": members[0]}] if len(members) > 1 else [],
            "ceremony": ceremony, "limits": {"budget": 5, "wakes": 8, "timeout": 900},
            "intention": f"The root `{members[0]}` answers every task."}


TEMPLATES = [template("supervisor-workers", "the root splits each task, one part per worker",
                      ["supervisor", "worker-1", "worker-2"], "daily every weekday 09:30 with worker-1 worker-2 -> supervisor"),
             template("lead-reviewers", "the root does the work, each reviewer checks its draft", ["lead", "reviewer"], None),
             template("chain", "each member hands the next step to the next one", ["first", "second", "third"], None),
             template("solo", "one member does every task", ["solo"], None),
             template("empty", "the smallest declaration", ["root"], None)]


ALL_ON = {"plan": True, "steering": True, "team": True}


def declaration(team: str, members: list[tuple], limits: dict, started: bool = True) -> dict:
    """The declaration of `team` as `team declaration --json` says it: `declared`, what the next start writes -- its
    members in their order, the first the root, each `(name, path)` or `(name, path, packages, born)`: whether its
    agent is born and the packages it plays, `{name: on}` (team 0.38.0; born, every package on, by default) --, the
    limits of `TEAM.md` alone."""
    return {"team": team, "path": f"teams/{team}/TEAM.md", "text": f"---\nname: {team}\n---\n", "digest": "abc123abc123",
            "verdict": {"ok": True, "refusal": None}, "started": {**STARTED, "digest": "abc123abc123"} if started else None,
            "changed": False, "pending": [],
            "declared": {"agents": [{"member": one[0], "path": one[1], "born": one[3] if len(one) > 3 else True,
                                     "packages": [{"name": name, "on": on}
                                                  for name, on in (one[2] if len(one) > 2 else ALL_ON).items()]}
                                    for one in members], "root": members[0][0],
                         "reports": [], "principals": [], "limits": limits, "schedule": None, "ceremonies": [],
                         "entries": {}, "work": None}}


# `core-review` declares a member more than it started with (`scribe`) and a budget below the season's own
DECLARATIONS = {
    "core-review": declaration("core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer"),
                                               ("scribe", "agents/scribe", {"plan": True, "team": True})],
                               {"budget": 1.0, "budget-wakes": 40}),
    "ops": declaration("ops", [("sre", "agents/sre"), ("dba", "agents/dba")], {}),
    "veille": declaration("veille", [("scout", "agents/scout"), ("writer", "agents/writer")], {"budget": 3.0},
                          started=False)}
REFUSED = {**DECLARATIONS["ops"], "verdict": {"ok": False, "refusal": "team-invalid -- `parallel: 0` is no whole "
                                                                      "number of 1 or more"},
           "pending": None, "declared": None}


def tail(last: dict | None) -> list[dict]:
    """An agent's `status --json` without a run: the providers and what it last played -- its packages are the
    declaration's (team 0.38.0)."""
    return [{"agent": "?", "providers": [D.PROVIDER], "last": last}]


# the agents of the members as a season reads them: `scout` and `writer` played before, the others never
SEASON_AGENTS = {"agents/scout": tail({"provider": D.PROVIDER, "policy": {"model": "opus", "effort": "high"}}),
                 "agents/writer": tail({"provider": D.PROVIDER, "policy": {"model": "sonnet"}}),
                 "agents/lead": tail(None), "agents/reviewer": tail(None), "agents/scribe": tail(None)}


def script(**extra) -> dict:
    """The two teams, `core-review` read the same at every call unless `states` says otherwise; its
    journal and T3's history for `log`, T2's result for `result`; the declaration of each team."""
    return {"badges": BADGES, "states": {"core-review": [CORE], "ops": [OPS],
                                         "veille": [{"team": "veille", "started": None, "state": "never",
                                                     "waiting_on": [], "required": REQUIRED}]},
            "log": {"core-review": TEAM_LOG, "core-review/T3": T3_LOG}, "results": RESULTS,
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
        faces = {**MEMBER_FACES, "status": {**MEMBER_FACES["status"], **(agents or {})}, "providers": PROVIDERS}
        chat_file.write_text(json.dumps({"faces": faces}), encoding="utf-8")
        self.journal = bench.temp() / f"{name}-team.log"
        self.chat_journal = bench.temp() / f"{name}-chat.log"
        self.env = {"PP_UI_FACES": str(self.faces), "PP_UI_TEAM_SCRIPT": str(team_file),
                    "PP_UI_TEAM_LOG": str(self.journal), "PP_UI_CHAT_SCRIPT": str(chat_file),
                    "PP_UI_CHAT_LOG": str(self.chat_journal)}

    def use(self, team_script: dict) -> None:
        """The witness replays this script from the next call on."""
        self.team_file.write_text(json.dumps(team_script), encoding="utf-8")

    def render(self, *args: str):
        return cli(self.engine, "ui", *args, cwd=self.ws, env=self.env)

    def journal_lines(self) -> list[str]:
        return self.journal.read_text(encoding="utf-8").splitlines() if self.journal.is_file() else []

    def chat_lines(self) -> list[str]:
        """-> what the witness of `agent` was asked: its faces, and an `open` for any `agent chat`."""
        return self.chat_journal.read_text(encoding="utf-8").splitlines() if self.chat_journal.is_file() else []

    def clear_journal(self) -> None:
        for one in (self.journal, self.journal.with_name(self.journal.name + ".seen.json"), self.chat_journal,
                    self.chat_journal.with_name(self.chat_journal.name + ".calls.json")):
            if one.is_file():
                one.unlink()

    def gestures(self) -> list[str]:
        """-> the gestures the witness played, each `team <argv>` as a shell would quote it."""
        return [one for one in self.journal_lines() if one.startswith("team ")]

    def alive(self) -> list[str]:
        """-> the processes of this house's witness of `team` still running."""
        found = subprocess.run(["pgrep", "-af", str(self.faces / "team")], capture_output=True, text=True)
        return [one for one in found.stdout.splitlines() if "pgrep" not in one]


def cells_of(row: str) -> list[str]:
    """-> the cells of a table's row: what two blanks or more part."""
    import re
    return [one for one in re.split(r"\s{2,}", row.strip(" │┃")) if one]


def sides_of(text: str) -> tuple[list[str], list[str]]:
    """-> the menu's side of the pane and the centre's, row by row: what stands left and right of the menu's edge."""
    rows = [one.split("│", 1) for one in text.split("\n") if "│" in one]
    return [one[0] for one in rows], [one[1] for one in rows]


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


def preview_in(done, start: str) -> str:
    """-> the command a render shows, `./pp team …`, from its first word `start` (`./pp team stop`) to the
    end of its line -- the box of an overlay cut off."""
    for line in done.stdout.split("\n"):
        at = line.find(start)
        if at >= 0:
            return line[at:].rstrip(" │┃|").rstrip()
    return ""


def preview_folded(done, start: str) -> str:
    """-> the command a render shows from its first word `start` on, its lines folded by the box joined again -- the
    command of a gesture's overlay, wider than its box."""
    lines = done.stdout.split("\n")
    at = next((index for index, line in enumerate(lines) if start in line), None)
    if at is None:
        return ""
    said = [lines[at][lines[at].find(start):].rstrip(" │┃|").rstrip()]
    for line in lines[at + 1:]:
        part = line.strip().strip("│┃|").strip()
        if not part or part.startswith("["):
            break
        said.append(part)
    return " ".join(said)


def overlay_preview(done, start: str) -> str:
    """-> the command an overlay shows under its fields, its lines folded by the box joined again -- what stands
    above the overlay (the head of a team) left out."""
    from types import SimpleNamespace
    return preview_folded(SimpleNamespace(stdout="\n".join(D.overlay_rows(done.stdout))), start)


def remedy_of(done) -> str:
    """-> the remedy line of a render: the footer's second line."""
    lines = done.stdout.rstrip("\n").split("\n")
    return lines[-2].strip() if len(lines) >= 2 else ""
