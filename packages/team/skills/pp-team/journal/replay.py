"""The `journal` domain, layer `replay`: the composer of the folds, the snapshot, and the reader of the journal.

A definition belongs here when it composes the team's state from the journal's events, or turns the state into the
snapshot the journal keeps and back again. `replay` finds the last snapshot on the lines as they were read and restarts
there; it decodes into an `Event` only a line it folds, one after that snapshot, whose kind has a body in `BODIES` -- a
line without a key its body requires stops the replay with `KeyError`, as the fold of before did --; a line of any other
kind goes to the folds, and stays in the state, as it was read. It for each event calls the folds of its kind through
`FOLDS` -- the table of every domain's `<D>_FOLDS`, in the order season, task, rhythm, wake, budget, health --, then
sets the last event of the team and of its task; the folds write a working dictionary, and `replay` returns the state
composed of its six parts. The snapshot is packed through `plain`: `packed` reads each value on its part, by
attribute -- `WHERE` names the part of each key that `PLAIN` keeps as it is --, under the keys and in the order the
snapshot has always had. It is unpacked into the same working state a fold
writes: each event the state keeps -- `started`, `messages`, `intents`, `launched`, `done`, `deferred`, `ends`, `fails`,
`silences`, `halts` -- is decoded by `Event.of`, as a line the replay folds is, and a kind without a body stays the line
the snapshot kept; so a state, folded or unpacked, keeps events, and `packed` writes the same snapshot again. Each fold
lives in the `replay.py` of its domain.

The reader of the journal is a fold too, and lives here. `event_read` turns a line that `log` or `watch` reads into an
event: decoded for the three kinds whose body the reader reads -- `team-started`, `task`, `post` --, without a body for
any other kind, which is said as its line. So `log` does not decode the whole history, and a line that no version
wrote is printed as before. A damaged `post` or `task` stops `log` as it stops the replay. `said_so_far` gives the
context the reader starts from, with the keys of a working state: `started` and the messages are events, a task is
`{from, to, messages}`. `read_on` folds each event into it -- the start, each task, each post -- and returns what to
say: a post in the words of its debt (`worded_folded`), None for a kind no version writes any more (`DEAD`), the line
of any other event. It calls the twins of `task/replay.py`, like the other folds, and no rule.

Nothing here reads anything but the events, the snapshot and the context it is given, prints anything or writes to
disk.
"""
from __future__ import annotations

from declaration.model import RETIRED_LIMITS
from house.model import plain
from journal.model import BODIES, DEAD, PLAIN, WHERE, Event, TeamState
from season.replay import SEASON_FOLDS
from task.replay import TASK_FOLDS, cited_folded, task_folded, worded_folded
from rhythm.replay import RHYTHM_FOLDS
from wake.replay import WAKE_FOLDS, carrier_folded
from budget.replay import BUDGET_FOLDS
from health.replay import HEALTH_FOLDS


