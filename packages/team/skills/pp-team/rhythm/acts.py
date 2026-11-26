"""The `rhythm` domain, layer `acts`: where the rhythm writes to the journal.

A definition belongs here when it writes what the rhythm decides: the ceremonies that are due rung (`rung`) and the
recurrences whose period opens sounded (`sounded`), which the tick calls, and a recurrence paused (`recurrence_paused`),
which `pause --recurrence` calls and which says what it did. Each reads the state, has a decision of `rhythm/rules.py`
compose the events under the journal's lock, and hands them to the journal's writer; the hour is read only where the
tick and the verb have always read it. It imports no act: the tick imports it, and a recurrence taken back, which plays
a tick itself, is a verb (`recurrence_resumed`, `rhythm/verbs.py`). It may use the lower layers of any domain.
"""
from __future__ import annotations

from pathlib import Path

from house.model import Declined
from house.rules import journal_of
from house.store import refuse, tick_now
from task.rules import live_recurrences
from task.faces import principal_unknown
from rhythm.rules import due_period, recurrence_paused_of, recurrence_period, ringing, sounding
from rhythm.faces import recurrence_unknown, recurrence_was_stopped
from journal.store import state_of, written


def suspended(recurrence: dict) -> bool:
    """Whether a recurrence is stopped or paused: `recurrence_period` then says None without reading the hour, and
    the tick reads none for it."""
    return recurrence.stopped is not None or bool(recurrence.paused)


def sounded(conductor, root: Path, name: str, journal: Path) -> int:
    """Step 4, after the ceremonies: each live recurrence whose period is due SOUNDS it -- once per period, the
    journal the judge, the period judged again under the journal's lock; a paused team, and a team a delete has
    begun to remove (`deleting`), sound nothing. -> the events written."""
    count = 0
    for one in live_recurrences(state_of(journal)):
        if recurrence_period(one, None if suspended(one) else tick_now()) is None:
            continue

        def judge(now_state: dict, events: list[dict], key=one.id) -> list[dict]:
            recurrence = now_state.rhythm.recurrences.get(key)
            period = (recurrence_period(recurrence, None if suspended(recurrence) else tick_now())
                      if recurrence is not None else None)
            season = now_state.season
            return ([] if season.paused or season.stopped or season.deleting or period is None
                    else sounding(now_state, recurrence, period))
        count += len(written(conductor, root, journal, name, judge))
    return count


def rung(conductor, root: Path, name: str, journal: Path) -> int:
    """Step 4: each ceremony whose period is due and not yet rung is RUNG -- once per period,
    the journal the judge: two ticks in one minute ring once. A paused team rings nothing, nor a team a delete
    has begun to remove (`deleting`), judged under the journal's lock at the write. -> the events written."""
    state = state_of(journal)
    started = state.season.started
    ceremonies = (started.body.ceremonies if started is not None else None) or []
    count = 0
    for one in ceremonies:
        state = state_of(journal)
        period = due_period(one, state, tick_now() if one["mode"] == "every" else None)   # an `after` reads no hour
        if period is not None:
            count += len(written(conductor, root, journal, name, lambda now_state, events, one=one, period=period:
                                 [] if (now_state.season.paused or now_state.season.stopped
                                        or now_state.season.deleting)
                                 else ringing(now_state, name, one, period, now=tick_now())))
    return count


def recurrence_paused(root: Path, conductor, name: str, owner: str, asked: dict) -> int:
    """`team pause <name> --recurrence <R<n>> [--as <principal>]`: ONE recurrence SUSPENDED -- `recurrence-paused
    {recurrence, by}`, judged under the journal's lock (`team-not-started`, `principal-unknown`, `recurrence-unknown`,
    `recurrence-stopped`, `recurrence-paused`); no tick. It sounds no period and arms no timer until its resume, stays
    live -- changed by `team recurrence`, stopped by `team stop --recurrence` -- and its open occurrence lives on; the
    team's pause is another matter."""

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            return recurrence_paused_of(state, owner, asked["as"], name, asked["recurrence"])
        except Declined as declined:
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started.")
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "recurrence-unknown":
                refuse(recurrence_unknown(*data))
            if code == "recurrence-stopped":
                refuse(recurrence_was_stopped(*data))
            if code == "recurrence-paused":
                recurrence, = data
                refuse(f"recurrence-paused -- {recurrence.id} is paused since #{recurrence.paused['id']}: "
                       f"`team resume {name} --recurrence {recurrence.id}` takes it back.")
            raise ValueError(f"no sentence for the refusal `{code}`")

    made = written(conductor, root, journal_of(root, name), name, judge)[0]
    print(f"pp-team: {name} · recurrence {made.body.recurrence} paused #{made.id} by {made.body.by} -- no period "
          f"sounds until `team resume {name} --recurrence {made.body.recurrence}`, its open occurrence lives on")
    return 0
