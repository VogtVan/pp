"""Scenario `ui-team-delete` -- `D` deletes a team on its name typed (cut from `ui-team-guarded`, rule 10), on the
bench's `pp-team` witness -- what plays read from its journal, no command on screen:
- `D` deletes the team chosen: what the dry run of `team delete ops --json` would remove shown, the agents it lists as
  checks; `enter` plays nothing until `ops` is typed -- `tab` goes from the checks to the name --; typed,
  `team delete ops --yes` plays once and the team leaves the menu; `team-busy`
  goes to the remedy line, nothing played
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

DRY = "team delete ops --json"
DELETE = "team delete ops --yes"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-delete")

    # --- D: the dry run, the name typed, --yes once; team-busy to the remedy ---------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,ctrl+enter")
    dry = house.gestures()
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,tab,o,p,s,ctrl+enter")
    menu = [one.split()[0] for one in T.sides_of(done.stdout)[0] if one.split()]
    if (shown.returncode == 0 and done.returncode == 0 and "./pp" not in shown.stdout and dry == [DRY]
            and "teams/ops" in shown.stdout and "b11111" in shown.stdout
            and house.gestures() == [DRY, DELETE] and "ops" not in menu and "core-review" in menu):
        held("D deletes a team on its name typed", f"the dry run shown, no command; enter alone played {dry}; typed: "
             f"{house.gestures()}, the menu {menu}")
    else:
        failures.append(f"  ✗ delete                      rc={shown.returncode},{done.returncode} {dry} "
                        f"{house.gestures()} {menu} {shown.stdout[-1600:]!r} {done.stderr[-400:]!r}")
    house.use(T.script(answers={"delete": {"rc": 2, "err": "pp-team: team-busy -- ops is at work (T1): stop it "
                                                           "first (`team stop ops --kill`), then delete it.\n"}}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x40", "--press", "down,D,o,p,s,ctrl+enter")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and house.gestures() == [DRY] and "team-busy" in remedy and "./pp" not in done.stdout:
        held("D on a team at work: team-busy on the remedy line", f"{remedy[:60]!r}; nothing played")
    else:
        failures.append(f"  ✗ delete busy                 rc={done.returncode} {house.gestures()} {remedy!r} "
                        f"{done.stdout[-1200:]!r}")
    return 0
