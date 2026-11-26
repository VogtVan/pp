"""The `documents` domain, layer `verbs`: the command line of the verbs a member's run calls for its team's documents.

A definition belongs here when it plays such a verb: it verifies a member's vector, prints what that vector mounts at
each exchange, or prints the document a wake-up plays, and refuses with the usage. A verb is where the skill meets
its caller: it may print, end the call and use every other layer.
"""
from __future__ import annotations

import json
import os

from house.model import USAGE
from house.store import machine_house, named_team, refuse
from house.verbs import flags
from documents.model import ENTRY_FLAGS, MEMBER_FAMILY
from documents.store import season_view
from documents.acts import entry_of, member_judged


def verify_verb(rest: list[str]) -> int:
    """`pp-team verify` (the vector on stdin): the VERIFIER of the family `team-member:<team>/<member>` -- the
    engine's call when a launcher is given a member's vector, never an agent's. Judged by `member_judged`; a family
    this package does not declare refuses `family-foreign`. Reads only, writes nothing, takes no lock."""
    if rest:
        refuse(USAGE)
    root, conductor = machine_house()
    prefix, _, ident = conductor.reading.piped().strip().partition(":")
    if prefix != MEMBER_FAMILY:
        refuse(f"family-foreign -- `{prefix}:` is not a family this package verifies ({MEMBER_FAMILY})")
    member_judged(root, conductor, ident)
    return 0


def mount_verb(rest: list[str]) -> int:
    """`pp-team mount <team>/<member>`: what the member's vector mounts -- the launcher's gesture at every exchange
    of the member's run, never an agent's. Judged as `verify` judges (`member_judged`), then the member's view in the
    season under way (`season_view`): ONE line `::mount` with an entry per document of its roles, in the
    start's order -- `{"doc": "roles/TEAM-<team>-<name>.md", "body": true}` for one that
    mounts, the same with `"constraints": false, "tools": false` for one that is served. Nothing printed for a member
    without one. Reads only, writes nothing, takes no lock, never a tick."""
    if len(rest) != 1:
        refuse(USAGE)
    root, conductor = machine_house()
    name, member, started = member_judged(root, conductor, rest[0])
    entries = [{"doc": one["document"], "body": True,
                **({} if one["effect"] == "mounted" else {"constraints": False, "tools": False})}
               for one in season_view(root, conductor, name, started, member) if one["by"] == "vector"]
    if entries:
        print("::mount " + json.dumps(entries))
    return 0


def entry_verb(rest: list[str]) -> int:
    """`team entry <name> [--run <key>]` -- prints the document the team's wake-up under that run
    (`PP_RUN` when `--run` is absent) plays this exchange (`entry_of`): the decider of the team's
    document, played by the agent's engine -- whose `PP_HOME` names the AGENT, so the house is the
    machine the skill lives in, never the instance served. A team never started, a key no wake-up
    of the team holds: the neutral `TEAM-IDLE.md`, so that the agent's exchange always goes on.
    Nothing written."""
    root, conductor = machine_house()
    name, rest = named_team(conductor, rest)
    asked = flags(rest, ENTRY_FLAGS)
    run = asked["run"] or os.environ.get("PP_RUN", "").strip()
    if not run:
        refuse(USAGE)
    print(entry_of(root, name, run))
    return 0
