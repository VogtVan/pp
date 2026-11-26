"""The `status` domain, layer `verbs`: the command line of the verbs that say where the teams stand.

A definition belongs here when it plays such a verb: it prints a team's status as text or as JSON, one line per team, or
the house's roster, and refuses with the usage. A verb is where the skill meets its caller: it may print, end the call
and use every other layer.
"""
from __future__ import annotations

import json
from pathlib import Path

from house.model import TEAMS, TEAM_DOC
from house.rules import journal_of, team_doc
from house.store import caller, machine_house, named_team, refuse, tick_now
from house.verbs import flags
from status.model import ROSTER_FLAGS, STATUS_FLAGS
from declaration.faces import labelled
from declaration.acts import declared_members, team_description, team_name
from season.rules import path_of, schedule_seconds
from season.store import changed_since_start, required_by_team
from documents.store import in_team_run, template_description
from task.rules import inbox, owed_by, owner_box, worded
from task.faces import counted
from rhythm.rules import recurrence_next
from rhythm.faces import said_when
from wake.rules import launched_at, run_of, suspicion_of
from budget.rules import share_of
from net.acts import schedule_face
from journal.store import state_of
from journal.acts import faced
from status.faces import team_badges
from status.acts import roster_of, status_object


def status_of(root: Path, conductor, name: str) -> int:
    """`team status <name>`: the state read from the journal -- nothing written."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = faced(root, conductor, name)
    started = state.season.started
    if started is None:
        print(f"team {name} · declared, not started")
        return 0
    principals = list(started.body.principals or [])
    owner = str(started.body.owner)
    print(f"team {name} · owner {owner} · principals {', '.join(principals) or '—'}"
          f" · started {started.at} (#{started.id})")
    paused = state.season.paused
    if paused:
        print(f"paused since {paused.get('at')} by {paused.get('by')} (#{paused.get('id')}) · nobody is woken "
              f"until team resume")
    if state.season.stopped:
        print(f"off season since {state.season.stopped.get('at')} by {state.season.stopped.get('by')} "
              f"(#{state.season.stopped.get('id')}) · nobody is woken until team start")
    if changed_since_start(root, name, started):
        print("TEAM.md changed since the start · the body reaches the members at their next exchange · "
              "the front matter waits a stop then a start")
    limits = state.season.limits
    if limits:
        said = [f"parallel {limits['parallel']}" if "parallel" in limits else "",
                f"budget {limits['budget']:g} USD" if "budget" in limits else "",
                f"retries {limits['retries']}" if "retries" in limits else "",
                f"timeout {limits['timeout']:g}" if "timeout" in limits else "",
                f"launches {limits['launches']}" if "launches" in limits else "",
                f"budget-launches {limits['budget-launches']}" if "budget-launches" in limits else "",
                f"suspect-max {limits['suspect-max']} s" if "suspect-max" in limits else "",
                f"silence {limits['silence']}" if "silence" in limits else ""]
        print("limits · " + " · ".join(one for one in said if one))
    seasons = int(state.season.seasons or 1)
    own = started.line.get("season") or {}           # the season as the line says it: the body translates its keys
    if seasons > 1 or own or started.body.profiles:
        print(f"season {seasons} · since {started.at}"
              + (f" · budget {own['budget']:g} USD" if own.get("budget") is not None else "")
              + (f" · budget-launches {own['budget-launches']}" if own.get("budget-launches") is not None else "")
              + (f" · silence {own['silence']}" if own.get("silence") is not None else "")
              + (f" · profiles {', '.join(started.body.profiles or {})}" if started.body.profiles else "")
              + f" · cost {state.budget.cost:g} USD, {float(state.budget.total or 0.0):g} USD over every season")
    retired = (started.body.launch or {}).get("max_budget_usd")
    if retired is not None:
        print(f"launch · the start's --max-budget-usd {float(retired):g} is never passed: a wake-up's share is "
              "computed on budget:")
    seconds = schedule_seconds(started)
    if seconds is None:
        print("schedule · off")
    else:
        face = schedule_face(root, name, started, state)
        print(f"schedule · every {seconds} s · " + ("timer armed" if face["timer"] else "no timer") + " · relaunch "
              + ("laid" if face["relaunch"] else "absent" + (f" ({face['reason']})" if face["reason"] else "")))
    print(f"cost {state.budget.cost:.2f} USD" + (" · budget spent" if state.budget.budget_spent else ""))
    share = share_of(state)
    if share is not None:
        print(f"budget {share['spent']:g}/{share['cap']:g} USD · reserved {share['reserved']:.2f} · "
              f"left {share['left']:.2f}")
    for one in state.rhythm.recurrences.values():
        last = state.task.tasks.get(one.last or "")
        print(f"{one.id}" + (f" {one.name}" if one.name else "")
              + f" · every {said_when(one.when)} · to {one.to}"
              + (f" · from {one.task}" if one.task else "")
              + (f" · context {one.context}%" if one.context is not None else "")
              + (f" · stopped #{one.stopped['id']}" if one.stopped
                 else f" · paused #{one.paused['id']}" if one.paused else f" · next {recurrence_next(one, tick_now())}")
              + (f" · last {last.id} {last.state}" if last is not None else ""))
    for task in state.task.tasks.values():
        resumed = state.task.resumed.get(task.id) if task.state == "open" else None
        print(f"{task.id}" + (f" {task.name}" if task.name else "") + f" · {task.state}"
              + (f" · resumed #{resumed}" if resumed else "") + (f" · of {task.recurrence}" if task.recurrence else "")
              + f" · to {task.to} · {len(task.messages)} message(s)")
    for agent in started.body.agents or {}:
        waiting = inbox(state, agent)
        line = (f"{agent} · {path_of(state, agent)} · inbox {len(waiting)}"
                + (f" ({counted([worded(state, one) for one in waiting])})" if waiting else ""))
        held = run_of(state, agent)
        if held is not None:
            key, how, tasks = held
            line += f" · run {key} · {how}" + (f" since {launched_at(state, agent)}" if how == "running" else "")
            line += " · on " + " ".join(tasks) if tasks else ""
        carried = state.wake.runs.get(agent) or {}
        if len(carried) > 1:                                 # one run per carrier: each said
            line += " · runs " + " ".join(f"{carrier} {run}" for carrier, run in carried.items())
        owed = owed_by(state, agent)
        if owed:
            line += f" · owes {len(owed)}"
        suspicion = suspicion_of(state, agent)
        if suspicion is not None:
            line += f" · suspected · tried again at {suspicion['until']:%H:%M:%S}"
        print(line)
    box = owner_box(state, owner)
    print(f"owner inbox {len(box)}")
    for one in (worded(state, one) for one in box):
        print(f"  #{one['id']} {'question' if one.get('verb') == 'ask' else one.get('verb')} from {one.get('from')} "
              f"on {one.get('task')}" + (f" · about {one['about']}" if one.get("about") else "")
              + (" · returned" if state.task.returned_to.get(one["id"]) == owner else ""))
    last = state.season.last or {}
    print(f"last event #{last.get('id')} {last.get('kind')} at {last.get('at')}")
    return 0


def status(rest: list[str]) -> int:
    """`team status [<name>] [--json]`: the text the owner reads, or under `--json` the face a
    program reads -- ONE object for the team named, one line per team declared without a name, each with
    `required`: the packages a member may not switch off (`required_by_team`, sorted), read once; without a name each
    line also says `declared_members [{member, path, description}]` as its `TEAM.md` declares them (`[]` when it is refused).
    Read in the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, rest = named_team(conductor, rest)
    as_json = flags(rest, STATUS_FLAGS)["json"]
    if name is not None:
        if not as_json:
            return status_of(root, conductor, name)
        if not team_doc(root, name).is_file():
            refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
        print(json.dumps({**status_object(root, conductor, name, faced(root, conductor, name)),
                          "name": team_name(root, conductor, name),
                          "description": team_description(root, conductor, name),
                          "required": sorted(required_by_team(root, conductor))}, ensure_ascii=False))
        return 0
    home = root.parent / TEAMS
    found = sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else []
    if as_json:
        needed = sorted(required_by_team(root, conductor)) if found else []
        template = template_description(root, conductor) if found else ""
        for one in found:
            print(json.dumps({**team_badges(one, faced(root, conductor, one)),
                              "name": team_name(root, conductor, one),
                              "description": team_description(root, conductor, one),
                              "declared_members": declared_members(root, conductor, one, template),
                              "required": needed},
                             ensure_ascii=False))
        return 0
    if not found:
        print(f"pp-team: no team declared under {home} yet.")
        return 0
    for name in found:
        state = state_of(journal_of(root, name))
        if state.season.started is None:
            print(f"{labelled(team_name(root, conductor, name), name)} · declared, not started")
            continue
        by_state: dict[str, int] = {}
        for task in state.task.tasks.values():
            by_state[task.state] = by_state.get(task.state, 0) + 1
        tally = ", ".join(f"{count} {kind}" for kind, count in by_state.items()) or "none"
        last = state.season.last or {}
        print(f"{labelled(team_name(root, conductor, name), name)} · {len(state.task.tasks)} task(s): {tally} · "
              f"last event #{last.get('id')} {last.get('kind')} "
              f"at {last.get('at')}")
    return 0


