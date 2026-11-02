"""Scenario `ui-tasks-live` -- the tasks a wake-up plays, on the bench's `pp-team` witness whose script changes by
`use()`:
- the face saying `running` on core-review's T3 (`reviewer`) and on ops' T1 (`sre`): each of the two lines carries the
  spinner before its name, the tab's title the spinner and the count of such tasks, and the spinner's interval is
  alive (the render's word `spinning`)
- the face read without `running`: no glyph on a line nor in the title, no interval alive
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")

SPINNER = P.palette_constant("SPINNER")


def task_of(face: dict, task: str) -> dict:
    return next(one for one in face["tasks"] if one["id"] == task)


def line_of(text: str, mark: str) -> str:
    return next((one for one in text.split("\n") if mark in one), "")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    script = T.script()
    script["states"].update({"core-review": [T.LIVE_CORE], "ops": [T.LIVE_OPS]})
    house = T.Teams(bench, "ui-tasks-live", script)
    t3, t1 = task_of(T.LIVE_CORE, "T3"), task_of(T.LIVE_OPS, "T1")
    names = (t3["name"], t1["text"][:20])
    turning = sum(1 for face in (T.LIVE_CORE, T.LIVE_OPS) for one in face["tasks"] if one.get("running"))
    glyph = f"[{re.escape(SPINNER)}]"

    # --- two tasks a wake-up plays ---------------------------------------------------------------------
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning,down")
    rows = [line_of(done.stdout, name) for name in names]
    title = next((one for one in done.stdout.split("\n") if re.search(rf"{glyph} {turning}\b", one)
                  and not any(name in one for name in names)), "")
    last = P.status_of(done.stdout)
    if (done.returncode == 0 and all(re.search(glyph, one) for one in rows) and title
            and last == "spinning 1"):
        held("the tasks a wake-up plays turn", f"{rows[0].strip()[:40]!r}, {rows[1].strip()[:40]!r}; "
             f"{title.strip()[-24:]!r}; {last}")
    else:
        failures.append(f"  ✗ live tasks                  rc={done.returncode} {rows!r} {title!r} {last!r} "
                        f"{done.stdout[-2000:]!r} {done.stderr[-400:]!r}")

    # --- none plays: no glyph, no interval ------------------------------------------------------------
    house.use(T.script())
    done = house.render("--render", "tasks", "--size", "150x40", "--press", "spinning,down")
    review = line_of(done.stdout, names[0])
    last = P.status_of(done.stdout)
    if done.returncode == 0 and review and not re.search(glyph, done.stdout) and last == "spinning 0":
        held("no wake-up, nothing turns", f"{review.strip()[:40]!r}; {last}")
    else:
        failures.append(f"  ✗ at rest                     rc={done.returncode} {review!r} {last!r} "
                        f"{done.stdout[-1500:]!r}")

    return 0
