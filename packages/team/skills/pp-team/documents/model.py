"""The `documents` domain, layer `model`: what a team's documents are, held as plain values.

A definition belongs here when it is data about the documents a team serves its members, and does nothing: the names of
the files a team's directory holds, the vector family of a member, the prefix of a team's laws, or a type that carries
one of them. Nothing here reads the disk, the clock or the environment.
"""
from __future__ import annotations

MESSAGES = "messages.jsonl"      # the house's record pp-agent writes at every launch: read here for a late launch
ENTRY_FLAGS = {"run": True}
NO_DESCRIPTION = "no description"                # the sheet's word for a member without a description of its own
IDLE = "TEAM-IDLE.md"                            # the neutral successor: a wake-up whose trigger names no entry
SPEC = "TEAM_WORK.md"                            # how a team works: the package's `refs/`, served after the intention
IDLE_SOURCE = "agent-idle.md"                    # beside the entry `pp-team.py` -> the team's directory: the same bytes for every team
DECIDER = "pp-team entry"                        # what a team document's `decide:` plays: this skill's verb
ACT_FORMAT = "team-act"                          # the OUTPUT format an act is a production of (procs/TEAM-ACT.md declares it)
TURN_DOC = "TURN.md"                             # the kit's turn: the name its overlay takes in the team's directory
RETIRED_IN_TEAM = {TURN_DOC: ("retired/agent-turn-0.32.txt", "retired/agent-turn-0.39.txt")}   # the team's own law of
                                                 # an earlier version, in the team's directory: replaced at the start
SHEET = "members"                                # the name of the members' sheet: no document takes it
ROLES_DIR = "roles"                              # under the team's directory: the documents of a role, which the
                                                 # engine's flat reading of the root never sees -- mounted by a vector
MEMBER_FAMILY = "team-member"                    # the vector family this package declares: `team-member:<team>/<member>`
MOUNT_MOMENT = "turn.begin"                      # the one moment a document of a role may declare: its vector mounts
                                                 # it before the message of every exchange
TEAM_LAW = "TM"                                  # the prefix of a team's laws: every code a mounted document declares
