"""Scenario `ui-real-team-inbox` -- the owner's inbox at the post, on the REAL verbs of `team` (plan ui, batch
le-reel-du-centre; cut from `ui-real-team-budget`, rule 10), its wake-ups played by the team witness, never a
provider: `dev` asks the owner a question -- `b` shows it, read from the real `team inbox --json`; `x` there writes
`inbox-seen` at the journal
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team, ask, owner, begun = R.asking(bench, "ui-real-team-inbox")

    shown = team.render("--render", "teams", "--size", "200x50", "--press", "b")
    question = f"#{ask.get('id')} ask from dev on T1"
    seen = team.render("--render", "teams", "--size", "200x50", "--press", "b,x")
    marks = team.kinds("inbox-seen")
    if begun and shown.returncode == 0 and seen.returncode == 0 and ask and question in _flat(shown.stdout) and len(marks) == 1:
        held("b reads the real inbox, x marks it seen", f"{question!r}; inbox-seen #{marks[0].get('id')}")
    else:
        failures.append(f"  ✗ inbox                       begun={begun} ask={ask} marks={marks} {shown.stdout[-1200:]!r}")
    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
