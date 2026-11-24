"""Scenario `ui-team-form-season-tabs` -- the sections of the season's form (batch les-reglages-des-formulaires), on the
bench's `pp-team` witness replaying the faces of team 1.26.0: `core-review`, its SEASON.md writing no context:
- `S`: five sections, in the order Preset, Documents, Launch, Members, Season's word (batch les-volets-par-onglet) --
  no First task, no Values; Launch holds
  `work`, the season's budget, its launches and its silence, and neither the context nor the lines; its budget
  focused, the line of keys offers no new line (`enter` goes to the next field)
- Members: the table of the lines first, titled Members, its first column `member`; the context under it, opened on
  90; no field of a first task anywhere (`name`, `message`)
- `ctrl+s` with nothing changed: `team declare core-review --season --context 90` -- the default written --, then
  `team start core-review`, no `--message`
Its siblings: `ui-team-form-season` (SEASON.md written, then started), `ui-team-form-limits` (a context SEASON.md writes),
`ui-team-form-season-documents` (the season's documents, cut from this one).
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-season-tabs", F.script())

    # --- Launch: the work, the budget, the launches, the silence -----------------------------------------------------
    launch = house.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_LAUNCH},boxes")
    rows, tabs, keys = F.fields(launch.stdout), F.tabs_row(launch.stdout), F.keys_row(launch.stdout)
    titled = [P.field_title(one) for one in ("work", "season budget", "season launches", "silence")]
    if (launch.returncode == 0 and tabs == F.SEASON_TABS and all(one in rows for one in titled)
            and not any(one in rows for one in ("Context", "Members", "Lines", "Name", "Message"))
            and keys and F.NEW_LINE not in keys):
        held("five sections; Launch without the context nor the lines", f"{tabs}; {titled}; keys {keys!r}")
    else:
        failures.append(f"  ✗ launch                      rc={launch.returncode} {tabs} {rows} {keys!r} "
                        f"{launch.stdout[-1500:]!r} {launch.stderr[-300:]!r}")

    # --- Members: the table first, then the context at 90 -----------------------------------------------------------
    members = house.render("--render", "teams", *F.SIZE, "--press", f"S,{F.TO_LINES},boxes")
    rows = F.fields(members.stdout)
    table = next((n for n, row in enumerate(rows) if row == "Members"), None)
    context = next((n for n, row in enumerate(rows) if row == "Context"), None)
    head = rows[table + 1].split() if table is not None and table + 1 < len(rows) else []
    if (members.returncode == 0 and table is not None and context is not None and table < context
            and head[:2] == ["member", "agent"] and P.field_of(rows, "context") == ["90"]
            and not any(one in rows for one in ("Name", "Message", "Lines"))):
        held("Members: the table, then the context at 90", f"{rows[table]!r} {head[:3]} then context "
             f"{P.field_of(rows, 'context')}")
    else:
        failures.append(f"  ✗ members                     rc={members.returncode} {rows} {members.stdout[-1500:]!r} "
                        f"{members.stderr[-300:]!r}")

    # --- ctrl+s: the default context reaches the start ---------------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", "S,ctrl+s")
    if house.gestures() == [T.NEXT_DECLARED, T.NEXT]:
        held("ctrl+s starts with the context of 90, no task", T.NEXT)
    else:
        failures.append(f"  ✗ ctrl+s                      {house.gestures()}")
    return 0
