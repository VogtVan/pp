"""The `rhythm` domain, layer `rules`: when a ceremony or a recurrence rings, and what the rhythm writes.

A definition belongs here when it computes its answer from the state and its arguments: a recurrence's rhythm read from
its words and checked, the period due and the next one, a recurrence found by its name. It also holds the DECISIONS of
the rhythm, which compose by `made` and `but` the bodies the journal's writer receives: what a ring writes (`ringing`,
given the hour as `now`), with the words it asks of the facilitator and of each participant (`consignes`), and what a
recurrence that sounds writes (`sounding`); what `team ring` writes; a recurrence born from a task, started now or
changed, each judged in two steps around the reading of the hour; a recurrence born from `team post --every`
(`recurrence_posted`), the hour given, with the keys and the order of `post`; a recurrence taken back, paused or stopped
(`recurrence_stopped`, for `team stop --recurrence`). A decision DECLINES by a code with its data, and the verb or the
act says the sentence; No rule here refuses: `every_of` and `recurrence_description`, which read the words of a flag,
decline by the sentence the refusal prints, and their verb refuses it; `held_recurrence`, which decisions call, declines
by a code (`recurrence-unknown`, `recurrence-stopped`), as they do. No rule here reads the clock: the period due and the
next one (`due_period`, `next_due`, `recurrence_period`, `recurrence_next`) and every decision receive the hour as
`now`, a value the act or the verb reads and gives. It reads no disk, no clock and no environment and prints nothing;
anything else that needs the system belongs to `store` or to an act.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta

from house.model import Declined, decline
from declaration.model import DESCRIPTION_CHARS, DOWS
from task.model import Post, TaskBorn
from rhythm.model import (UNITS, CeremonyDue, RecurrenceBorn, RecurrenceChanged, RecurrencePaused, RecurrenceResumed,
                          RecurrenceSkipped, RecurrenceStopped)
from declaration.rules import described_well, when_of
from task.rules import next_task, principal_of


def every_of(text: str) -> dict:
    """-> the period a recurrence's `--every` names: a dated one, `{kind, at}` as `when_of` reads it, or a DURATION
    `<n>m|<n>h|<n>d` -- n a whole number from 1, a minute at least --, `{kind: "interval", every, seconds}`;
    `every-invalid` naming both forms otherwise. A ceremony reads `when_of` alone: it has no duration."""
    words = text.split()
    found = when_of(words)
    duration = re.fullmatch(r"([1-9][0-9]*)([mhd])", words[0]) if len(words) == 1 else None
    if found is None and duration is not None:
        found = {"kind": "interval", "every": words[0], "seconds": int(duration.group(1)) * UNITS[duration.group(2)]}
    if found is None:
        decline(f"every-invalid -- `--every {' '.join(words)[:40]}`: a recurrence comes back "
               "`day|weekday|mon..sun HH:MM`, the local hour, or every `<n>m|<n>h|<n>d`.")
    return found


def conforms(when: dict, day) -> bool:
    """-> whether an `every` ceremony rings on that day (a date or a date-time): every day, a
    weekday, or its one day of the week -- the ONE reading of the rhythm's days."""
    kind = when.get("kind")
    weekday = day.weekday()
    return kind == "day" or (kind == "weekday" and weekday < 5) or (kind in DOWS and weekday == DOWS.index(kind))


def due_period(ceremony: dict, state: dict, now: datetime) -> str | None:
    """-> the period the ceremony owes a ring for at the hour `now`, or None. An `every` ceremony is due once
    its day conforms and its hour is past (the period is the local date); an `after` one is
    due for each period its followed ceremony RESOLVED and it did not ring yet (inherited).
    The periods already rung are the state's (`rung`): a snapshot carries them."""
    already = set(state.rhythm.rung.get(str(ceremony["name"]), []))
    if ceremony["mode"] == "every":
        when = ceremony.get("when") or {}
        since = state.season.since
        if conforms(when, now) and now.strftime("%H:%M") >= str(when.get("at")):
            period = now.date().isoformat()
            moment = datetime.fromisoformat(f"{period}T{when.get('at')}")
            if period not in already and (not since or moment > datetime.fromisoformat(str(since))):
                return period
        return None
    for period in sorted(set(state.rhythm.rung.get(str(ceremony["after"]), []))):
        held_task = next((one for one in state.task.tasks.values()
                          if one.ceremony == ceremony["after"] and one.period == period), None)
        if held_task is not None and held_task.state == "resolved" and period not in already:
            return period
    return None


