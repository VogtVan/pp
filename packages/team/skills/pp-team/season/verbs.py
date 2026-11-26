"""The `season` domain, layer `verbs`: the verbs that open, hold and close a season.

A definition belongs here when it plays such a verb or serves its command line: it starts or stops a season, stops a
task or a recurrence, pauses a team or takes a paused team back (`unpause`, which `team resume` without a task calls:
judged, the event written, the relaunch entry laid again and a tick played), reads the flags of `start` -- the team's,
and each member's profile -- or the season's flags another verb takes, and refuses with the usage. What `start`, `stop`
and `pause` write is decided by the rules of `season`, `task` and `rhythm`: the verb chains them in the order of today's
refusals, reads the hour for a season taken back only, plays `stop --kill`'s kills under the journal's lock between two
decisions, and says the sentence of each code they decline (`season_refusal`). A verb is where the skill meets its
caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

import hashlib
import json
import sys

from pathlib import Path

from house.model import Declined, USAGE
from house.rules import journal_of, team_doc, team_root
from house.store import house, machine_house, named_team, owner_of, refuse, tick_now
from house.verbs import flags, retired_flags
from template.model import SEASON_DOC
from declaration.model import DECLARE_FLAGS
from season.model import MEMBER_FLAGS, PAUSE_FLAGS, SEASON_LAUNCH, START_FLAGS, STOP_FLAGS
from declaration.acts import declared
from season.rules import (paused_decided, season_asked, season_stopped, start_asked, team_started,
                          unpause_asked, unpaused_decided)
from season.faces import in_season, off_season
from season.acts import season_flagged, season_opened
from documents.rules import documents_kept
from documents.acts import documents_planned, documents_written, entries_judged
from task.rules import (live_recurrences, named, principal_of, start_opened, stop_chosen,
                        stop_decided)
from task.faces import principal_unknown
from rhythm.rules import recurrence_stopped
from rhythm.faces import recurrence_unknown, recurrence_was_stopped
from rhythm.acts import recurrence_paused
from wake.rules import open_intents
from wake.acts import born, kills
from net.acts import disarmed, netted, relaunch_removed, relaunch_said
from journal.faces import deleting_said
from journal.store import state_of, written
from tick.rules import netless
from tick.acts import ticked
from admin.store import cleared


def season_declared(rest: list[str]) -> tuple[list[str], dict | None]:
    """-> (`declare`'s own flags, the season's flags of `start` `{asked, packages, profiles}`) of a `declare
    --season`: the words read by `start`'s reader (`season_flags`) -- what follows a `--member <name>` that member's
    profile, a `--package` the season's --, then a flag of `SEASON_LAUNCH` and its word taken out of the team's part,
    `--json` wherever it stands; the rest is `declare`'s (`asked_declare`). Without `--season`, (the words, None). A
    season's flag given twice, or short of its word, is the usage."""
    if "--season" not in rest:
        return rest, None
    team_part, packages, profiles = season_flags([one for one in rest if one != "--json"])
    kept, asked, index = [], {}, 0
    while index < len(team_part):
        flag = team_part[index][2:] if team_part[index].startswith("--") else ""
        if flag in SEASON_LAUNCH:
            if flag in asked or index + 1 >= len(team_part):
                refuse(USAGE)
            asked[flag] = team_part[index + 1]
            index += 2
            continue
        words = DECLARE_FLAGS.get(flag)
        step = 1 + (words if isinstance(words, int) else 0)
        kept += team_part[index:index + step]
        index += step
    return kept + [one for one in rest if one == "--json"], {"asked": asked, "packages": packages, "profiles": profiles}


