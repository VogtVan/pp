"""Scenario `ui-team-season-kept-preset` -- `E` on a team whose owner wrote more of TEAM.md than `team declare` can
take back, on the bench's witnesses (`_teams`): `core-review` as `OWNED` says it -- its principals `pm qa`, its
preset, its budget, a TEAM.md that writes no `root:`; its field changed read, the reason on the line of state -- naming the value taken
out, never `NOTHING_CHANGED` -- and the witness's journal:
- the preset put on the empty entry: nothing played, the form left open on its reason
Cut from `ui-team-season-kept` (rule 10), which takes a principal out and empties the budget.
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
F = support(__file__, "team_forms")    # the keys that type, the readers of a form by its zones
P = F.P

NOTHING = P.palette_constant("NOTHING_CHANGED")
BLANK = P.palette_constant("PRESET_BLANK")
TO_PRESET = F.team_to("Preset")            # Preset: the preset first
# each change: its keys, the field it changes, what the field then shows, a word its reason says
CHANGES = [("template emptied", f"{TO_PRESET},space,up,enter,ctrl+enter", "preset", [BLANK], "template")]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-kept-preset",
                    T.script(declarations={**T.DECLARATIONS, "core-review": T.OWNED}), agents=T.SEASON_AGENTS)

    # --- what the verb cannot write: one render per change, its field read, its reason, nothing played --------------
    for said, keys, field, shown, word in CHANGES:
        house.clear_journal()
        kept = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"E,{keys},boxes")
        value, reason = P.field_of(F.fields(kept.stdout), field), F.state(kept.stdout)
        if (kept.returncode == 0 and value in (shown, [] if shown == [""] else shown) and word in reason.split()
                and NOTHING not in reason and house.gestures() == []):
            held(f"{said}: said, nothing played", f"{field} {value}; {reason[:80]!r}")
        else:
            failures.append(f"  ✗ {said:<28}rc={kept.returncode} {field} {value} {reason!r} {house.gestures()} "
                            f"{F.fields(kept.stdout)[-14:]!r} {kept.stderr[-300:]!r}")

    return 0
