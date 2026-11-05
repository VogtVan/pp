"""Scenario `team-timer-race` -- 4 case(s): the writers of a team's timer mark `tick.timer` play at the same instant
(batch le-minuteur-sous-windows, KC33): the timer reaching its deadline takes its mark and ticks while four `team tick`
of the same team arm. One team under `schedule: 5m` with a live recurrence -- a deadline always stands, no harness is
ever launched before it.
- (i) three rounds, each from a disarmed team: a timer spawned with its token and its mark, due at once, and four ticks
  played together; once the losers left, ONE mark stands, it names a live process, and the one `team timer` alive
  carries the mark's token
- (j) the stop of the recurrence disarms: the mark gone, no `team timer` of the team alive
- (k) the stop and the ticks, together: three rounds, each a recurrence posted and armed, then its stop played at the
  same instant as four ticks -- once the stop answered, the mark gone and no `team timer` of the team alive
- (l) the stop inside the tick's window, played on purpose: `armed` read the team needing its net, and the stop of its
  last recurrence plays -- its write and its disarm -- just before the timer is spawned and its mark written; the
  timer spawned then does not outlive the stop: the mark gone, no `team timer` alive
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

from tests.harness import support

T = support(__file__, "team")

TEAM = "---\nagents: |\n  rm agents/rm\nroot: rm\nschedule: 5m\n---\nOne member, one recurrence.\n"
ROUNDS, WRITERS = 3, 4


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench, script={})
    team = h.module()
    h.declare("race", TEAM)
    started = h.call("team", "start", "race", *h.harnessed, "--no-tick")
    posed = h.call("team", "post", "race", "--message", "later", "--to", "rm", "--every", "day 23:59", "--no-tick")
    mark = h.records / "teams" / "race" / "tick.timer"

    def timers() -> list[str]:
        """-> the tokens of the `team timer race` processes alive."""
        said = subprocess.run(["pgrep", "-af", "team timer race "], capture_output=True, text=True).stdout
        return [found.group(1) for line in said.splitlines() if (found := re.search(r"--token (\w+)", line))]

    def settled_timers(bound: float = 8.0) -> list[str]:
        """-> the tokens alive once the losers left: a timer whose mark carries another token leaves within
        TIMER_WAIT, or at its next step of sleep."""
        deadline = time.monotonic() + bound
        alive = timers()
        while time.monotonic() < deadline and len(alive) > 1:
            time.sleep(0.25)
            alive = timers()
        return alive

    # --- (i) the timer at its deadline and four ticks, together ---------------------------------------------------
    rounds = []
    for one in range(ROUNDS):
        team.disarmed(h.house, "race")
        token = f"{one + 1:016x}"
        due = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() + 1))
        timer = subprocess.Popen([sys.executable, str(h.engine), "--instance", str(h.house), "team", "timer", "race",
                                  "--sleep", "0.3", "--due", due, "--token", token], cwd=h.ws,
                                 env={**os.environ, **h.env}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 start_new_session=True)
        mark.write_text(json.dumps({"pid": timer.pid, "due": due, "token": token}), encoding="utf-8")
        with ThreadPoolExecutor(WRITERS) as pool:
            ticks = list(pool.map(lambda _: h.call("team", "tick", "race"), range(WRITERS)))
        try:
            ended = timer.wait(timeout=20)
        except subprocess.TimeoutExpired:
            timer.kill()
            ended = None
        alive = settled_timers()
        standing = team.timer_standing(h.house, "race")
        rounds.append({"ticks": [tick.returncode for tick in ticks], "ended": ended, "alive": alive,
                       "standing": bool(standing), "same": alive == [standing.get("token")],
                       "lives": bool(standing) and team.alive(int(standing["pid"]))})
    if (started.returncode == 0 and posed.returncode == 0
            and all(r["ticks"] == [0] * WRITERS and r["ended"] == 0 and r["standing"] and r["same"] and r["lives"]
                    for r in rounds)):
        held("(i) the timer and four ticks, together", f"{ROUNDS} rounds: the timer at its deadline ended, one mark "
             "naming a live process, one team timer alive carrying the mark's token")
    else:
        failures.append(f"  ✗ (i) the race               rc={started.returncode}/{posed.returncode} rounds={rounds} "
                        f"{started.stderr[-160:]!r} {posed.stderr[-160:]!r}")

    # --- (j) the stop of the recurrence disarms --------------------------------------------------------------------
    stopped = h.call("team", "stop", "race", "--recurrence", "R1", "--no-tick")
    gone_at = time.monotonic() + 8
    while time.monotonic() < gone_at and (timers() or mark.exists()):
        time.sleep(0.25)
    if stopped.returncode == 0 and not mark.exists() and not timers():
        held("(j) the stop disarms", "the recurrence stopped: the mark gone, no team timer of race alive")
    else:
        failures.append(f"  ✗ (j) the stop               rc={stopped.returncode} mark={mark.exists()} alive={timers()} "
                        f"{stopped.stderr[-160:]!r}")

    # --- (k) the stop and four ticks, together ----------------------------------------------------------------------
    races = []
    for one in range(ROUNDS):
        laid = h.call("team", "post", "race", "--message", "later", "--to", "rm", "--every", "day 23:59")
        recurrence = f"R{one + 2}"
        with ThreadPoolExecutor(WRITERS + 1) as pool:
            calls = [pool.submit(h.call, "team", "stop", "race", "--recurrence", recurrence, "--no-tick")]
            calls += [pool.submit(h.call, "team", "tick", "race") for _ in range(WRITERS)]
            played = [call.result().returncode for call in calls]
        left_at = time.monotonic() + 8
        while time.monotonic() < left_at and (timers() or mark.exists()):
            time.sleep(0.25)
        races.append({"laid": laid.returncode, "played": played, "mark": mark.exists(), "alive": timers()})
        team.disarmed(h.house, "race")                        # the next round starts from a disarmed team
    if all(r["laid"] == 0 and r["played"] == [0] * (WRITERS + 1) and not r["mark"] and not r["alive"] for r in races):
        held("(k) the stop and four ticks, together", f"{ROUNDS} rounds: the mark gone and no team timer alive once "
             "the stop answered")
    else:
        failures.append(f"  ✗ (k) the stop and the ticks  rounds={races}")

    # --- (l) the stop inside the tick's window, on purpose -------------------------------------------------------------
    team.disarmed(h.house, "race")
    laid = h.call("team", "post", "race", "--message", "later", "--to", "rm", "--every", "day 23:59", "--no-tick")
    spawn, stops = team.subprocess.Popen, []

    def stop_first(*args, **kwargs):
        """The stop of the last recurrence, played between `armed`'s read of the team and the timer's spawn."""
        team.subprocess.Popen = spawn                       # the module is shared: the stop's own calls spawn as ever
        if not stops:
            stops.append(h.call("team", "stop", "race", "--recurrence", f"R{ROUNDS + 2}", "--no-tick"))
        return spawn(*args, **kwargs)
    saved = {key: os.environ.get(key) for key in h.env}
    os.environ.update(h.env)
    team.subprocess.Popen = stop_first
    try:
        root, conductor = team.house()
        team.armed(root, conductor, "race", team.journal_of(root, "race"))
    finally:
        team.subprocess.Popen = spawn
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    left_at = time.monotonic() + 4
    while time.monotonic() < left_at and (timers() or mark.exists()):
        time.sleep(0.25)
    window = {"laid": laid.returncode, "stopped": [one.returncode for one in stops], "mark": mark.exists(),
              "alive": timers()}
    team.disarmed(h.house, "race")
    if window == {"laid": 0, "stopped": [0], "mark": False, "alive": []}:
        held("(l) the stop inside the tick's window", "the stop played between armed's read and the spawn: the timer "
             "spawned after it does not outlive it -- the mark gone, no team timer alive")
    else:
        failures.append(f"  ✗ (l) the window             {window}")
    return 0
