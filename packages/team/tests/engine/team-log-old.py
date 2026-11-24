"""Scenario `team-log-old` -- 5 case(s): the readers of a journal on the journal team 0.32.2 wrote
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
  its members without a role key
The same readers from an agent that borrows the house's machine are `team-readers-from-agent`'s.
"""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor
import signal
import subprocess
import sys
import threading
import time

from tests.harness import support

T = support(__file__, "team")


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
    rows = [
        (day1 + "10:00:00", started_),
        (day1 + "10:00:00", {"kind": "task", "task": "T1", "from": "house", "to": "lead", "name": "one", "text": "one"}),
        (day1 + "10:00:00", {"kind": "post", "task": "T1", "from": "house", "to": "lead", "verb": "do", "text": "one"}),
        (day1 + "10:00:00", {"kind": "wake-intent", "tag": "a", "agent": "lead", "task": "T1", "messages": []}),
        (day1 + "10:00:05", {"kind": "wake-launched", "tag": "a", "agent": "lead", "run": "r1"}),
        (day1 + "10:10:00", {"kind": "post", "task": "T1", "from": "lead", "to": "w1", "verb": "do", "text": "x", "ref": "do-w1"}),
        (day1 + "10:10:00", {"kind": "post", "task": "T1", "from": "lead", "to": "w2", "verb": "do", "text": "y"}),
        (day1 + "10:20:05", {"kind": "wake-ended", "tag": "a", "agent": "lead", "run": "r1", "cost": 2.0, "tokens": 1000,
                             "context": {"tokens": 400, "used": 0.2, "window": 2000}}),
        (day1 + "10:20:05", {"kind": "wake-intent", "tag": "b", "agent": "w1", "task": "T1", "messages": []}),
        (day1 + "10:20:05", {"kind": "wake-intent", "tag": "c", "agent": "w2", "task": "T1", "messages": []}),
        (day1 + "10:20:10", {"kind": "wake-launched", "tag": "b", "agent": "w1", "run": "r2"}),
        (day1 + "10:20:15", {"kind": "wake-launched", "tag": "c", "agent": "w2", "run": "r3"}),
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
        (day1 + "11:00:00", {"kind": "wake-intent", "tag": "d", "agent": "w2", "task": "T1", "messages": []}),
        (day1 + "11:00:20", {"kind": "wake-launched", "tag": "d", "agent": "w2", "run": "r3"}),
        (day1 + "11:30:20", {"kind": "post", "task": "T1", "from": "w2", "to": "lead", "verb": "re", "re": "do-w2", "text": "b"}),
        (day1 + "11:30:20", {"kind": "wake-ended", "tag": "d", "agent": "w2", "run": "r3", "cost": 1.5,
                             "context": {"tokens": 800, "used": 0.4, "window": 2000}}),
        (day1 + "11:30:20", {"kind": "wake-intent", "tag": "e", "agent": "lead", "task": "T1", "messages": []}),
        (day1 + "11:30:25", {"kind": "wake-launched", "tag": "e", "agent": "lead", "run": "r1"}),
        (day1 + "11:45:00", {"kind": "task", "task": "T2", "from": "house", "to": "lead", "name": "two", "text": "two"}),
        (day1 + "11:45:00", {"kind": "post", "task": "T2", "from": "house", "to": "lead", "verb": "do", "text": "two"}),
        (day1 + "11:50:00", {"kind": "stopped", "task": "T2", "by": "house"}),
        (day1 + "12:10:25", {"kind": "wake-ended", "tag": "e", "agent": "lead", "run": "r1", "cost": 1.0, "tokens": 500,
                             "context": {"tokens": 300, "used": 0.1, "window": 2000}}),
        (day1 + "12:10:25", {"kind": "done", "task": "T1", "result": "ok"}),
        (day1 + "12:15:00", {"kind": "task", "task": "T4", "from": "house", "to": "w1", "name": "four", "text": "4"}),
        (day1 + "12:15:00", {"kind": "post", "task": "T4", "from": "house", "to": "w1", "verb": "do", "text": "4"}),
        (day1 + "12:15:00", {"kind": "wake-intent", "tag": "g", "agent": "w1", "task": "T4", "messages": []}),
        (day1 + "12:15:10", {"kind": "wake-launched", "tag": "g", "agent": "w1", "run": "r2"}),
        (day1 + "12:25:10", {"kind": "wake-ended", "tag": "g", "agent": "w1", "run": "r2", "cost": 1.0, "tokens": 100,
                             "context": {"tokens": 50, "used": 0.25, "window": 2000}}),
        (day1 + "12:30:00", {"kind": "season-stopped", "by": "house", "tasks": [], "recurrences": []}),
        ("2026-11-21T09:00:00", started_),
        ("2026-11-21T10:00:00", {"kind": "season-stopped", "by": "house", "tasks": [], "recurrences": []}),
        (day3 + "08:00:00", started_),
        (day3 + "08:00:00", {"kind": "task", "task": "T3", "from": "house", "to": "lead", "name": "three", "text": "3"}),
        (day3 + "08:00:00", {"kind": "post", "task": "T3", "from": "house", "to": "lead", "verb": "do", "text": "3"}),
        (day3 + "08:00:00", {"kind": "wake-intent", "tag": "f", "agent": "lead", "task": "T3", "messages": []}),
        (day3 + "08:00:04", {"kind": "wake-launched", "tag": "f", "agent": "lead", "run": "r4"}),
        (day3 + "08:05:00", {"kind": "run-renewed", "member": "lead", "task": "T3", "run": "r1"}),
        (day3 + "08:10:04", {"kind": "wake-ended", "tag": "f", "agent": "lead", "run": "r4", "tokens": 2000,
                             "context": {"tokens": 900, "used": 0.3, "window": 3000}}),
        (day3 + "08:20:00", {"kind": "silence", "agent": "w1", "task": "T3", "passages": 2}),
        (day3 + "08:30:00", {"kind": "wake-intent", "tag": "h", "agent": "w1", "task": "T4", "messages": []}),
        (day3 + "08:30:05", {"kind": "wake-launched", "tag": "h", "agent": "w1", "run": "r5"}),
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
        "yield": {"usd_per_closed": 9.0, "launches_per_closed": 6.0, "tokens_per_closed": 5400.0, "usd_per_launch": 1.5},
        "task_cost": {"usd": {"min": 1.0, "median": 1.0, "max": 8.0, "series": [8.0, None, 1.0]},
                      "launches": {"min": 0, "median": 1, "max": 5, "series": [5, 0, 1]},
                      "tokens": {"min": 100, "median": 100, "max": 5300, "series": [5300, None, 100]}},
        "roles": [{"role": "chief", "members": ["lead"], "cost": usd_only(3.0, 2, 1500),
                   "share": {"usd": 0.3333, "launches": 0.3333, "tokens": 0.2778}},
                  {"role": "workers", "members": ["w1", "w2"], "cost": usd_only(6.0, 4, 3900, True),
                   "share": {"usd": 0.6667, "launches": 0.6667, "tokens": 0.7222}}],
        "time": {"elapsed": 82800, "active": 7800, "effort": 9000, "active_share": 0.0942, "parallelism": 1.1538,
                 "slot": 7200, "effort_by_slot": [7775, 1225] + [0] * 10},
        "opening": {"count": 6, "median": 5, "p90": 20},
        "principal": {"asked": 1, "answered": 1, "wait_median": 1800, "wait_max": 1800,
                      "from_principal": {"asked": 0, "answered": 0, "wait_median": None, "wait_max": None}},
        "context": {"median": 0.25, "p90": 0.5, "max": 0.5, "renewals": 0},
        "losses": {"failed": 1, "cost": usd_only(0.5, 1, None), "reasons": {"harness-error": 1}, "silences": 0,
                   "do_extra": 1, "pairs_extra": 1, "pairs": 5, "do_per_pair": 1.2},
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
               "yield": {"usd_per_closed": 0.5, "launches_per_closed": 2.0, "tokens_per_closed": 2200.0,
                         "usd_per_launch": 0.25},
               "opening": {"count": 2, "median": 4, "p90": 5},
               "context": {"median": 0.3, "p90": 0.35, "max": 0.35, "renewals": 1},
               "by_task": [{"task": "T3", "name": "three", "season": 3, "state": "open", "cost": usd_only(None, 1, 2000),
                            "do": 1, "re": 0, "failures": 0, "time": {"elapsed": 1200, "active": 600, "effort": 600},
                            "first": day3 + "08:00:00+00:00", "last": day3 + "08:20:00+00:00", "context_max": 0.3},
                           {"task": "T4", "name": "four", "season": 1, "state": "resolved", "cost": usd_only(0.5, 1, 200),
                            "do": 0, "re": 0, "failures": 0, "time": {"elapsed": 605, "active": 600, "effort": 600},
                            "first": day3 + "08:30:00+00:00", "last": day3 + "08:40:05+00:00", "context_max": 0.35}]}

    def summed(season: dict) -> dict:
        """-> the cost of a season's tasks, summed base by base from its `by_task` lines."""
        lines = season.get("by_task") or []
        usd = [one["cost"]["usd"] for one in lines if one["cost"]["usd"] is not None]
        tokens = [one["cost"]["tokens"] for one in lines if one["cost"]["tokens"] is not None]
        return {"usd": sum(usd) if usd else None, "launches": sum(one["cost"]["launches"] for one in lines),
                "tokens": sum(tokens) if tokens else None}
    t4_total = {"task": "T4", "name": "four", "state": "resolved", "cost": usd_only(1.5, 2, 300), "do": 1, "re": 0,
                "failures": 0, "time": {"elapsed": 159905, "active": 1200, "effort": 1200},   # 44 h 25 min 05 s of wall
                "first": day1 + "12:15:00+00:00", "last": day3 + "08:40:05+00:00", "context_max": 0.35}
    alone = lambda line: {key: value for key, value in line.items() if key != "season"}
    totals = [alone(owed_1["by_task"][0]), alone(owed_1["by_task"][1]), t4_total, alone(s3_owed["by_task"][0])]
    s3_losses = {"failed": 0, "cost": usd_only(None, 0, None), "reasons": {}, "silences": 1, "do_extra": 0,
                 "pairs_extra": 0, "pairs": 1, "do_per_pair": 1.0}
    if (one_rc.returncode == 0 and one_ == {"team": "ledger", "base": "usd", "season": owed_1}
            and bare_rc.returncode == 0 and bare.get("base") == "usd"
            and {key: now_.get(key) for key in s3_owed} == s3_owed and now_.get("losses") == s3_losses
            and now_.get("time", {}).get("active") == 1200 and now_.get("time", {}).get("effort") == 1200
            and summed(owed_1) == {"usd": 9.0, "launches": 6, "tokens": 5400}
            and summed(now_) == {"usd": 0.5, "launches": 2, "tokens": 2200}
            and all_rc.returncode == 0 and [one["season"] for one in every_["seasons"]] == [1, 3]
            and every_["seasons"][0] == owed_1 and every_["empty"] == [2] and every_.get("by_task") == totals
            and every_["median"]["tasks"] == {"closed": 1, "stopped": 0}
            and every_["median"]["cost"] == {"usd": 0.5, "launches": 2, "tokens": 2200}
            and every_["median"]["time"]["effort"] == 1200 and every_["median"]["opening"] == {"median": 4}
            and all(one.returncode == 0 and one.stdout.strip() for one in texts)
            and all(played.returncode == 2 and code in played.stderr for code, played in refusals.items())
            and h.journal_of("ledger").read_bytes() == written_before
            and old_rc.returncode == 0 and aged_.get("cost") == usd_only(0.08, 10, None)
            and aged_.get("tasks") == {"born": 2, "closed": 1, "stopped": 0, "open": 1}
            and aged_.get("losses", {}).get("reasons") == {"wake-dead": 2}
            and [(one["role"], one["members"], one["share"]["usd"]) for one in aged_.get("roles") or []]
            == [(None, ["m", "r1", "r2"], 1.0)]):
        held("(e) stats reads the seasons", "season 1: 9.0 USD, 6 launches, 5400 tokens estimated, 1 closed 1 stopped "
             "1 open, chief 33 % workers 67 %, 7800 s active of 82800, x1.1538, opening median 5 s p90 20 s, 1 question "
             "answered in 1800 s, 1 failure, 1 do more on 5 pairs, T4 by its season-1 wake-up alone, its members line "
             "by line; bare: season 3 running, T3 usd null, T4 by its season-3 wake-up, closed there; by_task sums to "
             "each season's cost; --all: seasons 1 and 3, their median, 2 empty, T1 T2 T4 T3 over all their seasons, T4 "
             "1.5 USD on 2 launches from seasons 1 and 3, 159905 s elapsed; 5 texts; team-unknown, "
             "season-unknown, cost-invalid, team-not-started bare and under --all; nothing written; the old journal: "
             "0.08 USD, 10 launches, its tokens null, T1 closed, 2 wake-dead, every member without a role key")
    else:
        failures.append(f"  ✗ (e) stats                   rc={one_rc.returncode}/{bare_rc.returncode}/{all_rc.returncode} "
                        f"one={json.dumps((one_ or {}).get('season'))} owed={json.dumps(owed_1)} "
                        f"bare={json.dumps({key: now_.get(key) for key in s3_owed})} losses={now_.get('losses')} "
                        f"time={now_.get('time')} all={json.dumps({k: v for k, v in (every_ or {}).items() if k != 'seasons'})} "
                        f"totals={json.dumps(totals)} "
                        f"texts={[one.returncode for one in texts]} {[one.stderr[-120:] for one in texts if one.returncode]} "
                        f"refusals={ {code: (p.returncode, p.stderr[-120:]) for code, p in refusals.items()} } "
                        f"old={ {key: aged_.get(key) for key in ('cost', 'tasks', 'roles')} } {one_rc.stderr[-300:]!r}")
    return 0
