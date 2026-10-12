"""Scenario `ui-team-confirmed` -- the gestures of a team and of a task shown then played (plan ui, batches
les-gestes-du-pilote and les-deux-onglets), on the bench's `pp-team` witness:
- `s` on the Tasks tab (stop the task) and `T` (tick) on the Teams tab: the command in an overlay, `enter` plays
  it as shown, `escape` plays nothing (`x`, the inbox seen, lives in the overlay of the inbox: `ui-team-box`)
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-confirmed")

    for pane, keys, command in (("tasks", "s", "./pp team stop core-review --task T3"),
                                ("teams", "T", "./pp team tick core-review")):
        shown = house.render("--render", pane, "--size", "130x40", "--press", keys)
        preview = T.preview_in(shown, command.rsplit(" core-review", 1)[0])
        house.clear_journal()
        done = house.render("--render", pane, "--size", "130x40", "--press", keys + ",enter")
        played = house.gestures()
        house.clear_journal()
        none = house.render("--render", pane, "--size", "130x40", "--press", keys + ",escape")
        if (shown.returncode == 0 and done.returncode == 0 and preview == command
                and played == [command[len("./pp "):]] and none.returncode == 0 and house.gestures() == []):
            held(f"{keys.rsplit(',', 1)[-1]} shows, then plays", f"{command!r}; escape plays nothing")
        else:
            failures.append(f"  ✗ {keys:<28} rc={shown.returncode},{done.returncode} {preview!r} {played} "
                            f"{house.gestures()} {shown.stdout[-900:]!r}")

    return 0
