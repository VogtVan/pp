"""The `task` domain, layer `verbs`: the command line of the verbs that post to a team and read its tasks.

A definition belongs here when it plays such a verb: it posts a message or a new task, takes back a task a guard
stopped, prints a task's result or the owner's inbox as lines or as JSON, marks what the owner has read, and refuses
with the usage. What `post`, `inbox --seen` and `resume --task` write is decided by `task/rules.py`: the verb reads
its flags, the hour and the budget, hands them to the decisions, writes what they compose, and says the sentence of
each refusal they decline; the recurrence `post` makes is composed by `recurrence_posted` (`rhythm/rules.py`). A
verb is where the skill meets its caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

import json

from house.model import TEAMS, TEAM_DOC, USAGE, Declined
from house.rules import journal_of, team_doc, vector_formed
from house.store import caller, house, machine_house, named_team, owner_of, refuse, tick_now
from house.verbs import flags
from template.model import ALL
from task.model import INBOX_FLAGS, POST_FLAGS, RESUMED, RESUME_FLAGS
from declaration.faces import labelled
from declaration.acts import team_name
from season.rules import limit_of
from season.faces import off_season
from season.verbs import unpause
from documents.store import in_team_run
from task.rules import (inbox_seen_decided, named, post_checked, post_decided, resume_checked,
                        resume_decided)
from task.faces import inbox_line, inbox_object, principal_unknown
from rhythm.rules import every_of, recurrence_description, recurrence_posted
from rhythm.faces import said_when
from rhythm.verbs import recurrence_resumed
from wake.verbs import quota_lifted
from budget.acts import spent
from net.acts import netted
from journal.faces import deleting_said
from journal.store import state_of, written
from tick.rules import netless
from tick.acts import ticked


def post(rest: list[str]) -> int:
    root, conductor = machine_house()                      # the house's team, whatever instance posts
    name, rest = named_team(conductor, rest)
    asked = flags(rest, POST_FLAGS)
    if asked["reply"] is not None and (asked["task"] is None or asked["stop"]):
        refuse(USAGE)
    if asked["ask"] and (asked["task"] is None or asked["reply"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a principal's question: on an open task, alone
    if asked["name"] is not None and asked["task"] is not None:   # a name is given at a task's birth alone
        refuse(USAGE)
    if asked["every"] is not None and (asked["task"] is not None or asked["reply"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a recurrence is laid on a task to come alone
    if asked["description"] is not None and asked["every"] is None:
        refuse(USAGE)                                             # a description: a recurrence's alone
    if asked["context"] is not None and (asked["task"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a context limit: a recurrence's, or a task's at its birth
    if asked["vector"] and (asked["task"] is not None or asked["every"] is not None or asked["stop"]):
        refuse(USAGE)                                             # a vector is laid on a task at its birth alone
    for vector in asked["vector"]:
        if not vector_formed(vector):
            refuse(f"vector-invalid -- `{vector}`: a vector is `<family>:<id>`, both sides said, no blank.")
    vectors = list(dict.fromkeys(asked["vector"]))
    try:                                          # the flags read in their order: the first wrong one refuses
        limit = limit_of(asked["context"]) if asked["context"] is not None else None
        describing = ({} if asked["description"] is None
                      else {"description": recurrence_description(asked["description"])})
        when = None
        if asked["every"] is not None:
            when = every_of(asked["every"])
    except Declined as declining:
        refuse(str(declining))
    if asked["message"] is None and not asked["stop"]:
        refuse("message-missing -- a post carries its text: --message <text> (optional under --stop).")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)
    try:
        naming = named(conductor, asked)
    except Declined as declining:
        refuse(str(declining))

    def judge(state: dict, events: list[dict]) -> list:
        try:
            sender, agents = post_checked(state, owner, asked["as"], asked["to"])
            if when is not None:                  # a recurrence: nothing opens now, the tick sounds its periods
                return recurrence_posted(state, sender, asked["to"] or str(state.season.started.body.root), naming,
                                         asked["message"], when, tick_now().isoformat(timespec="seconds"), limit,
                                         describing)
            return post_decided(state, sender, agents, asked["to"], asked["task"], asked["message"], asked["ask"],
                                asked["stop"], asked["reply"], naming, vectors, limit)
        except Declined as declined:              # the decision's refusal by its code, said here in its words
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started: `team start {name} --message …` first.")
            if code == "team-deleting":
                refuse(deleting_said(name))
            if code == "season-stopped":
                refuse(off_season(name, state))
            if code == "participant-unknown":
                to, = data
                refuse(f"participant-unknown -- `--to {to}` names a member nobody declared.")
            if code == "task-unknown":
                task, = data
                refuse(f"task-unknown -- no task `{task}` of {name}: the tasks are "
                       f"{', '.join(state.task.tasks) or 'none'}.")
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "task-closed":
                task, held = data
                refuse(f"task-closed -- {task} is {held}: a post opens a new task instead.")
            if code == "message-unknown":
                reply, task = data
                refuse(f"message-unknown -- no post #{reply} on {task}.")
            raise ValueError(f"no sentence for the refusal `{code}`")

    made = written(conductor, root, journal, name, judge)
    head = made[0].body
    if made[0].kind == "recurrence":
        print(f"pp-team: {name} · recurrence {head.recurrence} to {head.to} · every "
              f"{said_when(head.when)}"
              + (f" · context {head.context}%" if head.context is not None else "")
              + f" · #{made[0].id} -- the tick opens one task per period")
    if made[0].kind == "task":
        print(f"pp-team: {name} · task {head.task} to {head.to}"
              + (f" · context {head.context}%" if head.context is not None else "")
              + f" · post #{made[1].id} do {made[1].body.sender} -> {made[1].body.to}")
    for one in made:
        if one.kind == "stopped":
            posted = any(other.kind == "post" for other in made)
            print(f"pp-team: {name} · {one.body.task} · stopped #{one.id}" + ("" if posted else " -- nobody held it"))
        elif one.kind == "post" and made[0].kind != "task":
            print(f"pp-team: {name} · {one.body.task} · post #{one.id} {one.body.verb} {one.body.sender} -> "
                  f"{one.body.to}")
        elif one.kind == "returned":
            print(f"pp-team: {name} · post #{one.body.message} returned to {one.body.to}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # a post lays the net again when it finds it gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def result(rest: list[str]) -> int:
    """`team result`: a resolved task's result as JSON on stdout."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    if len(rest) > 1 or (rest and rest[0].startswith("--")):
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    state = state_of(journal_of(root, name))
    if rest:
        task = state.task.tasks.get(rest[0])
        if task is None:
            refuse(f"task-unknown -- no task `{rest[0]}` of {name}: the tasks are {', '.join(state.task.tasks) or 'none'}.")
        if task.state != "resolved":
            refuse(f"task-open -- {task.id} is {task.state}: no result yet.")
        chosen = state.task.done[task.id]
    else:
        resolved = list(state.task.done.values())
        if not resolved:
            refuse(f"result-missing -- no task of {name} is resolved yet.")
        chosen = resolved[-1]
    print(json.dumps(chosen.body.result, ensure_ascii=False))
    return 0