def packed(state: dict) -> dict:
    """-> the replayed state as JSON data, for ONE `snapshot` event: sets and tuples become
    lists, tuple keys and integer keys become rows (JSON would turn an integer key into its
    digits, and a reader asking by the id would find nothing). The messages of RESOLVED
    tasks are PRUNED unless the owner's box still reads them (a post to the owner, a post
    returned to the owner): no reader replays them -- the inboxes filter resolved tasks out, a reply cites
    an open task's post, a post the tick returned to a member is read at that member's next head alone -- and the
    pruning is what makes a long journal's state light."""
    tasks, wake = state.task, state.wake
    started = state.season.started
    owner = str(started.body.owner if started is not None else None)
    resolved = {task_id for task_id, one in tasks.tasks.items() if one.state == "resolved"}
    kept = {key: value for key, value in tasks.messages.items()
            if value.body.task not in resolved or value.body.to == owner or tasks.returned_to.get(key) == owner}
    return plain({**{key: getattr(getattr(state, WHERE[key]), key) for key in PLAIN},
                  "messages": {str(key): value for key, value in kept.items()},
                  "returned_to": [[key, to] for key, to in tasks.returned_to.items()],
                  "delivered": sorted(tasks.delivered),
                  "ended": sorted(wake.ended),
                  "failures": [[agent, task, count] for (agent, task), count in wake.failures.items()],
                  "terminals": sorted([agent, task] for agent, task in tasks.terminals),
                  "runs": [[member, carrier, run] for member, held in wake.runs.items() for carrier, run in held.items()],
                  "returned": sorted(tasks.returned),
                  "killed": sorted(wake.killed),
                  "kills": sorted([agent, task] for agent, task in wake.kills),
                  "launches_spent": sorted(one for one in state.budget.launches_spent if one is not None),
                  "reset": dict(wake.reset),
                  "resumed": dict(tasks.resumed),
                  "fell": sorted([agent, task] for agent, task in wake.fell),
                  "standing": sorted([agent, task] for agent, task in wake.standing),
                  "debts": [[key, value] for key, value in tasks.debts.items()],
                  "health": {member: dict(one) for member, one in state.health.health.items()},
                  "house": sorted(wake.house),
                  "read": sorted(tasks.read)})


def unpacked(data: dict) -> dict:
    """-> the state a `snapshot` event kept, back in its working types; a key a snapshot of an earlier
    version did not keep takes its empty value."""
    empty = {"fails": [], "routed": {}, "flow": {}, "deleting": False, "recurrences": {}, "silences": [], "halts": [],
             "quotas": {}, "stopped": None, "since": None,
             "context": {}}
    standing = data.get("standing") or []
    if isinstance(standing, dict):                   # a snapshot of before (team 1.4.7): member -> the task it stood on
        standing = list(standing.items())
    return kept_decoded({**{key: data.get(key, empty.get(key)) for key in PLAIN},
            "limits": {RETIRED_LIMITS.get(key, key): value                # a snapshot of before (team 0.39.0): its
                       for key, value in (data.get("limits") or {}).items()},   # bounds counted wake-ups
            "messages": {int(key): value for key, value in (data.get("messages") or {}).items()},
            "returned_to": {int(key): to for key, to in (data.get("returned_to") or [])},
            "total": float(data["total"] if data.get("total") is not None else data.get("cost") or 0.0),   # a
            #                                     snapshot of before (team 1.18): the cost of its season alone
            "delivered": set(data.get("delivered") or []),
            "ended": set(data.get("ended") or []),
            "failures": {(agent, task): count for agent, task, count in (data.get("failures") or [])},
            "terminals": {(agent, task) for agent, task in (data.get("terminals") or [])},
            "runs": runs_unpacked(data.get("runs") or [], data),
            "returned": set(data.get("returned") or []),
            "killed": set(data.get("killed") or []),
            "kills": {(agent, task) for agent, task in (data.get("kills") or [])},
            "launches_spent": set(data.get("launches_spent") or data.get("wakes_spent") or []),   # `wakes_spent`: a snapshot of before
            "reset": dict(data.get("reset") or {}),
            "resumed": dict(data.get("resumed") or {}),
            "fell": {(agent, task) for agent, task in (data.get("fell") or [])},
            "standing": {(agent, task) for agent, task in standing},
            "debts": ({int(key): value for key, value in data["debts"]} if "debts" in data
                      else debts_rebuilt(data)),
            "health": {member: dict(one) for member, one in (data.get("health") or {}).items()},
            "house": set(data.get("house") or []),
            "read": set(data.get("read") or [])})


KEPT_ONE = ("started",)                                              # the keys of a state that keep ONE event,
KEPT_BY_KEY = ("messages", "intents", "launched", "done")            # an event by its id, its tag or its task,
KEPT_LISTS = ("deferred", "ends", "fails", "silences", "halts")      # or a list of events


