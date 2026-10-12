"""Scenario `ui-real-team-declaration` -- the declaration of a team at the post, on the REAL verbs of `team` (plan
ui, batch le-reel-du-centre; cut from `ui-real-team-budget`, rule 10), its wake-ups played by the team witness,
never a provider: `essai` started -- `e` says `verdict ok` and nothing pending, read from the real `team declaration
--json`; `TEAM.md` edited in the house (`root: dev`), `e` says the key `root` waiting a start
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-declaration", {"lead": [{"body": {"done": "started"}}]})
    begun = team.start("go")
    started = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))

    read = team.render("--render", "teams", "--size", "200x50", "--press", "e")
    team.edit("root: lead", "root: dev")
    gap = team.render("--render", "teams", "--size", "200x50", "--press", "e")
    before, after = _flat(read.stdout), _flat(gap.stdout)
    if (begun.returncode == 0 and started and read.returncode == 0 and gap.returncode == 0 and "verdict ok" in before
            and "nothing pending" in before and "root · lead → dev" in after and "1 key(s) wait a start" in after
            and not team.alive()):
        held("e reads the real declaration and its gap", "verdict ok, nothing pending; root edited: root · lead → dev")
    else:
        failures.append(f"  ✗ declaration                 started={started} {read.stdout[-1200:]!r} {gap.stdout[-1200:]!r}")
    return 0
