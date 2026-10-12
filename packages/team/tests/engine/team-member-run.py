"""Scenario `team-member-run` -- 3 case(s) (batch le-tick, rework: the members, team 0.13.1; split
out of `team-review` by les-scenarios-par-maison, 2026-10-07): a member holds ONE run, ONE key and
ONE session for the team's whole work, and its tasks arrive in that run; each case names the
invariant of `team-sim-reframe.py` or `team-sim-members.py` it replays.
- (n) one run per member [47] (I18): nm's T2 arrives in the run of its T1 (`--run`), one session at
  `sessions.jsonl`; `status` says `nm · agents/nm · inbox 0 · run <key> · ended · on T1 T2`
- (p) an unreadable answer keeps its run [56] (I18): ur's opening answers a `do` off the edges --
  `wake-failed response-unreadable` carrying its run; the retry resumes that key, one session
- (s) the kill spares a wake-up that has answered [58] (I16, I12): sa and sb answered by (run, index),
  both still releasing their wake locks: `stop --kill` spares both (their launchers alive, no
  `wake-killed`), the tick ends each `wake-ended` with its cost
"""
from __future__ import annotations

import json
import subprocess
import sys
import time

from tests.harness import holding, support

T = support(__file__, "team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        "nm": {"T1": [{"sleep": 0.1, "body": {"done": "first"}}],
               "T2": [{"sleep": 0.1, "body": {"done": "second"}}]},
        "ur": [{"sleep": 0.1, "body": {"do": ["ux"]}},
               {"sleep": 0.1, "body": {"done": "read at last"}}]})
    by_kind, all_ended, intents_on, result_of, runs_launched = (
        T.by_kind, T.all_ended, T.intents_on, T.result_of, T.runs_launched)

    # --- (n) one run per member [47] -- I18 ------------------------------------------------------------
    h.declare("one", "---\nagents: |\n  nm agents/nm\nroot: nm\nschedule: off\n---\nOne member, two tasks.\n")
    one_t = h.call("team", "start", "one", "--message", "first task", *h.harnessed)
    first_n = h.settled("one", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    time.sleep(0.5)                                   # the on-end tick has left
    two_t = h.call("team", "post", "one", "--to", "nm", "--message", "second task")
    second_n = h.settled("one", lambda found: bool(by_kind(found, "done", task="T2")) and all_ended(found), timeout=60)
    found_nm = h.events("one")
    key_nm = next((one.get("run") for one in by_kind(found_nm, "wake-ended", agent="nm")), "")
    on_t2 = intents_on(found_nm, "nm", "T2")
    line_nm = h.status_line("one", "nm · ")
    if (one_t.returncode == 0 and first_n and two_t.returncode == 0 and second_n and key_nm
            and len(on_t2) == 1 and on_t2[0].get("run") == key_nm and runs_launched(found_nm, "nm") == {key_nm}
            and len({session for _, session in h.sessions_at("agents/nm")}) == 1
            and line_nm == f"nm · agents/nm · inbox 0 · run {key_nm} · ended · on T1 T2"
            and result_of(found_nm, "T2") == "second"):
        held("(n) one run per member", f"nm's T2 arrives in its run {key_nm} (--run): one key, one session at "
             f"sessions.jsonl; status says {line_nm!r} -- I18")
    else:
        failures.append(f"  ✗ (n) one run per member      {one_t.returncode}/{two_t.returncode} first={first_n} "
                        f"second={second_n} key={key_nm} t2={[(one['id'], one.get('run')) for one in on_t2]} "
                        f"runs={runs_launched(found_nm, 'nm')} sessions={h.sessions_at('agents/nm')} line={line_nm!r}")

    # --- (p) an unreadable answer keeps its run [56] -- I18 ----------------------------------------------
    h.declare("stray", "---\nagents: |\n  ur agents/ur\n  ux agents/ux\nreports: |\n  ur -> ux\nroot: ur\n"
                       "retries: 1\nschedule: off\n---\nAn answer off the edges.\n")
    stray = h.call("team", "start", "stray", "--message", "read it", *h.harnessed)
    done_p = h.settled("stray", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_s = h.events("stray")
    failed_s = by_kind(found_s, "wake-failed", agent="ur")
    intents_s = by_kind(found_s, "wake-intent", agent="ur")
    key_s = next((one.get("run") for one in by_kind(found_s, "wake-launched", agent="ur")), "")
    if (stray.returncode == 0 and done_p and len(failed_s) == 1
            and str(failed_s[0].get("reason")).startswith("response-unreadable") and failed_s[0].get("run") == key_s
            and len(intents_s) == 2 and intents_s[1].get("run") == key_s and runs_launched(found_s, "ur") == {key_s}
            and len({session for _, session in h.sessions_at("agents/ur")}) == 1
            and result_of(found_s, "T1") == "read at last"):
        held("(p) an unreadable answer keeps its run", f"ur's opening answers a do off the edges: wake-failed "
             f"response-unreadable with its run {key_s}; the retry resumes that key, one session; T1 done -- I18")
    else:
        failures.append(f"  ✗ (p) unreadable keeps its run {stray.returncode} done={done_p} "
                        f"failed={[(one.get('reason'), one.get('run')) for one in failed_s]} "
                        f"intents={[(one['id'], one.get('run')) for one in intents_s]} key={key_s} "
                        f"sessions={h.sessions_at('agents/ur')}")

    # --- (s) the kill spares a wake-up that has answered [58] -- I16, I12 ------------------------------
    h.declare("spare", "---\nagents: |\n  sa agents/sa\n  sb agents/sb\nreports: |\n  sb -> sa\nroot: sa\n"
                       "retries: 0\nschedule: off\n---\nAnswered, still releasing.\n")
    spare = h.call("team", "start", "spare", "--message", "answer it", *h.harnessed, "--no-tick")
    noted = h.call("team", "post", "spare", "--task", "T1", "--to", "sb", "--message", "look too", "--no-tick")
    found_s = h.events("spare")
    do_s = next(one["id"] for one in by_kind(found_s, "post", verb="do"))
    note_s = next(one["id"] for one in by_kind(found_s, "post", verb="note"))
    sleepers = {member: subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
                for member in ("sa", "sb")}     # each a launcher's process group, as `ended_now` aims at
    last_s = max(one["id"] for one in found_s)
    with h.journal_of("spare").open("a", encoding="utf-8") as handle:   # two wake-ups launched on T1
        for offset, line in enumerate((
                {"kind": "wake-intent", "tag": "spare-sa", "agent": "sa", "path": "agents/sa", "task": "T1",
                 "run": None, "index": 1, "messages": [do_s]},
                {"kind": "wake-launched", "tag": "spare-sa", "agent": "sa", "run": "aaa111", "pid": sleepers["sa"].pid},
                {"kind": "wake-intent", "tag": "spare-sb", "agent": "sb", "path": "agents/sb", "task": "T1",
                 "run": None, "index": 1, "messages": [note_s]},
                {"kind": "wake-launched", "tag": "spare-sb", "agent": "sb", "run": "bbb222", "pid": sleepers["sb"].pid}), 1):
            handle.write(json.dumps({"at": "2026-10-04T12:00:00+00:00", "id": last_s + offset, "team": "spare",
                                     **line}) + "\n")
    with (h.records / "responses.jsonl").open("a", encoding="utf-8") as handle:   # both answered
        for line in ({"agent": "agents/sa", "run": "aaa111", "index": 1, "cost_usd": 0.20},
                     {"agent": "agents/sb", "run": "bbb222", "index": 1, "cost_usd": 0.30}):
            handle.write(json.dumps({"at": "2026-10-04T12:00:05+00:00", **line, "response": '{"done": true}',
                                     "denials": [], "error": None, "harness_rc": 0}) + "\n")
    state_sa = h.meta_of("agents/sa") / ".sys" / "state"
    state_sb = h.meta_of("agents/sb") / ".sys" / "state"
    with holding(state_sa / "session-aaa111.wake.lock"), holding(state_sb / "session-bbb222.wake.lock"):
        killed_s = h.call("team", "stop", "spare", "--task", "T1", "--kill", "--no-tick")
        time.sleep(0.3)
        alive_s = {member: popen.poll() is None for member, popen in sleepers.items()}
        ticked_s = h.call("team", "tick", "spare")
    for popen in sleepers.values():
        if popen.poll() is None:
            popen.kill()
        popen.wait()
    found_s = h.events("spare")
    ends_s = {one.get("agent"): ("ended", None, one.get("cost")) for one in by_kind(found_s, "wake-ended")}
    ends_s.update({one.get("agent"): ("failed", (one.get("final"), str(one.get("reason"))), one.get("cost"))
                   for one in by_kind(found_s, "wake-failed")})
    cost_s = h.status_line("spare", "cost")
    if (spare.returncode == 0 and noted.returncode == 0 and killed_s.returncode == 0 and ticked_s.returncode == 0
            and not by_kind(found_s, "wake-killed") and alive_s == {"sa": True, "sb": True}
            and killed_s.stdout.count("spared -- the reap ends it") == 2 and "nothing to kill" in killed_s.stdout
            and by_kind(found_s, "stopped", task="T1")
            and ends_s == {"sa": ("ended", None, 0.2), "sb": ("ended", None, 0.3)}
            and cost_s == "cost 0.50 USD"):
        held("(s) the kill spares a wake-up that has answered", "sa and sb answered by (run, index), both still "
             "releasing their wake locks: stop --kill spares both (their launchers alive, no wake-killed), the tick "
             "ends each wake-ended with its cost; cost 0.50 USD -- I16")
    else:
        failures.append(f"  ✗ (s) the kill spares          {spare.returncode}/{noted.returncode}/{killed_s.returncode}/"
                        f"{ticked_s.returncode} alive={alive_s} killed={by_kind(found_s, 'wake-killed')} ends={ends_s} "
                        f"{cost_s!r} {killed_s.stdout[-300:]!r} {killed_s.stderr[-200:]!r}")
    return 0