def kept_event(one):
    """-> an event a snapshot kept, decoded as a line the replay folds is: an `Event` when its kind has a body -- a
    required key missing raises `KeyError`, as on a line --, the dictionary as it was kept for any other kind."""
    if type(one) is not dict or BODIES.get(one.get("kind")) is None:
        return one
    return Event.of(one)


def kept_decoded(state: dict) -> dict:
    """-> the working state `unpacked` makes, each event it keeps (`KEPT_ONE`, `KEPT_BY_KEY`, `KEPT_LISTS`) decoded by
    `kept_event`, its line kept: `packed` writes the same snapshot again."""
    for key in KEPT_ONE:
        state[key] = kept_event(state.get(key))
    for key in KEPT_BY_KEY:                          # a key a snapshot did not keep stays as it was read (`None`)
        if type(state.get(key)) is dict:
            state[key] = {at: kept_event(one) for at, one in state[key].items()}
    for key in KEPT_LISTS:
        if type(state.get(key)) is list:
            state[key] = [kept_event(one) for one in state[key]]
    return state


def debts_rebuilt(data: dict) -> dict:
    """-> the debts a snapshot of team 0.32.2 or before did not keep, rebuilt from the messages it kept: a
    `do` or an `ask` to a member on an open task owes until an answer of its member cites it."""
    messages = {int(key): kept_event(value) for key, value in (data.get("messages") or {}).items()}   # decoded as
    started = kept_event(data.get("started"))        # `kept_decoded` decodes them: the twins read the events
    agents = (started.body.agents if started is not None else None) or {}
    open_tasks = {key for key, one in (data.get("tasks") or {}).items() if one.get("state") == "open"}
    debts: dict = {}
    state = {"messages": {}, "started": started}
    for key in sorted(messages):
        one = messages[key]
        state["messages"][key] = one
        if one.body.verb in ("do", "ask") and one.body.to in agents and one.body.task in open_tasks:
            debts[key] = None
        cited = cited_folded(state, one)
        if cited is not None and debts.get(cited, "x") is None and messages[cited].body.to == one.body.sender:
            debts[cited] = key
    return debts


def runs_unpacked(rows: list, data: dict) -> dict:
    """-> the runs each member holds by CARRIER, from a snapshot's rows `[member, carrier, run]`; a row
    `[member, run]` of team 1.0.0 goes to the carrier of the task of the member's last intent."""
    found: dict = {}
    for row in rows:
        if len(row) == 3:
            found.setdefault(row[0], {})[row[1]] = row[2]
            continue
        last = max((one for one in (data.get("intents") or {}).values() if one.get("agent") == row[0]),
                   key=lambda one: int(one.get("id") or 0), default=None)
        if last is not None:
            found.setdefault(row[0], {})[carrier_folded(data, last.get("task"))] = row[1]
    return found