def inbox_verb(rest: list[str]) -> int:
    """`team inbox`: one line per team where something waits for the owner -- under `--json` one
    object per such team, nothing in a run a team opened; `--seen` writes the owner's cursor at the team's
    journal, `--seen --id <n>` marks the one message n read (`inbox-read`) -- the writes of the readers, never
    beside `--json`."""
    # without `--seen`, the house's teams whatever instance calls; `--seen` writes at the instance that calls
    root, conductor = house() if "--seen" in rest else machine_house()
    name = None
    if rest and not rest[0].startswith("--"):
        name, rest = named_team(conductor, rest)
    asked = flags(rest, INBOX_FLAGS)
    if (asked["seen"] and asked["json"]) or (asked["id"] is not None and not asked["seen"]):
        refuse(USAGE)
    one_id = None
    if asked["id"] is not None:
        try:
            one_id = int(asked["id"])
        except ValueError:
            refuse(f"inbox-id-unknown -- `{asked['id']}`: --id names a message of the inbox by its number.")
    if asked["seen"]:
        if name is None:
            refuse("inbox --seen names the team whose inbox was read: `team inbox <name> --seen`.")
        if not team_doc(root, name).is_file():
            refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")

        def judge(state: dict, events: list[dict]) -> list:
            upto = max((int(one.get("id") or 0) for one in events), default=0) if one_id is None else 0
            try:
                return inbox_seen_decided(state, one_id, upto)
            except Declined as declined:          # the decision's refusal by its code, said here in its words
                code, *data = declined.args
                if code == "team-not-started":
                    refuse(f"team-not-started -- {name} was never started.")
                if code == "inbox-question":
                    refuse(f"inbox-question -- #{one_id} waits for your answer: `team post {name} --task <id> "
                           f"--reply {one_id}` takes it out of the inbox.")
                if code == "inbox-id-unknown":
                    refuse(f"inbox-id-unknown -- #{one_id} is not in the inbox of {name}: `team inbox {name} --json` "
                           "says the ids it holds.")
                raise ValueError(f"no sentence for the refusal `{code}`")

        made = written(conductor, root, journal_of(root, name), name, judge)
        if one_id is not None:
            print(f"pp-team: {name} · #{one_id} read")
            return 0
        print(f"pp-team: {name} · inbox seen up to #{made[0].body.upto}" if made else f"pp-team: {name} · inbox seen already")
        return 0
    meta = caller()
    if meta is not None and in_team_run(root, conductor, meta):
        return 0                                   # the owner's inbox is the owner's: a member's run reads none
    home = root.parent / TEAMS
    names = [name] if name else (sorted(one.name for one in home.iterdir() if (one / TEAM_DOC).is_file()) if home.is_dir() else [])
    for one in names:
        state = state_of(journal_of(root, one))
        if state.season.started is None:
            continue
        if asked["json"]:
            found = inbox_object(one, state)
            if found is not None:
                print(json.dumps({**found, "name": team_name(root, conductor, one)}, ensure_ascii=False))
            continue
        line = inbox_line(labelled(team_name(root, conductor, one), one), state)
        if line:
            print(line)
    return 0


