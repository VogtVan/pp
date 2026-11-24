"""Scenario `team-journal` -- 14 case(s) (batch l-equipe-et-son-journal, 2026-10-01, and its
rework; split out of `team-review` by les-scenarios-par-maison, 2026-10-07): a review team on
a throwaway house -- declared, started, posted to, stopped and read; no wake-up, no tick.
- a declared team starts: `team start review --message …` answers 0, the four agents are born
  at their paths under the house (every line `<name> <path>`, the name its path here), the journal
  opens on `team-started`, `task T1` and the `do` post owner -> m
- a wrong declaration refuses before anything is written: an edge to an agent nobody declared
  (`participant-unknown`), an `after` that loops (`ceremony-cycle`), no `root` (`root-missing`),
  an agents line without its path (`team-invalid`), no `TEAM.md` (`team-unknown`), a season of the
  standing team naming a member nobody declared (`--member nobody`: `participant-unknown`, team
  0.31.0 -- a season on a standing team is no longer refused) -- no agent created, no journal written
- a post enters at any time: a note on T1, a new task T2 to r1, a post `--as pm` from the mandator,
  `--as nobody` refused `principal-unknown`
- a post on a closed task is refused: `stop --task T2` writes `stopped`, then the stop, and returns the
  `do` left undelivered to its author, `post --task T2` refuses `task-closed`
- the state is read from the journal: `status review` twice gives the same bytes and moves nothing
- two posts at once do not mix: two lines, two ids, the journal reads again
- `status` without a name lists the teams declared under `teams/`, started or not
- a last line still being written is skipped by `status`; a torn line elsewhere refuses by its name
- (m3) a line written before (team 0.13.0): `m manager` is the member m played by the agent born at
  `manager`; its face (`status --json`) says the path `manager` and one `do` in its inbox
- (k) a journal WRITTEN BY team 0.39.0 read (batch les-avis-et-la-relecture, KTM19): the fixture `journals/0.39.0.jsonl`
  -- 32 events team 0.39.0 wrote on a disposable house of master e58dbfb8 by the recipe `journals/0.39.0.recipe.txt`
  (a season under `wakes: 2` and `budget-wakes: 3`, two launches, `wakes-spent`, a ceremony rung at hand, `budget-spent
  {unit: wakes}`, `budget-raised {wakes}`, a final failure, a `snapshot`), with the `status --json` 0.39.0 rendered of it
  (`0.39.0.status.json`, the clock frozen) --: the face 0.40.0 renders of the same bytes equals it under the TABLE OF
  NAMES (`wakes` -> `launches`, `budget-wakes` -> `budget-launches`, in `limits`, `season`, the guard and the count),
  every other difference NAMED (`GAPS`: what the house, not the journal, says -- and what team 0.41.0 says to the
  second or in seconds), the journal byte-identical
- (s) `log` says every kind a journal carries: on a journal written by hand, one event of each kind no other case
  writes (a refusal, a halt, a quota, a kill, a deferral, a ring, a resume, a recurrence and its life, a run renewed
  for its model and for its context, a budget spent in launches and in USD, a silence of now and of before) is said
  on one line, `#<id> <kind>` then what the event names
- (t) the replay of events that name nothing the journal declared -- a task, a tag, a recurrence, a run --, read by a
  probe on a journal written by hand: the tasks, the failures, the recurrences and the standing pairs stay as they
  were, a quota holds the member and its run becomes the carrier's, `run-reset` forgets the standing pair of the run
  it names; the debts a snapshot did not keep are rebuilt as the replay holds them; an `ask` and an `info` that name
  nobody go to the member that delegated the task, else to its author; an `info` to a name the team does not know is
  refused
- (u) `post --task T1 --stop` stops a task as `stop --task` does: `stopped`, the stop to its member and the return
  of its `do` to its author written, the three said on stdout
- (r) a message handed back, read from a journal written by hand: a `re` the tick wrote in b's place under `suspected`
  alone -- the form of a journal of before -- reads as a debt delivered, never as a message returned; one under
  `returned` reads as a message returned to its author (`returned`, `returned_to`), out of b's inbox, its debt
  settled; the head of the author shows each message cited with the text and the vector it was posted with;
  `log --json` gives each post as `event_object` makes it -- what `watch --json` writes --, `returned` on the second
  alone, and the text of `log` marks that post alone; the journal byte-identical
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from tests.harness import race, support

JOURNALS = Path(__file__).resolve().parent / "journals"
EVERY = {"kind": "weekday", "at": "09:30"}            # a recurrence's period, as its events keep it
# (s) one event of each kind `log` says and no other case writes, with what its line must name after `#<id> <kind>`
# and, for some, what it must not: the unit of a budget, said for launches alone
KINDS = [({"kind": "task", "task": "T1", "from": "house", "to": "m", "text": "sort"}, ["T1"]),
         ({"kind": "wake-refused", "agent": "m", "run": "r1", "why": "off the form"}, ["m", "r1"]),
         ({"kind": "wake-halted", "agent": "m", "task": "T1", "count": 3, "reason": "wake-dead"}, ["T1", "3", "wake-dead"]),
         ({"kind": "quota-reached", "agent": "m", "task": "T1", "tag": "q1", "until": "2026-10-01T12:00:00",
           "said": "limit"}, ["2026-10-01T12:00:00", "limit"]),
         ({"kind": "wake-killed", "agent": "m", "task": "T1", "tag": "q1", "run": "r1", "pid": 42}, ["r1", "42"]),
         ({"kind": "deferred", "agent": "m", "task": "T1"}, ["m", "T1"]),
         ({"kind": "ceremony-due", "ceremony": "daily", "period": "2026-10-01", "by": "house"}, ["daily", "2026-10-01"]),
         ({"kind": "resumed", "task": "T1", "by": "house", "from": ["m"]}, ["T1", "house"]),
         ({"kind": "recurrence", "recurrence": "R1", "name": "weekly", "from": "house", "to": "m", "when": EVERY,
           "text": "again", "task": "T1", "context": 50}, ["R1", "weekly", "09:30", "50%", "again"]),
         ({"kind": "recurrence-skipped", "recurrence": "R1", "period": "2026-10-01", "open": "T1"}, ["R1", "T1"]),
         ({"kind": "recurrence-stopped", "recurrence": "R1", "by": "house"}, ["R1", "house"]),
         ({"kind": "recurrence-paused", "recurrence": "R1", "by": "house"}, ["R1", "house"]),
         ({"kind": "recurrence-resumed", "recurrence": "R1", "by": "house"}, ["R1", "house"]),
         ({"kind": "recurrence-changed", "recurrence": "R1", "by": "house", "when": EVERY, "context": None,
           "description": "the week", "text": "anew"}, ["R1", "09:30", "anew"]),
         ({"kind": "run-renewed", "member": "m", "run": "r1", "task": "T1", "why": "model",
           "was": {"model": "small", "provider": None}, "now": {"model": "large", "provider": None}}, ["small", "large"]),
         ({"kind": "run-renewed", "member": "m", "run": "r2", "recurrence": "R1", "task": "T1", "why": "context",
           "used": 0.8, "limit": 70}, ["r2", "R1", "80%", "70%"]),
         ({"kind": "budget-spent", "spent": 3, "budget": 3, "unit": "launches"}, ["3", "launches"]),
         ({"kind": "budget-spent", "spent": 1.5, "budget": 1.5}, ["1.5"], ["launches"]),
         ({"kind": "silence", "agent": "m", "task": "T1", "passages": 5}, ["m", "T1", "5"]),
         ({"kind": "silence", "agent": "m", "task": "T1", "exchanges": 7}, ["m", "T1", "7"])]   # a journal of before
OWED, UNREAD = "sort the first shelf", "sort the second shelf"   # what a writes to b: a do delivered, an ask never delivered
BACK = [{"kind": "team-started", "agents": {"a": "agents/a", "b": "agents/b"}, "reports": [{"from": ["b"], "to": "a"}],
         "root": "a", "principals": [], "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None,
         "digest": "000000000000"},
        {"kind": "task", "task": "T1", "from": "house", "to": "a", "text": "sort the shelves"},
        {"kind": "post", "task": "T1", "from": "house", "to": "a", "verb": "do", "text": "sort the shelves"},
        {"kind": "post", "task": "T1", "from": "a", "to": "b", "verb": "do", "text": OWED, "vector": "node:7"},
        {"kind": "wake-intent", "tag": "b-T1-1", "agent": "b", "path": "agents/b", "task": "T1", "run": "k1", "index": 1,
         "messages": [4]},
        {"kind": "wake-launched", "tag": "b-T1-1", "agent": "b", "run": "k1", "pid": 1, "launch": 1},
        {"kind": "wake-ended", "tag": "b-T1-1", "agent": "b", "run": "k1", "launch": 1, "state": "parked", "cost": 0.01},
        {"kind": "post", "task": "T1", "from": "a", "to": "b", "verb": "ask", "text": UNREAD},
        {"kind": "post", "task": "T1", "from": "b", "to": "a", "verb": "re", "re": 4, "by": "tick", "suspected": True,
         "text": "x"},
        {"kind": "post", "task": "T1", "from": "b", "to": "a", "verb": "re", "re": 8, "by": "tick", "returned": True,
         "text": "x"}]
# (t) a team of two, a delegated: its opening and what a's member b did -- a debt answered, a launch that failed standing
LOOSE = [BACK[0],
         {"kind": "task", "task": "T1", "from": "house", "to": "a", "text": "sort the shelves"},
         {"kind": "post", "task": "T1", "from": "house", "to": "a", "verb": "do", "text": "sort the shelves"},
         {"kind": "post", "task": "T1", "from": "a", "to": "b", "verb": "do", "text": OWED},
         {"kind": "post", "task": "T1", "from": "a", "to": "b", "verb": "ask", "text": "which shelf first?"},
         {"kind": "post", "task": "T1", "from": "b", "to": "a", "verb": "re", "re": 5, "text": "the first"},
         {"kind": "wake-intent", "tag": "t1", "agent": "b", "path": "agents/b", "task": "T1", "index": 1, "messages": [4]},
         {"kind": "wake-launched", "tag": "t1", "agent": "b", "run": "k1", "pid": 1, "launch": 1},
         {"kind": "wake-failed", "tag": "t1", "agent": "b", "task": "T1", "reason": "wake-dead", "state": "standing",
          "run": "k1"}]
# the events that name what the journal never declared -- a task, a tag, a recurrence, a run --, and two quotas of b
UNDECLARED = [{"kind": "post", "task": "T9", "from": "a", "to": "b", "verb": "info", "text": "on no task"},
              {"kind": "stopped", "task": "T9", "by": "house"},
              {"kind": "quota-reached", "tag": "zz", "agent": "b", "task": "T1", "until": None},
              {"kind": "quota-reached", "tag": "t1", "agent": "b", "task": "T1", "until": "2026-11-14T09:00:00"},
              {"kind": "quota-reached", "tag": "t1", "agent": "b", "task": "T1", "until": "2026-11-14T09:00:00",
               "run": "k2"},
              {"kind": "wake-failed", "tag": "zz", "agent": "b", "task": "T1", "reason": "wake-dead"},
              {"kind": "done", "task": "T9", "result": "of no task"},
              {"kind": "recurrence-skipped", "recurrence": "R9", "period": "2026-11-13", "open": "T1"},
              {"kind": "recurrence-stopped", "recurrence": "R9", "by": "house"},
              {"kind": "recurrence-paused", "recurrence": "R9", "by": "house"},
              {"kind": "recurrence-resumed", "recurrence": "R9", "by": "house", "since": "2026-11-13T21:00:00"},
              {"kind": "run-renewed", "member": "b", "run": "another", "task": "T1", "why": "context", "used": 0.8,
               "limit": 70}]
# then b's run forgotten
CLOSING = [{"kind": "run-reset", "member": "b", "run": "k2"}]
# the probe of (t): the journal replayed at its three cuts, the snapshot's debts rebuilt, two acts that name nobody
PROBE = """events = [json.loads(line) for line in Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()]
base, loose, whole = (mod.replay(events[:int(cut)]) for cut in (sys.argv[2], sys.argv[3], len(events)))
pairs = lambda state: sorted(list(pair) for pair in state["standing"])
held = lambda state: {key: {name: value for name, value in task.items() if name != "last"}   # its last event apart
                      for key, task in state["tasks"].items()}