def replay(events: list[dict]) -> dict:
    """-> the team's STATE, computed from its journal alone: the last `team-started`, the tasks
    with their state and their messages, every message by its id, the messages delivered (the
    ones an intent carried, the ones returned, a stop to an agent whose wake-up was killed), the
    intents and their launches, ends, failures and kills, the terminals, the delegations, the
    runs each member holds, ONE per CARRIER of its tasks (`carrier_of`) -- the last that answered there, readable or not --, the stops posted
    to each agent, the results, the owner's cursor (`inbox-seen`), the members `team reset` took
    their run from (`run-reset`, the member's run dropped), the (member, task) whose terminal a final
    failure wrote, the starts counted (`seasons` -- each a SEASON: its limits TEAM.md's under the season's own,
    the cost, `budget-spent` and `launches-spent` afresh, the members' runs kept), the bounds `team budget` raised (`budget-raised`: the limits raised, `budget_spent`
    lifted), and the last `resumed` of each task -- `team resume` opens the task again, sets its
    members' failures to zero, drops the terminals its final failures wrote and lifts `launches-spent`:
    the task's counters count from there. A journal written by team 0.39.0 counted wake-ups: its
    `team-started.limits` and `season` keys `launches` and `budget-launches` are read as `launches` and
    `budget-launches`, its `wakes-spent` as `launches-spent`, its `budget-raised {wakes}` as `{launches}`;
    nothing is written under those names again. The run a failed launch leaves: `wake-failed {state}`, read at
    agent's face, says whether it STANDS (relaunched while its retries last) or is parked; a final failure stands
    nobody. A `stop` posted to an agent whose run stands on the task is not delivered at once: it rides the head
    of one more launch (`dues`). A ceremony's task rung at hand keeps who rang it (`by`, from
    its `ceremony-due`). The team is PAUSED from a `paused` to its `unpaused` (`paused` `{by, at, id}`,
    else None). Each task keeps its `text` and its `last` event `{id, kind, at}` -- the last
    event that belongs to it (`task_folded`). The DEBTS: each `do` or `ask` posted to a member on an open
    task opens one (`None`), the first answer of that member that cites it settles it (the answer's id;
    `closed` when the task resolves); the delegations are the `do`s between members, and a member is
    TERMINAL on a task once its last `do` there is answered -- by it, or in its place after a final failure
    (`delegation` and `terminal` events of a journal written before team 0.33.0 read the same). A `launch-missing` counts no failure: nothing was launched. A
    post to a principal is delivered at its writing: the principal's box reads it, and it is
    never returned. A task stops by its `stopped` event, whatever holds it (a `stop` post stops
    it too: a journal written before the event). The HEALTH of each member (`health`, the failure detector
    ◇P): `falls` its final failures in a row since it last answered -- on a task not stopped, a `budget-share`
    apart -- and `at` the hour of the last, the member SUSPECTED while `falls` stands; a launch the HOUSE refused
    (`wake-failed {house: true}`, never final) counts no failure and no fall (`house`: its tags); a wake-up that ends
    answered makes a suspected member REPENT (`falls` back to 0, its failures counted afresh, `repents` one
    more: one silent retry more); `team resume --task` ends the suspicion of the task's members, a season ends
    every suspicion. A `silence {agent, task, passages}` the tick wrote (row 115) is a fall too (`cause: silence`),
    lifted by a routed act of the member alone -- never by a launch that ends saying nothing. The tick's
    answer in a suspected member's place takes the message it answers out of the member's inbox (`delivered`): under
    `suspected`, a message a `wake-intent` of the member carried; under `returned`, a message none carried, which is
    RETURNED to its author as well (`returned`, `returned_to`). A `suspected` alone, as a journal of before writes it
    on both, reads as a message carried. The RECURRENCES the owner posted
    (`recurrence {R<n>}`) keep the periods they sounded -- by an occurrence, a task that carries `recurrence` and
    `period`, or by a `recurrence-skipped` --, their last occurrence, their stop (`recurrence-stopped`) and their
    suspension (`recurrence-paused`, `paused {by, at, id}`, lifted by `recurrence-resumed`, which replaces `since` and
    counts its first slot one later); a `recurrence-changed` replaces its `when` and its `since`, its context limit
    (`context`) or its text, the periods sounded kept: a period is its date, counted once; a recurrence born of a task (`recurrence {task}`) has that task
    for its last occurrence; a `run-renewed` detaches the run it names from its carrier -- its recurrence, its
    ceremony or its task --: the member's next wake-up there opens a new one. A task keeps the context limit of its
    birth (`context`, None without one). Each member's CONTEXT is the `context` of its last `wake-ended` (`None` without one, or for a journal written
    before team 0.54.0). The season under way ENDS at its `season-stopped` (`stopped` `{by, at, id, tasks,
    recurrences}`, None in season or before a start; its pause ends with it); the next `team-started` opens the next
    one, and its `since` -- written when it follows a stop -- is the hour nothing before is caught up from: each
    recurrence counts from it, as after its resume, and an `every` ceremony owes no period whose hour is not after it."""
    state: dict = {"started": None, "tasks": {}, "messages": {}, "delivered": set(),
                   "intents": {}, "launched": {}, "ended": set(), "failures": {}, "terminals": set(),
                   "delegations": [], "runs": {}, "done": {}, "returned": set(),
                   "schedule": True,
                   "limits": {}, "cost": 0.0, "total": 0.0, "budget_spent": False, "deferred": [], "returned_to": {},
                   "killed": set(), "kills": set(), "stops": {}, "seen": 0, "read": set(),
                   "launches_spent": set(), "rung": {}, "ends": [], "fails": [], "last": None, "reset": {},
                   "resumed": {}, "fell": set(), "seasons": 0, "paused": None, "debts": {}, "health": {},
                   "routed": {}, "flow": {}, "standing": set(), "house": set(),
                   "deleting": False, "recurrences": {},
                   "silences": [], "context": {}, "halts": [], "quotas": {}, "stopped": None, "since": None}
    floor = 0
    snap = next((one for one in reversed(events) if one.get("kind") == "snapshot"), None)   # on the lines as read
    if snap is not None:                           # the replay restarts at the LAST snapshot
        snap = Event.of(snap)
        state = unpacked(snap.body.state or {})
        floor = int(snap.body.upto or 0)
    state["rung_by"], state["carried"] = {}, dict(state.get("intents") or {})   # the fold of task's memories, unpacked
    for one in events:
        line = one if type(one) is dict else one.line   # the line it was read from: read as the dictionary it is
        kind = line.get("kind")
        if kind == "snapshot" or int(line.get("id") or 0) <= floor:
            continue
        made = BODIES.get(kind) if line is one else None
        if made is not None:                        # a line it folds, of a typed kind: decoded into its event -- a
            one = Event(line, made.of(line))        # line without a required key raises here, as its fold did
        state["last"] = {"id": line.get("id"), "kind": kind, "at": line.get("at")}
        folds = FOLDS.get(kind)
        if folds:                                   # `before`: the state as it stood before the event, for a part
            before = {"started": state["started"]} if kind == "team-started" else state   # after the fold's own --
            for folded in folds:                    # the state itself, but for the season a team-started replaces
                folded(state, before, one)
        task = state["tasks"].get(task_folded(state, line))   # its task, read in the line: no passage through the event
        if task is not None:
            task["last"] = {"id": line.get("id"), "kind": kind, "at": line.get("at")}
    del state["rung_by"], state["carried"]
    return TeamState.of(state)


