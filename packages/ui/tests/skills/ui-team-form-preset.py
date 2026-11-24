"""Scenario `ui-team-form-preset` -- the section Preset of the form of TEAM.md (batch les-volets-par-onglet), on the
bench's `pp-team` witness (`_team_new`): `N`, the team `ram`, its first preset `teams/supervisor-workers` declaring
`daily` and `focus`, the second `teams/lead-reviewers` declaring `daily` alone:
- Preset shows the preset, then one field per value it declares: `daily` and `focus`
- `daily` and `focus` typed, then the second preset chosen: the fields made anew -- `daily` keeps what was typed,
  `focus` gone, and its value typed with it: no field shows it, no document of the list declares it --, the file in the
  side pane holds `daily = 4h` under the new preset and no `focus`
- `enter`: `team declare ram --template teams/lead-reviewers --value daily=4h --schedule 30s --json` -- the value a line of `values:`,
  never `--value focus=x`, which `team declare` would refuse `value-unknown` (todo la-valeur-tapee-orpheline)
Its siblings: `ui-team-form-documents-holes` (Preset without a preset, a document's value not listed there),
`ui-team-season-preset` (the preset of a season and its fields).
"""
from __future__ import annotations

from tests.harness import support

N = support(__file__, "team_new")
F, T, P = N.F, N.T, N.P

LEAD = {**N.LEAD, "values": N.FIRST["values"][:1]}         # lead-reviewers, declaring `daily` alone
TEMPLATES = [one if one["template"] != LEAD["template"] else LEAD for one in T.TEMPLATES]
OPENED = N.keys(N.NAMED, N.TO_PRESET)
# daily and focus typed, then the second preset
SWITCHED = N.keys(OPENED, "tab", N.typed("4h"), "tab,x", "shift+tab,shift+tab,space,down,enter")
DECLARED = f"team declare ram --template {LEAD['template']} --value daily=4h {N.BORN}"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-preset", T.script(templates=TEMPLATES))

    # --- the first preset: one field per value it declares ------------------------------------------------------------
    opened = house.render("--render", "teams", *N.SIZE, "--press", f"{OPENED},boxes")
    rows = F.fields(opened.stdout)
    titles = [P.field_title(one["name"]) for one in N.FIRST["values"]]
    if opened.returncode == 0 and all(one in rows for one in titles):
        held("Preset: a field per value the preset declares", f"{titles}")
    else:
        failures.append(f"  ✗ fields                      rc={opened.returncode} {rows} {opened.stderr[-300:]!r}")

    # --- another preset: the fields made anew, the value of a name both declare kept ---------------------------------
    switched = house.render("--render", "teams", *N.SIZE, "--press", f"{SWITCHED},boxes")
    rows, file = F.fields(switched.stdout), F.zone_rows(switched.stdout, "form-file")
    if (switched.returncode == 0 and P.field_of(rows, "daily") == ["4h"] and P.field_title("focus") not in rows
            and "daily = 4h" in file and f"template: {LEAD['template']}" in file
            and not any(row.startswith("focus") for row in file)):
        held("another preset: its fields, the value typed kept by name", f"daily {P.field_of(rows, 'daily')}; "
             f"no focus; the file: daily = 4h")
    else:
        failures.append(f"  ✗ switched                    rc={switched.returncode} {rows} {file} "
                        f"{switched.stderr[-300:]!r}")

    # --- enter: the value written to values: ---------------------------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *N.SIZE, "--press", f"{SWITCHED},ctrl+enter")
    if house.gestures() == [DECLARED]:
        held("a value of Preset written to values:", DECLARED)
    else:
        failures.append(f"  ✗ written                     {house.gestures()}")
    return 0
