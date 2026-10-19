"""Scenario `team-status-debt` -- 4 case(s): `team status --json` speaks the debt and the health of a team, read on
journals written by hand. The team `debt`: the supervisor's two `do`s, r1's `ask` to r2 and to the owner, r2's answer
to its `do`, a relance of r1 under way, a guard's notice. The team `frail`: `weak` fails for good on the `do` `lead`
gave it, then answers at its try.
- (a) the object: each member's `owes` (`{id, verb, from, task, reminded}`), each task's `dos` (`answered` the id of the
  answer, `null` while owed), its `waits` (`answered` of `of`), `running[].relance`; the line of the team counts `asks`
  (the agents' questions to the owner) and `notices`; `waiting` says `questions` and `notices`
- (b) the owner's view: r1 owes one message, the owner's inbox holds r1's `ask` #16 and the team's `notice` #24, both
  on T1
- (a) suspected: `members[weak].health` is `{suspected: true, falls: 1, tried_at, repents: 0}`, `tried_at` the local
  hour of its try to the minute (its final failure + the calendar's base, 5 min under `schedule: off`); `waiting_on`
  says `suspected`, never `blocked`
- (b) repented: once its try ended answered, `health` is `{suspected: false, falls: 0, tried_at: null, repents: 1}`
  and `waiting_on` no longer says `suspected`; a member that never fell says `health: null`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "team")

AT = "2026-10-01T09:00:00+00:00"
DEBT = [
    {"kind": "team-started", "agents": {"sup": "agents/sup", "r1": "agents/r1", "r2": "agents/r2"},
     "reports": [{"from": ["r1", "r2"], "to": "sup"}], "root": "sup", "principals": [], "owner": "house",
     "ceremonies": [], "entries": {}, "work": None, "launch": {}, "limits": {}, "schedule": None, "digest": "000000000000"},
    {"kind": "task", "task": "T1", "from": "house", "to": "sup", "text": "price the RAM"},                       # 2
    {"kind": "post", "task": "T1", "from": "house", "to": "sup", "verb": "do", "text": "price the RAM"},          # 3
    {"kind": "wake-intent", "tag": "sup-a", "agent": "sup", "path": "agents/sup", "task": "T1", "run": None,
     "index": 1, "messages": [3]},                                                                               # 4
    {"kind": "wake-launched", "tag": "sup-a", "agent": "sup", "run": "aaa001", "pid": 1},                        # 5
    {"kind": "wake-ended", "tag": "sup-a", "agent": "sup", "run": "aaa001", "index": 1, "cost": 0.01},           # 6
    {"kind": "post", "task": "T1", "from": "sup", "to": "r1", "verb": "do", "text": "DDR4"},                      # 7
    {"kind": "post", "task": "T1", "from": "sup", "to": "r2", "verb": "do", "text": "DDR5"},                      # 8
    {"kind": "wait", "agent": "sup", "task": "T1", "any": 2, "to": ["r1", "r2"]},                                # 9
    {"kind": "wake-intent", "tag": "r1-a", "agent": "r1", "path": "agents/r1", "task": "T1", "run": None,
     "index": 1, "messages": [7]},                                                                               # 10
    {"kind": "wake-intent", "tag": "r2-a", "agent": "r2", "path": "agents/r2", "task": "T1", "run": None,
     "index": 1, "messages": [8]},                                                                               # 11
    {"kind": "wake-launched", "tag": "r1-a", "agent": "r1", "run": "bbb001", "pid": 2},                          # 12
    {"kind": "wake-launched", "tag": "r2-a", "agent": "r2", "run": "ccc001", "pid": 3},                          # 13
    {"kind": "wake-ended", "tag": "r1-a", "agent": "r1", "run": "bbb001", "index": 1, "cost": 0.01},            # 14
    {"kind": "post", "task": "T1", "from": "r1", "to": "r2", "verb": "ask", "text": "which vendor?"},            # 15
    {"kind": "post", "task": "T1", "from": "r1", "to": "house", "verb": "ask", "text": "which budget?"},         # 16
    {"kind": "wake-ended", "tag": "r2-a", "agent": "r2", "run": "ccc001", "index": 1, "cost": 0.01},            # 17
    {"kind": "post", "task": "T1", "from": "r2", "to": "sup", "verb": "re", "re": 8, "text": "DDR5 at 90"},      # 18
    {"kind": "wake-intent", "tag": "r2-b", "agent": "r2", "path": "agents/r2", "task": "T1", "run": "ccc001",
     "index": 2, "messages": [15]},                                                                              # 19
    {"kind": "wake-launched", "tag": "r2-b", "agent": "r2", "run": "ccc001", "pid": 4},                          # 20
    {"kind": "wake-ended", "tag": "r2-b", "agent": "r2", "run": "ccc001", "index": 2, "cost": 0.01},            # 21
    {"kind": "wake-intent", "tag": "r1-b", "agent": "r1", "path": "agents/r1", "task": "T1", "run": "bbb001",
     "index": 2, "messages": [7], "relance": "owed"},                                                            # 22
    {"kind": "budget-spent", "spent": 3, "budget": 3, "unit": "wakes"},                                         # 23
    {"kind": "post", "task": "T1", "from": "debt", "to": "house", "verb": "notice",
     "text": "the budget is spent: 3 of 3 wake-ups; sup stays due on T1"},                                      # 24
]

FELL = "2026-10-01T09:10:00+00:00"
FRAIL = [
    {"kind": "team-started", "agents": {"lead": "agents/lead", "weak": "agents/weak"},
     "reports": [{"from": ["weak"], "to": "lead"}], "root": "lead", "principals": [], "owner": "house",
     "ceremonies": [], "entries": {}, "work": None, "launch": {}, "limits": {"retries": 0}, "schedule": None,
     "digest": "000000000000"},
    {"kind": "task", "task": "T1", "from": "house", "to": "lead", "text": "price the RAM"},
    {"kind": "post", "task": "T1", "from": "house", "to": "lead", "verb": "do", "text": "price the RAM"},        # 3
    {"kind": "wake-intent", "tag": "lead-a", "agent": "lead", "path": "agents/lead", "task": "T1", "run": None,
     "index": 1, "messages": [3]},
    {"kind": "wake-launched", "tag": "lead-a", "agent": "lead", "run": "ddd001", "pid": 1},
    {"kind": "wake-ended", "tag": "lead-a", "agent": "lead", "run": "ddd001", "index": 1, "cost": 0.01},
    {"kind": "post", "task": "T1", "from": "lead", "to": "weak", "verb": "do", "text": "DDR5"},                  # 7
    {"kind": "wake-intent", "tag": "weak-a", "agent": "weak", "path": "agents/weak", "task": "T1", "run": None,
     "index": 1, "messages": [7]},
    {"kind": "wake-launched", "tag": "weak-a", "agent": "weak", "run": "eee001", "pid": 3},
    {"kind": "wake-failed", "tag": "weak-a", "agent": "weak", "task": "T1", "final": True, "reason": "wake-dead",
     "at": FELL},
]
REPENTED = [
    {"kind": "post", "task": "T1", "from": "house", "to": "weak", "verb": "note", "text": "try again"},          # 11
    {"kind": "wake-intent", "tag": "weak-b", "agent": "weak", "path": "agents/weak", "task": "T1", "run": "eee001",
     "index": 2, "messages": [11]},
    {"kind": "wake-launched", "tag": "weak-b", "agent": "weak", "run": "eee001", "pid": 4},
    {"kind": "wake-ended", "tag": "weak-b", "agent": "weak", "run": "eee001", "index": 2, "cost": 0.01},
]


def health(found: dict) -> dict:
    return {one.get("member"): one.get("health", "absent") for one in found.get("members") or []}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    h.declare("debt", "---\nagents: |\n  sup agents/sup\n  r1 agents/r1\n  r2 agents/r2\nreports: |\n  r1 r2 -> sup\n"
                      "root: sup\nschedule: off\n---\nPrice the RAM together.\n")
    h.declare("frail", "---\nagents: |\n  lead agents/lead\n  weak agents/weak\nreports: |\n  weak -> lead\nroot: lead\n"
                       "retries: 0\nschedule: off\n---\nPrice the RAM.\n")
    h.written("debt", DEBT, AT)

    # --- (a) the object and the line ------------------------------------------------------------------------
    face = h.face("debt")
    line = next((one for one in h.face() if one.get("team") == "debt"), {})
    owes = {one.get("member"): one.get("owes") for one in face.get("members") or []}
    task = next(iter(face.get("tasks") or []), {})
    waiting = face.get("waiting") or {}
    wanted_owes = {"sup": [{"id": 3, "verb": "do", "from": "house", "task": "T1", "reminded": 0}],
                   "r1": [{"id": 7, "verb": "do", "from": "sup", "task": "T1", "reminded": 1}],
                   "r2": [{"id": 15, "verb": "ask", "from": "r1", "task": "T1", "reminded": 0}]}
    wanted_dos = [{"id": 7, "from": "sup", "to": "r1", "answered": None}, {"id": 8, "from": "sup", "to": "r2", "answered": 18}]
    wanted_waits = [{"member": "sup", "any": 2, "answered": 1, "of": 2, "open": True}]
    if (owes == wanted_owes and task.get("dos") == wanted_dos and "delegations" not in task
            and task.get("waits") == wanted_waits and [one.get("relance") for one in task.get("running") or []] == ["owed"]
            and line.get("asks") == 1 and line.get("notices") == 1
            and [one.get("id") for one in waiting.get("questions") or []] == [16]
            and [(one.get("id"), one.get("awaits")) for one in waiting.get("notices") or []] == [(24, False)]):
        held("(a) the object speaks the debt", "owes per member (r1's do reminded once), dos with answered (#8 by #18), "
             "waits 1 of 2, running relance owed; asks 1, notices 1; waiting questions #16, notices #24")
    else:
        failures.append(f"  ✗ (a) the object             owes={owes} dos={task.get('dos')} "
                        f"delegations={task.get('delegations')} waits={task.get('waits')} running={task.get('running')} "
                        f"line={line.get('asks')}/{line.get('notices')} waiting={waiting}")

    # --- (b) the owner's view: r1's debt, the owner's inbox ----------------------------------------------------
    r1 = len(owes.get("r1") or [])
    box = [(one.get("id"), one.get("verb"), one.get("from"), one.get("task")) for one in face.get("owner_inbox") or []]
    if r1 == 1 and box == [(16, "ask", "r1", "T1"), (24, "notice", "debt", "T1")]:
        held("(b) the text speaks the debt", f"r1 owes {r1}; the owner's inbox {box}")
    else:
        failures.append(f"  ✗ (b) the owner's view       r1 owes={r1} box={box}")

    # --- (a) suspected ------------------------------------------------------------------------------------------
    h.written("frail", FRAIL, AT)
    tried = T.local_after(FELL, 5)
    found = h.face("frail")
    wanted = {"lead": None,
              "weak": {"suspected": True, "falls": 1, "tried_at": tried.strftime("%Y-%m-%dT%H:%M"), "repents": 0}}
    if (health(found) == wanted and "suspected" in (found.get("waiting_on") or [])
            and "blocked" not in (found.get("waiting_on") or [])):
        held("(a) suspected", f"weak health {wanted['weak']}; waiting_on {found.get('waiting_on')}")
    else:
        failures.append(f"  ✗ (a) suspected              health={health(found)} waiting_on={found.get('waiting_on')}")

    # --- (b) repented -------------------------------------------------------------------------------------------
    h.written("frail", FRAIL + REPENTED, AT)
    found = h.face("frail")
    wanted = {"lead": None, "weak": {"suspected": False, "falls": 0, "tried_at": None, "repents": 1}}
    if health(found) == wanted and "suspected" not in (found.get("waiting_on") or []):
        held("(b) repented", f"weak health {wanted['weak']}; lead null; waiting_on {found.get('waiting_on')}")
    else:
        failures.append(f"  ✗ (b) repented               health={health(found)} waiting_on={found.get('waiting_on')}")
    return 0