def resume_verb(rest: list[str]) -> int:
    """`team resume <name> --task <id> [--to <member>|all] [--message <text>] [--as <principal>] [--no-tick]`: takes
    back ONE task a guard left with nobody due -- stopped, held by a member's final failure, or past
    `launches:` --, judged under the journal's lock before anything is written; then `resumed {task, by,
    from}`, the origin the task's counters count from, and an `info` from the resumer to each member it
    revives: the holders at the stop, the members whose final failure stands, the members with
    messages due past `launches:` -- under `--to`, to the member it names alone, or to every member of the
    season under `all`; a member the season does not know refuses `member-unknown`, `--to` without `--task` is the
    usage. The posts returned at the stop stay returned; the team's `budget` and
    `budget-launches` are never reset; off season it refuses `season-stopped`. Then the relaunch entry laid again,
    and a tick unless `--no-tick`.
    With `--recurrence`, one suspended recurrence taken back (`recurrence_resumed`): beside `--task` or `--message`,
    the usage. In the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, RESUME_FLAGS)
    if asked["to"] is not None and asked["task"] is None:
        refuse(USAGE)                                     # --to names whom a task's resume tells
    if asked["quota"]:
        if asked["task"] is not None or asked["recurrence"] is not None or asked["message"] is not None:
            refuse(USAGE)                                 # a limit lifted alone: a task by --task
        return quota_lifted(root, conductor, name, asked)
    if asked["member"] is not None:
        refuse(USAGE)                                     # --member names whose limit --quota lifts
    if asked["recurrence"] is not None:
        if asked["task"] is not None or asked["message"] is not None:
            refuse(USAGE)                                 # a recurrence resumes alone: a task by --task
        return recurrence_resumed(root, conductor, name, asked)
    if asked["task"] is None:
        if asked["message"] is not None:
            refuse(USAGE)
        return unpause(root, conductor, name, asked)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)
    text = asked["message"] if asked["message"] is not None else RESUMED

    def judge(state: dict, events: list[dict]) -> list:
        try:
            sender, season, task = resume_checked(state, owner, asked["as"], asked["to"], asked["task"])
            why = spent(root, state)              # read between two refusals: after task-resolved, before the rest
            return resume_decided(state, sender, season, task, asked["to"], text, why)
        except Declined as declined:              # the decision's refusal by its code, said here in its words
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started.")
            if code == "team-deleting":
                refuse(deleting_said(name))
            if code == "season-stopped":
                refuse(off_season(name, state))
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "member-unknown":
                member, season = data
                refuse(f"member-unknown -- `{member}` is no member of {name}'s season: its members are "
                       f"{', '.join(season)}, or `{ALL}`.")
            if code == "task-unknown":
                task, = data
                refuse(f"task-unknown -- no task `{task}` of {name}: the tasks are "
                       f"{', '.join(state.task.tasks) or 'none'}.")
            if code == "task-resolved":
                task, = data
                refuse(f"task-resolved -- {task} is resolved: a post opens a new task instead.")
            if code == "budget-spent":
                why, = data
                refuse(f"budget-spent -- {name}: {why}; a resume never resets the team's budget -- `team budget "
                       f"{name} <usd> | --launches <n>` raises it.")
            if code == "task-not-blocked":
                task, = data
                refuse(f"task-not-blocked -- {task} is open, no final failure stands on it and its launches "
                       "are not spent: nothing to take back.")
            raise ValueError(f"no sentence for the refusal `{code}`")

    made = written(conductor, root, journal, name, judge)
    for one in made:
        if one.kind == "resumed":
            print(f"pp-team: {name} · {one.body.task} · resumed #{one.id} from {', '.join(one.body.sender)}")
        else:
            print(f"pp-team: {name} · {one.body.task} · post #{one.id} info {one.body.sender} -> {one.body.to}")
    netted(root, conductor, name, state_of(journal))   # the task open again: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0