def roster_verb(rest: list[str]) -> int:
    """`team roster [--json]`: the teams of the house and their live recurrences, the caller's part in each -- read
    at the house `machine_house()` resolves; nothing printed without a team, nor in a run a team opened. Nothing
    written, no lock, never a tick."""
    root, conductor = machine_house()
    asked = flags(rest, ROSTER_FLAGS)
    meta = caller()
    if meta is not None and in_team_run(root, conductor, meta):
        return 0
    found = roster_of(root, conductor, meta)
    if not found["teams"]:
        return 0
    if asked["json"]:
        print(json.dumps(found, ensure_ascii=False))
        return 0
    cell = lambda value: "—" if value in (None, "") else " ".join(str(value).split()).replace("|", "\\|")
    lines = ["**The teams of the house**", "", "| team | what it does | root | members | state | your part |",
             "|---|---|---|---|---|---|"]
    lines += [f"| {cell(one['name'])} | {cell(one['description'])} | {cell(one['root'])} | {one['members']} | "
              f"{cell(one['state'])} | {cell(one['membership'])} |" for one in found["teams"]]
    if found["recurrences"]:
        lines += ["", "**The recurrences**", "", "| team | id | what it does | when | next | paused |",
                  "|---|---|---|---|---|---|"]
        lines += [f"| {cell(one['team'])} | {cell(one['id'])} | {cell(one['description'])} | {cell(one['when'])} | "
                  f"{cell(one['next_due'])} | {'yes' if one['paused'] else 'no'} |" for one in found["recurrences"]]
    print("\n".join(lines))
    return 0
