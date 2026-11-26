"""The `rhythm` domain, layer `verbs`: the command line of the verbs that ring a ceremony or change a recurrence.

A definition belongs here when it plays such a verb: it reads its arguments, rings a ceremony at hand, changes a live
recurrence or starts it now, takes a suspended recurrence back (`recurrence_resumed`, which `resume --recurrence` calls)
-- judged, the hour read, the event written, the relaunch entry laid again and a tick played --, and refuses with the
usage. What it writes is decided by `rhythm/rules.py`: the verb hands the decisions what it read, reads the hour between
two decisions when a refusal comes before it, and only when the change needs it, writes what they compose, and says the
sentence of each code they decline (`refusal_of`). A verb is where the skill meets its caller: it may print, end the
call and use every other layer.
"""
from __future__ import annotations

from pathlib import Path

from house.model import USAGE, Declined
from house.rules import journal_of, team_doc
from house.store import house, machine_house, named_team, owner_of, refuse, tick_now
from house.verbs import flags
from rhythm.model import RECURRENCE_FLAGS, RING_FLAGS
from season.rules import limit_of
from season.faces import off_season
from rhythm.rules import (every_of, recurrence_born, recurrence_born_asked, recurrence_change_asked,
                          recurrence_changed, recurrence_description, recurrence_launch_asked, recurrence_launched,
                          recurrence_resume_asked, recurrence_resumed_of, ring_asked, ringing)
from task.faces import principal_unknown
from rhythm.faces import recurrence_unknown, recurrence_was_stopped, said_when
from net.acts import netted
from journal.faces import deleting_said
from journal.store import state_of, written
from tick.rules import netless
from tick.acts import ticked


