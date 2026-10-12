"""Scenario `ui-team-resume` -- `r` on the Tasks tab (plan ui, batches les-gestes-du-pilote and
les-deux-onglets), on the bench's
`pp-team` witness:
- `r` resumes the task under the cursor, written in an overlay with the command under it: a message empty,
  none; typed, `--message`; the principal chosen there, `--as`
- a refusal of the verb (`task-not-blocked`) goes to the remedy line as the verb said it
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-resume")

    shown = house.render("--render", "tasks", "--size", "130x40", "--press", "r,a,g,a,i,n")
    preview = T.preview_in(shown, "./pp team resume")
    house.clear_journal()
    bare = house.render("--render", "tasks", "--size", "130x40", "--press", "r,enter")
    played = house.gestures()
    house.clear_journal()
    said = house.render("--render", "tasks", "--size", "130x40", "--press", "r,a,g,a,i,n,enter")
    if (bare.returncode == 0 and said.returncode == 0 and played == ["team resume core-review --task T3"]
            and preview == "./pp team resume core-review --task T3 --message again"
            and house.gestures() == ["team resume core-review --task T3 --message again"]):
        held("r resumes the task", f"without a message, then with one -- {preview!r} shown first")
    else:
        failures.append(f"  ✗ resume                      {played} {house.gestures()} {said.stdout[-900:]!r}")

    house.clear_journal()
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "r,a,g,a,i,n,tab,space,down,enter,enter")
    if done.returncode == 0 and house.gestures() == ["team resume core-review --task T3 --message again --as pm"]:
        held("r takes the task back as a principal", house.gestures()[0])
    else:
        failures.append(f"  ✗ as                          rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r}")

    house.use(T.script(answers={"resume": {"rc": 2, "err": "pp-team: task-not-blocked -- T3 has a member due: "
                                                         "nothing to take back.\n"}}))
    done = house.render("--render", "tasks", "--size", "130x40", "--press", "r,enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and "task-not-blocked -- T3 has a member due" in remedy:
        held("a refusal goes to the remedy line as said", remedy)
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {remedy!r} {done.stdout[-700:]!r}")
    return 0
