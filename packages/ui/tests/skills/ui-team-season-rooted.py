"""Scenario `ui-team-season-rooted` -- the root of a team in the form of TEAM.md (cut from `ui-team-season-kept`,
rule 10), on the bench's witnesses (`_teams`): `core-review` as `ROOTED` says it (`root: lead` written) and as `OWNED`
says it (no `root:` written); the reason on the line of state, the witness's journal:
- the root written emptied: nothing played, the form left open on its reason, never `NOTHING_CHANGED`
- a root TEAM.md does not write left empty takes nothing out of TEAM.md: beside a principal added, `team declare
  core-review --principal ops --json`, the principal alone
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
F = support(__file__, "team_forms")    # the keys that type, the readers of a form by its zones
P = F.P

NOTHING = P.palette_constant("NOTHING_CHANGED")
TO_ROOT = F.team_to("Members") + ",tab"    # Members: the members, the root, then the principals
EMPTIED = ",".join(["backspace"] * 6)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-rooted", T.script(declarations={**T.DECLARATIONS, "core-review": T.ROOTED}),
                    agents=T.SEASON_AGENTS)

    # --- the root written, emptied: said, nothing played ---------------------------------------------------------------
    kept = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"E,{TO_ROOT},end,{EMPTIED},ctrl+enter,boxes")
    value, reason = P.field_of(F.fields(kept.stdout), "root"), F.state(kept.stdout)
    if (kept.returncode == 0 and value in ([], [""]) and "root" in reason.split() and NOTHING not in reason
            and house.gestures() == []):
        held("root emptied: said, nothing played", f"root {value}; {reason[:80]!r}")
    else:
        failures.append(f"  ✗ root emptied                rc={kept.returncode} {value} {reason!r} {house.gestures()}")

    # --- a root TEAM.md does not write, left empty beside a principal added: the principal alone ----------------------
    house.use(T.script(declarations={**T.DECLARATIONS, "core-review": T.OWNED}))
    house.clear_journal()
    added = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"E,{TO_ROOT},tab,end," + F.typed(" ops") + ",ctrl+enter")
    wanted = ["team declare core-review --principal ops --json"]
    if added.returncode == 0 and house.gestures() == wanted:
        held("a root TEAM.md does not write, left empty, takes nothing out", wanted[0])
    else:
        failures.append(f"  ✗ unwritten root              rc={added.returncode} {house.gestures()} "
                        f"{added.stdout[-1500:]!r}")
    return 0
