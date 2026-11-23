"""Scenario `team-timer-lock` -- 2 case(s): a team's timer and the machine's maintenance lock (batch
le-minuteur-hors-du-verrou, team 1.4.1). One team under `schedule: 2m` with a daily ceremony, the clock frozen three
seconds before its ring (`PP_NOW`): every tick arms a timer due three seconds later, and the timer's own tick, under
the same clock, arms the next -- a chain of timers that wakes nobody.
- (i) while the timer sleeps, the machine's EXCLUSIVE lock is taken -- an `upgrade` would play; no `team timer` is
  played by the house's console (before team 1.4.1 the console held the lock shared through the whole sleep)
- (j) a maintenance at the timer's deadline: the exclusive held across it, the timer's tick refused
  `maintenance-in-progress` and played again once the lock is given back -- a new timer armed under another token;
  `timer-armed` written once, by the start's tick: the timer's own ticks write none
"""
from __future__ import annotations

import json
import subprocess
import time

from conductor.state import lock

from tests.harness import support

T = support(__file__, "team")

TEAM = ("---\nagents: |\n  s agents/s\nroot: s\nschedule: 2m\n"
        "ceremonies: |\n  daily every weekday 09:30 with s -> s\n---\nA chain of timers.\n")
FROZEN = "2026-10-01T09:29:57"                       # a Thursday, three seconds before the daily's ring


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    h = T.House(bench)
    mark = h.records / "teams" / "sleeper" / "tick.timer"

    def token() -> str:
        try:
            return str(json.loads(mark.read_text(encoding="utf-8")).get("token", ""))
        except (OSError, ValueError):
            return ""

    def marked(other: str, within: float) -> str:
        """-> the token of a mark that stands and is not `other`, waited for `within` seconds; '' when none came."""
        until = time.monotonic() + within
        while time.monotonic() < until:
            found = token()
            if found and found != other:
                return found
            time.sleep(0.1)
        return ""

    def consoles() -> str:
        return subprocess.run(["pgrep", "-f", "pp.py --instance .* team timer sleeper "], capture_output=True,
                              text=True).stdout.strip()

    h.declare("sleeper", TEAM)
    started = h.call("team", "start", "sleeper", now=FROZEN)
    first = marked("", 5)
    time.sleep(1.0)                                      # the timer at its sleep, its deadline two seconds ahead

    # --- (i) the exclusive lock while the timer sleeps -----------------------------------------------------------------
    lease = lock.try_(lock.maintenance_of(h.house))
    if started.returncode == 0 and first and lease is not None and not consoles():
        held("(i) the exclusive while the timer sleeps", "the timer armed (its mark stands), the machine's exclusive "
             "taken at once, no team timer played by the console")
    else:
        failures.append(f"  ✗ (i) the exclusive            rc={started.returncode} mark={bool(first)} "
                        f"exclusive={lease is not None} consoles={consoles()!r} {started.stderr[-200:]!r}")

    # --- (j) a maintenance at the deadline ------------------------------------------------------------------------------
    if lease is not None:
        time.sleep(5)                                   # the deadline passes under the maintenance
        during = token()
        lock.release(lease)
        after = marked(first, 10)
        armed = [one for one in h.events("sleeper") if one.get("kind") == "timer-armed"]
        if after and during in ("", first) and len(armed) == 1:
            held("(j) a maintenance at the deadline", "the tick refused under the exclusive, played again once it was "
                 "given back: a new timer under another token; timer-armed written once")
        else:
            failures.append(f"  ✗ (j) the maintenance          during={during!r} after={after!r} first={first!r} "
                            f"armed={len(armed)}")
    else:
        failures.append("  ✗ (j) the maintenance          the exclusive was never taken")

    h.call("team", "delete", "sleeper", "--yes")
    return 0