def said_so_far() -> dict:
    """-> what a reader of the journal keeps of the events it read, to say the next ones (`read_on`)."""
    return {"started": None, "messages": {}, "tasks": {}}


def event_read(line: dict) -> Event:
    """-> the event a line of the journal carries, as its reader reads it (`read_on`): decoded for the three kinds whose
    body it reads -- `team-started`, `task`, `post` --, without a body for any other, which it says as its line."""
    return Event.of(line) if line.get("kind") in ("team-started", "task", "post") else Event(line)


def read_on(context: dict, one: Event) -> dict | None:
    """-> one event as `log` and `watch` say it, `context` -- what the events before it said -- kept up to date: a post
    in the words of the debt (`worded_folded`), None for an event no version writes any more (`DEAD`), any other as
    its line says it."""
    kind = one.kind
    if kind == "team-started":
        context["started"] = one
    elif kind == "task":
        body = one.body
        context["tasks"][body.task] = {"from": body.sender, "to": body.to, "messages": []}
    elif kind == "post":
        held = context["tasks"].get(one.body.task)
        if held is not None and one.id not in context["messages"]:
            held["messages"].append(one.id)
        context["messages"][one.id] = one
        return worded_folded(context, one)
    return None if kind in DEAD else one.line


PARTS = (SEASON_FOLDS, TASK_FOLDS, RHYTHM_FOLDS, WAKE_FOLDS, BUDGET_FOLDS, HEALTH_FOLDS)   # in the order of the domains
FOLDS = {kind: tuple(part[kind] for part in PARTS if kind in part)   # a kind -> its folds, in the order of the domains
         for kind in set().union(*PARTS)}