def next_due(ceremony: dict, state: dict, now: datetime) -> str | None:
    """-> the local date-time `YYYY-MM-DDTHH:MM` of an `every` ceremony's next ring from the hour `now`: today when
    the day conforms and its period is not rung yet -- its hour past or not --, else the next
    conforming day; None for an `after` ceremony, which follows the one it names. A ring at hand
    (`manual-<id>`) takes no date: it moves nothing here, as in `due_period`."""
    if ceremony["mode"] != "every":
        return None
    when = ceremony.get("when") or {}
    already = set(state.rhythm.rung.get(str(ceremony["name"]), []))
    since = datetime.fromisoformat(str(state.season.since)) if state.season.since else None
    today = now.date()
    for ahead in range(8):
        day = today + timedelta(days=ahead)
        moment = f"{day.isoformat()}T{when.get('at')}"
        if (conforms(when, day) and day.isoformat() not in already
                and (since is None or datetime.fromisoformat(moment) > since)):
            return moment
    return None


def recurrence_description(given: str) -> str:
    """-> the description `--description` gives a recurrence: one sentence of what it does, beside its short name --
    one line, its edges stripped, 1 to `DESCRIPTION_CHARS` printable characters; `description-invalid` otherwise."""
    text = given.strip()
    if not described_well(text):
        decline(f"description-invalid -- `--description {' '.join(given.split())[:40]}`: a recurrence's description is "
               f"one line of 1 to {DESCRIPTION_CHARS} printable characters.")
    return text


def ringing(state: dict, team: str, ceremony: dict, period: str, by: str | None = None, *, now: datetime) -> list:
    """-> the events one ring writes: `ceremony-due` (with `by`, the principal, for a ring at
    hand), ONE ceremony task from the team to the facilitator, its OPENING `do` from the team to the
    facilitator, then a `do` post facilitator -> each participant -- each answer reaches the facilitator as a
    message, the line's quorum is said in its consigne, and its answer to the opening resolves the task. The task is
    NAMED `<ceremony> YYYY-MM-DD HH:MM`, `now` the local hour of the ring, and says a consigne."""
    task = next_task(state)
    facilitator = str(ceremony["facilitator"])
    at = now.strftime("%Y-%m-%d %H:%M")
    asked, taking = consignes(team, ceremony, at)
    due = CeremonyDue.made(ceremony=ceremony["name"], period=period)
    if by is not None:
        due = due.but(by=by)
    events: list = [due,
                    TaskBorn.made(task=task, sender=team, to=facilitator, ceremony=ceremony["name"], period=period,
                                  name=f"{ceremony['name']} {at}", text=asked),
                    Post.made(task=task, sender=team, to=facilitator, verb="do", text=asked)]
    for one in ceremony["participants"]:
        events.append(Post.made(task=task, sender=facilitator, to=one, verb="do", text=taking))
    return events


def sounds_at(recurrence: dict, day) -> datetime:
    """-> the local date-time a recurrence's period of that day sounds at: the day, at the recurrence's hour."""
    hour, minute = (int(part) for part in str(recurrence.when["at"]).split(":"))
    return datetime(day.year, day.month, day.day, hour, minute)


