"""Scenario `team-kill` -- 5 case(s): the end of a wake-up under way -- killed by the owner's `stop --kill`, killed
by the tick past the team's `timeout:`, or spared because it has answered. Six teams run side by side in one house,
each under its own names; each case waits for its team, then reads its journal, its face and the processes.
- a stop --kill kills: k delegates to k1, which sleeps; `team stop kill --task T1 --kill` ends k1's launcher and its
  witness (their pids gone), writes `wake-killed` with the launch's tag, run and pid; no response of k1 at the
  house's record, no retry, k not woken for its stop; the face says k1's run `killed`
- (q) the kill beside another task: km plays T2 in its run while it holds T1; `stop --kill --task T2` ends that
  wake-up alone; kd's answer on T1 resumes km's same key and session, T1 done
- a stuck wake-up is freed: under `timeout: 2`, a witness asleep past the bound is killed by a tick
  (`wake-failed wake-timeout`, its pid gone), the retry resolves the task; under `retries: 0` the first timeout is
  final and the tick answers the delegate's `do` in its place, which wakes its parent
- (k) a kept answer is never killed: under `timeout: 1`, a wake-up launched long ago whose answer is kept on its
  run, its wake lock held: the tick writes `wake-ended` with its cost, never `wake-timeout`
- (s) the kill spares a wake-up that has answered: sa and sb answered by (run, index), both still releasing their
  wake locks: `stop --kill` spares both (their launchers alive, no `wake-killed`), the tick ends each `wake-ended`
  with its cost
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from tests.harness import holding, support

T = support(__file__, "team")


def until(predicate, timeout: float = 30.0) -> bool:
    """Polls `predicate` until it holds; False past the bound."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.1)
    return bool(predicate())


def gone(pid) -> bool:
    """-> whether no process answers at `pid` (a pid never known counts as not gone)."""
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    return False


def witnesses_at(h, path: str) -> list[str]:
    """-> the pids of the house's witnesses alive whose working directory is the member's home `path`."""
    home = h.ws.joinpath(*path.split("/")).resolve()
    found = []
    for pid in T.witness_alive(h).split():
        try:
            if Path(f"/proc/{pid}/cwd").resolve() == home:
                found.append(pid)
        except OSError:
            pass
    return found


