"""Scenario `ui-team-new-task` -- `n` on the Tasks tab, a new task written in its overlay (plan ui, batch
les-overlays-des-gestes; cut from `ui-team-gestures`, rule 10), on the bench's `pp-team` witness:
- its team the one of the task under the cursor, its name as typed, accents kept: `post core-review --name
  'Réunion fournisseurs' --message go`, the command under the fields played word for word
- its team chosen in the overlay: `post ops --message go`, its `to` and `as` following the team chosen
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new-task")

    # --- n on the Tasks tab: a name, accents kept ----------------------------------------------------
    named = "./pp team post core-review --name 'Réunion fournisseurs' --message go"
    keys = "n,g,o,shift+tab,shift+tab,shift+tab," + ",".join(
        "space" if one == " " else one for one in "Réunion fournisseurs")
    shown = house.render("--render", "tasks", "--size", "200x50", "--press", keys)
    preview = T.preview_in(shown, "./pp team post")
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", keys + ",enter")
    if shown.returncode == 0 and done.returncode == 0 and preview == named and house.gestures() == [named[len("./pp "):]]:
        held("n names its task as typed", f"{preview!r} shown, then played")
    else:
        failures.append(f"  ✗ named                       rc={shown.returncode},{done.returncode} {preview!r} "
                        f"{house.gestures()} {shown.stdout[-1200:]!r} {shown.stderr[-300:]!r}")

    # --- n on the Tasks tab: the team chosen in the overlay ------------------------------------------
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press",
                        "n,g,o,shift+tab,shift+tab,shift+tab,shift+tab,space,down,enter,enter")
    if done.returncode == 0 and house.gestures() == ["team post ops --message go"]:
        held("n gives the team chosen its task", house.gestures()[0])
    else:
        failures.append(f"  ✗ team chosen                 rc={done.returncode} {house.gestures()} {done.stdout[-1200:]!r}")
    return 0