def season_flags(rest: list[str]) -> tuple[list[str], list[str], dict]:
    """-> (the team's flags, the team's packages, the members' profiles): what follows a `--member <name>` up to the
    next one is that member's -- `--provider`, `--model`, `--effort`, `--permissions` and `--package <name>=on|off`
    repeated --, as `{member: {key: value, packages: [...]}}`; the flags before the first `--member` are the team's,
    its `--package <name>=on|off`, repeated, taken apart as the team's packages. Anything else is the usage."""
    at, team_part, packages, profiles = 0, [], [], {}
    while at < len(rest) and rest[at] != "--member":
        if rest[at] == "--package":
            if at + 1 >= len(rest):
                refuse(USAGE)
            packages.append(rest[at + 1])
            at += 2
            continue
        team_part.append(rest[at])
        at += 1
    while at < len(rest):
        if at + 1 >= len(rest) or rest[at + 1].startswith("--"):
            refuse(USAGE)
        profile = profiles.setdefault(rest[at + 1], {})
        at += 2
        while at < len(rest) and rest[at] != "--member":
            key = rest[at][2:] if rest[at].startswith("--") else ""
            if key not in MEMBER_FLAGS or at + 1 >= len(rest):
                refuse(USAGE)
            if key == "package":
                profile.setdefault("packages", []).append(rest[at + 1])
            else:
                profile[key] = rest[at + 1]
            at += 2
    return team_part, packages, profiles


