"""The `net` domain, layer `verbs`: the command line of the timer's own process.

A definition belongs here when it plays the process the tick spawns as a timer: it reads its arguments, sleeps until its
hour, checks it is still the timer the team expects, and plays the team's tick. A verb is where the skill meets its
caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

import time
from datetime import datetime

from house.model import USAGE
from house.store import house, named_team, refuse, tick_now
from house.verbs import flags
from net.model import TIMER_WAIT
from net.rules import timer_mark
from net.acts import ticked_by_console, timer_relayed, timer_standing


def timer_verb(rest: list[str]) -> int:
    """`team timer <name> --sleep <seconds> --due <local date-time> --token <token>`: the TIMER's own process, spawned
    by the tick (`armed`) as the entry `pp-team.py` itself, outside the console: it holds no hold on the machine while it sleeps,
    and a maintenance plays meanwhile. It knows itself by the TOKEN the tick handed it, never by a pid: under Windows
    uv's launcher stands between the process the tick spawned and the Python that plays the entry. It waits for its
    mark to carry its token (TIMER_WAIT at most: a mark the tick never wrote, it leaves). Then it sleeps until the
    first of two moments: `--sleep` seconds have passed, or the wall clock (`tick_now`) reaches `--due` -- the wall
    clock counts the time the machine slept, a monotonic clock does not. It leaves at once when its mark no longer
    carries its token: disarmed, or replaced by a timer due earlier. Then it takes its mark away and plays ONE tick by
    the house's console (`ticked_by_console`), which arms the next timer when a deadline still stands; a tick that
    FAILS and leaves no timer standing, the timer arms the next itself (`timer_relayed`). Then it dies: no process
    outlives its deadline."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, {"sleep": True, "due": True, "token": True})
    if not asked["token"]:
        refuse(USAGE)
    try:
        left = float(asked["sleep"] or "")
    except ValueError:
        refuse(USAGE)
    try:
        due = datetime.fromisoformat(asked["due"]) if asked["due"] else None
    except ValueError:
        refuse(USAGE)
    if due is not None and due.tzinfo is not None:
        due = due.astimezone().replace(tzinfo=None)
    mark = timer_mark(root, name)
    token = asked["token"]
    named_at = time.monotonic() + TIMER_WAIT
    while timer_standing(root, name).get("token") != token:
        if time.monotonic() >= named_at:
            return 0                                             # never named: not the team's timer
        time.sleep(0.05)
    deadline = time.monotonic() + max(0.0, left)
    while time.monotonic() < deadline and (due is None or tick_now() < due):
        if timer_standing(root, name).get("token") != token:
            return 0                                             # disarmed, or replaced
        time.sleep(min(0.5, max(0.0, deadline - time.monotonic())))
    if timer_standing(root, name).get("token") == token:
        mark.unlink(missing_ok=True)
    played = ticked_by_console(root, conductor, name)
    if played.returncode != 0:
        timer_relayed(root, conductor, name, played.stderr)
    return played.returncode
