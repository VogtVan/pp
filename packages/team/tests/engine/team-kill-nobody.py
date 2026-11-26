"""Scenario `team-kill-nobody` -- 2 case(s) (lot le-filet-complete: split beside `team-kill` and
`team-stop-wakes-nobody`, both past their target alone): the end of a wake-up that has NO process to kill -- not
launched yet, its launcher gone already, a launch that kept no pid, a launcher born in another process space. Two
teams in one house, `schedule: off`, each journal's wake-ups written by the bench while the team rests.
- (a) a stop --kill that kills nobody: on T1, n1's intent without any launch and n2's launch whose pid names a process
  group gone already -- `team stop --task T1 --kill` writes `stopped` and no `wake-killed`; the next tick reaps both on
  the stopped task, each FINAL at once -- n1's `launch-missing` too, which is never final on a task that runs --, no
  `wake-halted`
- (b) the tick's timeout kills nobody: under `timeout: 1`, s1's launch kept no pid and s2's was born in another process
  space (its pid a live process of the bench's), both begun long ago, their wake locks held by the bench, no end at
  their flows -- the tick fails both `wake-timeout` and the bench's process lives on
"""
from __future__ import annotations

import json
import subprocess
import sys
from contextlib import ExitStack

from tests.harness import holding, support

T = support(__file__, "team")


def appended(h, name: str, events: list[dict]) -> None:
    """Events appended to the team's journal by the bench, numbered after its last, stamped long ago."""
    last = max((int(one.get("id") or 0) for one in h.events(name)), default=0)
    with h.journal_of(name).open("a", encoding="utf-8") as handle:
        for offset, one in enumerate(events, 1):
            handle.write(json.dumps({"at": "2026-10-03T12:00:00+00:00", "id": last + offset, "team": name, **one}) + "\n")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    quick = [{"sleep": 0.1, "body": {"done": True}}]
    h = T.House(bench, script={"n1": quick, "n2": quick, "s1": quick, "s2": quick})
    by_kind = T.by_kind

    # --- (a) a stop --kill that kills nobody -----------------------------------------------------------------------
    h.declare("nobody", "---\nagents: |\n  n1 agents/n1\n  n2 agents/n2\nreports: |\n  n2 -> n1\nroot: n1\n"
                        "schedule: off\n---\nNothing to kill.\n")
    begun = h.call("team", "start", "nobody", "--message", "hold on", *h.harnessed, "--no-tick")
    gone = subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True)   # a launcher's group, ended
    gone.wait()
    opening = next((one["id"] for one in by_kind(h.events("nobody"), "post", verb="do")), 0)
    appended(h, "nobody", [
        {"kind": "wake-intent", "tag": "n1-T1-aaaaaa", "agent": "n1", "path": "agents/n1", "task": "T1", "run": None,
         "messages": [opening]},                                               # not launched yet
        {"kind": "wake-intent", "tag": "n2-T1-bbbbbb", "agent": "n2", "path": "agents/n2", "task": "T1", "run": None,
         "messages": []},
        {"kind": "wake-launched", "tag": "n2-T1-bbbbbb", "agent": "n2", "run": "b0b0b0", "pid": gone.pid, "launch": 1}])
    stopped = h.call("team", "stop", "nobody", "--task", "T1", "--kill", "--no-tick")
    after_stop = h.events("nobody")
    ticked = h.call("team", "tick", "nobody")
    found = h.events("nobody")
    fails = {one.get("agent"): (one.get("final"), one.get("reason")) for one in by_kind(found, "wake-failed")}
    if (begun.returncode == 0 and opening and stopped.returncode == 0 and ticked.returncode == 0
            and by_kind(after_stop, "stopped", task="T1") and not by_kind(found, "wake-killed")
            and fails == {"n1": (True, "launch-missing"), "n2": (True, "wake-dead")}
            and not by_kind(found, "wake-halted")):
        held("(a) a stop --kill kills nobody", "n1 not launched yet, n2's group gone already: stopped, no wake-killed; "
             "the tick reaps both final on the stopped task -- launch-missing final too --, no wake-halted")
    else:
        failures.append(f"  ✗ (a) kills nobody           rc={begun.returncode}/{stopped.returncode}/{ticked.returncode} "
                        f"opening={opening} stopped={bool(by_kind(after_stop, 'stopped', task='T1'))} "
                        f"killed={by_kind(found, 'wake-killed')} fails={fails} halted={by_kind(found, 'wake-halted')} "
                        f"{stopped.stderr[-200:]!r} {ticked.stderr[-200:]!r}")

    # --- (b) the tick's timeout kills nobody ---------------------------------------------------------------------
    h.declare("stuck", "---\nagents: |\n  s1 agents/s1\n  s2 agents/s2\nreports: |\n  s2 -> s1\nroot: s1\ntimeout: 1\n"
                       "retries: 0\nschedule: off\n---\nStuck without a pid.\n")
    begun_b = h.call("team", "start", "stuck", "--message", "hold on", *h.harnessed, "--no-tick")
    opening_b = next((one["id"] for one in by_kind(h.events("stuck"), "post", verb="do")), 0)
    sleeper = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"], start_new_session=True)
    appended(h, "stuck", [
        {"kind": "wake-intent", "tag": "s1-T1-cccccc", "agent": "s1", "path": "agents/s1", "task": "T1", "run": None,
         "messages": [opening_b]},
        {"kind": "wake-launched", "tag": "s1-T1-cccccc", "agent": "s1", "run": "c1c1c1", "pid": None, "launch": 1},
        {"kind": "wake-intent", "tag": "s2-T1-dddddd", "agent": "s2", "path": "agents/s2", "task": "T1", "run": None,
         "messages": []},
        {"kind": "wake-launched", "tag": "s2-T1-dddddd", "agent": "s2", "run": "d2d2d2", "pid": sleeper.pid,
         "launch": 1, "space": "pid:[1]"}])                                    # another process space than the tick's
    try:
        with ExitStack() as locks:                                             # both launches still hold their runs
            for path, run in (("agents/s1", "c1c1c1"), ("agents/s2", "d2d2d2")):
                state = h.meta_of(path) / ".sys" / "state"
                state.mkdir(parents=True, exist_ok=True)
                locks.enter_context(holding(state / f"session-{run}.wake.lock"))
            ticked_b = h.call("team", "tick", "stuck")
            alive = sleeper.poll() is None
    finally:
        if sleeper.poll() is None:
            sleeper.kill()
        sleeper.wait()
    found_b = h.events("stuck")
    fails_b = {one.get("agent"): one.get("reason") for one in by_kind(found_b, "wake-failed")}
    if (begun_b.returncode == 0 and opening_b and ticked_b.returncode == 0 and alive
            and fails_b == {"s1": "wake-timeout", "s2": "wake-timeout"} and not by_kind(found_b, "wake-killed")):
        held("(b) the tick's timeout kills nobody", "s1's launch without a pid and s2's of another space, held past "
             "timeout 1: both wake-failed wake-timeout, the bench's process alive")
    else:
        failures.append(f"  ✗ (b) timeout kills nobody   rc={begun_b.returncode}/{ticked_b.returncode} alive={alive} "
                        f"fails={fails_b} {ticked_b.stderr[-200:]!r}")
    return 0
