"""The `net` domain, layer `model`: what the team's net is, held as plain values.

The net is what wakes a team when no call does: a timer the tick arms, and the house's relaunch entry that arms the
timers again after a restart. A definition belongs here when it is data about the net: the names of the files the timer
and the relaunch entry keep, how long a timer waits and how often it tries again, the variables that stand in for the
crontab, the scheduler and the Windows Run key, the Windows constants read on any system, or a type that carries one of
them. One value here changes while a tick plays: a list of one element, set in place, that says the tick is the timer's
own. Nothing here reads the disk, the clock or the environment.

It also holds the body of the net's one kind of event, `TimerArmed`, in the tuple `NET_BODIES` that `journal/model.py`
reads to decode the journal. The net has no part of the state and no fold: no fold reads `timer-armed`. The body of
`schedule-off`, which turns the net off, lives in `season/model.py`: the season folds it and a task writes it.
"""
from __future__ import annotations

from dataclasses import dataclass

from house.model import Body

TICK_TIMER = "tick.timer"        # beside the journal: the TIMER armed under the minute, {pid, due}, one at most
TIMER_WAIT = 2.0                 # seconds a timer waits for its mark to carry its token, before it leaves
TIMER_RETRY = 2.0                # seconds a timer waits before it plays its tick again under a maintenance
TIMER_RETRIES = 300              # the ticks a timer plays again under a maintenance at most: ten minutes
CREATE_NEW_PROCESS_GROUP = 0x00000200   # Windows' process creation flags and answers, read on any system
CREATE_NO_WINDOW = 0x08000000
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259
ERROR_ACCESS_DENIED = 5
CRONTAB = "PP_CRONTAB"                           # names a file that stands for the user's crontab: the bench, a try
SCHEDULER = "PP_SCHEDULER"                       # names the scheduler's façade, `nt` or `posix`: the bench plays both
RUNKEY = "PP_RUNKEY"                             # names a file that stands for the user's Run key: one value per line
TIMER_ENV = "PP_TEAM_TIMER"                      # marks the tick a timer plays: read then taken out by `tick`
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"   # under HKEY_CURRENT_USER: played at the user's logon
WSL_DISTRO = "WSL_DISTRO_NAME"                   # set by WSL in its distribution: the posix façade lays the Run key too
RELAUNCH_PREFIX = "pp-team"                      # the head of the house's value in the Run key
RELAUNCH_LOCK = "relaunch.lock"                  # under the house's state: the relaunch entry laid, judged, removed
RELAUNCH_PATH = "relaunch.path"                  # under the house's state: the PATH of the process that laid the entry
TIMER_TICKING = [False]          # set in the timer's own tick: the timer it arms next is no news for the journal --
#                                  a list of one, written in place: every module that imports the name sees the write


@dataclass(frozen=True, eq=False)
class TimerArmed(Body):
    """`timer-armed`: the tick armed the team's timer, due at `due`."""
    KIND = "timer-armed"
    due: str | None = None


NET_BODIES: tuple = (TimerArmed,)   # the bodies of this domain's kinds: `journal/model.py` reads them
