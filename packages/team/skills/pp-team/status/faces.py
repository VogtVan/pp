"""The `status` domain, layer `faces`: how a team's state is put into words a program reads.

A definition belongs here when it turns the state it is given into words -- the line of a team without a name, the
team's state and what it waits on -- and gives them back without printing them. It reads nothing: the one object of
`status --json`, which reads the season and the records, is composed by `status/acts.py`. Of what `waiting()` returns,
`team_state` reads a question, an event, by attribute, and a notice, the dictionary `worded()` makes, by key.
"""
from __future__ import annotations

from season.rules import season_now
from season.faces import paused_face
from task.rules import dues, loud, members_of, waiting
from wake.rules import open_intents, played, suspicion_of




def team_badges(name: str, state: dict) -> dict:
    """-> one line of `team status --json` without a name: the team, its start, its state and what it
    waits on, its tasks by state, the wake-ups under way, what waits for the owner as the inbox counts it
    (`waiting()`: `asks` the agents' questions, `notices` the team's notices, `done` the tasks resolved not seen),
    the last event, its season (`season_now`) -- none for a team never started."""
    started = state.season.started
    if started is None:
        return {"team": name, "started": None, **team_state(state)}
    by_state = {"open": 0, "stopped": 0, "resolved": 0}
    for task in state.task.tasks.values():
        by_state[task.state] = by_state.get(task.state, 0) + 1
    waits = waiting(state)
    return {"team": name, "started": {"at": started.at, "id": started.id},
            **team_state(state), "paused": paused_face(state), "tasks": by_state, "running": len(played(state)),
            "asks": len(waits["questions"]), "notices": len(waits["notices"]), "done": len(waits["done"]),
            "last": state.season.last, "season": season_now(state)}


def team_state(state: dict) -> dict:
    """-> `{state, waiting_on}`, the team as its face says it -- derived from the replay, never written:
    `never` before a start, `paused` from a `team pause` to its resume (above every other state),
    `working` while a wake-up plays -- a launch the house sees (`played`) --, `idle` when no task is open, else `waiting`
    with every guard that holds: `reap` first (a launch nobody holds, its end not read: the next tick reaps it), then, in the
    order `woken_on` judges them -- `launches` (an open task launches-spent), `budget` (money or budget-launches
    spent) --, then `owner` (a question to the owner, or a notice that holds a member, on an open task), `suspected` (a
    member of an open task is suspected: its final failure stands), `due` (messages due: the next tick launches)."""
    if state.season.started is None:
        return {"state": "never", "waiting_on": []}
    if state.season.paused:
        return {"state": "paused", "waiting_on": []}
    if played(state):
        return {"state": "working", "waiting_on": []}
    open_tasks = [task for task, one in state.task.tasks.items() if one.state == "open"]
    if not open_tasks:
        return {"state": "idle", "waiting_on": []}
    members = list(state.season.started.body.agents or {})
    due = {task for member in members for task, box in dues(state, member) if loud(state, box)}
    holds = []
    if any(one.body.task in open_tasks for one in open_intents(state)):   # none plays: every one of them is gone
        holds.append("reap")
    if any(task in state.budget.launches_spent for task in open_tasks):
        holds.append("launches")
    if state.budget.budget_spent:
        holds.append("budget")
    waits = waiting(state)
    if (any(one.body.task in open_tasks for one in waits["questions"])
            or any(one.get("task") in open_tasks for one in waits["notices"] if one["awaits"])):
        holds.append("owner")
    if any(suspicion_of(state, member) is not None for task in open_tasks for member in members_of(state, task)):
        holds.append("suspected")
    if not state.budget.budget_spent and any(task not in state.budget.launches_spent for task in due):
        holds.append("due")
    return {"state": "waiting", "waiting_on": holds}
