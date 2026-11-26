"""The `status` domain, layer `acts`: the roster of the house and the face of one team, each read as it plays.

A definition belongs here when it chains the reads of other domains for a status verb: every team the house declares,
read as it plays, with its live recurrences and the part the caller plays in each; and the one object of `status
--json`, which reads the season, the launches since the start and a member's vector before it composes the face
(`status_object`). Only verbs call it. It may use the lower layers of any domain.
"""
from __future__ import annotations

from pathlib import Path

from house.model import Declined, TEAMS, TEAM_DOC
from house.rules import agent_meta
from house.store import tick_now
from season.model import CLOSED
from declaration.acts import team_description, team_name, team_played
from season.rules import path_of, season_now, set_of
from season.faces import paused_face
from season.store import changed_since_start, packages_at
from season.acts import launch_face, season_played
from documents.store import member_vector
from task.rules import answer_of_debt, holders, inbox, owed_by, owner_box, waiting, worded
from rhythm.rules import due_period, next_due, recurrence_next, recurrence_period
from rhythm.faces import said_when
from wake.rules import carrier_name, cursor_of, last_launch, run_of, running_on, shared
from wake.faces import quota_face, run_face
from budget.rules import share_of
from budget.acts import launched_since_start
from health.rules import silence_limit, silence_of, silent_tasks
from health.faces import health_face
from net.acts import schedule_face
from journal.acts import faced
from status.faces import team_state


def roster_of(root: Path, conductor, meta: Path | None) -> dict:
    """-> `{teams, recurrences}` of the house: each team declared under `teams/` -- its row as the team plays
    (`team_played`: its members, its root, `TEAM.md`'s or its template's form's; none of a declaration refused), the part
    the instance `meta` plays in it by the paths of `agents:` --, then each live recurrence of a started team."""
    home = root.parent / TEAMS
    names = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    teams, recurrences = [], []
    for name in names:
        try:
            team = team_played(root, conductor, name)
            agents, head = list(team.agents.items()), team.root
        except (Declined, OSError, SystemExit):
            agents, head = [], None
        mine = [member for member, path in agents
                if meta is not None and meta != root.resolve() and agent_meta(root, path).resolve() == meta]
        part = (f"root ({head})" if head in mine else
                f"member ({', '.join(mine)})" if mine else "—")
        state = faced(root, conductor, name)
        teams.append({"team": name, "name": team_name(root, conductor, name),
                      "description": team_description(root, conductor, name), "root": head,
                      "members": len(agents), "state": team_state(state)["state"], "membership": part})
        for one in state.rhythm.recurrences.values():
            if one.stopped is None:
                recurrences.append({"team": name, "id": one.id, "description": one.description or one.name,
                                    "when": said_when(one.when) if one.when else None,
                                    "next_due": recurrence_next(one, tick_now()) if not one.paused else None,
                                    "paused": bool(one.paused)})
    return {"teams": teams, "recurrences": recurrences}


