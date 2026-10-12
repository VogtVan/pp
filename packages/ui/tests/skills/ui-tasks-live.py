"""Scenario `ui-tasks-live` -- the tasks a wake-up plays turn (plan ui, batch les-taches-vivantes), on the bench's
`pp-team` witness, the face saying `running` on core-review's T3 (`reviewer`) and on ops' T1 (`sre`):
- each of the two lines carries the spinner before its name, the tab's title says `4·Tasks <glyph> 2`, and the
  spinner's interval is alive (the render's word `spinning`)
- the face read without `running`: no glyph on a line, the title back to `4·Tasks`, no interval alive
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")

GLYPHS = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def _line(text: str, name: str) -> str:
    return next((one for one in text.split("\n") if name in one), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script()
    script["states"].update({"core-review": [T.LIVE_CORE], "ops": [T.LIVE_OPS]})
    house = T.Teams(bench, "ui-tasks-live", script)

    # --- two tasks a wake-up plays ---------------------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning")
    review, rotate = _line(done.stdout, "review PR 88"), _line(done.stdout, "rotate the certificates")
    title = next((one for one in done.stdout.split("\n") if "4·Tasks" in one), "")
    last = done.stdout.rstrip("\n").split("\n")[-1]
    if (done.returncode == 0 and any(glyph in review for glyph in GLYPHS) and any(glyph in rotate for glyph in GLYPHS)
            and re.search(rf"4·Tasks [{GLYPHS}] 2\b", title) and last == "spinning 1"):
        held("the tasks a wake-up plays turn", f"{review.strip()[:40]!r}, {rotate.strip()[:40]!r}; "
             f"{title.strip()[-16:]!r}; {last}")
    else:
        failures.append(f"  ✗ live tasks                  rc={done.returncode} {review!r} {rotate!r} {title!r} {last!r} "
                        f"{done.stdout[-2000:]!r} {done.stderr[-400:]!r}")

    # --- none plays: no glyph, the plain title, no interval ----------------------------------------------
    house.use(T.script())
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning")
    review = _line(done.stdout, "review PR 88")
    title = next((one for one in done.stdout.split("\n") if "4·Tasks" in one), "")
    last = done.stdout.rstrip("\n").split("\n")[-1]
    if (done.returncode == 0 and review and not any(glyph in review for glyph in GLYPHS)
            and not re.search(rf"4·Tasks [{GLYPHS}]", title) and last == "spinning 0"):
        held("no wake-up, nothing turns", f"{review.strip()[:40]!r}; {title.strip()[-12:]!r}; {last}")
    else:
        failures.append(f"  ✗ at rest                     rc={done.returncode} {review!r} {title!r} {last!r} "
                        f"{done.stdout[-1500:]!r}")
    return 0
