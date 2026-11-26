"""Scenario `team-log-old` -- 7 case(s): the readers of a journal on the journal team 0.32.2 wrote
(`T.OLD_JOURNAL`) -- a team `old` (m root, r1 and r2 reporting to m) declared and never played here.
- (a) `log --json` on the old journal: no `delegation`, no `terminal`; every post a `do`, an `ask`, a `re` or a
  `notice`; r1's and r2's `done` to m are `re` to the `do` each received (`was: done`), m's `reply` a `re` to
  r2's ask (`was: reply`), r1's `escalate` to m a `re` to its `do` (`was: escalate`), m's `escalate` to the
  owner the team's `notice` about m
- (b) `log` on the old journal: its lines carry the ids `--json` carries -- no `delegation` nor `terminal`
  line, the notice #56 said
- (c) `watch --json`: two events of the old kinds appended while it watches -- the `delegation` is never said,
  the `done` is said `re`
- (d) `status --json`: the face of the old journal is read -- T1 resolved, T2 open, its members m, r1 and r2
- (e) `stats` (team 1.35.12) reads the seasons of a journal written here, its numbers chosen at the case -- three
  seasons of `ledger` (lead under `chief`, w1 and w2 under `workers`): season 1 six wake-ups (one failed, one
  without `tokens`, its context the estimate), T1 closed and T2 stopped, T4 born and worked, a question to the owner,
  a `do` twice to w2; season 2 empty; season 3 under way, T3 and its wake-up without a cost -- its `usd` null, never
  0 --, a run renewed, a silence, T4 worked again and closed -- `--season 1 --json` gives every measure the case
  writes, T4 by its season-1 wake-up alone; bare, the season under way: T4 there by its season-3 wake-up alone, closed
  there; each season's `by_task` sums to its cost; `--all --json` the two seasons not empty, their median, season 2
  apart, and its own `by_task`: each task over all its seasons -- T4 the sum of its lines of seasons 1 and 3, its
  elapsed time the wall from the first event of its first line to the last of its last (`first`, `last`: some 44 h),
  the largest of their contexts, its state the last one's --, without `season`; the text renders; `team-unknown`, `season-unknown`, `cost-invalid`, `team-not-started` (bare and `--all`);
  nothing written; the old journal reads too: its cost, its tasks, its failures,
  its members without a role key; the measures of the head (team 1.36.62): each season its `delegations` (the `do`
  of its `by_task`), its cost `per_delegation`, `per_launch` and `per_effort_hour`, its `root` member with its share,
  its `budget` -- season 1 capped by its `team-started` and raised by its `budget-raised`, in USD and in launches,
  stopped so no `hours_left`; season 3 capped in USD alone, running, its hours left at its pace --, `against` the
  median of the seasons played (a null median judges nothing; `over` the seasons where the measure is known),
  read alone too; no task stopped: its cost and share 0 where the season's cost is known; each `by_task` line its `share`, its
  `per_delegation` and its `against`, each `by_member` line its `share`, its `stopped_tasks` (the tasks stopped at
  its end, their cost, its share); under `--all` the `total` of the seasons
  played, the `task_cost` with its `concentration`, each task's `seasons` and `per_delegation`; the text says
  `spent`, `work`, `price`, `load` in its base and the line `all`; since team 1.36.63 no season, no median and no text
  gives the yield, the cost of a task of a season, the roles or the `do` more (`do_extra`, `pairs_extra`, `pairs`,
  `do_per_pair`), `--all`'s `task_cost` kept, and the text says a cost, a pace, a median and a ratio with two decimals,
  hours with one, while the JSON keeps four; since team 1.36.64 each season gives its launches `by_model` (the model of
  their `wake-launched`, a launch without one under null, the shares summing to 1), `by_duration` and `context.by_band`
  (a launch at a bound in the band it opens, one without a context in no band of context, the bands of duration
  summing to the finished launches), `time.cost_by_slot` (a cost in the slot of its end, the slots summing to the
  cost), the `per_effort_hour` of each task and member with its `against.per_effort_hour`, the `models` of a member,
  most used first; `--all` gives each task's `per_effort_hour` over all its seasons; the text says each of them, a
  model and a band per line (D10); an empty band or slot costs 0, and its share is 0, where the season's cost is known
  (D11)
- (f) `stats` on the edges of a journal (team `tally`, written here): an event without `at`, a task stopped then
  `resumed` (open again at its season's end), a wake-up that never launched (no effort), a last season ended by its
  `season-stopped` while a wake-up of it ends three hours later (its effort past the season's one slot), a task whose
  second season is stamped before its first (`first` the earlier) and a task whose events never say an hour (`first`
  and `last` null over all its seasons); no cap: `budget` null; an empty season read alone is judged against the one
  season played (`over` 1), a null median gives no ratio; the `total` of `--all` leaves the empty season out, a task of
  two seasons says both, the cost of a task over the launched tasks of the seasons played; a season without
  `root` gives its cost and share null; a task stopped at its season's end (T5) in its `stopped_tasks`, the one resumed not;
  no season and no median gives a field the face retired (team 1.36.63), and the texts of the empty season and of
  `--all` say no unknown figure as `None`; season 2's launch without a model under null, in the band of 1800 s and in
  no band of context, its cost in the slot of its end past the season's stop; T5's cost, never launched, in season 1's
  first slot and in no line of `by_model`, nor `a` (D10); a member without effort has no cost of an effort hour, and
  is judged against the median (team 1.36.64); season 2's empty slot and bands cost 0 in USD, its tokens unknown (D11);
  T5's cost, never launched, on season 1's null line of `by_model`, and season 2's slot that only `k`'s kill ends in at
  0 (D12)
- (g) `watch` on a journal that carries a snapshot (team `seen`) and wake-ups open: under `--task T1 --until-done`
  the launched wake-up on T1 is followed, the one on T2 never launched is not, the watch does not leave while an
  intent is open; a `wake-intent` on T1 appended while it watches is said, a post on T2 is not, the snapshot never;
  once that intent is said the bench interrupts the watch, which closes the reader of the flow it still follows and
  ends rc 0; `--until-done` on a team at rest whose open task owes a `do` (team `owed`) lasts
  its `--for` too
The same readers from an agent that borrows the house's machine are `team-readers-from-agent`'s.
"""
from __future__ import annotations

import json
import math
import os
import re
from concurrent.futures import ThreadPoolExecutor
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

from tests.harness import support

T = support(__file__, "team")
RETIRED = ("yield", "task_cost", "roles")                       # what a season's face no longer gives (team 1.36.63)
RETIRED_LOSSES = ("do_extra", "pairs_extra", "pairs", "do_per_pair")   # nor its losses
SEASON_LINES = 12          # the lines of a season's text: its head, the four of its head, then its seven blocks