def nobody(state):                      # an info to a name the team does not know: refused, nothing routed
    try:
        return [one.get("to") for one in mod.routed(state, {"agent": "a", "task": "T1"},
                                                    [{"info": {"to": "nobody", "text": "noted"}}])]
    except mod.Refused:
        return "refused"
snapshot = json.loads(json.dumps(mod.packed(loose)))
del snapshot["debts"]
print(json.dumps({
    "tasks": held(base) == held(loose), "failures": base["failures"] == loose["failures"],
    "recurrences": loose["recurrences"], "message": 10 in loose["messages"], "quotas": sorted(loose["quotas"]),
    "runs": [base["runs"].get("b"), loose["runs"].get("b")], "flow": "k2" in loose["flow"],
    "standing": [pairs(base), pairs(loose), pairs(whole)],
    "debts": sorted([key, value] for key, value in whole["debts"].items()),
    "rebuilt": mod.unpacked(snapshot)["debts"] == loose["debts"],
    "asked": [one.get("to") for one in mod.routed(base, {"agent": "b", "task": "T1"}, [{"ask": "which one?"}])],
    "told": [one.get("to") for one in mod.routed(base, {"agent": "a", "task": "T1"}, [{"info": {"text": "noted"}}])],
    "nobody": nobody(base)}))
