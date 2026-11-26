"""The `tick` domain, layer `rules`: what a tick has to do and what it writes, worked out from the team's state.

A definition belongs here when it computes its answer from the state and the values it is given: whether a member is due
a launch, the hour the next tick is due, whether the team still needs its net. It also holds the DECISIONS of a
member's wake-up: each takes the state and what the act measured or launched, and composes the bodies the act writes
-- the task's launches spent and the owner's notice, the budget spent in money or in launches and its notice, the
wake-up put off, the intent of the wake-up, the launch -- or gives nothing when there is nothing to write. A body is
composed by `made`, a key the line leaves out when it has no value is simply not given, and a notice's text is
composed here, as the line writes it. It reads no disk, no clock and no environment and prints nothing: the time and
the result of an effect come to it as arguments, and what needs the system belongs to `store` or to an act.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from budget.model import BudgetSpent, LaunchesSpent
from task.model import Deferred, Post
from wake.model import WakeIntent, WakeLaunched
from task.rules import dues, live_recurrences, loud
from rhythm.rules import next_due, recurrence_next
from wake.rules import busy, halted_of, launches_of_run, quota_of, suspicion_of
from season.rules import launch_kept
from health.rules import silent_tasks, standing_of


def due_now(state: dict, member: str, clock: datetime) -> bool:
    """-> whether the member is due a launch the tick did not play: idle, no provider's limit holding it, something to
    receive on an open task whose launches are not spent and that does not halt it, the budget not spent -- held by
    `parallel:` or by the budget's rest, launched by a later tick --, or one of its runs standing on an open or a
    resolved task (`standing_of`) that does not halt it."""
    if busy(state, member) or state.budget.budget_spent or quota_of(state, member, clock) is not None:
        return False
    if any(halted_of(state, member, task) is None for task in standing_of(state, member)):
        return True
    return any(task not in state.budget.launches_spent and halted_of(state, member, task) is None and loud(state, box)
               for task, box in dues(state, member))


def deadline_of(state: dict, clock: datetime, step: int) -> datetime | None:
    """-> the hour the next tick is DUE under the timer, None when nothing is due: a launch under way (its `timeout:`
    when one is declared, else the step), a suspected member within its interval with something to deliver, to
    answer or a run standing (its `until`: a fallen standing run is continued once its interval passed, never at
    the step), a member due but not launched (the step), a member a provider's limit holds (its `until`, however far:
    the limit itself says when to launch it again, so never the step), the next ring of an `every` ceremony or the
    next period of a live recurrence -- the earliest of them, never before the next second. A paused team waits on its launches
    under way alone, and so does a team off season."""
    soon = clock + timedelta(seconds=step)
    due: list[datetime] = []
    timeout = state.season.limits.get("timeout")
    for tag in state.wake.intents:
        if tag in state.wake.ended:
            continue
        launched = state.wake.launched.get(tag)
        if launched is not None and timeout is not None and launched.at:
            born = datetime.fromisoformat(str(launched.at)).astimezone().replace(tzinfo=None)
            due.append(min(soon, born + timedelta(seconds=float(timeout))))
        else:
            due.append(soon)
    started = state.season.started
    if not state.season.paused and not state.season.stopped:
        for member in list((started.body.agents if started is not None else None) or {}):
            suspicion = suspicion_of(state, member)
            if suspicion is not None and clock < suspicion["until"]:
                if (silent_tasks(state, member) or standing_of(state, member)
                        or any(loud(state, box) for _, box in dues(state, member))):
                    due.append(min(soon, suspicion["until"]))
            elif due_now(state, member, clock):
                due.append(soon)
            held = quota_of(state, member, clock)
            if held is not None and held.get("until") is not None:   # its provider's limit ends: launched again
                ends = datetime.fromisoformat(str(held["until"])).astimezone().replace(tzinfo=None)
                due.append(max(ends, clock + timedelta(seconds=1)))
        for ceremony in (started.body.ceremonies if started is not None else None) or []:
            ring = next_due(ceremony, state, clock)
            if ring is not None:
                due.append(max(datetime.fromisoformat(ring), clock + timedelta(seconds=1)))
        for recurrence in live_recurrences(state):
            sound = recurrence_next(recurrence, clock)
            if sound is not None:
                due.append(max(datetime.fromisoformat(sound), clock + timedelta(seconds=1)))
    return max(min(due), clock + timedelta(seconds=1)) if due else None


def netless(state: dict) -> bool:
    """-> whether the team no longer needs its net: started, and off season or with no task open, no ceremony
    declared, no recurrence live -- the condition under which `schedule-off` is written."""
    started = state.season.started
    if started is not None and state.season.stopped:
        return True
    return (started is not None
            and not any(one.state == "open" for one in state.task.tasks.values())
            and not (started.body.ceremonies or [])
            and not live_recurrences(state))



def launches_spent_of(state: dict, started: dict, name: str, agent: str, task: str, spent: int, bound: int) -> list:
    """-> what a member due on a task whose launches are spent writes: `launches-spent` and the owner's notice, once
    -- nothing when the task's bound is already said."""
    if task in state.budget.launches_spent:
        return []
    return [LaunchesSpent.made(task=task, spent=spent, launches=bound),
            Post.made(task=task, sender=name, to=str(started.body.owner), verb="notice",
                      text=f"the task's launches are spent: {spent} of {bound}; {agent} stays due on {task}")]