def gone(season: dict) -> list[str]:
    """-> the fields of a season's face that the face no longer gives, found there: none owed."""
    return [key for key in RETIRED if key in season] + [f"losses.{key}" for key in RETIRED_LOSSES
                                                         if key in (season.get("losses") or {})]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)

    def faced(*args: str) -> tuple:
        played = h.call("team", *args)
        try:
            found = [json.loads(line) for line in played.stdout.splitlines() if line.strip()]
        except ValueError:
            found = None
        return played, found

    def ids(played) -> list[int]:
        return [int(line.split()[0].lstrip("#")) for line in played.stdout.splitlines() if line.startswith("#")]

    h.declare("old", T.OLD_DECLARED)
    h.journal_of("old").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("old").write_text(T.OLD_JOURNAL, encoding="utf-8")

    # --- (a) log --json on the old journal ---------------------------------------------------------------------
    played, said = faced("log", "old", "--json")
    said = said or []
    by_id = {one.get("id"): one for one in said}
    kinds = {one.get("event") for one in said}
    verbs = {one.get("verb") for one in said if one.get("event") == "post"}

    def seen(key: int) -> tuple:
        one = by_id.get(key) or {}
        return tuple(one.get(field) for field in ("verb", "re", "was", "from", "about"))

    wanted = {21: ("re", 7, "done", "r1", None), 23: ("re", 16, "reply", "m", None), 28: ("re", 9, "done", "r2", None),
              50: ("re", 41, "escalate", "r1", None), 56: ("notice", None, "escalate", "old", "m")}
    got_a = {key: seen(key) for key in wanted}
    if (played.returncode == 0 and not kinds & {"delegation", "terminal"} and verbs <= {"do", "ask", "re", "notice", "info", "stop"}
            and got_a == wanted and 8 not in by_id and 20 not in by_id):
        held("(a) log --json speaks the debt", f"no delegation, no terminal; posts {sorted(verbs)}; #21 #23 #28 #50 said re "
             "(was done, reply, done, escalate), #56 the team's notice about m")
    else:
        failures.append(f"  ✗ (a) log --json             rc={played.returncode} kinds={sorted(map(str, kinds))} "
                        f"verbs={sorted(map(str, verbs))} got={got_a}")

    # --- (b) log, the text: the ids --json carries, the dead events' ids absent ---------------------------------
    text = h.call("team", "log", "old")
    dead = {one["id"] for one in h.events("old") if one.get("kind") in ("delegation", "terminal")}
    if (text.returncode == 0 and ids(text) == [one.get("id") for one in said] and dead and not dead & set(ids(text))
            and 56 in ids(text)):
        held("(b) log speaks the debt", f"{len(ids(text))} lines, the ids of --json; no dead line ({sorted(dead)} absent); "
             "#56 said")
    else:
        failures.append(f"  ✗ (b) log                    rc={text.returncode} ids={ids(text)} json={[one.get('id') for one in said]} "
                        f"dead={sorted(dead)}")

    # --- (c) watch --json: the old kinds appended while it watches ---------------------------------------------
    watcher = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", "old", "--json",
                                "--heartbeat", "1", "--for", "15"], cwd=h.ws, env={**os.environ, **h.env},
                               stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, start_new_session=True)
    heard: list[str] = []
    reader = threading.Thread(target=lambda: heard.extend(iter(watcher.stderr.readline, "")), daemon=True)
    reader.start()
    deadline = time.monotonic() + 10
    while not heard and time.monotonic() < deadline:          # the first quiet beat: the watch follows the journal
        time.sleep(0.1)
    with h.journal_of("old").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": "2026-10-13T05:42:00+00:00", "id": 57, "kind": "delegation", "team": "old",
                                 "from": "m", "to": "r2", "task": "T2"}) + "\n")
        handle.write(json.dumps({"at": "2026-10-13T05:42:00+00:00", "id": 58, "kind": "post", "team": "old", "task": "T2",
                                 "from": "m", "to": "r2", "verb": "do", "text": "look"}) + "\n")
        handle.write(json.dumps({"at": "2026-10-13T05:42:01+00:00", "id": 59, "kind": "post", "team": "old", "task": "T2",
                                 "from": "r2", "to": "m", "verb": "done", "text": "looked"}) + "\n")

    def flow() -> list[dict]:
        found = []
        for one in list(heard):
            try:
                found.append(json.loads(one))
            except ValueError:
                pass
        return found

    deadline = time.monotonic() + 10
    while not any(one.get("id") == 59 for one in flow()) and time.monotonic() < deadline:
        time.sleep(0.1)
    os.killpg(watcher.pid, signal.SIGTERM)                    # read: the watch and what it launched end here
    watcher.wait(timeout=10)
    reader.join(timeout=5)
    ids_c = {one.get("id"): one for one in flow() if one.get("team") == "old"}
    if 57 not in ids_c and (ids_c.get(58) or {}).get("verb") == "do" and \
            ((ids_c.get(59) or {}).get("verb"), (ids_c.get(59) or {}).get("re"), (ids_c.get(59) or {}).get("was")) == ("re", 58, "done"):
        held("(c) watch --json speaks the debt", "the delegation #57 never said; #59 r2's done said re #58 (was done)")
    else:
        failures.append(f"  ✗ (c) watch --json           ids={sorted(map(str, ids_c))} #59={ids_c.get(59)} {''.join(heard)[-300:]!r}")

    # --- (d) status --json: the face of the old journal ---------------------------------------------------------
    face = h.face("old")
    tasks = {one.get("id"): one.get("state") for one in face.get("tasks") or []}
    members = {one.get("member") for one in face.get("members") or []}
    if tasks == {"T1": "resolved", "T2": "open"} and {"m", "r1", "r2"} <= members:
        held("(d) status --json reads the old journal", f"tasks {tasks}, members {sorted(members)}")
    else:
        failures.append(f"  ✗ (d) status --json          tasks={tasks} members={sorted(members)} face={str(face)[-300:]!r}")
    # --- (e) stats reads the seasons of a journal ------------------------------------------------------------------
    h.declare("idle", "---\nagents: |\n  s agents/s\nroot: s\n---\nNever started.\n")
    h.declare("ledger", "---\nagents: |\n  lead agents/lead\n  w1 agents/w1\n  w2 agents/w2\nreports: |\n"
                        "  w1 w2 -> lead\nroot: lead\nroles: |\n  chief lead\n  workers w1 w2\nschedule: off\n---\nCount.\n")
    started_ = {"kind": "team-started", "team": "ledger", "agents": {"lead": "agents/lead", "w1": "agents/w1",
                "w2": "agents/w2"}, "reports": [{"from": ["w1", "w2"], "to": "lead"}], "root": "lead", "principals": [],
                "owner": "house", "roles": {"chief": ["lead"], "workers": ["w1", "w2"]}, "limits": {}}
    day1, day3 = "2026-11-20T", "2026-11-22T"
    capped_1 = {**started_, "limits": {"budget": 10.0, "budget-launches": 20}}   # season 1: USD and launches capped
    capped_3 = {**started_, "limits": {"budget": 2.0}}                           # season 3: USD alone
    rows = [
        (day1 + "10:00:00", capped_1),
        (day1 + "10:00:00", {"kind": "task", "task": "T1", "from": "house", "to": "lead", "name": "one", "text": "one"}),
        (day1 + "10:00:00", {"kind": "post", "task": "T1", "from": "house", "to": "lead", "verb": "do", "text": "one"}),
        (day1 + "10:00:00", {"kind": "wake-intent", "tag": "a", "agent": "lead", "task": "T1", "messages": []}),
        (day1 + "10:00:05", {"kind": "wake-launched", "tag": "a", "agent": "lead", "run": "r1",
                             "model": "fable", "provider": "claude"}),
        (day1 + "10:10:00", {"kind": "post", "task": "T1", "from": "lead", "to": "w1", "verb": "do", "text": "x", "ref": "do-w1"}),
        (day1 + "10:10:00", {"kind": "post", "task": "T1", "from": "lead", "to": "w2", "verb": "do", "text": "y"}),
        (day1 + "10:20:05", {"kind": "wake-ended", "tag": "a", "agent": "lead", "run": "r1", "cost": 2.0, "tokens": 1000,
                             "context": {"tokens": 400, "used": 0.2, "window": 2000}}),
        (day1 + "10:20:05", {"kind": "wake-intent", "tag": "b", "agent": "w1", "task": "T1", "messages": []}),
        (day1 + "10:20:05", {"kind": "wake-intent", "tag": "c", "agent": "w2", "task": "T1", "messages": []}),
        (day1 + "10:20:10", {"kind": "wake-launched", "tag": "b", "agent": "w1", "run": "r2",
                             "model": "opus", "provider": "claude"}),
        (day1 + "10:20:15", {"kind": "wake-launched", "tag": "c", "agent": "w2", "run": "r3",
                             "model": "opus", "provider": "claude"}),
        (day1 + "10:30:00", {"kind": "post", "task": "T1", "from": "w1", "to": "house", "verb": "ask", "text": "which?",
                             "ref": "ask"}),
        (day1 + "10:40:15", {"kind": "wake-failed", "tag": "c", "agent": "w2", "task": "T1", "final": False,
                             "reason": "harness-error: boom", "cost": 0.5}),
        (day1 + "10:50:10", {"kind": "post", "task": "T1", "from": "w1", "to": "lead", "verb": "re", "re": "do-w1", "text": "a"}),
        (day1 + "10:50:10", {"kind": "wake-ended", "tag": "b", "agent": "w1", "run": "r2", "cost": 3.0, "tokens": 3000,
                             "context": {"tokens": 1000, "used": 0.5, "window": 2000}}),
        (day1 + "11:00:00", {"kind": "post", "task": "T1", "from": "house", "to": "w1", "verb": "reply", "reply": "ask",
                             "text": "this"}),
        (day1 + "11:00:00", {"kind": "post", "task": "T1", "from": "lead", "to": "w2", "verb": "do", "text": "y again",
                             "ref": "do-w2"}),
        (day1 + "11:00:00", {"kind": "budget-raised", "by": "house", "budget": 12.0}),
        (day1 + "11:00:00", {"kind": "wake-intent", "tag": "d", "agent": "w2", "task": "T1", "messages": []}),
        (day1 + "11:00:20", {"kind": "wake-launched", "tag": "d", "agent": "w2", "run": "r3"}),   # no model written
        (day1 + "11:30:20", {"kind": "post", "task": "T1", "from": "w2", "to": "lead", "verb": "re", "re": "do-w2", "text": "b"}),
        (day1 + "11:30:20", {"kind": "wake-ended", "tag": "d", "agent": "w2", "run": "r3", "cost": 1.5,
                             "context": {"tokens": 800, "used": 0.4, "window": 2000}}),
        (day1 + "11:30:20", {"kind": "wake-intent", "tag": "e", "agent": "lead", "task": "T1", "messages": []}),
        (day1 + "11:30:25", {"kind": "wake-launched", "tag": "e", "agent": "lead", "run": "r1",
                             "model": "fable", "provider": "claude"}),
        (day1 + "11:45:00", {"kind": "task", "task": "T2", "from": "house", "to": "lead", "name": "two", "text": "two"}),
        (day1 + "11:45:00", {"kind": "post", "task": "T2", "from": "house", "to": "lead", "verb": "do", "text": "two"}),
        (day1 + "11:50:00", {"kind": "stopped", "task": "T2", "by": "house"}),
        (day1 + "12:10:25", {"kind": "wake-ended", "tag": "e", "agent": "lead", "run": "r1", "cost": 1.0, "tokens": 500,
                             "context": {"tokens": 300, "used": 0.1, "window": 2000}}),
        (day1 + "12:10:25", {"kind": "done", "task": "T1", "result": "ok"}),
        (day1 + "12:15:00", {"kind": "task", "task": "T4", "from": "house", "to": "w1", "name": "four", "text": "4"}),
        (day1 + "12:15:00", {"kind": "post", "task": "T4", "from": "house", "to": "w1", "verb": "do", "text": "4"}),
        (day1 + "12:15:00", {"kind": "wake-intent", "tag": "g", "agent": "w1", "task": "T4", "messages": []}),
        (day1 + "12:15:10", {"kind": "wake-launched", "tag": "g", "agent": "w1", "run": "r2",
                             "model": "fable", "provider": "claude"}),
        (day1 + "12:25:10", {"kind": "wake-ended", "tag": "g", "agent": "w1", "run": "r2", "cost": 1.0, "tokens": 100,
                             "context": {"tokens": 50, "used": 0.25, "window": 2000}}),
        (day1 + "12:30:00", {"kind": "season-stopped", "by": "house", "tasks": [], "recurrences": []}),
        ("2026-11-21T09:00:00", started_),
        ("2026-11-21T10:00:00", {"kind": "season-stopped", "by": "house", "tasks": [], "recurrences": []}),
        (day3 + "08:00:00", capped_3),
        (day3 + "08:00:00", {"kind": "task", "task": "T3", "from": "house", "to": "lead", "name": "three", "text": "3"}),
        (day3 + "08:00:00", {"kind": "post", "task": "T3", "from": "house", "to": "lead", "verb": "do", "text": "3"}),
        (day3 + "08:00:00", {"kind": "wake-intent", "tag": "f", "agent": "lead", "task": "T3", "messages": []}),
        (day3 + "08:00:04", {"kind": "wake-launched", "tag": "f", "agent": "lead", "run": "r4",
                             "model": "fable", "provider": "claude"}),
        (day3 + "08:05:00", {"kind": "run-renewed", "member": "lead", "task": "T3", "run": "r1"}),
        (day3 + "08:10:04", {"kind": "wake-ended", "tag": "f", "agent": "lead", "run": "r4", "tokens": 2000,
                             "context": {"tokens": 900, "used": 0.3, "window": 3000}}),
        (day3 + "08:20:00", {"kind": "silence", "agent": "w1", "task": "T3", "passages": 2}),
        (day3 + "08:30:00", {"kind": "wake-intent", "tag": "h", "agent": "w1", "task": "T4", "messages": []}),
        (day3 + "08:30:05", {"kind": "wake-launched", "tag": "h", "agent": "w1", "run": "r5",
                             "model": "opus", "provider": "claude"}),
        (day3 + "08:40:05", {"kind": "wake-ended", "tag": "h", "agent": "w1", "run": "r5", "cost": 0.5, "tokens": 200,
                             "context": {"tokens": 70, "used": 0.35, "window": 2000}}),
        (day3 + "08:40:05", {"kind": "done", "task": "T4", "result": "four"})]
    refs, lines_ = {}, []
    for rank, (at, row) in enumerate(rows, 1):
        one = {"at": at + "+00:00", "id": rank, **{key: value for key, value in row.items() if key != "ref"}}
        if "ref" in row:
            refs[row["ref"]] = rank
        lines_.append(one)
    for one in lines_:                                  # an answer cites the id of the message it answers
        for key in ("re", "reply"):
            if key in one:
                one[key] = refs[one[key]]
    h.journal_of("ledger").parent.mkdir(parents=True, exist_ok=True)
    h.journal_of("ledger").write_text("".join(json.dumps(one) + "\n" for one in lines_), encoding="utf-8")
    written_before = h.journal_of("ledger").read_bytes()

    asks_ = {"one": ("ledger", "--season", "1", "--json"), "bare": ("ledger", "--json"), "all": ("ledger", "--all", "--json"),
             "text": ("ledger",), "text-2": ("ledger", "--season", "2"), "text-all": ("ledger", "--all"),
             "text-tokens": ("ledger", "--cost", "tokens"), "text-launches": ("ledger", "--cost", "launches", "--season", "1"),
             "team-unknown": ("nothing",), "season-unknown": ("ledger", "--season", "9"),
             "cost-invalid": ("ledger", "--cost", "euros"), "team-not-started": ("idle",), "old": ("old", "--json"),
             "team-not-started-all": ("idle", "--all", "--json")}
    with ThreadPoolExecutor(max_workers=len(asks_)) as pool:   # readers all: played side by side
        played_ = dict(zip(asks_, pool.map(lambda args: h.call("team", "stats", *args), asks_.values())))

    def stats(key: str):
        played = played_[key]
        try:
            return played, json.loads(played.stdout) if played.stdout.strip() else None
        except ValueError:
            return played, None

    usd_only = lambda usd, launches, tokens, estimated=False: {"usd": usd, "launches": launches, "tokens": tokens,
                                                              "tokens_estimated": estimated}
    owed_1 = {
        "season": 1, "started": day1 + "10:00:00+00:00", "ended": "2026-11-21T09:00:00+00:00",
        "stopped": day1 + "12:30:00+00:00", "state": "stopped", "empty": False,
        "tasks": {"born": 3, "closed": 1, "stopped": 1, "open": 1},
        "cost": usd_only(9.0, 6, 5400, True),
        "time": {"elapsed": 82800, "active": 7800, "effort": 9000, "active_share": 0.0942, "parallelism": 1.1538,
                 "slot": 7200, "effort_by_slot": [7775, 1225] + [0] * 10},
        "opening": {"count": 6, "median": 5, "p90": 20},
        "principal": {"asked": 1, "answered": 1, "wait_median": 1800, "wait_max": 1800,
                      "from_principal": {"asked": 0, "answered": 0, "wait_median": None, "wait_max": None}},
        "context": {"median": 0.25, "p90": 0.5, "max": 0.5, "renewals": 0},
        "losses": {"failed": 1, "cost": usd_only(0.5, 1, None), "reasons": {"harness-error": 1}, "silences": 0},
        "by_task": [{"task": "T1", "name": "one", "season": 1, "state": "resolved", "cost": usd_only(8.0, 5, 5300, True),
                     "do": 4, "re": 2, "failures": 1, "time": {"elapsed": 7825, "active": 7200, "effort": 8400},
                     "first": day1 + "10:00:00+00:00", "last": day1 + "12:10:25+00:00", "context_max": 0.5},
                    {"task": "T2", "name": "two", "season": 1, "state": "stopped", "cost": usd_only(None, 0, None),
                     "do": 1, "re": 0, "failures": 0, "time": {"elapsed": 300, "active": 0, "effort": 0},
                     "first": day1 + "11:45:00+00:00", "last": day1 + "11:50:00+00:00", "context_max": None},
                    {"task": "T4", "name": "four", "season": 1, "state": "open", "cost": usd_only(1.0, 1, 100),
                     "do": 1, "re": 0, "failures": 0, "time": {"elapsed": 610, "active": 600, "effort": 600},
                     "first": day1 + "12:15:00+00:00", "last": day1 + "12:25:10+00:00", "context_max": 0.25}],
        "by_member": [{"member": "lead", "roles": ["chief"], "cost": usd_only(3.0, 2, 1500),
                       "per_launch": {"usd": 1.5, "tokens": 750.0}, "do": 2, "re": 0, "failures": 0,
                       "time": {"elapsed": 7820, "active": 3600, "effort": 3600}, "context_max": 0.2, "do_re_median": None},
                      {"member": "w1", "roles": ["workers"], "cost": usd_only(4.0, 2, 3100),
                       "per_launch": {"usd": 2.0, "tokens": 1550.0}, "do": 2, "re": 1, "failures": 0,
                       "time": {"elapsed": 7500, "active": 2400, "effort": 2400}, "context_max": 0.5, "do_re_median": 2410},
                      {"member": "w2", "roles": ["workers"], "cost": usd_only(2.0, 2, 800, True),
                       "per_launch": {"usd": 1.0, "tokens": 400.0}, "do": 2, "re": 1, "failures": 1,
                       "time": {"elapsed": 4205, "active": 3000, "effort": 3000}, "context_max": 0.4,
                       "do_re_median": 1820}]}
    vs = lambda median, ratio, over=2: {"median": median, "ratio": ratio, "over": over}
    # the median of seasons 1 and 3 (the nearest rank: the lower of two): per delegation 0.5 USD, 1.0 launches, 900.0
    # tokens; per effort hour 1.5 USD, 2160.0 tokens; 0 failed (no ratio); a context p90 of 0.35
    owed_1.update({
        "delegations": 6, "per_delegation": {"usd": 1.5, "launches": 1.0, "tokens": 900.0},
        "per_launch": {"usd": 1.5, "tokens": 900.0}, "per_effort_hour": {"usd": 3.6, "tokens": 2160.0},
        "root": {"member": "lead", "cost": usd_only(3.0, 2, 1500), "share": {"usd": 0.3333, "launches": 0.3333,
                                                                             "tokens": 0.2778}},
        "stopped_tasks": {"tasks": 1, "cost": usd_only(0.0, 0, 0), "share": {"usd": 0.0, "launches": 0.0,
                                                                              "tokens": 0.0}},
        "budget": {"usd": {"cap": 12.0, "spent": 9.0, "share": 0.75, "per_active_hour": 4.1538, "hours_left": None},
                   "launches": {"cap": 20, "spent": 6, "share": 0.3, "per_active_hour": 2.7692, "hours_left": None}},
        "against": {"per_delegation": {"usd": vs(0.5, 3.0), "launches": vs(1.0, 1.0), "tokens": vs(900.0, 1.0)},
                    "per_effort_hour": {"usd": vs(1.5, 2.4), "tokens": vs(2160.0, 1.0)},
                    "losses": {"failed": vs(0, None)}, "context": {"p90": vs(0.35, 1.4286)}}})
    for line, (share, each, against) in zip(owed_1["by_task"], (
            ({"usd": 0.8889, "launches": 0.8333, "tokens": 0.9815}, {"usd": 2.0, "launches": 1.25, "tokens": 1325.0},
             (4.0, 1.25, 1.4722)),
            ({"usd": None, "launches": 0.0, "tokens": None}, {"usd": None, "launches": 0.0, "tokens": None},
             (None, 0.0, None)),
            ({"usd": 0.1111, "launches": 0.1667, "tokens": 0.0185}, {"usd": 1.0, "launches": 1.0, "tokens": 100.0},
             (2.0, 1.0, 0.1111)))):
        line.update(share=share, per_delegation=each, against={"per_delegation": {
            "usd": vs(0.5, against[0]), "launches": vs(1.0, against[1]), "tokens": vs(900.0, against[2])}})
    for line, share in zip(owed_1["by_member"], ({"usd": 0.3333, "launches": 0.3333, "tokens": 0.2778},
                                                 {"usd": 0.4444, "launches": 0.3333, "tokens": 0.5741},
                                                 {"usd": 0.2222, "launches": 0.3333, "tokens": 0.1481})):
        line["share"] = share
    # the launches of season 1 (team 1.36.64): a fable 1200 s, b opus 1800 s, c opus 1200 s failed (no context), d no
    # model 1800 s, e fable 2400 s, g fable 600 s -- g at the bound 600 s of a band of duration, b and d at 1800 s, g at
    # the bound 25 % of a band of context, b at 50 %
    peh = lambda usd, tokens: {"usd": usd, "tokens": tokens}
    part = lambda cost, share, effort, per_launch, per_hour: {"launches": cost["launches"], "cost": cost,
                                                              "share": share, "effort": effort,
                                                              "per_launch": per_launch, "per_effort_hour": per_hour}
    band = lambda low, high, cost, share, effort, per_launch, per_hour: {
        "from": low, "to": high, **{key: value for key, value in part(cost, share, effort, per_launch, per_hour).items()
                                    if key != "effort"}}
    zero_share = {"usd": 0.0, "launches": 0.0, "tokens": 0.0}           # D11: nothing, never unknown, where the
    empty = lambda low, high: band(low, high, usd_only(0.0, 0, 0), zero_share, 0, peh(None, None), peh(None, None))
    #                                                                     season's cost is known in the base
    owed_1["by_model"] = [
        {"model": "fable", "provider": "claude", **part(usd_only(4.0, 3, 1600), {"usd": 0.4444, "launches": 0.5,
                                                                               "tokens": 0.2963},
                                                       4200, peh(1.3333, 533.3333), peh(3.4286, 1371.4286))},
        {"model": "opus", "provider": "claude", **part(usd_only(3.5, 2, 3000), {"usd": 0.3889, "launches": 0.3333,
                                                                              "tokens": 0.5556},
                                                      3000, peh(1.75, 1500.0), peh(4.2, 3600.0))},
        {"model": None, "provider": None, **part(usd_only(1.5, 1, 800, True), {"usd": 0.1667, "launches": 0.1667,
                                                                             "tokens": 0.1481},
                                                    1800, peh(1.5, 800.0), peh(3.0, 1600.0))}]
    owed_1["by_duration"] = [empty(0, 60), empty(60, 180), empty(180, 600),
                             band(600, 1800, usd_only(3.5, 3, 1100), {"usd": 0.3889, "launches": 0.5, "tokens": 0.2037},
                                  3000, peh(1.1667, 366.6667), peh(4.2, 1320.0)),
                             band(1800, None, usd_only(5.5, 3, 4300, True),
                                  {"usd": 0.6111, "launches": 0.5, "tokens": 0.7963}, 6000, peh(1.8333, 1433.3333),
                                  peh(3.3, 2580.0))]
    owed_1["context"]["by_band"] = [
        band(0.0, 0.25, usd_only(3.0, 2, 1500), {"usd": 0.3333, "launches": 0.3333, "tokens": 0.2778}, 3600,
             peh(1.5, 750.0), peh(3.0, 1500.0)),
        band(0.25, 0.5, usd_only(2.5, 2, 900, True), {"usd": 0.2778, "launches": 0.3333, "tokens": 0.1667}, 2400,
             peh(1.25, 450.0), peh(3.75, 1350.0)),
        band(0.5, 0.75, usd_only(3.0, 1, 3000), {"usd": 0.3333, "launches": 0.1667, "tokens": 0.5556}, 1800,
             peh(3.0, 3000.0), peh(6.0, 6000.0)),
        empty(0.75, 0.9), empty(0.9, None)]
    owed_1["time"]["cost_by_slot"] = {"usd": [7.0, 2.0] + [0.0] * 10, "launches": [4, 2] + [0] * 10,
                                      "tokens": [4800, 600] + [0] * 10}
    for line, (each, ratios) in zip(owed_1["by_task"], ((peh(3.4286, 2271.4286), (2.2857, 1.0516)),
                                                        (peh(None, None), (None, None)),
                                                        (peh(6.0, 600.0), (4.0, 0.2778)))):
        line["per_effort_hour"] = each
        line["against"]["per_effort_hour"] = {"usd": vs(1.5, ratios[0]), "tokens": vs(2160.0, ratios[1])}
    for line, models, each, ratios in zip(owed_1["by_member"], (["fable"], ["opus", "fable"], ["opus", None]),
                                          (peh(3.0, 1500.0), peh(6.0, 4650.0), peh(2.4, 960.0)),
                                          ((2.0, 0.6944), (4.0, 2.1528), (1.6, 0.4444))):
        line.update(models=models, per_effort_hour=each,
                    against={"per_effort_hour": {"usd": vs(1.5, ratios[0]), "tokens": vs(2160.0, ratios[1])}})
    one_rc, one_ = stats("one")
    bare_rc, bare = stats("bare")
    all_rc, every_ = stats("all")
    texts = [played_[key] for key in asks_ if key.startswith("text")]
    old_rc, aged = stats("old")
    aged_ = (aged or {}).get("season") or {}
    refusals = {code: played_[key] for key, code in (("team-unknown", "team-unknown"), ("season-unknown", "season-unknown"),
                                                     ("cost-invalid", "cost-invalid"), ("team-not-started", "team-not-started"),
                                                     ("team-not-started-all", "team-not-started"))}
    now_ = (bare or {}).get("season") or {}
    s3_owed = {"season": 3, "state": "running", "ended": None, "stopped": None, "empty": False,
               "tasks": {"born": 1, "closed": 1, "stopped": 0, "open": 1}, "cost": usd_only(0.5, 2, 2200),
               "opening": {"count": 2, "median": 4, "p90": 5},
               "context": {"median": 0.3, "p90": 0.35, "max": 0.35, "renewals": 1},   # its bands, below
               "by_task": [{"task": "T3", "name": "three", "season": 3, "state": "open", "cost": usd_only(None, 1, 2000),
                            "do": 1, "re": 0, "failures": 0, "time": {"elapsed": 1200, "active": 600, "effort": 600},
                            "first": day3 + "08:00:00+00:00", "last": day3 + "08:20:00+00:00", "context_max": 0.3},
                           {"task": "T4", "name": "four", "season": 1, "state": "resolved", "cost": usd_only(0.5, 1, 200),
                            "do": 0, "re": 0, "failures": 0, "time": {"elapsed": 605, "active": 600, "effort": 600},
                            "first": day3 + "08:30:00+00:00", "last": day3 + "08:40:05+00:00", "context_max": 0.35}]}
    s3_owed.update({
        "delegations": 1, "per_delegation": {"usd": 0.5, "launches": 2.0, "tokens": 2200.0},
        "per_launch": {"usd": 0.25, "tokens": 1100.0}, "per_effort_hour": {"usd": 1.5, "tokens": 6600.0},
        "root": {"member": "lead", "cost": usd_only(None, 1, 2000), "share": {"usd": None, "launches": 0.5,
                                                                              "tokens": 0.9091}},
        "stopped_tasks": {"tasks": 0, "cost": usd_only(0.0, 0, 0), "share": {"usd": 0.0, "launches": 0.0,
                                                                              "tokens": 0.0}},
        "budget": {"usd": {"cap": 2.0, "spent": 0.5, "share": 0.25, "per_active_hour": 1.5, "hours_left": 1.0},
                   "launches": None},
        "against": {"per_delegation": {"usd": vs(0.5, 1.0), "launches": vs(1.0, 2.0), "tokens": vs(900.0, 2.4444)},
                    "per_effort_hour": {"usd": vs(1.5, 1.0), "tokens": vs(2160.0, 3.0556)},
                    "losses": {"failed": vs(0, None)}, "context": {"p90": vs(0.35, 1.0)}}})
    s3_owed["context"]["by_band"] = [empty(0.0, 0.25),                  # f at 30 %, h at 35 %: 1200 s of effort
                                     band(0.25, 0.5, usd_only(0.5, 2, 2200), {"usd": 1.0, "launches": 1.0, "tokens": 1.0},
                                          1200, peh(0.25, 1100.0), peh(1.5, 6600.0)),
                                     empty(0.5, 0.75), empty(0.75, 0.9), empty(0.9, None)]
    s3_owed["by_task"][0].update(share={"usd": None, "launches": 0.5, "tokens": 0.9091},
                                 per_delegation={"usd": None, "launches": 1.0, "tokens": 2000.0},
                                 per_effort_hour=peh(None, 12000.0),
                                 against={"per_delegation": {"usd": vs(0.5, None), "launches": vs(1.0, 1.0),
                                                             "tokens": vs(900.0, 2.2222)},
                                          "per_effort_hour": {"usd": vs(1.5, None), "tokens": vs(2160.0, 5.5556)}})
    s3_owed["by_task"][1].update(share={"usd": 1.0, "launches": 0.5, "tokens": 0.0909},
                                 per_delegation={"usd": None, "launches": None, "tokens": None},
                                 per_effort_hour=peh(3.0, 1200.0),
                                 against={"per_delegation": {"usd": vs(0.5, None), "launches": vs(1.0, None),
                                                             "tokens": vs(900.0, None)},
                                          "per_effort_hour": {"usd": vs(1.5, 2.0), "tokens": vs(2160.0, 0.5556)}})

    def launches_missed(season: dict) -> list:
        """-> what a season's launches break (team 1.36.64): the shares of `by_model` summing to 1 where the season's
        cost is known, the launches of `by_duration` to its finished launches, the slots of `cost_by_slot` to its cost
        -- one entry per miss."""
        lost, finished = [], season.get("finished")
        for base in ("usd", "launches", "tokens"):
            shares = [one["share"][base] for one in season.get("by_model") or [] if one["share"][base] is not None]
            if season["cost"][base] and not math.isclose(sum(shares), 1.0, abs_tol=1e-3):
                lost.append(("by_model share", base, shares))
            slots = [one for one in ((season["time"].get("cost_by_slot") or {}).get(base) or []) if one is not None]
            if season["cost"][base] is not None and not math.isclose(sum(slots), season["cost"][base], abs_tol=1e-6):
                lost.append(("cost_by_slot", base, slots))
        if sum(one["launches"] for one in season.get("by_duration") or []) != finished:
            lost.append(("by_duration launches", finished, season.get("by_duration")))
        return lost

    def summed(season: dict) -> dict:
        """-> the cost of a season's tasks, summed base by base from its `by_task` lines."""
        lines = season.get("by_task") or []
        usd = [one["cost"]["usd"] for one in lines if one["cost"]["usd"] is not None]
        tokens = [one["cost"]["tokens"] for one in lines if one["cost"]["tokens"] is not None]
        return {"usd": sum(usd) if usd else None, "launches": sum(one["cost"]["launches"] for one in lines),
                "tokens": sum(tokens) if tokens else None}
    t4_total = {"task": "T4", "name": "four", "state": "resolved", "cost": usd_only(1.5, 2, 300), "do": 1, "re": 0,
                "failures": 0, "time": {"elapsed": 159905, "active": 1200, "effort": 1200},   # 44 h 25 min 05 s of wall
                "first": day1 + "12:15:00+00:00", "last": day3 + "08:40:05+00:00", "context_max": 0.35,
                "seasons": [1, 3], "per_delegation": {"usd": 1.5, "launches": 2.0, "tokens": 300.0},
                "per_effort_hour": {"usd": 4.5, "tokens": 900.0}}   # over its 1200 s of effort, never a season's
    alone = lambda line, seasons: {**{key: value for key, value in line.items()
                                      if key not in ("season", "share", "against")}, "seasons": seasons}
    totals = [alone(owed_1["by_task"][0], [1]), alone(owed_1["by_task"][1], [1]), t4_total,
              alone(s3_owed["by_task"][0], [3])]
    total_owed = {"seasons": 2, "cost": usd_only(9.5, 8, 7600, True), "delegations": 7,
                  "per_delegation": {"usd": 1.3571, "launches": 1.1429, "tokens": 1085.7143},
                  "per_launch": {"usd": 1.1875, "tokens": 950.0}, "per_effort_hour": {"usd": 3.3529, "tokens": 2682.3529},
                  "tasks": {"closed": 2, "stopped": 1, "open": 1}, "failed": 1,
                  "stopped_tasks": {"tasks": 1, "cost": usd_only(0.0, 0, 0),
                                    "share": {"usd": 0.0, "launches": 0.0, "tokens": 0.0}}}
    task_cost_owed = {"usd": {"median": 1.5, "p90": 8.0, "concentration": {"tasks": 1, "of": 2}},
                      "launches": {"median": 2, "p90": 5, "concentration": {"tasks": 2, "of": 3}},
                      "tokens": {"median": 2000, "p90": 5300, "concentration": {"tasks": 2, "of": 3}}}

    def told(key: str, label: str) -> str:
        """-> the line of a text that its label opens, '' without one."""
        return next((line for line in played_[key].stdout.splitlines() if line.split()[:1] == [label]), "")

    def figures(line: str) -> list[str]:
        return re.findall(r"\d+(?:\.\d+)?", line)

    def missed(line: str, values: list) -> list:
        """-> the values of the face a line does not say: each `(value, decimals)` among its figures, said with those
        decimals (E10: a cost, a pace, a median and a ratio with two, hours with one; a count, a share as its percent
        with none), each figure of the line answering ONE value only; a name among its words; a value the face does
        not hold (null) owes nothing."""
        found, lost = figures(line), []
        for one in values:
            value, decimals = one if isinstance(one, tuple) else (one, 0)
            if value is None:
                continue
            if isinstance(value, str):
                if value not in line.split():
                    lost.append(value)
                continue
            said = f"{float(value):.{decimals}f}"
            if said in found:
                found.remove(said)                       # said once: a figure answers no other value
            else:
                lost.append(one)
        return lost
    percent = lambda share: None if share is None else round(100 * share)

    def head_owed(face: dict, base: str) -> dict:
        """-> each line of a season's head and the values of its JSON face it says in `base`, each with the decimals the
        text says it with (E10): a cost two in USD, none in launches or tokens; a pace, a median, a ratio two; hours
        one -- the JSON keeping its four."""
        budget, judged = (face.get("budget") or {}).get(base), face["against"]["per_delegation"]
        money = 2 if base == "usd" else 0
        return {"spent": [(face["cost"][base], money), *([(budget["cap"], money), percent(budget["share"]),
                                                          (budget["per_active_hour"], 2), (budget["hours_left"], 1)]
                                                         if budget else [])],
                "work": [face["delegations"], *(face["tasks"][key] for key in ("closed", "stopped", "open"))],
                "price": [(face["per_delegation"][base], 2), (judged[base]["median"], 2), (judged[base]["ratio"], 2),
                          (face["per_effort_hour"].get(base), 2), (face["per_launch"].get(base), 2)],
                "load": [(face["per_delegation"]["launches"], 2), (judged["launches"]["median"], 2),
                         (judged["launches"]["ratio"], 2), face["root"]["member"], percent(face["root"]["share"][base])],
                "time": [(face["time"]["parallelism"], 2)]}
    def tables_owed(face: dict, base: str) -> dict:
        """-> the lines of a season's text that say its launches (team 1.36.64) and the values of its JSON face each
        says in `base`: per model, per band of duration, per band of context -- each line its launches, its cost, its
        share, and its cost per launch and per effort hour, the two left out under `launches` --, and its cost by slot."""
        money = 2 if base == "usd" else 0

        def entry(one: dict) -> list:
            return [one["launches"], *([(one["cost"][base], money)] if base != "launches" else []),
                    percent(one["share"][base]),
                    *([(one["per_launch"][base], 2), (one["per_effort_hour"][base], 2)] if base != "launches" else [])]
        return {"model": [[one["model"], *entry(one)] for one in face["by_model"]],
                "duration": [entry(one) for one in face["by_duration"]],
                "band": [entry(one) for one in face["context"]["by_band"]],
                "slots": [[(value, money) for value in face["time"]["cost_by_slot"][base]]]}

    def told_all(key: str, label: str) -> list[str]:
        """-> the lines of a text that its label opens, in their order."""
        return [line for line in played_[key].stdout.splitlines() if line.split()[:1] == [label]]
    NO_LAUNCHES = {"by_model": [], "by_duration": [], "context": {"by_band": []}}
    launch_lines = lambda face: len(face["by_model"]) + len(face["by_duration"]) + len(face["context"]["by_band"]) + 1
    # the text of each base says the fields of the JSON face of the same season: season 1 in launches, season 3 in USD
    # and in tokens, the total of --all
    texts_missed = {}
    for key, face, base in (("text-launches", (one_ or {}).get("season"), "launches"),
                            ("text", (bare or {}).get("season"), "usd"),
                            ("text-tokens", (bare or {}).get("season"), "tokens")):
        try:
            owed, lines = head_owed(face, base), tables_owed(face, base)
        except (KeyError, TypeError) as error:
            texts_missed[(key, "face")] = repr(error)
            continue
        for label, entries in lines.items():           # one line per model, per band, its own figures on it
            said_ = told_all(key, label)
            if len(said_) != len(entries) or any(missed(line, values) for line, values in zip(said_, entries)):
                texts_missed[(key, label)] = (said_, [missed(line, values) for line, values in zip(said_, entries)])
        for label, values in owed.items():
            if not told(key, label) or missed(told(key, label), values):
                texts_missed[(key, label)] = (told(key, label), missed(told(key, label), values))
        if (face.get("budget") or {}).get(base) is None and len(told(key, "spent").split()) != 3:
            texts_missed[(key, "spent", "the cost alone")] = told(key, "spent")
    total_ = (every_ or {}).get("total") or {}
    try:
        owed_all = [total_["seasons"], (total_["cost"]["usd"], 2), total_["delegations"],
                    (total_["per_delegation"]["usd"], 2), *(total_["tasks"][key] for key in ("closed", "stopped", "open")),
                    total_["failed"]]
    except (KeyError, TypeError) as error:
        owed_all = [repr(error)]
    if not told("text-all", "all") or missed(told("text-all", "all"), owed_all):
        texts_missed[("text-all", "all")] = (told("text-all", "all"), missed(told("text-all", "all"), owed_all))
    # what the face no longer says (le-retrait-de-la-face), read by the structure of each text: a season's text holds
    # its lines and no other -- no line for the cost of a task or the roles --, `--all` one line per season played
    # beside its head, its total and its empty seasons; the cost and the losses of a season say the figures of their
    # fields and no other -- no cost per closed task, no `do` more --; no figure keeps more than two decimals
    def exact(line: str, values: list) -> bool:
        """-> whether a line says each value of the face and no other figure."""
        said_ = [one for one in values if (one[0] if isinstance(one, tuple) else one) is not None]
        return bool(line) and not missed(line, values) and len(figures(line)) == len(said_)
    faced_ = {"text-launches": (one_ or {}).get("season"), "text": now_, "text-tokens": now_,
              "text-2": {"by_model": [], "by_duration": owed_1["by_duration"], "context": owed_1["context"]}}
    every_lines = 1 + len((every_ or {}).get("seasons") or []) + 1 + bool((every_ or {}).get("empty"))
    retired_said = {key: len(played_[key].stdout.splitlines()) for key in asks_ if key.startswith("text")
                    if len(played_[key].stdout.splitlines()) != (every_lines if key == "text-all" else SEASON_LINES + launch_lines(faced_[key] or NO_LAUNCHES))}
    for key, face, base in (("text-launches", (one_ or {}).get("season"), "launches"),
                            ("text", (bare or {}).get("season"), "usd"), ("text-tokens", (bare or {}).get("season"), "tokens")):
        money, losses = 2 if base == "usd" else 0, (face or {}).get("losses") or {}
        if not exact(told(key, "cost"), [((face or {}).get("cost", {}).get(base), money),
                                         (face or {}).get("cost", {}).get("launches")]):
            retired_said[(key, "cost")] = told(key, "cost")
        if not exact(told(key, "losses"), [losses.get("failed"), ((losses.get("cost") or {}).get(base), money),
                                           *(losses.get("reasons") or {}).values(), losses.get("silences")]):
            retired_said[(key, "losses")] = told(key, "losses")
    retired_said.update({(key, "decimals"): [line for line in played_[key].stdout.splitlines()
                                             if re.search(r"\d\.\d{3}", line)]
                         for key in asks_ if key.startswith("text")
                         if any(re.search(r"\d\.\d{3}", line) for line in played_[key].stdout.splitlines())})
    s3_losses = {"failed": 0, "cost": usd_only(None, 0, None), "reasons": {}, "silences": 1}
    gone_med = lambda median: (["yield"] if "yield" in median else []) + [
        f"losses.{key}" for key in RETIRED_LOSSES if key in median.get("losses", {})]
    if (one_rc.returncode == 0 and one_ == {"team": "ledger", "base": "usd", "season": owed_1}
            and bare_rc.returncode == 0 and bare.get("base") == "usd"
            and {key: now_.get(key) for key in s3_owed} == s3_owed and now_.get("losses") == s3_losses
            and now_.get("time", {}).get("active") == 1200 and now_.get("time", {}).get("effort") == 1200
            and summed(owed_1) == {"usd": 9.0, "launches": 6, "tokens": 5400}
            and summed(now_) == {"usd": 0.5, "launches": 2, "tokens": 2200}
            and all_rc.returncode == 0 and [one["season"] for one in every_["seasons"]] == [1, 3]
            and every_["seasons"][0] == owed_1 and every_["empty"] == [2] and every_.get("by_task") == totals
            and not gone(now_) and not any(gone(one) for one in every_["seasons"]) and not gone_med(every_["median"])
            and not launches_missed({**owed_1, "finished": 6}) and not launches_missed({**now_, "finished": 2})
            and [(one["model"], one["provider"], one["launches"]) for one in now_.get("by_model") or []]
            == [("fable", "claude", 1), ("opus", "claude", 1)]
            and [((one["cost"] or {}).get("usd"), (one["share"] or {}).get("usd")) for one in now_.get("by_model") or []]
            == [(0.0, 0.0), (0.5, 1.0)]                 # f reports no cost: 0 where the season's is known (D12)
            and every_["median"].get("per_effort_hour") == {"usd": 1.5, "tokens": 2160.0}
            and every_.get("total") == total_owed and every_.get("task_cost") == task_cost_owed
            and every_["median"].get("per_delegation") == {"usd": 0.5, "launches": 1.0, "tokens": 900.0}
            and every_["median"].get("per_effort_hour") == {"usd": 1.5, "tokens": 2160.0}
            and every_["median"]["losses"].get("failed") == 0 and every_["median"]["context"].get("p90") == 0.35
            and not texts_missed and not retired_said
            and every_["median"]["tasks"] == {"closed": 1, "stopped": 0}
            and every_["median"]["cost"] == {"usd": 0.5, "launches": 2, "tokens": 2200}
            and every_["median"]["time"]["effort"] == 1200 and every_["median"]["opening"] == {"median": 4}
            and all(one.returncode == 0 and one.stdout.strip() for one in texts)
            and all(played.returncode == 2 and code in played.stderr for code, played in refusals.items())
            and h.journal_of("ledger").read_bytes() == written_before
            and old_rc.returncode == 0 and aged_.get("cost") == usd_only(0.08, 10, None)
            and aged_.get("tasks") == {"born": 2, "closed": 1, "stopped": 0, "open": 1}
            and aged_.get("losses", {}).get("reasons") == {"wake-dead": 2}
            and not gone(aged_) and [one["model"] for one in aged_.get("by_model") or []] == [None]
            and all(one["models"] == [None] for one in aged_.get("by_member") or [])
            and [(one["member"], one["roles"]) for one in aged_.get("by_member") or []]
            == [("m", []), ("r1", []), ("r2", [])]):
        held("(e) stats reads the seasons", "season 1: 9.0 USD, 6 launches, 5400 tokens estimated, 1 closed 1 stopped "
             "1 open, 7800 s active of 82800, x1.1538, opening median 5 s p90 20 s, 1 question "
             "answered in 1800 s, 1 failure, T4 by its season-1 wake-up alone, its members line "
             "by line; bare: season 3 running, T3 usd null, T4 by its season-3 wake-up, closed there; by_task sums to "
             "each season's cost; --all: seasons 1 and 3, their median, 2 empty, T1 T2 T4 T3 over all their seasons, T4 "
             "1.5 USD on 2 launches from seasons 1 and 3, 159905 s elapsed; 5 texts; the head: 6 delegations at "
             "1.5 USD x3.0 the median, 3.6 USD an effort hour, lead 33 %, 9.0 of 12.0 USD raised and 6 of 20 launches, "
             "season 3 1.0 h left at 1.5 USD an active hour; --all: 7 delegations, 1.3571 USD each, 80 % of the "
             "tokens in 2 tasks of 3; spent, work, price, load, time and all said, a pace, a median and a ratio with "
             "two decimals and hours with one while the JSON keeps four; season 1 by model (fable, opus, none: shares "
             "summing to 1), by duration (g at 600 s, b and d at 1800 s in the band their bound opens) and by context (c "
             "in none), its cost by slot of its end (7.00 and 2.00 USD), the cost of an effort hour of each task and "
             "member against the season's median, w1's two models, each said in the text, a model and a band per "
             "line; an empty band or slot costs 0; no season, no median, no text says the yield, "
             "the cost of a task, the roles or the do more any longer, --all's task_cost kept; team-unknown, "
             "season-unknown, cost-invalid, team-not-started bare and under --all; nothing written; the old journal: "
             "0.08 USD, 10 launches, its tokens null, T1 closed, 2 wake-dead, every member without a role key")
    else:
        failures.append(f"  ✗ (e) stats                   rc={one_rc.returncode}/{bare_rc.returncode}/{all_rc.returncode} "
                        f"one={json.dumps((one_ or {}).get('season'))} owed={json.dumps(owed_1)} "
                        f"bare={json.dumps({key: now_.get(key) for key in s3_owed})} losses={now_.get('losses')} "
                        f"time={now_.get('time')} all={json.dumps({k: v for k, v in (every_ or {}).items() if k != 'seasons'})} "
                        f"totals={json.dumps(totals)} total={json.dumps((every_ or {}).get('total'))} "
                        f"task_cost={json.dumps((every_ or {}).get('task_cost'))} texts={texts_missed} "
                        f"launches={launches_missed({**owed_1, 'finished': 6})}/"
                        f"{launches_missed({**now_, 'finished': 2}) if now_ else '-'} "
                        f"models={[(one.get('model'), one.get('launches')) for one in now_.get('by_model') or []]} "
                        f"retired={retired_said} gone={gone(now_)}/{[gone(one) for one in (every_ or {}).get('seasons') or []]}/"
                        f"{gone_med((every_ or {}).get('median') or {})}/{gone(aged_)} "
                        f"texts={[one.returncode for one in texts]} {[one.stderr[-120:] for one in texts if one.returncode]} "
                        f"refusals={ {code: (p.returncode, p.stderr[-120:]) for code, p in refusals.items()} } "
                        f"old={ {key: aged_.get(key) for key in ('cost', 'tasks', 'by_member')} } {one_rc.stderr[-300:]!r}")

    # --- (f) stats on the edges of a journal ---------------------------------------------------------------------
    h.declare("tally", "---\nagents: |\n  lead agents/lead\nroot: lead\nschedule: off\n---\nTally.\n")
    s1, s2 = "2026-11-20T10:00:00+00:00", "2026-11-21T09:00:00+00:00"
    begun_t = {"kind": "team-started", "agents": {"lead": "agents/lead"}, "reports": [], "root": "lead", "principals": [],
               "owner": "house", "limits": {}}
    h.written("tally", [
        {**begun_t, "at": s1},                                                                           # 1
        {"kind": "task", "task": "T1", "from": "house", "to": "lead", "name": "one", "text": "1"},        # 2
        {"kind": "post", "task": "T1", "from": "house", "to": "lead", "verb": "do", "text": "1", "at": None},   # 3: no hour
        {"kind": "wake-intent", "tag": "a", "agent": "lead", "task": "T1", "messages": [3]},              # 4: never launched
        {"kind": "wake-failed", "tag": "a", "agent": "lead", "task": "T1", "final": False, "reason": "launch-missing",
         "at": "2026-11-20T10:01:00+00:00"},
        {"kind": "stopped", "task": "T1", "by": "house", "at": "2026-11-20T10:02:00+00:00"},
        {"kind": "resumed", "task": "T1", "by": "house", "from": ["stopped"], "at": "2026-11-20T10:03:00+00:00"},
        {"kind": "task", "task": "T2", "from": "house", "to": "lead", "name": "two", "text": "2",
         "at": "2026-11-20T10:05:00+00:00"},
        {"kind": "task", "task": "T3", "from": "house", "to": "lead", "name": "three", "text": "3", "at": None},
        {"kind": "task", "task": "T5", "from": "house", "to": "lead", "name": "five", "text": "5",
         "at": "2026-11-20T10:10:00+00:00"},
        {"kind": "wake-intent", "tag": "e", "agent": "lead", "task": "T5", "messages": [],
         "at": "2026-11-20T10:10:00+00:00"},                                                  # never launched, its cost said
        {"kind": "wake-failed", "tag": "e", "agent": "lead", "task": "T5", "final": True, "reason": "launch-missing",
         "cost": 0.5, "at": "2026-11-20T10:11:00+00:00"},
        {"kind": "stopped", "task": "T5", "by": "house", "at": "2026-11-20T10:12:00+00:00"},
        {**{key: value for key, value in begun_t.items() if key != "root"}, "at": s2},          # season 2, no root
        {"kind": "done", "task": "T2", "result": "two", "at": "2026-11-19T08:00:00+00:00"},              # stamped before
        {"kind": "done", "task": "T3", "result": "three", "at": None},
        {"kind": "wake-intent", "tag": "b", "agent": "lead", "task": "T2", "messages": []},
        {"kind": "wake-launched", "tag": "b", "agent": "lead", "run": "kb", "at": "2026-11-21T09:00:05+00:00"},
        {"kind": "wake-intent", "tag": "k", "agent": "lead", "task": "T2", "messages": [],
         "at": "2026-11-21T09:00:06+00:00"},                                                    # never launched, killed:
        {"kind": "wake-killed", "tag": "k", "agent": "lead", "task": "T2", "at": "2026-11-21T09:00:08+00:00"},   # no cost
        {"kind": "season-stopped", "by": "house", "tasks": [], "recurrences": [], "at": "2026-11-21T09:00:10+00:00"},
        {"kind": "wake-ended", "tag": "b", "agent": "lead", "run": "kb", "cost": 1.0, "at": "2026-11-21T12:00:05+00:00"}],
        at=s1)
    with ThreadPoolExecutor(max_workers=3) as pool:
        tally_ = dict(zip(("all", "s1", "last", "text-s1", "text-all"),
                          pool.map(lambda args: h.call("team", "stats", "tally", *args),
                                   (("--all", "--json"), ("--season", "1", "--json"), ("--json",), ("--season", "1"),
                                    ("--all",)))))

    def read_f(key: str) -> dict:
        try:
            return json.loads(tally_[key].stdout)
        except ValueError:
            return {}
    all_f, s1_f, last_f = read_f("all"), (read_f("s1").get("season") or {}), (read_f("last").get("season") or {})
    totals_f = {one.get("task"): (one.get("state"), one.get("first"), one.get("last")) for one in all_f.get("by_task") or []}
    t1_f = next((one for one in s1_f.get("by_task") or [] if one.get("task") == "T1"), {})
    seasons_f = {one.get("task"): one.get("seasons") for one in all_f.get("by_task") or []}
    if (all(one.returncode == 0 for one in tally_.values())
            and totals_f.get("T1") == ("open", s1, "2026-11-20T10:03:00+00:00")
            and totals_f.get("T2") == ("resolved", "2026-11-19T08:00:00+00:00", "2026-11-21T12:00:05+00:00")
            and totals_f.get("T3") == ("resolved", None, None)
            and (t1_f.get("state"), t1_f.get("failures"), t1_f.get("first")) == ("open", 1, s1)
            and s1_f.get("empty") is True and (s1_f.get("time") or {}).get("effort") == 0
            and (last_f.get("season"), last_f.get("state"), last_f.get("stopped")) == (2, "stopped", "2026-11-21T09:00:10+00:00")
            and (last_f.get("time") or {}).get("effort_by_slot") == [7195, 3605]
            and all_f.get("empty") == [1]
            and s1_f.get("budget", 0) is None and last_f.get("budget", 0) is None
            and ((s1_f.get("against") or {}).get("per_delegation") or {}).get("usd") == {"median": None, "ratio": None,
                                                                                         "over": 0}
            and ((last_f.get("against") or {}).get("losses") or {}).get("failed") == {"median": 0, "ratio": None,
                                                                                      "over": 1}
            and ((all_f.get("total") or {}).get("seasons"), (all_f.get("total") or {}).get("tasks"),
                 ((all_f.get("total") or {}).get("cost") or {}).get("usd")) == (1, {"closed": 2, "stopped": 0, "open": 0},
                                                                               1.0)
            and seasons_f.get("T2") == [1, 2]
            and not any(gone(one) for one in (s1_f, last_f, *(all_f.get("seasons") or [])))
            and "yield" not in (all_f.get("median") or {"yield": 0})
            and not set(RETIRED_LOSSES) & set(((all_f.get("median") or {}).get("losses") or {}))
            and all(tally_[key].stdout.strip() and "None" not in tally_[key].stdout for key in ("text-s1", "text-all"))
            and [(one.get("model"), one.get("launches"), (one.get("cost") or {}).get("usd"), one.get("effort"))
                 for one in last_f.get("by_model") or []] == [(None, 1, 1.0, 10800)]
            and [one.get("models") for one in last_f.get("by_member") or []] == [[None]]
            and s1_f.get("by_model") == [{"model": None, "provider": None, "launches": 0,   # D12: T5's e, never
                                          "cost": {"usd": 0.5, "launches": 0, "tokens": None,   # launched, carries its
                                                   "tokens_estimated": False},                 # cost on the null line;
                                          "share": {"usd": 1.0, "launches": 0.0, "tokens": None},   # a, without one,
                                          "effort": 0, "per_launch": {"usd": None, "tokens": None},   # in no line
                                          "per_effort_hour": {"usd": None, "tokens": None}}]
            and [one.get("launches") for one in last_f.get("by_duration") or []] == [0, 0, 0, 0, 1]
            and [one.get("launches") for one in (last_f.get("context") or {}).get("by_band") or []] == [0, 0, 0, 0, 0]
            and (last_f.get("time") or {}).get("cost_by_slot") == {"usd": [0.0, 1.0], "launches": [0, 1],
                                                                   "tokens": [None, None]}   # its tokens unknown;
            #                                    slot 0 holds k's end alone, which reports no cost: 0, never null (D12)
            and [((one.get("cost") or {}).get("usd"), (one.get("share") or {}).get("usd"), (one.get("cost") or {}).get("tokens"))
                 for one in (last_f.get("context") or {}).get("by_band") or []] == [(0.0, 0.0, None)] * 5
            and ((s1_f.get("time") or {}).get("cost_by_slot") or {}).get("usd", [None])[:1] == [0.5]
            and [one.get("per_effort_hour") for one in s1_f.get("by_member") or []] == [{"usd": None, "tokens": None}]
            and (((last_f.get("by_member") or [{}])[0].get("against") or {}).get("per_effort_hour") or {}).get("usd")
            == {"median": 0.3333, "ratio": 1.0, "over": 1}
            and s1_f.get("stopped_tasks") == {"tasks": 1, "cost": {"usd": 0.5, "launches": 0, "tokens": None,
                                                                   "tokens_estimated": False},
                                              "share": {"usd": 1.0, "launches": 0.0, "tokens": None}}
            and last_f.get("root") == {"member": None, "cost": {"usd": None, "launches": None, "tokens": None,
                                                                 "tokens_estimated": False},
                                       "share": {"usd": None, "launches": None, "tokens": None}}
            and all_f.get("task_cost") == {"usd": {"median": 1.0, "p90": 1.0, "concentration": {"tasks": 1, "of": 1}},
                                           "launches": {"median": 1, "p90": 1, "concentration": {"tasks": 1, "of": 1}},
                                           "tokens": {"median": None, "p90": None,
                                                      "concentration": {"tasks": None, "of": 0}}}):
        held("(f) stats on the edges of a journal", "T1 stopped then resumed: open, its post without an hour skipped, its "
             "wake-up never launched a failure without effort; season 2 stopped by its season-stopped, b's effort past "
             "its one slot (7195 + 3605 s); T2 first at its earlier season-2 hour; T3 without any hour: first and last null; "
             "no cap, no budget; season 1 empty, judged over 1 season played; 0 failed the median, no ratio; the total "
             "of season 2 alone, T2 of seasons 1 and 2; T5 stopped at the end of season 1 in its stopped_tasks with "
             "its 0.5 USD, T1 resumed not; season 2 without a root: its cost and share null; the cost of a task over "
             "the launched tasks of season 2 alone; season 1 judged over the 0 seasons whose cost per delegation is "
             "known; neither season, nor the median, gives the yield, the cost of a task, the roles or the do more; the "
             "texts of the empty season and of --all said, no figure unknown said None; b without a model under null, "
             "in the band 1800 s and in no band of context, its 1.0 USD in the slot of its end; T5's 0.5 USD, never "
             "launched, in the first slot of season 1 and in no line of by_model; lead's hour of effort null without "
             "effort, against the median; the empty slot and bands of season 2 cost 0 in USD, its tokens unknown")
    else:
        failures.append(f"  ✗ (f) stats on the edges        rc={[one.returncode for one in tally_.values()]} totals={totals_f} "
                        f"t1={t1_f} s1={ {key: s1_f.get(key) for key in ('empty', 'time')} } "
                        f"last={ {key: last_f.get(key) for key in ('season', 'state', 'stopped', 'time')} } "
                        f"empty={all_f.get('empty')} budget={s1_f.get('budget', 0)}/{last_f.get('budget', 0)} "
                        f"against={s1_f.get('against')}/{last_f.get('against')} total={all_f.get('total')} "
                        f"seasons={seasons_f} stopped={s1_f.get('stopped_tasks')} root={last_f.get('root')} "
                        f"task_cost={all_f.get('task_cost')} gone={[gone(one) for one in (s1_f, last_f)]} "
                        f"models={last_f.get('by_model')} bands={(last_f.get('context') or {}).get('by_band')} "
                        f"durations={last_f.get('by_duration')} slots={(last_f.get('time') or {}).get('cost_by_slot')}/"
                        f"{(s1_f.get('time') or {}).get('cost_by_slot')} members={last_f.get('by_member')} "
                        f"median={all_f.get('median')} texts={[tally_[key].stdout[-300:] for key in ('text-s1', 'text-all')]} "
                        f"{tally_['all'].stderr[-200:]!r}")

    # --- (g) watch on a journal with a snapshot and wake-ups open -------------------------------------------------
    h.declare("seen", "---\nagents: |\n  a agents/a\n  b agents/b\nreports: |\n  b -> a\nroot: a\nschedule: off\n---\nSeen.\n")
    h.declare("owed", "---\nagents: |\n  c agents/c\nroot: c\nschedule: off\n---\nOwed.\n")
    pair_g = {"kind": "team-started", "agents": {"a": "agents/a", "b": "agents/b"}, "reports": [{"from": ["b"], "to": "a"}],
              "root": "a", "principals": [], "owner": "house", "ceremonies": [], "launch": {}, "limits": {}, "schedule": None}
    at_g = "2026-11-23T10:00:00+00:00"
    h.written("seen", [pair_g,
                       {"kind": "task", "task": "T1", "from": "house", "to": "a", "text": "one"},
                       {"kind": "post", "task": "T1", "from": "house", "to": "a", "verb": "do", "text": "one"},
                       {"kind": "task", "task": "T2", "from": "house", "to": "b", "text": "two"},
                       {"kind": "post", "task": "T2", "from": "house", "to": "b", "verb": "do", "text": "two"},
                       {"kind": "wake-intent", "tag": "a-T1", "agent": "a", "path": "agents/a", "task": "T1", "run": None,
                        "index": 1, "messages": [3]},
                       {"kind": "wake-launched", "tag": "a-T1", "agent": "a", "run": "ka", "launch": 1},
                       {"kind": "wake-intent", "tag": "b-T2", "agent": "b", "path": "agents/b", "task": "T2", "run": None,
                        "index": 1, "messages": [5]}], at=at_g)
    h.written("owed", [{**pair_g, "agents": {"c": "agents/c"}, "reports": [], "root": "c"},
                       {"kind": "task", "task": "T1", "from": "house", "to": "c", "text": "one"},
                       {"kind": "post", "task": "T1", "from": "house", "to": "c", "verb": "do", "text": "one"}], at=at_g)
    snapped_g = h.call("team", "snapshot", "seen")

    def watching_g(name: str, *flags: str) -> subprocess.Popen:
        return subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "watch", name, "--json",
                                 "--heartbeat", "1", "--until-done", *flags], cwd=h.ws, env={**os.environ, **h.env},
                                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, start_new_session=True)
    begun_g = time.monotonic()
    watchers_g = {"seen": watching_g("seen", "--task", "T1", "--for", "60"), "owed": watching_g("owed", "--for", "2")}
    heard_g: dict[str, list[str]] = {name: [] for name in watchers_g}
    readers_g = [threading.Thread(target=lambda name=name: heard_g[name].extend(iter(watchers_g[name].stderr.readline, "")),
                                  daemon=True) for name in watchers_g]
    for one in readers_g:
        one.start()

    def flow_g(name: str) -> list[dict]:
        found = []
        for one in list(heard_g[name]):
            try:
                found.append(json.loads(one))
            except ValueError:
                found.append({"unparsed": one})
        return found
    deadline = time.monotonic() + 30                  # the watch reads its journal: its first quiet beat said
    while not any(one.get("event") == "quiet" for one in flow_g("seen")) and time.monotonic() < deadline:
        time.sleep(0.1)
    last_g = max(one["id"] for one in h.events("seen"))
    with h.journal_of("seen").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": at_g, "id": last_g + 1, "kind": "wake-intent", "team": "seen", "tag": "b-T1",
                                 "agent": "b", "path": "agents/b", "task": "T1", "run": None, "index": 1, "messages": []}) + "\n")
        handle.write(json.dumps({"at": at_g, "id": last_g + 2, "kind": "post", "team": "seen", "task": "T2", "from": "house",
                                 "to": "b", "verb": "info", "text": "fyi"}) + "\n")
    deadline = time.monotonic() + 30                  # the appended intent said: the watch has read past the post too
    while (not any(one.get("id") == last_g + 1 for one in flow_g("seen")) and watchers_g["seen"].poll() is None
           and time.monotonic() < deadline):
        time.sleep(0.1)
    alive_g = watchers_g["seen"].poll() is None       # still watching: an intent open, its bound far
    def skill_of(pid: int) -> int | None:
        """-> the pid of the script `team watch` plays under the console `pid`, read in /proc: the one that hears Ctrl-C."""
        try:
            children = Path(f"/proc/{pid}/task/{pid}/children").read_text().split()
        except OSError:
            return None
        for child in children:
            try:
                line = Path(f"/proc/{child}/cmdline").read_bytes()
            except OSError:
                continue
            found = int(child) if b"pp-team.py" in line else skill_of(int(child))
            if found:
                return found
        return None
    watcher_g = skill_of(watchers_g["seen"].pid) if alive_g else None
    if watcher_g:
        os.kill(watcher_g, signal.SIGINT)              # Ctrl-C to the watch alone, as a terminal would give it
    rcs_g = {name: one.wait(timeout=30) for name, one in watchers_g.items()}
    took_g = time.monotonic() - begun_g
    for one in readers_g:
        one.join(timeout=5)
    seen_g, owed_g = flow_g("seen"), flow_g("owed")
    said_g = [one.get("id") for one in seen_g if one.get("team") == "seen" and one.get("event") != "quiet"]
    if (snapped_g.returncode == 0 and rcs_g == {"seen": 0, "owed": 0} and alive_g and watcher_g and took_g < 60
            and said_g == [last_g + 1] and not any("unparsed" in one or one.get("event") == "snapshot" for one in seen_g + owed_g)
            and any(one.get("event") == "quiet" for one in owed_g)
            and len([one for one in owed_g if one.get("event") == "quiet"]) >= 1):
        held("(g) watch on a snapshot and wake-ups open", f"seen, its journal snapshotted: --task T1 --until-done still "
             f"watching once #{last_g + 1} is said (an intent open), interrupted after {took_g:.1f}s: rc 0; the wake-intent #{last_g + 1} on T1 said, the post "
             f"#{last_g + 2} on T2 and the snapshot never; owed, its do due: --until-done lasts its --for 2, quiet beats said")
    else:
        failures.append(f"  ✗ (g) watch on a snapshot        snap={snapped_g.returncode} rc={rcs_g} alive={alive_g} took={took_g:.1f} "
                        f"said={said_g} seen={''.join(heard_g['seen'])[-300:]!r} owed={''.join(heard_g['owed'])[-300:]!r}")
    return 0