"""
FROZEN = "2026-10-01T08:00"                        # the clock the fixture's face was rendered under (its recipe)

# The table of names between team 0.39.0 and 0.40.0: a key or a value the fixture's face says in wake-ups, read in launches.
RENAMED = {"wakes": "launches", "budget-wakes": "budget-launches", "wakes-spent": "launches-spent"}

# What team 0.40.0 says otherwise of the same journal, each gap NAMED here -- nowhere else is a difference tolerated:
# the `--launches` flag of a season left with team 0.40.0-alpha (a wake-up is ONE launch), so the face of the team's
# launch flags and of each member's no longer carries `launches`.
GAPS = {"launch.launches": "the flag `--launches` of a season left with team 0.40.0-alpha: a wake-up is one launch",
        "members[].launch.launches": "the same flag, at each member's launch",
        "members[].health.tried_at": "team 0.41.0 says the hour of a try to the SECOND: an interval may last seconds",
        "schedule": "team 0.44.0 says the net as its step in seconds, its timer and its relaunch entry, where 0.39.0 "
                    "said its minutes and its calendar line",
        "name": "team 0.42.0 says the name a team is shown by, its TEAM.md's or its directory's",
        "tasks[].at": "team 0.43.0 says the hour a task was born",
        "tasks[].ended": "team 0.43.0 says the hour a task ended, null while it is open",
        "recurrences": "team 0.46.0 says a team's recurring tasks, none in a journal of before",
        "tasks[].recurrence": "team 0.46.0 says the recurrence that opened a task, null for every other",
        "waiting.infos": "team 0.47.0 says the infos sent to the owner, an act without debt; none in a journal of before",
        "total": "team 1.19.0 says the cost of every season beside the season's; a journal of before counts from its own",
        "members[].owes[].reminded": "the relances that carried a debt, counted until team 0.47; the silence of row 115 "
                                     "replaces the count (team 0.48.0)",
        "members[].silence": "team 0.48.0 says each member's silence on the tasks it owes on (empty for a member owing nothing)",
        "members[].silence[]": "team 0.48.0: each silence -- its task, its silent passages, its limit",
        "members[].health.cause": "team 0.48.0 says the cause of a fall, fall or silence",
        "members[].context": "team 0.54.0 says the context a member's last wake-up left, null in a journal of before",
        "launch.packages": "team 0.52.0 says the season's set, one switch per pin: a journal of before is read under "
                           "its rule, the pins it does not name off",
        "launch.packages[]": "team 0.52.0: each switch of the set, `<name>=on|off`",
        "members[].launch.packages": "the same set, at each member's launch",
        "members[].launch.packages[]": "each switch of a member's set",
        "members[].runs[]": "team 1.1.0 says a member's runs, one per task carrier -- its carrier, run, name, how, "
                            "since, context --, which 0.39.0 did not",
        "description": "team 1.7.0 says what a team does, its TEAM.md's `description:`, null without it",
        "members[].quota": "team 1.25.0 says a member's stop on its quota, null for a member never stopped on it",
        "season.state": "team 1.27.0 says whether the season runs or was stopped; a journal of before runs",
        "root": "team 1.35.13 says the team's root, the member the post's resume goes to by default"}


def renamed(value):
    """-> the fixture's face in the words of 0.40.0: every key and every string value of RENAMED, at any depth."""
    if isinstance(value, dict):
        return {RENAMED.get(key, key): renamed(one) for key, one in value.items()}
    if isinstance(value, list):
        return [renamed(one) for one in value]
    return RENAMED.get(value, value) if isinstance(value, str) else value