def start(rest: list[str]) -> int:
    """`team start`: a SEASON of the team -- the first, or the next one OFF SEASON, after `team stop`: a team in season
    refuses `season-running`, naming `team stop`; a start after a stop writes `since`, the hour from which nothing
    passed off season is caught up. `TEAM.md` read whole and
    judged, the season SEASON.md writes -- its launch, budget, packages, profiles and work, each covered by the
    start's flag for the same key (`season_opened`) -- and the gestures judged before any write; then the flags'
    values written into SEASON.md (`season_flagged`), the agents the house lacks born, the team's documents written,
    `team-started` (its `season`, `packages` and `profiles` when given)
    and, under `--message`, a task and its `do` -- without it no task opens, the season stands on its ceremonies and
    the posts to come; the relaunch entry laid under an open task or a declared ceremony, the first `post` laying it
    otherwise; a tick unless `--no-tick`. The members keep their runs."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if "--max-budget-usd" in rest:
        refuse("flag-retired -- `--max-budget-usd`: no cap per wake-up any more -- a wake-up's share is computed on "
               "the team's `budget:` of TEAM.md (each its part of the rest), and `team budget` raises it.")
    retired_flags(rest)
    team_part, flagged_packages, flagged_profiles = season_flags(rest)
    asked = flags(team_part, START_FLAGS)
    team = declared(root, conductor, name)
    try:                                               # SEASON.md, each value covered by its flag, judged whole
        opened = season_opened(root, conductor, name, team, asked, flagged_packages, flagged_profiles)
    except Declined as declining:
        refuse(str(declining))
    profiles = opened["profiles"]
    journal = journal_of(root, name)
    before = state_of(journal)
    if before.season.deleting:
        refuse(deleting_said(name))
    running = in_season(name, before, "a start")
    if running:
        refuse(running)
    standing = [one.id for one in before.task.tasks.values() if one.state == "open"]
    try:
        naming = named(conductor, asked) if asked["message"] is not None else {}
    except Declined as declining:
        refuse(str(declining))
    target = asked["to"] or team.root
    if target not in team.agents:
        refuse(f"participant-unknown -- `--to {target}` names a member nobody declared.")
    try:
        entries_judged(root, conductor, name, team)
        rendering, planned = documents_planned(root, conductor, name, before.season.started, team)
    except Declined as declining:
        refuse(str(declining))
    for key, members in team.roles.items():         # said, never refused: an author reserves a key
        if not members:
            print(f"pp-team: {name} · role `{key}` has no member -- reserved", file=sys.stderr)
    for one in rendering["documents"]:                 # said, never refused: a key reserved
        if one["members"] == []:
            print(f"pp-team: {name} · document `{one['template']}` reaches nobody -- no member holds "
                  f"{', '.join(f'`{key}`' for key in one['roles'])}", file=sys.stderr)
    season_path = team_root(root, name) / SEASON_DOC
    if season_flagged(conductor, season_path, asked, flagged_packages, flagged_profiles) and rendering["season"]:
        rendering["season"] = hashlib.sha256(season_path.read_bytes()).hexdigest()[:12]   # the file the season keeps
    created = born(root, conductor, list(team.agents.values()))
    launch = opened["launch"]
    rendered = documents_written(root, conductor, name, team, launch, profiles, planned)
    cleared(root, name, team)
    owner = owner_of(root, conductor)

    def judge(state: dict, events: list) -> list:
        try:
            due = start_asked(state)
        except Declined as declined:              # the decision's refusal by its code, said here in its words
            refuse(season_refusal(name, state, declined))
        since = tick_now().isoformat(timespec="seconds") if due else None   # the hour read for a season taken back
        return (team_started(team, owner, opened, documents_kept(rendering), rendered, rendering["season"], since)
                + start_opened(state, owner, target, naming, asked["message"]))

    made = written(conductor, root, journal, name, judge)
    said = (f" · task {made[1].body.task} to {target} · post #{made[2].id} do {owner} -> {target}"
            if len(made) > 1 else " · no task opened" + (f", {', '.join(standing)} open" if standing else ""))
    print(f"pp-team: {name} started · members {', '.join(team.agents)}"
          + (f" (born: {', '.join(created)})" if created else " (all standing)") + said)
    if team.schedule is not None and not netless(state_of(journal)):   # the relaunch entry under a task, a
        relaunch_said(root, conductor, name, journal)                    # ceremony or a recurrence; the first post
        #                                                                  lays it otherwise; the tick arms the timer
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def stop(rest: list[str]) -> int:
    """`team stop <name> [--task <id>] [--recurrence <R<n>>] [--kill] [--json] [--no-tick]`: without `--task` nor
    `--recurrence`, the SEASON stopped -- each open task stopped (`stopping`; `--kill` kills its runs too), then
    `season-stopped {by, tasks, recurrences}`, the tasks stopped and the recurrences it silences -- live and not
    paused: a paused one is silent already, is not named, and stays paused --, each kept as it stands; until the
    next `team start` the team is OFF SEASON: the tick wakes, rings and sounds nothing, its net leaves, and only then
    are `TEAM.md` and `SEASON.md` written. With `--task`, one task stopped; with `--recurrence`,
    one recurrence -- in season alone. Judged under the journal's lock: `team-not-started`, `season-stopped` (off
    season already). Under `--json` ONE object `{team, stopped: {id, tasks, recurrences}}` for a season stopped."""
    root, conductor = machine_house()                      # the house's team, whatever instance stops it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, STOP_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    said: list[str] = []
    if asked["recurrence"] is not None and (asked["task"] is not None or asked["kill"]):
        refuse(USAGE)                                             # a recurrence stops alone: its occurrence by --task
    season = asked["recurrence"] is None and asked["task"] is None

    def judge(state: dict, events: list) -> list:
        try:
            season_asked(state)
            if asked["recurrence"] is not None:        # a suspended one stops as well
                return recurrence_stopped(state, name, asked["recurrence"], owner)
            chosen = stop_chosen(state, asked["task"])
        except Declined as declined:              # the decision's refusal by its code, said here in its words
            refuse(season_refusal(name, state, declined))
        killed = [kills(root, conductor, name, state, task.id, said) if asked["kill"] else []   # under the lock,
                  for task in chosen]                                                             # task by task
        made = stop_decided(state, chosen, killed, owner)
        if season:
            made += season_stopped(owner, [task.id for task in chosen],
                                   [one.id for one in live_recurrences(state) if not one.paused])
        return made

    made = written(conductor, root, journal_of(root, name), name, judge)
    closing = next((one for one in made if one.kind == "season-stopped"), None)
    if made[0].kind == "recurrence-stopped":
        print(f"pp-team: {name} · recurrence {made[0].body.recurrence} stopped #{made[0].id} -- its open occurrence "
              "lives on")
    for line in said:
        print(f"pp-team: {name} · {line}")
    for one in made:
        if one.kind == "stopped":
            posted = any(other.kind == "post" and other.body.task == one.body.task for other in made)
            print(f"pp-team: {name} · {one.body.task} · stopped #{one.id}" + ("" if posted else " -- nobody held it"))
        elif one.kind == "post":
            print(f"pp-team: {name} · {one.body.task} · post #{one.id} stop {one.body.sender} -> {one.body.to}")
        elif one.kind == "returned":
            print(f"pp-team: {name} · post #{one.body.message} returned to {one.body.to}")
    if closing is not None:
        print(f"pp-team: {name} · season stopped #{closing.id} by {closing.body.by} · tasks stopped: "
              f"{', '.join(closing.body.tasks) or 'none'} · recurrences silenced: "
              f"{', '.join(closing.body.recurrences) or 'none'}"
              f" -- off season until `team start {name}`")
    if netless(state_of(journal_of(root, name))):
        relaunch_removed(root, conductor, name)    # the last task stopped, no ceremony, or off season: the net leaves
        disarmed(root, name)
    if asked["json"] and closing is not None:
        print(json.dumps({"team": name, "stopped": {"id": closing.id, "tasks": closing.body.tasks,
                                                    "recurrences": closing.body.recurrences}},
                         ensure_ascii=False))
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0


def pause_verb(rest: list[str]) -> int:
    """`team pause <name> [--as <principal>]`: the team PAUSED -- `paused {by}`, judged under the journal's
    lock; nothing killed, no tick: the wake-ups under way end on their own, and until `team resume <name>`
    the tick reaps and routes but rings and wakes nobody; a team off season refuses `season-stopped`, its stop ends
    the pause. With `--recurrence`, one recurrence suspended alone (`recurrence_paused`). In the HOUSE (`machine_house()`), whatever instance calls."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, PAUSE_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    if asked["recurrence"] is not None:
        return recurrence_paused(root, conductor, name, owner, asked)

    def judge(state: dict, events: list) -> list:
        try:
            season_asked(state)
            sender = principal_of(state, owner, asked["as"])   # read between two refusals; its code said below
            return paused_decided(state, sender)
        except Declined as declined:              # the decision's refusal by its code, said here in its words
            refuse(season_refusal(name, state, declined))

    made = written(conductor, root, journal_of(root, name), name, judge)[0]
    running = len(open_intents(state_of(journal_of(root, name))))
    print(f"pp-team: {name} · paused #{made.id} by {made.body.by} · {running} wake-up(s) under way end on their own"
          f" · nobody is woken until `team resume {name}`")
    return 0