def survives(popen: subprocess.Popen, grace: float = 0.3) -> bool:
    """-> whether the process is still alive after `grace` seconds (ends early when it dies)."""
    try:
        popen.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        return True
    return False


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={
        # a stop --kill kills: k1 sleeps long past the kill
        "k": [{"sleep": 0.2, "body": {"do": ["k1"]}}, {"sleep": 0.1, "body": {"done": "stopped"}}],
        "k1": [{"sleep": 30.0, "body": {"done": True}}],
        # (q) km holds T1 on kd while it plays T2
        "km": {"T1": [{"sleep": 0.1, "body": {"do": ["kd"]}},
                      {"sleep": 0.1, "body": {"done": "after the kill"}}],
               "T2": [{"sleep": 30.0, "body": {"done": "never"}}]},
        "kd": [{"sleep": 10.0, "body": {"done": True}}],
        # a stuck wake-up: x1 asleep past the bound, sane at its retry; x01 asleep, no retry
        "x": [{"sleep": 0.1, "body": {"do": ["x1"]}},
              {"sleep": 0.1, "body": {"done": "freed"}}],
        "x1": [{"sleep": 30, "body": {"done": True}},
               {"sleep": 0.1, "body": {"done": True}}],
        "x0": [{"sleep": 0.1, "body": {"do": ["x01"]}},
               {"sleep": 0.1, "body": {"done": "gave up"}}],
        "x01": [{"sleep": 30, "body": {"done": True}}]})
    by_kind, lines, all_ended, result_of, runs_launched = T.by_kind, T.lines, T.all_ended, T.result_of, T.runs_launched

    # --- every team declared and started before the first wait: they run side by side ----------------------
    h.declare("kill", "---\nagents: |\n  k k\n  k1 k1\nreports: |\n  k1 -> k\nroot: k\n---\nKill on demand.\n")
    h.declare("beside", "---\nagents: |\n  km agents/km\n  kd agents/kd\nreports: |\n  kd -> km\nroot: km\n"
                        "schedule: off\n---\nA kill beside.\n")
    h.declare("stuck", "---\nagents: |\n  x x\n  x1 x1\nreports: |\n  x1 -> x\nroot: x\ntimeout: 2\n---\nFree the stuck.\n")
    h.declare("stuck0", "---\nagents: |\n  x0 x0\n  x01 x01\nreports: |\n  x01 -> x0\nroot: x0\ntimeout: 2\nretries: 0\n"
                        "---\nGive up fast.\n")
    h.declare("late", "---\nagents: |\n  kx kx\nroot: kx\ntimeout: 1\nretries: 0\nschedule: off\n---\nAnswer late.\n")
    h.declare("spare", "---\nagents: |\n  sa agents/sa\n  sb agents/sb\nreports: |\n  sb -> sa\nroot: sa\n"
                       "retries: 0\nschedule: off\n---\nAnswered, still releasing.\n")
    killing = h.call("team", "start", "kill", "--message", "review very slowly", *h.harnessed)
    # km's T2 stands before the first tick: the tick that ends km's T1 opening launches kd on T1 and km on T2
    # together, so kd's answer comes after the kill
    beside = h.call("team", "start", "beside", "--message", "delegate it", *h.harnessed, "--no-tick")
    beside2 = h.call("team", "post", "beside", "--to", "km", "--message", "a long one", "--no-tick")
    opening_q = h.call("team", "tick", "beside").returncode == 0
    stuck = h.call("team", "start", "stuck", "--message", "review slowly", *h.harnessed)
    stuck0 = h.call("team", "start", "stuck0", "--message", "review slowly", *h.harnessed)
    late = h.call("team", "start", "late", "--message", "do it", *h.harnessed, "--no-tick")
    spare = h.call("team", "start", "spare", "--message", "answer it", *h.harnessed, "--no-tick")
    noted = h.call("team", "post", "spare", "--task", "T1", "--to", "sb", "--message", "look too", "--no-tick")

    # --- a stop --kill kills: the pids gone, nothing kept, no retry -----------------------------------------
    running_k = h.settled("kill", lambda found: bool(by_kind(found, "wake-launched", agent="k1")), timeout=60)
    launch_k = next(iter(by_kind(h.events("kill"), "wake-launched", agent="k1")), {})
    asleep_k = until(lambda: bool(witnesses_at(h, "k1")), timeout=30)          # k1's witness asleep
    killed_k = h.call("team", "stop", "kill", "--task", "T1", "--kill")
    ended_k = until(lambda: bool(by_kind(h.events("kill"), "wake-killed")) and all_ended(h.events("kill"))
                    and gone(launch_k.get("pid")) and not witnesses_at(h, "k1"), timeout=30)
    found = h.events("kill")
    killed_events = by_kind(found, "wake-killed")
    answers_k1 = [one for one in lines(h.records / "responses.jsonl") if one.get("agent") == "k1"]
    face_k1 = next((one for one in h.face("kill").get("members") or [] if one.get("member") == "k1"), {})
    if (killing.returncode == 0 and running_k and asleep_k and killed_k.returncode == 0 and ended_k
            and len(killed_events) == 1 and killed_events[0].get("agent") == "k1"
            and killed_events[0].get("pid") == launch_k.get("pid") and killed_events[0].get("run") == launch_k.get("run")
            and killed_events[0].get("tag") == launch_k.get("tag")
            and answers_k1 == [] and len(by_kind(found, "wake-intent", agent="k1")) == 1
            and not by_kind(found, "wake-failed") and len(by_kind(found, "wake-intent", agent="k")) == 1
            and face_k1.get("how") == "killed" and face_k1.get("run") == launch_k.get("run")):
        held("a stop --kill kills", f"pid {launch_k.get('pid')} and k1's witness gone, wake-killed "
             f"{killed_events[0].get('tag')}, no response of k1 at the record, no retry; k not woken for its stop; "
             f"the face: k1's run {face_k1.get('run')} {face_k1.get('how')}")
    else:
        failures.append(f"  ✗ kill                        {killing.returncode}/{killed_k.returncode} running={running_k} "
                        f"asleep={asleep_k} ended={ended_k} killed={killed_events} launch={launch_k} "
                        f"answers={len(answers_k1)} k1={face_k1} witnesses={witnesses_at(h, 'k1')} "
                        f"{killed_k.stdout[-200:]!r} {killed_k.stderr[-200:]!r}")

    # --- (q) the kill beside another task ----------------------------------------------------------------
    out_q = h.settled("beside", lambda found: bool(by_kind(found, "wake-launched", agent="kd")), timeout=60)
    plays_t2 = h.settled("beside", lambda found: any(one.get("task") == "T2" and one["tag"] in
                                                      {l.get("tag") for l in by_kind(found, "wake-launched", agent="km")}
                                                      for one in by_kind(found, "wake-intent", agent="km")), timeout=60)
    asleep_q = until(lambda: (h.out / "km@T2.count").is_file(), timeout=30)   # km's witness asleep on T2
    killed_q = h.call("team", "stop", "beside", "--task", "T2", "--kill")
    done_q = h.settled("beside", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    found_q = h.events("beside")
    kills_q = by_kind(found_q, "wake-killed")
    key_q = next((one.get("run") for one in by_kind(found_q, "wake-ended", agent="km")), "")
    after_kill = [one for one in by_kind(found_q, "wake-intent", agent="km") if kills_q and one["id"] > kills_q[0]["id"]]
    if (beside.returncode == 0 and opening_q and out_q and beside2.returncode == 0 and plays_t2 and asleep_q
            and killed_q.returncode == 0 and done_q and len(kills_q) == 1 and kills_q[0].get("agent") == "km"
            and kills_q[0].get("task") == "T2"
            and kills_q[0].get("run") == key_q and runs_launched(found_q, "km") == {key_q}
            and len(after_kill) == 1 and after_kill[0].get("task") == "T1" and after_kill[0].get("run") == key_q
            and len({session for _, session in h.sessions_at("agents/km")}) == 1
            and by_kind(found_q, "stopped", task="T2") and result_of(found_q, "T1") == "after the kill"):
        held("(q) the kill beside another task", f"km plays T2 in its run {key_q} while it holds T1: stop --kill "
             "T2 ends that wake-up alone (wake-killed on T2); kd's answer on T1 resumes km's same key and session, "
             "T1 done")
    else:
        failures.append(f"  ✗ (q) the kill beside         {beside.returncode}/{beside2.returncode}/{killed_q.returncode} "
                        f"out={out_q} plays={plays_t2} asleep={asleep_q} done={done_q} "
                        f"kills={[(one.get('agent'), one.get('task'), one.get('run')) for one in kills_q]} "
                        f"key={key_q} runs={runs_launched(found_q, 'km')} "
                        f"after={[(one['task'], one.get('run')) for one in after_kill]} "
                        f"sessions={h.sessions_at('agents/km')} {killed_q.stdout[-200:]!r} {killed_q.stderr[-200:]!r} "
                        f"journal={[(one['id'], one['kind'], one.get('agent') or one.get('from'), one.get('task'), one.get('messages')) for one in found_q if one['kind'] not in ('wake-launched',)]}")

    # --- a stuck wake-up is freed ------------------------------------------------------------------------
    running_x = h.settled("stuck", lambda found: bool(by_kind(found, "wake-launched", agent="x1")), timeout=60)
    launch_x1 = next(iter(by_kind(h.events("stuck"), "wake-launched", agent="x1")), {})
    running_x0 = h.settled("stuck0", lambda found: bool(by_kind(found, "wake-launched", agent="x01")), timeout=60)
    h.tick_until("stuck", lambda found: bool(by_kind(found, "wake-failed", agent="x1")), timeout=30)
    h.tick_until("stuck0", lambda found: bool(by_kind(found, "wake-failed", agent="x01")), timeout=30)
    done_x = h.settled("stuck", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    final_x0 = h.settled("stuck0", lambda found: bool(by_kind(found, "done", task="T1")) and all_ended(found), timeout=60)
    gone_x1 = until(lambda: gone(launch_x1.get("pid")), timeout=10)
    found_x = h.events("stuck")
    found_x0 = h.events("stuck0")
    timeouts = [(one.get("final"), one.get("reason")) for one in by_kind(found_x, "wake-failed", agent="x1")]
    timeouts0 = [(one.get("final"), one.get("reason")) for one in by_kind(found_x0, "wake-failed", agent="x01")]
    esc_x0 = [one for one in by_kind(found_x0, "post", verb="re") if one.get("to") == "x0" and one.get("by") == "tick"]
    if (stuck.returncode == 0 and stuck0.returncode == 0 and running_x and running_x0 and done_x and final_x0
            and timeouts == [(False, "wake-timeout")] and gone_x1
            and len(by_kind(found_x, "wake-intent", agent="x1")) == 2
            and result_of(found_x, "T1") == "freed"
            and timeouts0 == [(True, "wake-timeout")] and len(esc_x0) == 1
            and len(by_kind(found_x0, "wake-intent", agent="x01")) == 1):
        held("a stuck wake-up is freed", f"timeout 2: x1 killed by a tick past the bound (pid {launch_x1.get('pid')} "
             "gone), wake-failed wake-timeout, the retry resolves T1 (freed); retries 0: the first timeout is "
             "final, the tick answers x0's do in x01's place (gave up)")
    else:
        failures.append(f"  ✗ wake-timeout                {stuck.returncode}/{stuck0.returncode} run={running_x}/{running_x0} "
                        f"done={done_x}/{final_x0} t={timeouts} t0={timeouts0} gone={gone_x1} "
                        f"esc={len(esc_x0)} intents={len(by_kind(found_x, 'wake-intent', agent='x1'))}")

    # --- (k) a kept answer is never killed ---------------------------------------------------------------
    found_k = h.events("late")
    last_k = max(one["id"] for one in found_k)
    do_k = next(one["id"] for one in by_kind(found_k, "post", verb="do"))
    with h.journal_of("late").open("a", encoding="utf-8") as handle:   # a wake-up launched long ago
        for offset, line in enumerate((
                {"kind": "wake-intent", "tag": "late-kx", "agent": "kx", "task": "T1", "run": None, "index": 1,
                 "messages": [do_k]},
                {"kind": "wake-launched", "tag": "late-kx", "agent": "kx", "run": "abc123", "pid": None}), 1):
            handle.write(json.dumps({"at": "2026-10-03T12:00:00+00:00", "id": last_k + offset, "team": "late",
                                     **line}) + "\n")
    with (h.records / "responses.jsonl").open("a", encoding="utf-8") as handle:   # its answer, kept on its run
        handle.write(json.dumps({"at": "2026-10-03T12:00:05+00:00", "agent": "kx", "run": "abc123",
                                 "index": 1, "response": json.dumps({"re": do_k, "text": "late"}), "cost_usd": 0.25,
                                 "denials": [], "error": None, "harness_rc": 0}) + "\n")
    with holding(h.meta_of("kx") / ".sys" / "state" / "session-abc123.wake.lock"):   # still releasing
        ticked_k = h.call("team", "tick", "late")
    found_k = h.events("late")
    fails_k = [(one.get("final"), str(one.get("reason")), one.get("cost")) for one in by_kind(found_k, "wake-failed")]
    ends_k = [one.get("cost") for one in by_kind(found_k, "wake-ended", tag="late-kx")]
    face_k = h.face("late")
    if (late.returncode == 0 and ticked_k.returncode == 0
            and fails_k == [] and ends_k == [0.25]
            and face_k.get("cost") == 0.25):
        held("(k) a kept answer is never killed", "kx's answer kept on its run, its wake lock held past "
             "timeout 1: wake-ended with its cost 0.25, no wake-timeout")
    else:
        failures.append(f"  ✗ (k) the answer first       {late.returncode}/{ticked_k.returncode} fails={fails_k} ends={ends_k} "
                        f"cost={face_k.get('cost')!r} {ticked_k.stderr[-200:]!r}")

    # --- (s) the kill spares a wake-up that has answered -------------------------------------------------
    found_s = h.events("spare")
    do_s = next(one["id"] for one in by_kind(found_s, "post", verb="do"))
    note_s = next(one["id"] for one in by_kind(found_s, "post", verb="note"))
    sleepers = {member: subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
                for member in ("sa", "sb")}     # each a launcher's process group, as the kill aims at
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
        killed_seen = by_kind(h.events("spare"), "wake-killed")
        alive_s = {member: survives(popen) for member, popen in sleepers.items()}
        ticked_s = h.call("team", "tick", "spare")
    for popen in sleepers.values():
        if popen.poll() is None:
            popen.kill()
        popen.wait()
    found_s = h.events("spare")
    ends_s = {one.get("agent"): ("ended", None, one.get("cost")) for one in by_kind(found_s, "wake-ended")}
    ends_s.update({one.get("agent"): ("failed", (one.get("final"), str(one.get("reason"))), one.get("cost"))
                   for one in by_kind(found_s, "wake-failed")})
    face_s = h.face("spare")
    if (spare.returncode == 0 and noted.returncode == 0 and killed_s.returncode == 0 and ticked_s.returncode == 0
            and killed_seen == [] and not by_kind(found_s, "wake-killed") and alive_s == {"sa": True, "sb": True}
            and by_kind(found_s, "stopped", task="T1")
            and ends_s == {"sa": ("ended", None, 0.2), "sb": ("ended", None, 0.3)}
            and face_s.get("cost") == 0.5):
        held("(s) the kill spares a wake-up that has answered", "sa and sb answered by (run, index), both still "
             "releasing their wake locks: stop --kill spares both (their launchers alive, no wake-killed), the tick "
             "ends each wake-ended with its cost; the face's cost 0.5")
    else:
        failures.append(f"  ✗ (s) the kill spares          {spare.returncode}/{noted.returncode}/{killed_s.returncode}/"
                        f"{ticked_s.returncode} alive={alive_s} killed={by_kind(found_s, 'wake-killed')} ends={ends_s} "
                        f"cost={face_s.get('cost')!r} {killed_s.stdout[-300:]!r} {killed_s.stderr[-200:]!r}")
    return 0