def status_object(root: Path, conductor, name: str, state: dict) -> dict:
    """`team status <name> --json`: the team as ONE JSON-ready object, every field read from the
    state the text reads -- the team, its state and what it waits on (`team_state`), its season -- `state`
    `running` or `stopped`, and `stopped {at, by, id}` off season -- and the launch its next wake-up gets, its cost (`cost`, the season's) and `total` (every season's, a snapshot of before
    counting from its own season), its tasks (text, last event, holders, delegations, the wake-ups
    under way on it, their cost, the hour of its birth `at` and of its end `ended`, null while it is open), its
    members (run, state, their role keys `roles` -- the keys of the season's `roles:` that name the member, in the
    order declared, `[]` without one --, their launch, their runs by carrier -- each its own state, hour and context
    (`run_face`) --, the packages their run plays, what waits for
    them, the answers of the others they have not seen, and `vector`, `team-member:<team>/<member>`, when the season's view
    of the member holds a document of a role -- absent otherwise), its ceremonies (the next ring, whether the next tick rings, the last ring
    and who answered it), the owner's box and what still waits for them. `{team, started: null, state:
    "never", waiting_on: []}` for a team never started."""
    started = state.season.started
    if started is None:
        return {"team": name, "started": None, **team_state(state)}
    owner = str(started.body.owner)
    launch = launch_face(root, conductor, started)
    tasks = []
    for task in state.task.tasks.values():
        tasks.append({"id": task.id, "name": task.name, "text": task.text, "last": task.last,
                      "at": task.at, "ended": task.ended if task.state in CLOSED else None,
                      "state": task.state, "from": task.sender, "to": task.to,
                      "ceremony": task.ceremony, "period": task.period,
                      "recurrence": task.recurrence,
                      "messages": len(task.messages), "resumed": state.task.resumed.get(task.id),
                      "cost": round(float(task.cost or 0.0), 6),
                      "holders": holders(state, task) if task.state != "resolved" else [],
                      "dos": [{"id": one["id"], "from": one["from"], "to": one["to"],
                               "answered": answer_of_debt(state, one["id"])}
                              for one in state.task.delegations if one["task"] == task.id],
                      "running": running_on(state, task.id)})
    members = []
    held = started.body.roles or {}
    for member in started.body.agents or {}:
        run, how, carried = run_of(state, member) or (None, None, [])
        last = last_launch(state, member) if how == "running" else None
        current = run if run not in (None, "?", "—") else None   # the run of its last launch
        cursor = cursor_of(state, member, current, 10 ** 12)
        members.append({"member": member, "path": path_of(state, member), "run": run, "how": how,
                        "roles": [key for key, names in held.items() if member in names],
                        "since": last.at if last is not None else None, "tasks": carried,
                        "owes": [{"id": key, "verb": state.task.messages[key].body.verb,
                                  "from": state.task.messages[key].body.sender, "task": state.task.messages[key].body.task}
                                 for key in owed_by(state, member)],
                        "silence": [{"task": task, "passages": silence_of(state, member, task),
                                     "limit": silence_limit(state, member)} for task in silent_tasks(state, member)],
                        "health": health_face(state, member), "quota": quota_face(state, member, tick_now()),
                        "context": state.wake.context.get(member),
                        "launch": launch_face(root, conductor, started, member),
                        "runs": [{"carrier": carrier, "run": key, "name": carrier_name(state, name, carrier),
                                  **run_face(state, member, key)}
                                 for carrier, key in (state.wake.runs.get(member) or {}).items()],
                        "packages": packages_at(root, conductor, path_of(state, member), current,
                                                set_of(season_played(root, conductor, started, member)))["packages"],
                        "pending": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"),
                                     "task": one.get("task")} for one in (worded(state, one) for one in inbox(state, member))],
                        "unseen": [{"member": one.body.agent,
                                    "task": intent.body.task if (intent := state.wake.intents.get(one.body.tag)) is not None
                                    else None, "id": one.id}
                                   for one in shared(state, member, cursor)],
                        **({"vector": vector} if (vector := member_vector(root, conductor, name, started, member))
                           else {})})
    ceremonies = []
    for ceremony in started.body.ceremonies or []:
        rings = [task for task in state.task.tasks.values() if task.ceremony == ceremony["name"]]
        last = rings[-1] if rings else None
        ceremonies.append({"name": ceremony["name"], "mode": ceremony["mode"], "when": ceremony.get("when"),
                           "after": ceremony.get("after"), "participants": list(ceremony["participants"]),
                           "facilitator": ceremony["facilitator"], "quorum": ceremony.get("quorum"),
                           "next_due": next_due(ceremony, state, tick_now()),
                           "due": due_period(ceremony, state, tick_now()) is not None,
                           "last": None if last is None else {"period": last.period, "task": last.id,
                                                               "state": last.state, "by": last.by},
                           "progress": [] if last is None else
                           [{"member": one, "answered": (one, last.id) in state.task.terminals}
                            for one in ceremony["participants"]]})
    recurrences = []
    for one in state.rhythm.recurrences.values():
        last = state.task.tasks.get(one.last or "")
        recurrences.append({"id": one.id, "name": one.name, "text": one.text, "from": one.sender,
                            "to": one.to, "when": one.when, "since": one.since,
                            "context": one.context, "description": one.description,
                            "task": one.task, "next_due": recurrence_next(one, tick_now()),
                            "due": recurrence_period(one, tick_now()) is not None,
                            "stopped": one.stopped, "paused": one.paused,
                            "last": None if last is None else {"period": last.period, "task": last.id,
                                                               "state": last.state}})
    waits = waiting(state)
    return {"team": name, "owner": owner, "principals": list(started.body.principals or []),
            "root": started.body.root,
            "started": {"at": started.at, "id": started.id}, **team_state(state),
            "paused": paused_face(state),
            "season": {**season_now(state), "at": started.at,
                       **({"stopped": {key: state.season.stopped.get(key) for key in ("at", "by", "id")}}
                          if state.season.stopped else {}),
                       "budget": (started.line.get("season") or {}).get("budget"),
                       "budget-launches": (started.line.get("season") or {}).get(   # `budget-wakes`: a season of before
                           "budget-launches", (started.line.get("season") or {}).get("budget-wakes"))}, "launch": launch,
            "changed": changed_since_start(root, name, started), "limits": dict(state.season.limits),
            "schedule": schedule_face(root, name, started, state),
            "cost": round(state.budget.cost, 6), "total": round(float(state.budget.total or 0.0), 6),
            "budget_spent": state.budget.budget_spent, "budget": share_of(state),
            "launches": {"launched": launched_since_start(root, state), "bound": state.season.limits.get("budget-launches")},
            "last": state.season.last, "tasks": tasks, "members": members, "ceremonies": ceremonies,
            "recurrences": recurrences,
            "owner_inbox": [{"id": one["id"], "verb": one.get("verb"), "from": one.get("from"), "about": one.get("about"),
                             "task": one.get("task"), "returned": state.task.returned_to.get(one["id"]) == owner}
                            for one in (worded(state, one) for one in owner_box(state, owner))],
            "waiting": {"questions": [{"id": one.id, "verb": one.body.verb, "from": one.body.sender,
                                       "task": one.body.task} for one in waits["questions"]],
                        "notices": [{"id": one["id"], "from": one.get("from"), "about": one.get("about"),
                                     "task": one.get("task"), "awaits": one["awaits"]} for one in waits["notices"]],
                        "infos": [{"id": one.id, "from": one.body.sender, "task": one.body.task}
                                  for one in waits["infos"]],
                        "done": [one.body.task for one in waits["done"]], "returned": list(waits["returned"])}}
