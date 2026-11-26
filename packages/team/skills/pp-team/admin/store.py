"""The `admin` domain, layer `store`: where the house is cleaned of what a team left.

A definition belongs here when it reaches the disk to remove what a team or an earlier version laid in an agent's
instance, and says what it removed. A judgement that needs no system belongs to a rule.
"""
from __future__ import annotations

import sys
from pathlib import Path

from house.rules import agent_meta
from house.store import ENTRY
from admin.model import RETIRED


def cleared(root: Path, name: str, team: dict) -> None:
    """Removes from each agent of the team what an earlier version laid in its instance: the files at
    the team's very bytes (`RETIRED`: the law and the neutral successor of team 0.32, the decider skill)
    and `procs/TEAM-<name>.md` deciding by `team-entry <name>`; a file that differs is the agent's own --
    kept, and said. Nothing of a team is written there."""
    here = Path(ENTRY).resolve().parent
    for path in dict.fromkeys(team.agents.values()):
        meta = agent_meta(root, path)
        for where, source in RETIRED.items():
            target = meta.joinpath(*where)
            if not target.is_file():
                continue
            if (here / source).is_file() and target.read_bytes() == (here / source).read_bytes():
                target.unlink()
            else:
                print(f"pp-team: {path} · {'/'.join(where)} kept -- not the team's: the agent's own stays",
                      file=sys.stderr)
        skill = meta / "skills" / "team-entry"
        if skill.is_dir() and not any(skill.iterdir()):
            skill.rmdir()
        laid = meta / "procs" / f"TEAM-{name}.md"
        if laid.is_file():
            if f"decide: team-entry {name}" in laid.read_text(encoding="utf-8", errors="replace"):
                laid.unlink()
            else:
                print(f"pp-team: {path} · procs/TEAM-{name}.md kept -- not the team's: the agent's own stays",
                      file=sys.stderr)
