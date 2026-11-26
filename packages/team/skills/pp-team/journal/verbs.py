"""The `journal` domain, layer `verbs`: the command line of the verbs that show the journal or snapshot it.

A definition belongs here when it plays such a verb: it reads the verb's arguments, prints the journal's events as
lines or as JSON, or writes a snapshot -- judged first, the state packed, then composed by a decision of
`journal/rules.py` --, and refuses with the usage. A verb is where the skill meets its caller: it may print, end the
call and use every other layer.
"""
from __future__ import annotations

import json

from house.model import USAGE, Declined
from house.rules import journal_of, team_doc
from house.store import house, lines_of, machine_house, named_team, refuse
from house.verbs import flags
from journal.model import LOG_FLAGS
from journal.replay import event_read, packed, read_on, said_so_far
from journal.rules import of_task, snapshot_asked, snapshot_of
from journal.faces import event_object, harmless, shown
from journal.store import written


def snapshot_verb(rest: list[str]) -> int:
    """`team snapshot <name>`: ONE `snapshot {upto, state}` event, written under the
    journal's lock -- the replay restarts there; nothing is rewritten, no reader changes."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    if rest:
        refuse(USAGE)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            snapshot_asked(state)
        except Declined:
            refuse(f"team-not-started -- {name} was never started: `team start {name} --message …` first.")
        last = max((int(one.get("id") or 0) for one in events), default=0)
        return snapshot_of(last, packed(state))

    made = written(conductor, root, journal_of(root, name), name, judge)
    print(f"pp-team: {name} · snapshot #{made[0].id} upto #{made[0].body.upto}")
    return 0


def log_verb(rest: list[str]) -> int:
    """`team log`: the journal rendered, one line per event, by task and by tail, in the words of the debt (`read_on`);
    under `--json` one object per event, the form `watch --json` writes."""
    root, conductor = machine_house()                      # the house's team, whatever instance reads it
    name, rest = named_team(conductor, rest)
    asked = flags(rest, LOG_FLAGS)
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    context, events = said_so_far(), []
    for line in lines_of(journal_of(root, name)):
        one = event_read(line)                     # the kinds whose body the reader reads, decoded once read
        said = read_on(context, one) if one.kind != "snapshot" else None
        if said is not None:
            events.append(said)
    if asked["task"] is not None:
        events = of_task(events, asked["task"])
    if asked["last"] is not None:
        try:
            last = int(asked["last"])
        except ValueError:
            last = -1
        if last < 1:
            refuse(f"last-invalid -- `--last {asked['last']}`: a whole number of 1 or more.")
        events = events[-last:]
    for one in events:
        print(json.dumps(event_object(name, one), ensure_ascii=False) if asked["json"] else harmless(shown(one)))
    return 0
