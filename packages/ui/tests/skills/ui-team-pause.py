"""Scenario `ui-team-pause` -- `P` pauses the team chosen, or resumes it when the face says it paused (plan ui, batch
l-etat-et-les-gestes), on the bench's `pp-team` witness:
- `P` on `core-review` (working): its overlay shows `./pp team pause core-review` under its field `as`; `enter` plays
  it as shown, `escape` plays nothing; `as` on `pm` plays `--as pm`
- `P` on a team the face says paused: `./pp team resume core-review`, never a `--task`
- a refusal of the verb (`team-paused`) goes to the remedy line as the verb said it
- the footer says `[P] pause/resume` and `[X] stop all tasks`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines

PAUSED = {**T.CORE, "state": "paused", "paused": T.PAUSED_AT}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-pause")

    # --- pause, shown then played; escape --------------------------------------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "P")
    preview = T.preview_in(shown, "./pp team pause")
    keys = P.keys_of(shown.stdout)
    house.clear_journal()
    house.render("--render", "teams", "--size", "130x40", "--press", "P,escape")
    escaped = house.gestures()
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "P,enter")
    if (shown.returncode == 0 and done.returncode == 0 and preview == "./pp team pause core-review" and escaped == []
            and house.gestures() == ["team pause core-review"] and "pause core-review" in shown.stdout):
        held("P pauses the team as shown", f"{preview!r} under its field; escape: nothing; enter: the pause")
    else:
        failures.append(f"  ✗ pause                       {preview!r} {escaped} {house.gestures()} {shown.stdout[-1500:]!r} "
                        f"{shown.stderr[-300:]!r}")
    if "[P] pause/resume" in keys and "[X] stop all tasks" in keys:
        held("the footer says P and X", "[P] pause/resume · [X] stop all tasks")
    else:
        failures.append(f"  ✗ footer                      {keys!r}")

    # --- as a principal ------------------------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "P,space,down,enter,enter")
    if done.returncode == 0 and house.gestures() == ["team pause core-review --as pm"]:
        held("P as a principal", "as pm: team pause core-review --as pm")
    else:
        failures.append(f"  ✗ as                          {house.gestures()} {done.stdout[-1500:]!r}")

    # --- a team the face says paused: resume ------------------------------------------------------------------
    house.use(T.script(states={"core-review": [PAUSED], "ops": [T.OPS]}))
    house.clear_journal()
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "P")
    preview = T.preview_in(shown, "./pp team resume")
    done = house.render("--render", "teams", "--size", "130x40", "--press", "P,enter")
    if done.returncode == 0 and preview == "./pp team resume core-review" and house.gestures() == ["team resume core-review"]:
        held("P resumes a team paused", f"{preview!r}, no --task")
    else:
        failures.append(f"  ✗ resume                      {preview!r} {house.gestures()} {shown.stdout[-1500:]!r}")

    # --- a refusal on the remedy line -------------------------------------------------------------------------
    house.use(T.script(answers={"pause": {"rc": 2, "err": "pp-team: team-paused -- core-review is paused since "
                                                          "09:20 by house: team resume core-review takes it back.\n"}}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "P,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == ["team pause core-review"] and "team-paused -- core-review" in remedy:
        held("a refusal said as the verb said it", f"{remedy[:70]!r}")
    else:
        failures.append(f"  ✗ refused                     {house.gestures()} {remedy!r} {done.stdout[-900:]!r}")
    return 0
