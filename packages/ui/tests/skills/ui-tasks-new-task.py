"""Scenario `ui-tasks-new-task` -- giving a team a new task in its overlay, the command under the fields what `enter`
plays word for word, on the bench's `pp-team` witness:
- `n` on the Teams tab: a new task to the root, `post` without `--task`
- `n` on the Tasks tab: its team the one of the task under the cursor, its name as typed, accents kept --
  `post core-review --name 'Réunion fournisseurs' --message go`
- `n` on the Tasks tab, its team chosen in the overlay: `post ops --message go`, its `to` and `as` following the team
  chosen
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

NEW = "./pp team post core-review --message go"
NAME = "Réunion fournisseurs"
NAMED = f"./pp team post core-review --name '{NAME}' --message go"
CHOSEN = "team post ops --message go"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-new-task")

    # --- n on the Teams tab: a new task ---------------------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x50", "--press", "n,g,o")   # the field every under the message
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "n,g,o,enter")
    played = house.gestures()
    if shown.returncode == 0 and done.returncode == 0 and preview == NEW and played == [preview[len("./pp "):]]:
        held("n posts a new task", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ new task                    rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-900:]!r}")

    # --- n on the Tasks tab: a name, accents kept -----------------------------------------------------
    keys = "n,g,o,shift+tab,shift+tab,shift+tab," + ",".join("space" if one == " " else one for one in NAME)
    shown = house.render("--render", "tasks", "--size", "200x60", "--press", keys)
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", keys + ",enter")
    if shown.returncode == 0 and done.returncode == 0 and preview == NAMED and house.gestures() == [NAMED[len("./pp "):]]:
        held("n names its task as typed", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ named                       rc={shown.returncode},{done.returncode} {preview!r} "
                        f"{house.gestures()} {shown.stdout[-1200:]!r} {shown.stderr[-300:]!r}")

    # --- n on the Tasks tab: the team chosen in the overlay -------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press",
                        "n,g,o,shift+tab,shift+tab,shift+tab,shift+tab,space,down,enter,enter")
    if done.returncode == 0 and house.gestures() == [CHOSEN]:
        held("n gives the team chosen its task", house.gestures()[0])
    else:
        failures.append(f"  ✗ team chosen                 rc={done.returncode} {house.gestures()} {done.stdout[-1200:]!r}")

    return 0