def ring_verb(rest: list[str]) -> int:
    """`team ring <name> <ceremony> [--as <principal>] [--no-tick]`: rings ONE declared ceremony at
    hand, out of its hour -- the tick's ring (`ringing`) under the period `manual-<id>`, the id of its
    own `ceremony-due`, which `by` names the principal of; judged under the journal's lock before
    anything is written, one ring of a ceremony at a time (`ceremony-open`), in season alone (`season-stopped`). Then the relaunch entry
    laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    called, rest = rest[0], rest[1:]
    asked = flags(rest, RING_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            sender, ceremony = ring_asked(state, owner, asked["as"], called)
        except Declined as declined:
            refuse(refusal_of(name, state, declined))
        first = max((int(one.get("id") or 0) for one in events), default=0) + 1
        return ringing(state, name, ceremony, f"manual-{first}", by=sender, now=tick_now())

    made = written(conductor, root, journal, name, judge)
    task = next(one for one in made if one.kind == "task")
    print(f"pp-team: {name} · {called} rung at hand · {made[0].body.period} #{made[0].id} · task {task.body.task} "
          f"to {task.body.to}")
    netted(root, conductor, name, state_of(journal))   # a task open: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def recurrence_verb(rest: list[str]) -> int:
    """`team recurrence <name> <R<n>> [--every "<when>"] [--context <n>%|off] [--message <text>] [--description <text>]
    [--as <principal>] [--no-tick]`: CHANGES a live recurrence -- its period, its context limit, its text, its
    description, one of them at least. `recurrence-changed {recurrence, when, since, context, text, description, by}`
    carries what changes alone: `when` and `since` -- the local hour of the change -- for a new period, `context` for a
    new limit (`null` under `off`, the limit taken away), `text` for a new intention, `description` for a new sentence
    of what it does (`description-invalid` past one line of `DESCRIPTION_CHARS`); judged under the journal's lock before anything is written, `message-missing` for an
    empty text, `recurrence-unchanged` when every value asked is in force. The replay replaces what the event carries
    and keeps the periods it sounded: a new hour holds from its next period after the change, a new limit from the next
    first wake-up on an occurrence, a new text from the next occurrence -- an occurrence sounded keeps its own.
    `team recurrence <name> <R<n>> --now [--as <principal>] [--no-tick]`: LAUNCHES one occurrence more of a live
    recurrence, paused or not, now -- a `task` like a period's, from the recurrence's principal to its member, with
    `recurrence`, `now: true` and `by` and WITHOUT `period`, named `<name> YYYY-MM-DD HH:MM` at the local hour of the
    launch, then its `do` --; its planning untouched -- `when`, `since`, the periods sounded, the pause --, the task its
    LAST occurrence, so that a period skips while it is open. Judged under the journal's lock (`team-unknown`,
    `team-not-started`, `season-stopped` off season, `principal-unknown`, `recurrence-unknown`, `recurrence-stopped`,
    `recurrence-open` while its last occurrence is open); `--now` beside another flag of a change, the usage.
    `team recurrence <name> --task <T<n>> --every "<when>" [--context <n>%] [--description <text>] [--as <principal>]
    [--no-tick]`: lays a NEW recurrence on a task that exists -- `recurrence {R<n>, from, to, text, name, when, since,
    context, task, description?}`, its member,
    its text and its name the task's, its principal the one who plays the verb --; the replay makes the task its LAST
    occurrence, so that no period opens one while it is open (`task-unknown`, `task-recurrent` for an occurrence or a
    ring's task; `R<n>` or `--message` beside `--task`, the usage). Then the net laid again, and a tick unless
    `--no-tick`."""
    root, conductor = machine_house()                      # the house's recurrence, whatever instance changes it
    name, rest = named_team(conductor, rest)
    called = None
    if rest and not rest[0].startswith("--"):
        called, rest = rest[0], rest[1:]
    asked = flags(rest, RECURRENCE_FLAGS)
    changing = ("task", "every", "context", "message", "description")
    if asked["now"] and (called is None or any(asked[key] is not None for key in changing)):
        refuse(USAGE)                                 # a launch now is played alone, on a recurrence named
    if called is None and (asked["task"] is None or asked["every"] is None or asked["message"] is not None):
        refuse(USAGE)                                 # a recurrence born of a task: its period owed, its text the task's
    if called is not None and not asked["now"] and (asked["task"] is not None
                               or all(asked[key] is None for key in ("every", "context", "message", "description"))):
        refuse(USAGE)
    if asked["message"] is not None and not asked["message"].strip():
        refuse("message-missing -- a recurrence carries its text: --message <text>, not empty.")
    try:                                          # the flags read in their order: the first wrong one refuses
        when = None
        if asked["every"] is not None:
            when = every_of(asked["every"])
        limit = limit_of(asked["context"], off=called is not None) if asked["context"] is not None else None
        description = None if asked["description"] is None else recurrence_description(asked["description"])
    except Declined as declining:
        refuse(str(declining))
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            if called is None:
                sender, task = recurrence_born_asked(state, owner, asked["as"], asked["task"])
                return recurrence_born(state, sender, task, when, tick_now().isoformat(timespec="seconds"), limit,
                                       description)
            if asked["now"]:
                sender, recurrence = recurrence_launch_asked(state, owner, asked["as"], name, called)
                return recurrence_launched(state, sender, recurrence, tick_now())
            sender, recurrence, moved = recurrence_change_asked(state, owner, asked["as"], name, called, when)
            since = tick_now().isoformat(timespec="seconds") if moved else None
            return recurrence_changed(recurrence, sender, when, since, asked["context"] is not None, limit,
                                      asked["message"], description)
        except Declined as declined:
            refuse(refusal_of(name, state, declined))

    made = written(conductor, root, journal, name, judge)[0]
    said = made.body                              # the event written: a key it carries is said, `null` as off
    if made.kind == "task":
        print(f"pp-team: {name} · recurrence {said.recurrence} launched now · {said.task} to {said.to} by "
              f"{said.by} · #{made.id} -- its planning untouched, no period opens a task while {said.task} "
              "is open")
    elif made.kind == "recurrence":
        print(f"pp-team: {name} · recurrence {said.recurrence} to {said.to} from {said.task} · every "
              f"{said_when(said.when)}" + (f" · context {said.context}%" if said.context is not None else "")
              + f" · #{made.id} -- no period opens a task while {said.task} is open")
    else:
        print(f"pp-team: {name} · recurrence {said.recurrence}"
              + (f" · every {said_when(said.when)}" if "when" in made.line else "")
              + (f" · context {said.context}%" if said.context is not None
                 else " · context off" if "context" in made.line else "")
              + (" · text changed" if "text" in made.line else "")
              + (" · description changed" if "description" in made.line else "")
              + f" · #{made.id} -- from its next period"
              + (" and its next occurrence" if "context" in made.line else ""))
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # a live recurrence keeps the net
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def refusal_of(name: str, state: dict, declined: Declined) -> str:
    """-> the sentence a refusal of a rhythm's decision says, from its code and its data."""
    code, *data = declined.args
    if code == "team-not-started":
        return f"team-not-started -- {name} was never started."
    if code == "team-deleting":
        return deleting_said(name)
    if code == "season-stopped":
        return off_season(name, state)
    if code == "ceremony-unknown":
        called, names = data
        return (f"ceremony-unknown -- {name} declares no ceremony `{called}`: the ceremonies are "
                f"{', '.join(names) or 'none'}.")
    if code == "ceremony-open":
        held, called = data
        return (f"ceremony-open -- {held} of `{called}` is open: one ring at a time, ring again once it "
                "is resolved or stopped.")
    if code == "task-unknown":
        task, tasks = data
        return f"task-unknown -- no task `{task}` of {name}: the tasks are {', '.join(tasks) or 'none'}."
    if code == "task-recurrent":
        task, = data
        return (f"task-recurrent -- {task.id} is an occurrence of "
                + (f"{task.recurrence}" if task.recurrence else f"the ceremony `{task.ceremony}`")
                + ": its run has a carrier already.")
    if code == "principal-unknown":
        return principal_unknown(*data)
    if code == "recurrence-unknown":
        return recurrence_unknown(*data)
    if code == "recurrence-stopped":
        return recurrence_was_stopped(*data)
    if code == "recurrence-open":
        before, recurrence = data
        return (f"recurrence-open -- {before}, the last occurrence of {recurrence}, is still open: a member never "
                "holds the same work twice.")
    if code == "recurrence-unchanged":
        recurrence, = data
        return (f"recurrence-unchanged -- {recurrence.id} comes back every {said_when(recurrence.when)}, "
                "its context limit " + (f"{recurrence.context}%" if recurrence.context is not None else "off")
                + ", its text and its description as asked already.")
    raise ValueError(f"no sentence for the refusal `{code}`")


def recurrence_resumed(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> --recurrence <R<n>> [--as <principal>] [--no-tick]`: ONE suspended recurrence taken back --
    `recurrence-resumed {recurrence, by, since}`, `since` the local hour of the resume, judged under the journal's lock
    (`team-unknown`, `team-not-started`, `principal-unknown`, `recurrence-unknown`, `recurrence-stopped`,
    `recurrence-live`); nothing caught up: its next period is the first after `since`. Then the net laid again, and a
    tick unless `--no-tick`."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            sender, recurrence = recurrence_resume_asked(state, owner, asked["as"], name, asked["recurrence"])
        except Declined as declined:
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started.")
            if code == "team-deleting":
                refuse(deleting_said(name))
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "recurrence-unknown":
                refuse(recurrence_unknown(*data))
            if code == "recurrence-stopped":
                refuse(recurrence_was_stopped(*data))
            if code == "recurrence-live":
                recurrence, = data
                refuse(f"recurrence-live -- {recurrence.id} is not paused: `team pause {name} --recurrence "
                       f"{recurrence.id}` suspends it.")
            raise ValueError(f"no sentence for the refusal `{code}`")
        return recurrence_resumed_of(recurrence, sender, tick_now())

    made = written(conductor, root, journal, name, judge)[0]
    print(f"pp-team: {name} · recurrence {made.body.recurrence} resumed #{made.id} by {made.body.by} -- nothing "
          f"caught up, its next period after {made.body.since}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # the recurrence back: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0
