"""The `net` domain, layer `rules`: the net's marks and names, and the events of the net, worked out from the values
they are given.

A definition belongs here when it computes its answer from its arguments alone: the mark that finds the house's line
in the crontab, the name of its value in the Run key, the place of a timer's mark and of the kept path, the last
notice of a relaunch entry the system refused, the first open task a notice of the team rides. It also holds the
DECISIONS of the net, which compose the bodies its acts write: `timer-armed` at the hour given, and the owner's notice,
once a season, of a relaunch entry the system refused or of a timer's tick that failed -- nothing when the season said
it already. It reads no disk, no clock and no environment and prints nothing: the hour and what an effect gave come
to it as arguments, and what needs the system belongs to `store` or to an act.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from datetime import datetime

from house.rules import journal_of
from task.model import Post
from net.model import RELAUNCH_PATH, RELAUNCH_PREFIX, TICK_TIMER, TimerArmed


def mark_of(root: Path) -> str:
    """-> the mark that ends the house's one line in the crontab: how it is found again and removed."""
    return f"# pp-team {root}"


def marked(line: str, root: Path) -> bool:
    """-> whether a crontab line is the house's: its mark, or the mark of one of its teams that an earlier version laid
    (`# pp-team <house> <team>`) -- never the line of a house whose path only begins like this one's."""
    _, found, rest = line.rstrip().rpartition(" # pp-team ")
    return bool(found) and (rest == str(root) or rest.startswith(f"{root} "))


def value_name(root: Path) -> str:
    """-> the house's value in the user's Run key: `pp-team-<12 hex of the house's path>`, so that two houses of one
    user never take each other's."""
    return f"{RELAUNCH_PREFIX}-{hashlib.sha1(str(root).encode('utf-8')).hexdigest()[:12]}"


def kept_path(root: Path) -> Path:
    """-> where the house keeps the PATH of the process that laid its relaunch entry: `state/relaunch.path`."""
    return root / ".sys" / "state" / RELAUNCH_PATH


def relaunch_notice(state: dict) -> dict | None:
    """-> the last notice of the season that said the relaunch entry was refused, None when none did."""
    started = state.season.started
    since = int((started.id if started is not None else None) or 0)
    said = [one for one in state.task.messages.values()
            if one.body.relaunch and one.body.verb == "notice" and int(one.id) > since]
    return said[-1] if said else None


def timer_mark(root: Path, name: str) -> Path:
    return journal_of(root, name).parent / TICK_TIMER


def timer_armed_of(due: datetime) -> list:
    """-> what a tick writes when it arms a timer where none stood: `timer-armed`, its hour to the second."""
    return [TimerArmed.made(due=due.isoformat(timespec="seconds"))]


def first_open(state: dict) -> str | None:
    """-> the first task still open, which a notice of the team rides; None when none is."""
    return next((one.id for one in state.task.tasks.values() if one.state == "open"), None)


def relaunch_notice_of(state: dict, name: str, why: str) -> list:
    """-> the notice the owner gets ONCE per season when the system refuses the house's relaunch entry (`relaunch:
    true`, the refusal as its `why`) -- nothing when the season said it already."""
    if relaunch_notice(state) is not None:
        return []
    started = state.season.started
    return [Post.made(task=first_open(state), sender=name, to=str(started.body.owner if started is not None else None),
                      verb="notice", relaunch=True, why=why,
                      text=(f"the team {name} cannot be relaunched after a restart: the system refused its entry at "
                            f"logon ({why}). It runs on its timer until this session ends. To keep it running across a "
                            f"restart, let the user write their Run key (Windows) or start cron (Linux), then start the "
                            f"team again."))]


def timer_notice_of(state: dict, name: str, said: str, seconds: int) -> list:
    """-> the notice the owner gets ONCE per season when a timer's tick failed and the next timer was armed at the
    step (`timer: true`, the tick's stderr, clipped, as its `why`) -- nothing when the season said it already."""
    started = state.season.started
    since = int((started.id if started is not None else None) or 0)
    if any(one.body.timer and one.body.verb == "notice" and int(one.id) > since
           for one in state.task.messages.values()):
        return []
    why = " ".join(str(said or "").split())[-300:] or "no output"
    return [Post.made(task=first_open(state), sender=name, to=str(started.body.owner if started is not None else None),
                      verb="notice", timer=True, why=why,
                      text=f"the team {name}'s timer played a tick that failed ({why}); the next timer is armed at the "
                           f"step, {seconds} s: the team ticks on, and this is said once this season.")]
