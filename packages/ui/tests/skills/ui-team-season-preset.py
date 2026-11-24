"""Scenario `ui-team-season-preset` -- `S` on a team at work, another preset of its season chosen, then the season
opened (cut from `ui-team-season-new`, rule 10), on the bench's witnesses (`_teams`): `core-review`, in its first
season, its season's preset `seasons/files`; what plays read from the witness's journal:
- another preset of the season chosen: `team declare core-review --season --template seasons/plan-branch`, then `team
  start core-review --context 90` -- the season's context at the form's default, no task
- `S` opens on Preset (batch les-volets-par-onglet): the preset, then a field per value it declares -- `readers` --;
  another preset chosen, its own -- `base` --, the first's gone
- the fields made anew come late (the bench's `witness/_slow-fields`, 1 s, what a loaded machine does): the capture
  is taken once they are in their box -- `base` shown, `readers` gone -- all the same
- the choice told late (the same witness, 1 s: the list shows the preset chosen before the form hears of it): the
  capture shows the fields of the preset the list shows -- `base` shown, `readers` gone
"""
from __future__ import annotations

from pathlib import Path

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a form's fields

CHOSEN = "S,space,down,enter"          # `S` focuses the preset: the next one chosen
SLOW_FIELDS = Path(__file__).resolve().parents[1] / "witness" / "_slow-fields"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-preset", agents=T.SEASON_AGENTS)

    # --- Preset: the fields of the preset chosen ------------------------------------------------------------------------
    opened = house.render("--render", "teams", *T.SEASON_SMALL, "--press", "S,boxes")
    chosen = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"{CHOSEN},boxes")
    first, then = (P.overlay_rows(one.stdout) for one in (opened, chosen))
    readers, base = P.field_title("readers"), P.field_title("base")
    if readers in first and base not in first and base in then and readers not in then:
        held("Preset: the fields of the preset chosen, made anew", f"{readers}, then {base}")
    else:
        failures.append(f"  ✗ preset's fields             {first} {then}")

    # --- the fields made anew late: the capture waits for them --------------------------------------------------------
    plain = house.env
    house.env = {**plain, "PYTHONPATH": str(SLOW_FIELDS), "PP_UI_SLOW_FIELDS": "1"}
    late = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"{CHOSEN},boxes")
    house.env = plain
    slow = P.overlay_rows(late.stdout)
    if late.returncode == 0 and base in slow and readers not in slow:
        held("the fields made anew late are waited for", f"mounted 1 s after the preset was chosen: {base} shown, "
             f"{readers} gone")
    else:
        failures.append(f"  ✗ late fields                 rc={late.returncode} {slow} {late.stderr[-300:]!r}")

    # --- the choice told late: the capture shows the fields of the preset the list shows ----------------------------
    house.env = {**plain, "PYTHONPATH": str(SLOW_FIELDS), "PP_UI_SLOW_CHOICE": "1"}
    untold = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"{CHOSEN},boxes")
    house.env = plain
    shown = P.overlay_rows(untold.stdout)
    if untold.returncode == 0 and base in shown and readers not in shown:
        held("the choice told late is read on its list", f"told 1 s after the preset was chosen: {base} shown, "
             f"{readers} gone")
    else:
        failures.append(f"  ✗ late choice                 rc={untold.returncode} {shown} {untold.stderr[-300:]!r}")

    # --- another preset of the season --------------------------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *T.SEASON_SMALL, "--press", f"{CHOSEN},ctrl+s")
    wanted = [f"team declare core-review --season --template {T.SEASONS[1]['template']} --context 90 --json", T.NEXT]
    if done.returncode == 0 and house.gestures() == wanted:
        held("another preset of the season, then the season", f"{wanted}")
    else:
        failures.append(f"  ✗ preset                      rc={done.returncode} {house.gestures()} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")

    return 0