def slot_of(recurrence: dict, now: datetime) -> tuple[int, datetime]:
    """-> the SLOT of a recurrence by a duration under way at `now` -- its rank k and its instant, `since + k x seconds`,
    k never under the recurrence's first (0 at the pose, 1 after a change that gave the duration)."""
    since = datetime.fromisoformat(str(recurrence.since))
    seconds = int(recurrence.when["seconds"])
    rank = max(int((now - since).total_seconds() // seconds), int(recurrence.first or 0))
    return rank, since + timedelta(seconds=rank * seconds)


def slot_period(moment: datetime) -> str:
    """-> the period of a slot: its local instant `YYYY-MM-DDTHH:MM`."""
    return moment.isoformat(timespec="minutes")


def recurrence_period(recurrence: dict, now: datetime) -> str | None:
    """-> the period a live recurrence owes at the hour `now`, or None: its day conforms, its hour is past, that period sounds after
    the recurrence was posted (`since`) and it has not sounded yet -- by an occurrence or a skip. The period is the
    local date, as a ceremony's. By a DURATION, the slot under way alone -- its instant past and not sounded --: a
    slot that passed whole without a tick, or under a pause, never sounds later. None while it is suspended."""
    if recurrence.stopped is not None or recurrence.paused:
        return None
    if recurrence.when.get("kind") == "interval":
        _, moment = slot_of(recurrence, now)
        period = slot_period(moment)
        return period if moment <= now and period not in recurrence.sounded else None
    if not conforms(recurrence.when, now):
        return None
    moment = sounds_at(recurrence, now.date())
    period = now.date().isoformat()
    if now >= moment and moment > datetime.fromisoformat(str(recurrence.since)) \
            and period not in recurrence.sounded:
        return period
    return None


def recurrence_next(recurrence: dict, now: datetime) -> str | None:
    """-> the local date-time `YYYY-MM-DDTHH:MM` a live recurrence sounds at next from the hour `now`: the first
    conforming day from today,
    its period not sounded and after `since`; by a duration, the slot under way while it is not sounded, else the slot
    after it; None once it is stopped, and while it is suspended."""
    if recurrence.stopped is not None or recurrence.paused:
        return None
    if recurrence.when.get("kind") == "interval":                 # the slot under way while it owes, else the next
        _, moment = slot_of(recurrence, now)
        if moment <= now and slot_period(moment) in recurrence.sounded:
            moment += timedelta(seconds=int(recurrence.when["seconds"]))
        return slot_period(moment)
    since = datetime.fromisoformat(str(recurrence.since))
    today = now.date()
    for ahead in range(8):
        day = today + timedelta(days=ahead)
        if (conforms(recurrence.when, day) and day.isoformat() not in recurrence.sounded
                and sounds_at(recurrence, day) > since):
            return sounds_at(recurrence, day).isoformat(timespec="minutes")
    return None


def sounding(state: dict, recurrence: dict, period: str) -> list[dict]:
    """-> the events one period of a recurrence writes: its OCCURRENCE -- a task like one `post` opens, from the
    recurrence's principal to its member, NAMED `<name> YYYY-MM-DD HH:MM` (the recurrence's id without a name), with
    `recurrence` and `period`, then its opening `do` -- or, while the occurrence before it is still open,
    `recurrence-skipped {open}` and nothing opened: a member never holds the same work twice."""
    before = state.task.tasks.get(recurrence.last or "")
    if before is not None and before.state == "open":
        return [RecurrenceSkipped.made(recurrence=recurrence.id, period=period, open=before.id)]
    task = next_task(state)
    sender, to, text = recurrence.sender, recurrence.to, recurrence.text
    return [TaskBorn.made(task=task, sender=sender, to=to,
                          name=f"{recurrence.name or recurrence.id} "
                               + (period.replace("T", " ") if recurrence.when.get("kind") == "interval"
                                  else f"{period} {recurrence.when['at']}"), text=text,
                          recurrence=recurrence.id, period=period),
            Post.made(task=task, sender=sender, to=to, verb="do", text=text)]


def held_recurrence(state: dict, name: str, called: str) -> dict:
    """-> the recurrence `called` of the team, live; else `Declined` by its code: `recurrence-unknown` (the team, the id
    called, the ids), `recurrence-stopped` (the recurrence)."""
    recurrence = state.rhythm.recurrences.get(called)
    if recurrence is None:
        raise Declined("recurrence-unknown", name, called, list(state.rhythm.recurrences))
    if recurrence.stopped is not None:
        raise Declined("recurrence-stopped", recurrence)
    return recurrence


def same_period(one: dict, other: dict) -> bool:
    """-> whether two periods of a recurrence come back alike: the same dated period, or durations of the same
    seconds (`4h` and `240m`)."""
    if one.get("kind") == "interval" and other.get("kind") == "interval":
        return one.get("seconds") == other.get("seconds")
    return one == other



def recurrence_posted(state: dict, sender: str, to: str, naming: dict, text: str, when: dict, since: str, limit,
                      describing: dict) -> list:
    """-> `recurrence {R<n>, from, to, name?, text, when, since, context, description?}`: the recurrence `team post
    --every` lays, in the keys and the order `post` writes them -- `naming` and `describing` given or empty, `since`
    the local hour of the post."""
    return [RecurrenceBorn.made(recurrence=f"R{len(state.rhythm.recurrences) + 1}", sender=sender, to=to, **naming,
                                text=text, when=when, since=since, context=limit, **describing)]


def recurrence_stopped(state: dict, name: str, called: str, owner: str) -> list:
    """-> `recurrence-stopped {recurrence, by}`: `team stop --recurrence` -- the recurrence `called` live
    (`held_recurrence`, a suspended one as well), stopped by the owner."""
    recurrence = held_recurrence(state, name, called)
    return [RecurrenceStopped.made(recurrence=recurrence.id, by=owner)]


def ring_asked(state: dict, owner: str, principal: str | None, called: str) -> tuple:
    """-> (who rings, the ceremony): `team ring` judged before the hour is read -- the principal `--as` names
    (`principal_of`), the ceremony `called` declared and none of its tasks open; else `Declined` by its code:
    `team-not-started`, `team-deleting`, `season-stopped`, `ceremony-unknown` (the name, the names declared),
    `ceremony-open` (the open task, the ceremony)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if state.season.deleting:
        raise Declined("team-deleting")
    if state.season.stopped:
        raise Declined("season-stopped")
    sender = principal_of(state, owner, principal)
    declared = state.season.started.body.ceremonies or []
    ceremony = next((one for one in declared if one.get("name") == called), None)
    if ceremony is None:
        raise Declined("ceremony-unknown", called, [str(one.get("name")) for one in declared])
    held = [one.id for one in state.task.tasks.values() if one.ceremony == called and one.state == "open"]
    if held:
        raise Declined("ceremony-open", held[0], called)
    return sender, ceremony


def recurrence_born_asked(state: dict, owner: str, principal: str | None, task_id: str) -> tuple:
    """-> (who lays it, the task): a recurrence laid on the task `task_id`, judged before the hour is read; else
    `Declined`: `team-not-started`, `task-unknown` (the id, the ids), `task-recurrent` (the task)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    sender = principal_of(state, owner, principal)
    task = state.task.tasks.get(task_id)
    if task is None:
        raise Declined("task-unknown", task_id, list(state.task.tasks))
    if task.recurrence or task.ceremony:
        raise Declined("task-recurrent", task)
    return sender, task


def recurrence_born(state: dict, sender: str, task: dict, when: dict, since: str, limit, description) -> list:
    """-> `recurrence {R<n>, from, to, name?, text, when, since, context, task, description?}`: a new recurrence on the
    task, its member, its text and its name the task's; `since` the local hour it is laid."""
    return [RecurrenceBorn.made(recurrence=f"R{len(state.rhythm.recurrences) + 1}", sender=sender, to=task.to,
                                **({"name": task.name} if task.name else {}), text=task.text,
                                when=when, since=since, context=limit, task=task.id,
                                **({} if description is None else {"description": description}))]


def recurrence_launch_asked(state: dict, owner: str, principal: str | None, name: str, called: str) -> tuple:
    """-> (who launches, the recurrence): one occurrence more of `called` asked now, judged before the hour is read --
    in season, the recurrence live (`held_recurrence`), its last occurrence not open; else `Declined`:
    `team-not-started`, `season-stopped`, `recurrence-open` (the open task, the recurrence)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    sender = principal_of(state, owner, principal)
    if state.season.stopped:
        raise Declined("season-stopped")
    recurrence = held_recurrence(state, name, called)  # a suspended one launches, and stays suspended
    before = state.task.tasks.get(recurrence.last or "")
    if before is not None and before.state == "open":
        raise Declined("recurrence-open", before.id, recurrence.id)
    return sender, recurrence


def recurrence_launched(state: dict, sender: str, recurrence: dict, now: datetime) -> list:
    """-> the occurrence launched now: a `task` from the recurrence's principal to its member, with `recurrence`,
    `now: true` and `by`, named at the local hour `now`, then its `do`."""
    task = next_task(state)
    recurrent, to, text = recurrence.sender, recurrence.to, recurrence.text
    return [TaskBorn.made(task=task, sender=recurrent, to=to,
                          name=f"{recurrence.name or recurrence.id} {now.strftime('%Y-%m-%d %H:%M')}",
                          text=text, recurrence=recurrence.id, now=True, by=sender),
            Post.made(task=task, sender=recurrent, to=to, verb="do", text=text)]


def recurrence_change_asked(state: dict, owner: str, principal: str | None, name: str, called: str,
                            when: dict | None) -> tuple:
    """-> (who changes it, the recurrence, whether its period changes): a change of `called` judged before the hour
    is read -- the hour is read only for a new period; else `Declined("team-not-started")`."""
    if state.season.started is None:
        raise Declined("team-not-started")
    sender = principal_of(state, owner, principal)
    recurrence = held_recurrence(state, name, called)  # a suspended one changes, and stays suspended
    return sender, recurrence, when is not None and not same_period(recurrence.when, when)


def recurrence_changed(recurrence: dict, sender: str, when: dict | None, since: str | None, limited: bool, limit,
                       message: str | None, description: str | None) -> list:
    """-> `recurrence-changed {recurrence, when?, since?, context?, text?, description?, by}`: what changes alone --
    the period with its `since` when `since` is given, the context limit when one is asked (`limited`, `limit` None
    for off), the text, the description; else `Declined("recurrence-unchanged", recurrence)`."""
    changes: dict = {}
    if since is not None:
        changes.update(when=when, since=since)
    if limited and recurrence.context != limit:
        changes["context"] = limit
    if message is not None and recurrence.text != message:
        changes["text"] = message
    if description is not None and recurrence.description != description:
        changes["description"] = description
    if not changes:
        raise Declined("recurrence-unchanged", recurrence)
    return [RecurrenceChanged.made(recurrence=recurrence.id, **changes, by=sender)]


def recurrence_resume_asked(state: dict, owner: str, principal: str | None, name: str, called: str) -> tuple:
    """-> (who resumes, the recurrence): a suspended recurrence taken back, judged before the hour is read; else
    `Declined`: `team-not-started`, `team-deleting`, `recurrence-live` (the recurrence)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if state.season.deleting:
        raise Declined("team-deleting")
    sender = principal_of(state, owner, principal)
    recurrence = held_recurrence(state, name, called)
    if not recurrence.paused:
        raise Declined("recurrence-live", recurrence)
    return sender, recurrence


def recurrence_resumed_of(recurrence: dict, sender: str, now: datetime) -> list:
    """-> `recurrence-resumed {recurrence, by, since}`, `since` the local hour `now` of the resume."""
    return [RecurrenceResumed.made(recurrence=recurrence.id, by=sender, since=now.isoformat(timespec="seconds"))]


def recurrence_paused_of(state: dict, owner: str, principal: str | None, name: str, called: str) -> list:
    """-> `recurrence-paused {recurrence, by}`: a live recurrence suspended; else `Declined`: `team-not-started`,
    `recurrence-paused` (the recurrence)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    sender = principal_of(state, owner, principal)
    recurrence = held_recurrence(state, name, called)
    if recurrence.paused:
        raise Declined("recurrence-paused", recurrence)
    return [RecurrencePaused.made(recurrence=recurrence.id, by=sender)]


def consignes(team: str, ceremony: dict, at: str) -> tuple[str, str]:
    """-> (the facilitator's task text, each participant's `do` text): what a ring ASKS, never the
    ceremony's declaration line -- the team's intention and the ceremony's entry say what to do."""
    head = f"the ceremony `{ceremony['name']}` of team {team} rings ({at})"
    participants = ", ".join(str(one) for one in ceremony["participants"])
    enough = f" ({ceremony['quorum']} of them are enough)" if ceremony.get("quorum") else ""
    return (f"{head}: gather the answers of {participants}{enough}, then answer this message with the conclusion -- "
            "your answer closes the ceremony.",
            f"{head}: take part in it as the team's intention says, and answer {ceremony['facilitator']}.")
