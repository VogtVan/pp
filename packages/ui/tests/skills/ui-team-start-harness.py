"""Scenario `ui-team-start-harness` -- the harness of the post rides `S` (plan ui, batch la-grammaire-par-defaut; cut
from `ui-team-start` at the batch l-overlay-de-saison, rule 10), on the bench's witnesses:
- a `--harness` given after `--` to `./pp ui` rides the start, shown and played; no other flag of `--` does
- a `--provider` beside it rides with it, the grammar its output is read in: it replaces the provider of the
  overlay, a caller's command being no provider launched
- the harness stands before any `--member`: what follows one is that member's
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

KEYS = "down,down,S,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter"   # the message, then `all`'s model in its profile
START = f"./pp team start veille --message go --provider {T.D.PROVIDER} --model opus"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-start-harness")
    harnessed = START + " --harness 'run me'"
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", KEYS + ",ctrl+s",
                        "--", "--harness", "run me", "--launches", "3")
    if done.returncode == 0 and house.gestures() == [harnessed[5:]]:
        held("the harness of the post rides S", f"{harnessed}; --launches left to agent chat")
    else:
        failures.append(f"  ✗ harness                     rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    graded = "./pp team start veille --message go --model opus --harness 'run me' --provider p"
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", KEYS + ",ctrl+s",
                        "--", "--harness", "run me", "--provider", "p", "--launches", "3")
    if done.returncode == 0 and house.gestures() == [graded[5:]]:
        held("the grammar of the harness rides S with it", f"{graded}; the overlay's provider replaced")
    else:
        failures.append(f"  ✗ grammar                     rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    ordered = (f"team start core-review --budget 2 --provider {T.D.PROVIDER} --model opus --effort high --harness 'run me' "
               "--member reviewer --model sonnet --package plan=off")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "S,ctrl+s", "--", "--harness", "run me")
    if done.returncode == 0 and house.gestures() == [ordered]:
        held("the harness stands before any --member", ordered)
    else:
        failures.append(f"  ✗ harness before members      rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")
    return 0