def season_refusal(name: str, state: dict, declined: Declined) -> str:
    """-> the sentence a refusal of a season's decision -- `start`, `stop`, `pause` -- says, from its code and its data."""
    code, *data = declined.args
    if code == "team-not-started":
        return f"team-not-started -- {name} was never started."
    if code == "team-deleting":
        return deleting_said(name)
    if code == "season-stopped":
        return off_season(name, state)
    if code == "season-running":                  # `start`'s alone
        return str(in_season(name, state, "a start"))
    if code == "team-paused":
        return (f"team-paused -- {name} is paused since #{state.season.paused.get('id')}: `team resume {name}` takes it "
                "back.")
    if code == "principal-unknown":
        return principal_unknown(*data)
    if code == "recurrence-unknown":
        return recurrence_unknown(*data)
    if code == "recurrence-stopped":
        return recurrence_was_stopped(*data)
    if code == "task-unknown":
        task, = data
        return f"task-unknown -- no task `{task}` of {name}."
    if code == "task-closed":
        task, = data
        return f"task-closed -- {task.id} is {task.state} already."
    raise ValueError(f"no sentence for the refusal `{code}`")


def unpause(root: Path, conductor, name: str, asked: dict) -> int:
    """`team resume <name> [--as <principal>] [--no-tick]`: the paused team taken back -- `unpaused {by}`,
    judged under the journal's lock; then the relaunch entry laid again, and a tick unless `--no-tick`:
    what is due now, each member in its own run."""
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list) -> list:
        try:
            unpause_asked(state)
            sender = principal_of(state, owner, asked["as"])   # read between two refusals; its code said below
            return unpaused_decided(state, sender)
        except Declined as declined:              # the decision's refusal by its code, said here in its words
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started.")
            if code == "team-deleting":
                refuse(deleting_said(name))
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "team-not-paused":
                refuse(f"team-not-paused -- {name} is not paused: `team resume {name} --task <id>` takes a task "
                       "back.")
            raise ValueError(f"no sentence for the refusal `{code}`")

    made = written(conductor, root, journal, name, judge)[0]
    print(f"pp-team: {name} · unpaused #{made.id} by {made.body.by}")
    state = state_of(journal)
    if not netless(state):
        netted(root, conductor, name, state)       # the team back: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0
