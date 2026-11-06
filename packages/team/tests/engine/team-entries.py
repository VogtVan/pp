"""Scenario `team-entries` -- 3 case(s): an entry is a successor of the agent's DAG -- `procs/TEAM-<team>.md` at
the kit's `turn.begin`, its `next:` the entries then `TEAM-IDLE.md`, decided by the instance's skill `team-entry`,
which asks `team entry` -- at every exchange of a member's run; an entry missing at an agent refuses the start. Four
teams stand in one house, each under its own names; each case waits for its team, then reads its journal and the
traces of its runs.
- (t) the entry of a run already opened: pb opens T1's run, then T2's -- posted while fb plays T1 --, each electing
  `TEAM-IDLE.md`; the daily rung at a frozen Thursday 09:31 once its T2 wake-up is under way OPENS pb's run of the
  ceremony, the Friday's ring RESUMES it: that run elects `DAILY.md` at its opening and at its resume; fb concludes
  each daily in its ceremony run on `DAILY.md`, its task runs on `TEAM-IDLE.md`; no `door` line anywhere
- (u) the neutral and `do`: `entries: | do -> WORK.md` elects `WORK.md` at T1's opening AND at its resume -- wk
  asks the owner, the reply resumes T1's run --, and at T2's opening, its own run; `team entry <team> --run <key>`
  names a ceremony's wake-up's entry, an opening's found by its tag at `messages.jsonl`, the neutral for an ended
  wake-up and an unknown key -- the journal's bytes unchanged; the team's documents in its directory, none at the
  agent
- (v) an entry missing at an agent that plays it: `entry-missing` naming the agent and the document, exit 2 -- no
  agent born, no journal, no team document laid
"""
from __future__ import annotations

import json
import os
import time

from tests.harness import support

T = support(__file__, "team")

FRIDAY = "2026-10-02T"                                # the next weekday after T.THURSDAY: the daily's second ring


