"""Scenario `ui-team-new-start` -- `ctrl+s` in the form of `N` gives birth to the team, then starts it (plan ui, batch
le-formulaire-d-equipe), on the bench's witnesses: `team new veille-ram --template supervisor-workers`, then the path
of `S` on the team born -- its season (batch l-overlay-de-saison): its first message, the line `all` edited in its
profile -- and `team start veille-ram --message go …`, in this order in the witness's journal
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

KEYS = "N," + ",".join("veille-ram") + ",ctrl+s,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter,ctrl+s"
BORN = T.declaration("veille-ram", [(one, f"agents/veille-ram/{one}") for one in ("supervisor", "worker-1", "worker-2")],
                     {"budget": 5, "wakes": 8, "timeout": 900}, started=False)   # what `team new` wrote


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new-start", T.script(declarations={**T.DECLARATIONS, "veille-ram": BORN}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x60", "--press", KEYS)
    played = house.gestures()
    expected = ["team new veille-ram --template supervisor-workers",
                f"team start veille-ram --message go --provider {T.D.PROVIDER} --model opus"]
    if done.returncode == 0 and played == expected:
        held("ctrl+s gives birth to the team, then starts it", f"{played}")
    else:
        failures.append(f"  ✗ new then start              rc={done.returncode} {played} {done.stdout[-1800:]!r} "
                        f"{done.stderr[-400:]!r}")
    return 0
