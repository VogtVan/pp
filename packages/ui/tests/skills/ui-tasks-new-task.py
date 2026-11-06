"""Scenario `ui-tasks-new-task` -- giving a team a new task in its overlay, what `enter` plays read from the journal
of the bench's `pp-team` witness, no command shown on screen:
- `n` on the Teams tab: a new task to the root, `post` without `--task`, played from a 130x40 screen where its fields
  scroll
- `n` on the Tasks tab: its team the one of the task under the cursor, its name as typed, accents kept --
  `post core-review --name 'Réunion fournisseurs' --message go`
- `n` on the Tasks tab, its team chosen in the overlay: `post ops --message go`, its `to` and `as` following the team
  chosen
- `n` with a period and a context limit: `post core-review --every 4h --context 70% --message go`; the limit typed
  without a period is not passed
  (a long message, no command shown: `ui-tasks-long-message`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

NEW = "team post core-review --message go"
NAME = "Réunion fournisseurs"
NAMED = f"team post core-review --name '{NAME}' --message go"
CHOSEN = "team post ops --message go"
LIMITED = "team post core-review --every 4h --context 70% --message go"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-new-task")

    # --- n on the Teams tab: a new task ---------------------------------------------------------------
    done = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o,enter")   # the fields scrolled
    played = house.gestures()
    if done.returncode == 0 and played == [NEW] and "./pp" not in done.stdout:
        held("n posts a new task", f"{played[0]!r} played, no command on screen")
    else:
        failures.append(f"  ✗ new task                    rc={done.returncode} {played} {done.stdout[-900:]!r}")

    # --- n on the Tasks tab: a name, accents kept -----------------------------------------------------
    keys = "n,g,o,shift+tab,shift+tab,shift+tab," + ",".join("space" if one == " " else one for one in NAME)
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", keys + ",enter")
    if done.returncode == 0 and house.gestures() == [NAMED]:
        held("n names its task as typed", f"{NAMED!r} played")
    else:
        failures.append(f"  ✗ named                       rc={done.returncode} {house.gestures()} "
                        f"{done.stdout[-1200:]!r} {done.stderr[-300:]!r}")

    # --- n on the Tasks tab: the team chosen in the overlay -------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press",
                        "n,g,o,shift+tab,shift+tab,shift+tab,shift+tab,space,down,enter,enter")
    if done.returncode == 0 and house.gestures() == [CHOSEN]:
        held("n gives the team chosen its task", house.gestures()[0])
    else:
        failures.append(f"  ✗ team chosen                 rc={done.returncode} {house.gestures()} {done.stdout[-1200:]!r}")

    # --- n with a period and a context limit; a limit without a period ----------------------------------
    said, codes = [], []
    for keys in ("n,g,o,tab,4,h,tab,7,0,%,enter", "n,g,o,tab,tab,7,0,%,enter"):
        house.clear_journal()
        limited = house.render("--render", "teams", "--size", "130x60", "--press", keys)
        codes.append(limited.returncode)
        said += house.gestures()
    if codes == [0, 0] and said == [LIMITED, NEW]:
        held("n passes a context limit with a period alone", f"{said}")
    else:
        failures.append(f"  ✗ context limit               {said} {limited.stdout[-1500:]!r}")

    return 0