def flat(value, path: str = "") -> dict:
    """-> every leaf of a JSON value by its path, a list's items under `[]` so two faces compare member by member."""
    if isinstance(value, dict):
        if not value:
            return {path: {}}
        found = {}
        for key, one in value.items():
            found.update(flat(one, f"{path}.{key}" if path else str(key)))
        return found
    if isinstance(value, list):
        if not value:
            return {path: []}
        found = {}
        for n, one in enumerate(value):
            found.update(flat(one, f"{path}[]#{n}"))
        return found
    return {path: value}


def gapped(path: str) -> str | None:
    """-> the GAPS entry a leaf's path falls under, `members[]#0.how` -> `members[].how`; None when none."""
    bare = re.sub(r"\[\]#\d+", "[]", path)
    return next((one for one in GAPS if bare == one or bare.startswith(one + ".")), None)

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    journal = h.journal_of("review")

    # --- a declared team starts ---------------------------------------------------------------
    h.declare("review", T.REVIEW)
    started = h.call("team", "start", "review", "--message", "review PR 42", "--no-tick")
    found = h.events()
    kinds = [one.get("kind") for one in found]
    opening = found[0] if found else {}
    task = found[1] if len(found) > 1 else {}
    post = found[2] if len(found) > 2 else {}
    if (started.returncode == 0 and all(h.agent_stands(one) for one in ("m", "r1", "r2", "r3"))
            and kinds == ["team-started", "task", "post"]
            and [one.get("id") for one in found] == [1, 2, 3]
            and all(one.get("team") == "review" and one.get("at") for one in found)
            and opening.get("agents") == {"m": "m", "r1": "r1", "r2": "r2", "r3": "r3"}
            and opening.get("reports") == [{"from": ["r1", "r2", "r3"], "to": "m"}]
            and opening.get("root") == "m" and opening.get("principals") == ["pm"]
            and opening.get("owner") == "house"
            and [one.get("name") for one in opening.get("ceremonies", [])] == ["daily", "retro"]
            and opening.get("ceremonies", [{}])[1].get("after") == "daily"
            and task.get("task") == "T1" and task.get("from") == "house" and task.get("to") == "m"
            and post.get("task") == "T1" and post.get("verb") == "do" and post.get("from") == "house"
            and post.get("to") == "m" and post.get("text") == "review PR 42"
            and "T1" in started.stdout):
        held("a declared team starts", "team start review: rc 0, m r1 r2 r3 born at their paths, "
             "the journal opens on team-started, task T1, post do house -> m")
    else:
        failures.append(f"  ✗ team start                  rc={started.returncode} kinds={kinds} "
                        f"{started.stdout[-200:]!r} {started.stderr[-300:]!r}")

    # --- a wrong declaration refuses before anything is written -------------------------------
    h.declare("bad-edge", T.REVIEW.replace("r1 r2 r3 -> m", "r1 r9 -> m").replace("  m m\n", "  x1 x1\n")
              .replace("root: m", "root: x1").replace("-> m\n", "-> x1\n"))
    h.declare("bad-cycle", T.REVIEW.replace("daily every weekday 09:30 with r1 r2 r3 -> m", "daily after retro with r1 -> m")
              .replace("  m m\n", "  x2 x2\n").replace("root: m", "root: x2").replace("-> m\n", "-> x2\n"))
    h.declare("bad-root", T.REVIEW.replace("root: m\n", "").replace("  m m\n", "  x3 x3\n").replace("-> m\n", "-> x3\n"))
    h.declare("bad-type", T.REVIEW.replace("  r3 r3\n", "  x4\n").replace("r1 r2 r3 -> m", "r1 r2 -> m")
              .replace("with r1 r2 r3 -> m", "with r1 r2 -> m"))
    refused = {name: h.call("team", "start", name, "--message", "x", "--no-tick")
               for name in ("bad-edge", "bad-cycle", "bad-root", "bad-type", "nobody")}
    again = h.call("team", "start", "review", "--no-tick", "--member", "nobody", "--model", "m2")
    owed = {"bad-edge": "participant-unknown", "bad-cycle": "ceremony-cycle", "bad-root": "root-missing",
            "bad-type": "team-invalid", "nobody": "team-unknown"}
    journals = h.records / "teams"
    if (all(refused[name].returncode == 2 and code in refused[name].stderr and refused[name].stdout == ""
            for name, code in owed.items())
            and again.returncode == 2 and "participant-unknown" in again.stderr
            and not any(h.agent_stands(one) for one in ("x1", "x2", "x3", "x4", "r9"))
            and sorted(one.name for one in journals.iterdir()) == ["review"]
            and len(h.events()) == 3):
        held("a wrong declaration refuses before anything is written",
             "participant-unknown, ceremony-cycle, root-missing, team-invalid, team-unknown, a season's `--member nobody` "
             "-- no agent born, no journal written, the standing journal at 3 events")
    else:
        failures.append("  ✗ declaration refusals        "
                        + " ".join(f"{name}={one.returncode}:{one.stderr[-80:]!r}" for name, one in refused.items())
                        + f" again={again.returncode}:{again.stderr[-80:]!r} journals={sorted(one.name for one in journals.iterdir())}")

    # --- a post enters at any time ------------------------------------------------------------
    noted = h.call("team", "post", "review", "--task", "T1", "--message", "change of course", "--no-tick")
    opened = h.call("team", "post", "review", "--to", "r1", "--message", "look at the tests", "--no-tick")
    mandated = h.call("team", "post", "review", "--task", "T1", "--as", "pm", "--message", "from the product owner", "--no-tick")
    nobody = h.call("team", "post", "review", "--task", "T1", "--as", "nobody", "--message", "who", "--no-tick")
    found = h.events()
    by_kind = [(one.get("kind"), one.get("task"), one.get("verb"), one.get("from"), one.get("to")) for one in found[3:]]
    if (noted.returncode == 0 and opened.returncode == 0 and mandated.returncode == 0
            and nobody.returncode == 2 and "principal-unknown" in nobody.stderr
            and by_kind == [("post", "T1", "info", "house", "m"),
                            ("task", "T2", None, "house", "r1"),
                            ("post", "T2", "do", "house", "r1"),
                            ("post", "T1", "info", "pm", "m")]
            and [one.get("id") for one in found] == list(range(1, 8))
            and "T2" in opened.stdout and "#4" in noted.stdout):
        held("a post enters at any time", "an info on T1, a new task T2 to r1 with its do, an info --as pm "
             "from pm; --as nobody refuses principal-unknown")
    else:
        failures.append(f"  ✗ posts                       {noted.returncode}/{opened.returncode}/{mandated.returncode}/"
                        f"{nobody.returncode} {by_kind} {noted.stderr[-120:]!r} {opened.stderr[-120:]!r} "
                        f"{nobody.stderr[-120:]!r}")

    # --- a post on a closed task is refused ---------------------------------------------------
    stopped = h.call("team", "stop", "review", "--task", "T2", "--no-tick")
    late = h.call("team", "post", "review", "--task", "T2", "--message", "too late", "--no-tick")
    unknown = h.call("team", "post", "review", "--task", "T9", "--message", "nowhere", "--no-tick")
    found = h.events()
    halt, last, back = (found[-3], found[-2], found[-1]) if len(found) > 2 else ({}, {}, {})
    if (stopped.returncode == 0 and halt.get("kind") == "stopped" and halt.get("task") == "T2"
            and halt.get("by") == "house" and halt.get("id") == 8
            and last.get("kind") == "post" and last.get("verb") == "stop"
            and last.get("task") == "T2" and last.get("to") == "r1" and last.get("id") == 9
            and back.get("kind") == "returned" and back.get("message") == 6 and back.get("to") == "house"
            and late.returncode == 2 and "task-closed" in late.stderr
            and unknown.returncode == 2 and "task-unknown" in unknown.stderr and len(h.events()) == 10):
        held("a post on a closed task is refused", "stop --task T2 writes stopped #8, then post stop #9 and returns "
             "the do #6 to house; post --task T2 refuses task-closed, --task T9 task-unknown; the journal at 10 events")
    else:
        failures.append(f"  ✗ task-closed                 {stopped.returncode}/{late.returncode}/{unknown.returncode} "
                        f"{halt} {last} {back} {stopped.stderr[-120:]!r} {late.stderr[-120:]!r} {unknown.stderr[-120:]!r}")

    # --- the state is read from the journal ---------------------------------------------------
    before = journal.read_bytes()
    first = h.call("team", "status", "review")
    second = h.call("team", "status", "review")
    face = h.face("review")
    tasks = {one.get("id"): (one.get("state"), one.get("to"), one.get("messages")) for one in face.get("tasks") or []}
    boxes = {one.get("member"): (one.get("path"), [(box.get("verb"), box.get("from")) for box in one.get("pending") or []])
             for one in face.get("members") or []}
    owner_box = [(one.get("id"), one.get("verb"), one.get("from"), one.get("task"), one.get("returned"))
                 for one in face.get("owner_inbox") or []]
    if (first.returncode == 0 and first.stdout == second.stdout and first.stderr == second.stderr
            and journal.read_bytes() == before and face == h.face("review")
            and face.get("owner") == "house" and face.get("principals") == ["pm"]
            and tasks == {"T1": ("open", "m", 3), "T2": ("stopped", "r1", 2)}
            and boxes.get("m") == ("m", [("do", "house"), ("info", "house"), ("info", "pm")])
            and all(boxes.get(one) == (one, []) for one in ("r1", "r2", "r3"))
            and owner_box == [(6, "do", "house", "T2", True)]
            and (face.get("last") or {}).get("id") == 10 and (face.get("last") or {}).get("kind") == "returned"):
        held("the state is read from the journal", "status review twice: the same bytes, the journal untouched "
             "-- owner, pm, T1 open (m: do, note, note), T2 stopped (r1: its stop delivered at once; the do returned), the last event")
    else:
        failures.append(f"  ✗ status                      rc={first.returncode} same={first.stdout == second.stdout} "
                        f"{first.stdout[-400:]!r} {first.stderr[-200:]!r}")

    # --- two posts at once do not mix ---------------------------------------------------------
    count = len(h.events())
    raced = race(h.engine, [["--instance", str(h.house), "team", "post", "review", "--task", "T1", "--message", "one", "--no-tick"],
                            ["--instance", str(h.house), "team", "post", "review", "--task", "T1", "--message", "two", "--no-tick"]],
                 cwd=h.ws, env=h.env)
    found = h.events()
    ids = [one.get("id") for one in found]
    texts = sorted(str(one.get("text")) for one in found[count:])
    after = h.call("team", "status", "review")
    if (all(one.returncode == 0 for one in raced) and len(found) == count + 2
            and ids == list(range(1, count + 3)) and texts == ["one", "two"]
            and after.returncode == 0
            and [one.get("messages") for one in h.face("review").get("tasks") or [] if one.get("id") == "T1"] == [5]):
        held("two posts at once do not mix", f"race of two posts: two lines, ids {ids[-2:]}, the journal reads again")
    else:
        failures.append(f"  ✗ race                        {[one.returncode for one in raced]} ids={ids} texts={texts} "
                        f"{[one.stderr[-120:] for one in raced]!r} {h.face('review').get('tasks')}")

    # --- status without a name lists the teams declared ---------------------------------------
    h.declare("essai", T.REVIEW.replace("name: review", "name: essai"))
    listed = h.call("team", "status")
    lines = h.face()
    names = [one.get("team") for one in lines]
    by_team = {one.get("team"): one for one in lines}
    if (listed.returncode == 0 and len(listed.stdout.strip().splitlines()) == len(lines)
            and names == ["bad-cycle", "bad-edge", "bad-root", "bad-type", "essai", "review"]
            and (by_team["review"].get("tasks") or {}).get("open") == 1
            and sum((by_team["review"].get("tasks") or {}).values()) == 2
            and by_team["essai"].get("started") is None and by_team["essai"].get("state") == "never"):
        held("status without a name lists the teams", "one line per TEAM.md under teams/: review started with "
             "its tasks, essai declared and not started")
    else:
        failures.append(f"  ✗ status listing              rc={listed.returncode} {names} {lines} "
                        f"{listed.stderr[-200:]!r}")

    # --- a last line still being written is skipped; a torn line elsewhere refuses -------------
    whole = journal.read_text(encoding="utf-8")
    with journal.open("a", encoding="utf-8") as handle:
        handle.write('{"at": "2026-10-01T18:00')
    torn_tail = h.call("team", "status", "review")
    good, torn_line = journal.read_text(encoding="utf-8").rsplit("\n", 1)
    journal.write_text(torn_line + "\n" + good + "\n", encoding="utf-8")     # the torn line moved to the head
    torn_head = h.call("team", "status", "review")
    journal.write_text(whole, encoding="utf-8")                              # the journal whole again
    if (torn_tail.returncode == 0 and torn_tail.stdout == after.stdout and "Traceback" not in torn_tail.stderr
            and torn_head.returncode == 2 and journal.name in torn_head.stderr
            and re.search(r"\b1\b", torn_head.stderr) and "Traceback" not in torn_head.stderr):
        held("a torn last line is skipped, elsewhere it refuses", "status reads the whole lines; "
             "a torn line at the head: rc 2, the refusal naming journal.jsonl and its line 1")
    else:
        failures.append(f"  ✗ torn lines                  {torn_tail.returncode}/{torn_head.returncode} "
                        f"{torn_tail.stderr[-200:]!r} {torn_head.stderr[-200:]!r}")

    # --- (m3) a line written before reads as a name and a path [48] -----------------------------------------
    h.declare("older", "---\nname: review\nagents: |\n  m manager\nroot: m\nschedule: off\n---\nA line of before.\n")
    older = h.call("team", "start", "older", "--message", "read me", "--no-tick")
    status_o = h.call("team", "status", "older")
    member_o = next((one for one in h.face("older").get("members") or [] if one.get("member") == "m"), {})
    opening_o = next(iter(T.lines(h.journal_of("older"))), {})
    if (older.returncode == 0 and status_o.returncode == 0 and h.agent_stands("manager")
            and opening_o.get("agents") == {"m": "manager"} and member_o.get("path") == "manager"
            and [(one.get("verb"), one.get("from")) for one in member_o.get("pending") or []] == [("do", "house")]):
        held("(m3) a line of before is a name and a path", "`m manager`: the member m, played by the agent born "
             "at manager; its face says the path manager and one do in its inbox")
    else:
        failures.append(f"  ✗ (m3) a line of before       rc={older.returncode} manager={h.agent_stands('manager')} "
                        f"{opening_o.get('agents')} {member_o}")
    

    # --- (k) a journal written by team 0.39.0 read: the fixture --------------------------------------------------
    h.declare("old", (JOURNALS / "0.39.0.TEAM.md").read_text(encoding="utf-8"))
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(JOURNALS / "0.39.0.jsonl", h.journal_of("old"))
    before_k = h.journal_of("old").read_bytes()
    face_k = h.face("old", now=FROZEN)
    after_k = h.journal_of("old").read_bytes()
    kept = renamed(json.loads((JOURNALS / "0.39.0.status.json").read_text(encoding="utf-8")))
    was, now = flat(kept), flat(face_k)
    differing = sorted(path for path in set(was) | set(now) if was.get(path, "∅") != now.get(path, "∅"))
    unnamed = [path for path in differing if gapped(path) is None]
    gaps_seen = sorted({gapped(path) for path in differing} - {None})
    kinds_k = [one.get("kind") for one in h.events("old")]
    if (len(kinds_k) == 32 and kinds_k[0] == "team-started" and "wakes-spent" in kinds_k and "snapshot" in kinds_k
            and face_k.get("team") == "old" and not unnamed and gaps_seen == sorted(GAPS)
            and face_k.get("limits") == {"retries": 0, "launches": 2, "budget-launches": 6}
            and face_k.get("launches") == {"launched": 4, "bound": 6}
            and "wakes" not in json.dumps(face_k) and before_k == after_k):
        held("(k) a journal written by team 0.39.0 read", f"the fixture's 32 events (wakes 2 / budget-wakes 3, wakes-spent, "
             f"budget-spent {{unit: wakes}}, budget-raised {{wakes: 6}}, a ring, a final failure, a snapshot): the face "
             f"0.40.0 renders equals the face 0.39.0 kept under the table of names, {len(differing)} leaves apart, all under "
             f"the named gaps {gaps_seen}; the journal byte-identical")
    else:
        failures.append(f"  ✗ (k) a journal of 0.39.0     events={len(kinds_k)} team={face_k.get('team')} limits={face_k.get('limits')} "
                        f"launches={face_k.get('launches')} same={before_k == after_k} gaps={gaps_seen} "
                        f"unnamed={[(path, was.get(path, '∅'), now.get(path, '∅')) for path in unnamed][:12]}")

    # --- (r) a message handed back, read from a journal written by hand ------------------------------------------
    module = h.module()
    h.declare("back", "---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n---\nSort.\n")
    h.written("back", BACK, "2026-11-13T21:00:00+00:00")
    before_r = h.journal_of("back").read_bytes()
    events_r = T.lines(h.journal_of("back"))
    state_r = module.replay(events_r)
    logged_r = h.call("team", "log", "back", "--json")
    text_r = h.call("team", "log", "back")
    objects_r = [json.loads(one) for one in logged_r.stdout.splitlines() if one.strip()]
    marks_r = [one.split(" ", 1)[0] for one in text_r.stdout.splitlines()
               if getattr(module, "RETURNED_MARK", "\0") in one]
    heads_r = {key: T.handed_back(module, module.message_of(state_r, "a", state_r["messages"][key])) for key in (9, 10)}
    if (logged_r.returncode == 0 and text_r.returncode == 0
            and {4, 8} <= state_r["delivered"] and state_r["returned"] == {8} and state_r["returned_to"] == {8: "a"}
            and not module.owes(state_r, 4) and not module.owes(state_r, 8) and not module.inbox(state_r, "b")
            and heads_r[9] == {4: {"how": "suspected", "member": "b", "vector": "node:7", "text": OWED}}
            and heads_r[10] == {8: {"how": "returned", "member": "b", "vector": None, "text": UNREAD}}
            and objects_r == [module.event_object("back", one) for one in events_r]
            and [(one.get("id"), one.get("suspected"), one.get("returned")) for one in objects_r[-2:]]
            == [(9, True, None), (10, None, True)]
            and marks_r == ["#10"] and h.journal_of("back").read_bytes() == before_r):
        held("(r) a message handed back, from a journal written by hand", "the re #9 under suspected alone: #4 a debt "
             "delivered, not returned; the re #10 under returned: #8 returned to a, out of b's inbox, settled; a's head "
             "shows #4 with its text and its vector node:7, #8 with its text; log --json gives the objects watch "
             "--json writes, returned on #10 alone, the text of log marks #10 alone; the journal byte-identical")
    else:
        failures.append(f"  ✗ (r) a message handed back   rc={logged_r.returncode}/{text_r.returncode} "
                        f"delivered={sorted(state_r['delivered'])} returned={sorted(state_r['returned'])} "
                        f"to={state_r['returned_to']} owes={module.owes(state_r, 4)}/{module.owes(state_r, 8)} "
                        f"inbox={[one['id'] for one in module.inbox(state_r, 'b')]} heads={heads_r} "
                        f"objects={[(one.get('id'), one.get('suspected'), one.get('returned')) for one in objects_r[-2:]]} "
                        f"marks={marks_r} same={h.journal_of('back').read_bytes() == before_r}")

    # --- (s) log says every kind a journal carries ------------------------------------------------------------------
    opening_s = {key: value for key, value in h.events()[0].items() if key not in ("at", "id", "team")}
    h.declare("kinds", T.REVIEW)
    h.written("kinds", [opening_s, *(one[0] for one in KINDS)], "2026-10-01T09:00:00+00:00")
    said_s = h.call("team", "log", "kinds")
    lines_s = said_s.stdout.splitlines()[1:]              # after the line of team-started
    unsaid = []
    for number, (one, line) in enumerate(zip(KINDS, lines_s + [""] * len(KINDS)), 2):
        event, names, absent = one[0], one[1], one[2] if len(one) > 2 else []
        head, rest = line.split(" ", 2)[:2], line.split(" ", 2)[2:]      # `#<id> <kind>`, then what the event says
        said = rest[0] if rest else ""
        if head != [f"#{number}", event["kind"]] or not all(name in said for name in names) \
                or any(name in said for name in absent):
            unsaid.append((number, event["kind"], said))
    if said_s.returncode == 0 and len(lines_s) == len(KINDS) and not unsaid:
        held("(s) log says every kind a journal carries", f"a journal written by hand, {len(KINDS)} events of "
             f"{len({one[0]['kind'] for one in KINDS})} kinds: one line each, `#<id> <kind>` then what the event "
             "names -- a budget's unit for launches alone, a silence of before by its count")
    else:
        failures.append(f"  ✗ (s) the kinds of log        rc={said_s.returncode} lines={len(lines_s)}/{len(KINDS)} "
                        f"unsaid={unsaid} {said_s.stderr.strip()[-200:]!r}")

    # --- (t) the replay of events that name nothing the journal declared; an act that names nobody --------------------
    h.declare("loose", "---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n---\nSort.\n")
    h.written("loose", LOOSE + UNDECLARED + CLOSING, "2026-11-13T21:00:00+00:00")
    probe_t = T.probe_script(h, PROBE)
    read_t = subprocess.run([sys.executable, str(probe_t), str(h.journal_of("loose")), str(len(LOOSE)),
                             str(len(LOOSE) + len(UNDECLARED))], capture_output=True, text=True)
    try:
        seen_t = json.loads(read_t.stdout)
    except ValueError:
        seen_t = {}
    if seen_t == {"tasks": True, "failures": True, "recurrences": {}, "message": True, "quotas": ["b"],
                  "runs": [{"T1": "k1"}, {"T1": "k2"}], "flow": False,
                  "standing": [[["b", "T1"]], [["b", "T1"]], []],
                  "debts": [[3, None], [4, None], [5, 6]], "rebuilt": True, "asked": ["a"], "told": ["house"],
                  "nobody": "refused"}:
        held("(t) events that name nothing declared leave the state", f"{len(UNDECLARED)} events on a task, a tag and "
             "a recurrence the journal never declared: the tasks, the failures, the recurrences and the standing "
             "pairs as they were, the post kept, one quota for b, its run the quota's; a run-reset forgets the "
             "standing pair of its run; the debts a snapshot did not keep are rebuilt the same; an ask and an info "
             "that name nobody go to the one who delegated, else to the task's author; an info to a name the team "
             "does not know is refused")
    else:
        failures.append(f"  ✗ (t) the replay of the undeclared  rc={read_t.returncode} {seen_t} {read_t.stderr.strip()[-300:]!r}")

    # --- (u) post --stop stops a task as stop --task does ---------------------------------------------------------------
    begun_u = h.call("team", "start", "essai", "--message", "review PR 43", "--no-tick")
    opened_u = h.events("essai")
    stopped_u = h.call("team", "post", "essai", "--task", "T1", "--stop", "--no-tick")
    after_u = h.events("essai")[len(opened_u):]
    do_u = next((one["id"] for one in opened_u if one.get("kind") == "post" and one.get("verb") == "do"), None)
    if (begun_u.returncode == 0 and stopped_u.returncode == 0 and len(stopped_u.stdout.splitlines()) == 3
            and [(one.get("kind"), one.get("verb")) for one in after_u] == [("stopped", None), ("post", "stop"),
                                                                             ("returned", None)]
            and after_u[0].get("task") == "T1" and after_u[0].get("by") == "house"
            and (after_u[1].get("from"), after_u[1].get("to")) == ("house", "m")
            and after_u[2].get("message") == do_u and after_u[2].get("to") == "house"
            and all(f"#{number}" in stopped_u.stdout for number in (after_u[0]["id"], after_u[1]["id"], do_u))):
        held("(u) post --stop stops a task as stop --task does", f"essai's T1: stopped #{after_u[0]['id']}, the stop "
             f"#{after_u[1]['id']} to m and the do #{do_u} returned to house -- three events written, three lines said")
    else:
        failures.append(f"  ✗ (u) post --stop             rc={begun_u.returncode}/{stopped_u.returncode} {stopped_u.stdout!r} "
                        f"{stopped_u.stderr.strip()[-160:]!r} after={[(one.get('kind'), one.get('message')) for one in after_u]}")
    return 0