def budget_spent_of(state: dict, started: dict, name: str, agent: str, task: str, budget) -> list:
    """-> what a member due writes when the team has spent its budget in money: `budget-spent` and the owner's
    notice, once -- nothing when the budget is already said spent."""
    if state.budget.budget_spent:
        return []
    return [BudgetSpent.made(spent=round(state.budget.cost, 6), budget=budget),
            Post.made(task=task, sender=name, to=str(started.body.owner), verb="notice",
                      text=f"the budget is spent: {state.budget.cost:g} of {budget:g} USD; {agent} stays due on {task}")]


def launches_bound_of(state: dict, started: dict, name: str, agent: str, task: str, spent: int, bound: int) -> list:
    """-> what a member due writes when the team has spent its launches since the start (`budget-launches`):
    `budget-spent` in launches and the owner's notice, once."""
    if state.budget.budget_spent:
        return []
    return [BudgetSpent.made(spent=spent, budget=bound, unit="launches"),
            Post.made(task=task, sender=name, to=str(started.body.owner), verb="notice",
                      text=f"the budget is spent: {spent} of {bound} launches; {agent} stays due on {task}")]


def deferred_of(agent: str, task: str, *reserved: float) -> list:
    """-> the wake-up of a member put off: by the team's `parallel`, or, `reserved` given, by its share all held by
    the wake-ups under way."""
    return [Deferred.made(agent=agent, task=task, **({"reserved": reserved[0]} if reserved else {}))]


def wake_intent_of(state: dict, renewal, tag: str, agent: str, path: str, task: str, run: str | None, box: list,
              carried: list, continued: bool, beat: int | None, relance, allowance) -> list:
    """-> what a member's wake-up writes under the journal's lock: nothing when the team is paused or stopped
    meanwhile; else the renewal decided before (`renewal`, as it was given) then the `wake-intent` -- its messages
    the debts it carries then the box at its head, `run` None for a run that opens, `beat`, `relance` and
    `allowance` written only when they are."""
    if state.season.paused or state.season.stopped:
        return []
    return [*([renewal] if renewal is not None else []),
            WakeIntent.made(tag=tag, agent=agent, path=path, task=task, run=run,
                            messages=[one.id for one in box] if relance is None else carried + [one.id for one in box],
                            continued=continued, **({"beat": beat} if beat is not None else {}),
                            **({"relance": relance[0]} if relance else {}),
                            **({"allowance": allowance} if allowance is not None else {}))]


def wake_launched_of(state: dict, started: dict, tag: str, agent: str, report: dict, born: str, refused: str) -> list:
    """-> the `wake-launched` of a launch the launcher reported: its run and pid, its rank in the run read on the
    state under the lock, the model and provider the season gives, the process space it was born in and the name
    refused when there are."""
    return [WakeLaunched.made(tag=tag, agent=agent, run=report.get("key"), pid=report.get("pid"),
                              launch=launches_of_run(state, str(report.get("key"))) + 1, **launch_kept(started, agent),
                              **({"space": born} if born else {}),
                              **({"name_refused": refused} if refused else {}))]