def gone(pid) -> bool:
    """-> whether no process answers at `pid` (a pid never known counts as not gone)."""
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def released(found: list[dict]) -> bool:
    """-> whether every wake-up of the journal has ended AND its launcher has exited: the launcher plays its on-end
    tick after the wake lock goes and exits after it, so no tick of a wake-up is left to come."""
    return T.all_ended(found) and all(gone(one.get("pid")) for one in T.by_kind(found, "wake-launched"))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # (t) fb delegates T1 and T2 to pb, then concludes each; it concludes the daily
        "fb": {"T1": [{"sleep": 0.1, "body": {"do": ["pb"]}},
                      {"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"do": ["pb"]}},
                      {"sleep": 0.1, "body": {"done": "second"}}],
               "T3": [{"sleep": 0.1, "body": {"done": "standup"}}],
               "T4": [{"sleep": 0.1, "body": {"done": "standup again"}}]},
        # (u) wk asks the owner on T1, answers once replied; answers T2
        "wk": {"T1": [{"sleep": 0.1, "body": {"ask": {"to": "house", "text": "which file?"}}},
                      {"sleep": 0.1, "body": {"done": "one"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "two"}}]}})
    by_kind, intents_on, result_of, runs_launched = T.by_kind, T.intents_on, T.result_of, T.runs_launched

    # --- every team declared and started before the first wait: they stand side by side ----------------------
    for one in ("agents/fb", "agents/pb"):
        h.entry_laid(one, "DAILY.md", T.DAILY_DOC)
    h.entry_laid("agents/wk", "WORK.md", T.WORK_DOC)
    for one in ("agents/pk", "agents/fk"):           # a team whose wake-ups the bench forges, never launched
        h.entry_laid(one, "DAILY.md", T.DAILY_DOC)
        h.entry_laid(one, "WORK.md", T.WORK_DOC)
    h.entry_laid("agents/gf", "DAILY.md", T.DAILY_DOC)
    h.declare("beat", "---\nagents: |\n  fb agents/fb\n  pb agents/pb\nreports: |\n  pb -> fb\nroot: fb\n"
                      "ceremonies: |\n  daily every weekday 09:30 with pb -> fb\n"
                      "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nKeep the beat, member by member.\n")
    h.declare("dowork", "---\nagents: |\n  wk agents/wk\nroot: wk\nentries: |\n  do -> WORK.md\n"
                        "schedule: off\n---\nEvery task on WORK.md.\n")
    h.declare("pick", "---\nagents: |\n  fk agents/fk\n  pk agents/pk\nreports: |\n  pk -> fk\nroot: fk\n"
                      "ceremonies: |\n  daily every weekday 09:30 with pk -> fk\n"
                      "entries: |\n  daily -> DAILY.md\n  do -> WORK.md\nschedule: off\n---\nPick.\n")
    h.declare("gap", "---\nagents: |\n  gf agents/gf\n  gp agents/gp\nreports: |\n  gp -> gf\nroot: gf\n"
                     "ceremonies: |\n  daily every weekday 09:30 with gp -> gf\n"
                     "entries: |\n  daily -> DAILY.md\nschedule: off\n---\nA hole.\n")
    # T2 is posted while fb plays T1: the start's tick has woken fb on T1 alone, so pb's first `do` is T1's; the
    # end of each wake-up ticks, and the post's own tick wakes fb when it is free -- either order converges
    beat = h.call("team", "start", "beat", "--message", "first task", *h.harnessed, now="09:10")
    beat2 = h.call("team", "post", "beat", "--message", "second task", now="09:20")
    dowork = h.call("team", "start", "dowork", "--message", "one", *h.harnessed)
    dowork2 = h.call("team", "post", "dowork", "--message", "two")
    pick = h.call("team", "start", "pick", "--message", "x", *h.harnessed, "--no-tick")
    gap = h.call("team", "start", "gap", "--message", "x", *h.harnessed, "--no-tick")

    # --- (v) an entry missing at an agent refuses before anything is written ----------------------------------
    if (gap.returncode == 2 and "entry-missing" in gap.stderr and "agents/gp" in gap.stderr
            and "DAILY.md" in gap.stderr and gap.stdout == ""
            and not h.journal_of("gap").exists() and not h.agent_stands("agents/gp")
            and not (h.meta_of("agents/gf") / "procs" / "TEAM-gap.md").exists()):
        held("(v) an entry missing refuses", "DAILY.md absent at agents/gp: team start gap refuses entry-missing "
             "naming the agent and the document, exit 2; no agent born, no journal, no team document laid")
    else:
        failures.append(f"  ✗ (v) entry missing           rc={gap.returncode} journal={h.journal_of('gap').exists()} "
                        f"born={h.agent_stands('agents/gp')} {gap.stderr[-300:]!r}")

    # --- (u) the neutral and `do`; `team entry` writes nothing ---------------------------------------------
    found_k = h.events("pick")
    last_k = max((one["id"] for one in found_k), default=0)
    with h.journal_of("pick").open("a", encoding="utf-8") as handle:
        for offset, line in enumerate((
                {"kind": "task", "task": "T2", "from": "pick", "to": "fk", "ceremony": "daily", "period": "2026-10-01"},
                {"kind": "wake-intent", "tag": "pick-a", "agent": "pk", "path": "agents/pk", "task": "T2",
                 "run": "aaa111", "index": 2, "messages": []},
                {"kind": "wake-intent", "tag": "pick-b", "agent": "fk", "path": "agents/fk", "task": "T1",
                 "run": None, "index": 1, "messages": []},
                {"kind": "wake-intent", "tag": "pick-c", "agent": "pk", "path": "agents/pk", "task": "T1",
                 "run": "ccc333", "index": 1, "messages": []},
                {"kind": "wake-ended", "tag": "pick-c", "agent": "pk", "run": "ccc333", "index": 1, "cost": 0}), 1):
            handle.write(json.dumps({"at": "2026-10-04T12:00:00+00:00", "id": last_k + offset, "team": "pick",
                                     **line}) + "\n")
    with (h.records / "messages.jsonl").open("a", encoding="utf-8") as handle:   # pick-b's opening, before its event
        handle.write(json.dumps({"at": "2026-10-04T12:00:01+00:00", "from": "house", "to": "agents/fk",
                                 "run": "bbb222", "message": "x", "policy": {}, "tag": "pick-b", "pid": 1}) + "\n")
    before_k = h.journal_of("pick").read_bytes()
    said_k = {key: h.call("team", "entry", "pick", "--run", key) for key in ("aaa111", "bbb222", "ccc333", "ddd444")}
    bare_k = h.call("team", "entry", "pick")
    same_k = h.journal_of("pick").read_bytes() == before_k
    team_doc_k = h.teams / "pick" / "TEAM-pick.md"
    front_k = team_doc_k.read_text(encoding="utf-8") if team_doc_k.is_file() else ""
    laid_k = [(h.teams / "pick" / "TEAM-IDLE.md").is_file(), not (h.teams / "pick" / "TURN.md").exists(),
              not (h.meta_of("agents/pk") / "procs" / "TEAM-pick.md").exists(),
              not (h.meta_of("agents/pk") / "skills" / "team-entry").exists()]
    asks_u = lambda found: [one for one in by_kind(found, "post", verb="ask") if one.get("from") == "wk"
                            and one.get("task") == "T1"]
    asked_u = h.settled("dowork", lambda found: bool(asks_u(found)), timeout=60)
    ask_u = asks_u(h.events("dowork"))[0]["id"] if asked_u else -1
    replied_u = h.call("team", "post", "dowork", "--task", "T1", "--reply", str(ask_u), "--message", "WORK.md")
    two_u = h.settled("dowork", lambda found: bool(by_kind(found, "done", task="T2"))
                      and bool(by_kind(found, "done", task="T1")) and released(found), timeout=90)
    found_u = h.events("dowork")
    launched_u = {one.get("tag"): one.get("run") for one in by_kind(found_u, "wake-launched", agent="wk")}
    on_t1_u, on_t2_u = intents_on(found_u, "wk", "T1"), intents_on(found_u, "wk", "T2")
    key_wk = launched_u.get(on_t1_u[0]["tag"]) if on_t1_u else None       # T1's run: opened, then resumed
    key_wk2 = launched_u.get(on_t2_u[0]["tag"]) if on_t2_u else None      # T2's run: opened
    wk_elected = h.elected("agents/wk", key_wk)
    wk_elected2 = h.elected("agents/wk", key_wk2)
    if (dowork.returncode == 0 and dowork2.returncode == 0 and asked_u and replied_u.returncode == 0 and two_u
            and key_wk and key_wk2 and key_wk != key_wk2 and runs_launched(found_u, "wk") == {key_wk, key_wk2}
            and len(on_t1_u) == 2 and on_t1_u[1].get("run") == key_wk and len(on_t2_u) == 1
            and wk_elected == ["WORK.md", "WORK.md"] and wk_elected2 == ["WORK.md"]
            and pick.returncode == 0
            and {key: (one.returncode, one.stdout) for key, one in said_k.items()}
            == {"aaa111": (0, "DAILY.md\n"), "bbb222": (0, "WORK.md\n"), "ccc333": (0, "TEAM-IDLE.md\n"),
                "ddd444": (0, "TEAM-IDLE.md\n")}
            and bare_k.returncode == 2 and same_k
            and "attach: turn.begin" in front_k and "next: DAILY.md WORK.md TEAM-IDLE.md" in front_k
            and "decide: pp-team entry pick" in front_k and all(laid_k)):
        held("(u) the neutral and do", f"wk's T1 run opened then resumed: {wk_elected}; T2's opened: {wk_elected2}; "
             "team entry pick --run: a ceremony's wake-up DAILY.md, an opening found by its tag WORK.md, an ended "
             "one and an unknown key TEAM-IDLE.md, nothing written; TEAM-pick.md and TEAM-IDLE.md in teams/pick/, "
             "no TURN.md, none at the agent")
    else:
        failures.append(f"  ✗ (u) neutral and do           {dowork.returncode}/{dowork2.returncode}/{pick.returncode} "
                        f"asked={asked_u}/{replied_u.returncode} two={two_u} key={key_wk}/{key_wk2} "
                        f"runs={runs_launched(found_u, 'wk')} t1={[(one['id'], one.get('run')) for one in on_t1_u]} "
                        f"elected={wk_elected}/{wk_elected2} "
                        f"said={ {key: (one.returncode, one.stdout, one.stderr[-120:]) for key, one in said_k.items()} } "
                        f"bare={bare_k.returncode} same={same_k} front={front_k[:200]!r} laid={laid_k}")

    # --- (t) the entry of a run already opened ------------------------------------------------------------
    # the daily rings once pb is woken on T2: its T3 waits for its next wake-up. A tick finding the tick lock held
    # leaves the steps to the holder, whose clock is its own: the 09:31 tick is played again until the task stands.
    def ring_until(task: str, now: str) -> tuple[list, bool]:
        rings, rung = [], False
        deadline = time.monotonic() + 60
        while not rung and time.monotonic() < deadline:
            rings.append(h.call("team", "tick", "beat", now=now))
            rung = bool(by_kind(h.events("beat"), "task", task=task))
            if not rung:
                time.sleep(0.2)
        return rings, rung

    on_t2 = h.settled("beat", lambda found: bool(intents_on(found, "pb", "T2")), timeout=90)
    rings_t, rung_t = ring_until("T3", T.THURSDAY + "09:31") if on_t2 else ([], False)
    daily_t = rung_t and h.settled("beat", lambda found: bool(by_kind(found, "done", task="T3"))
                                   and bool(by_kind(found, "done", task="T2")) and bool(by_kind(found, "done", task="T1"))
                                   and released(found), timeout=90)
    rings_f, rung_f = ring_until("T4", FRIDAY + "09:31") if daily_t else ([], False)   # the daily's next period
    again_t = rung_f and h.settled("beat", lambda found: bool(by_kind(found, "done", task="T4")) and released(found),
                                   timeout=90)
    found_t = h.events("beat")
    tasks_t = {one.get("task"): one for one in by_kind(found_t, "task")}
    runs_t = {member: {task: next((one.get("run") for one in by_kind(found_t, "wake-launched", agent=member)
                                   if one.get("tag") in {i["tag"] for i in intents_on(found_t, member, task)}), None)
                       for task in ("T1", "T2", "T3", "T4")} for member in ("pb", "fb")}
    elected_t = {member: {task: h.elected(f"agents/{member}", key) for task, key in runs_t[member].items()
                          if task in ("T1", "T2", "T3")} for member in ("pb", "fb")}
    pb_on_daily = intents_on(found_t, "pb", "T3") + intents_on(found_t, "pb", "T4")
    doors_t = [one for member in ("pb", "fb") for key in set(runs_t[member].values())
               for one in h.doors_in(f"agents/{member}", key)]
    fb_task_runs = elected_t["fb"]["T1"] + elected_t["fb"]["T2"]
    if (beat.returncode == 0 and beat2.returncode == 0 and on_t2 and rung_t and rung_f
            and all(one.returncode == 0 for one in rings_t + rings_f) and daily_t and again_t
            and tasks_t["T3"].get("ceremony") == tasks_t["T4"].get("ceremony") == "daily"
            and [tasks_t["T3"].get("period"), tasks_t["T4"].get("period")] == ["2026-10-01", "2026-10-02"]
            and all(runs_t[member].values() for member in ("pb", "fb"))
            and len(set(runs_t["pb"].values()) - {None}) == 3 and runs_t["pb"]["T3"] == runs_t["pb"]["T4"]
            and runs_t["fb"]["T3"] == runs_t["fb"]["T4"] and len(set(runs_t["fb"].values()) - {None}) == 3
            and [one.get("run") for one in pb_on_daily] == [None, runs_t["pb"]["T3"]]
            and elected_t["pb"]["T1"] == ["TEAM-IDLE.md"] and elected_t["pb"]["T2"] == ["TEAM-IDLE.md"]
            and elected_t["pb"]["T3"] == ["DAILY.md", "DAILY.md"]
            and elected_t["fb"]["T3"] == ["DAILY.md", "DAILY.md"]
            and fb_task_runs and set(fb_task_runs) == {"TEAM-IDLE.md"}
            and doors_t == []
            and result_of(found_t, "T3") == "standup" and result_of(found_t, "T4") == "standup again"):
        held("(t) the entry of a run already opened", f"pb's T1 and T2 runs elect {elected_t['pb']['T1']} and "
             f"{elected_t['pb']['T2']}; Thursday's daily opens its ceremony run {runs_t['pb']['T3']}, Friday's "
             f"resumes it: {elected_t['pb']['T3']}; fb concludes both dailies in its ceremony run "
             f"{elected_t['fb']['T3']}, its task runs on TEAM-IDLE.md; no door")
    else:
        failures.append(f"  ✗ (t) entry on a resume       {beat.returncode}/{beat2.returncode}/"
                        f"{[one.returncode for one in rings_t + rings_f]} on_t2={on_t2} rung={rung_t}/{rung_f} "
                        f"daily={daily_t}/{again_t} runs={runs_t} "
                        f"on_daily={[(one['id'], one.get('task'), one.get('run')) for one in pb_on_daily]} "
                        f"elected={elected_t} doors={doors_t} "
                        f"periods={[(k, v.get('ceremony'), v.get('period')) for k, v in tasks_t.items()]} "
                        f"{beat.stderr[-200:]!r} {(rings_t[-1].stderr[-200:] if rings_t else '')!r}")
    return 0
