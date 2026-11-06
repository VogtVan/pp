"""Scenario `ui-tasks-long-message` -- a long message typed in the overlay `n` of the Tasks tab, on a 130x40 screen
(batch les-commandes-retirees), on the bench's `pp-team` witness: no command shows anywhere, the field `every` and the
line of keys stay in sight while the message grows, and `enter` plays the post with its message whole
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

LONG = "review the open pull requests and say what blocks each one then rank them by the risk they carry"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-tasks-long-message")

    # --- a long message: no command shown, the fields and the keys in sight ---------------------------------
    typed = "n," + ",".join("space" if one == " " else one for one in LONG)
    shown = house.render("--render", "tasks", "--size", "130x40", "--press", typed)
    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", typed + ",enter")
    screen = P.on_top(shown.stdout)
    if (shown.returncode == done.returncode == 0 and "./pp" not in shown.stdout and P.field_title("every") in screen
            and "plays" in screen and house.gestures()
            and house.gestures()[0].endswith(f"--message '{LONG}'")):
        held("a long message shows no command and keeps the fields in sight", f"{len(LONG)} characters typed, played")
    else:
        failures.append(f"  ✗ long message                {'./pp' in shown.stdout} {P.field_title('every') in screen} "
                        f"{"plays" in screen} {house.gestures()} {screen[-1800:]!r}")

    return 0
