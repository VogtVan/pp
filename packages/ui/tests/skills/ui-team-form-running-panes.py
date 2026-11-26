"""Scenario `ui-team-form-running-panes` -- in season the two forms show the same sections and the same side panes as
off season (batch les-volets-par-onglet, todo la-saison-lue-onglets-et-volets; cut from `ui-team-form-running`, rule
10), on the bench's `pp-team` witness, `core-review` in season:
- `E` in season: its bar says Team, Preset, Members, Documents, Limits, Owner's word, and each section shows the zones
  of the side pane the table says off season (`ui-team-form-frame`)
- `S` in season, opened on Members: its bar says Preset, Documents, Launch, Members, Season's word, and each section
  shows its zones the same way
- `s` in season on a SEASON.md that writes a preset and its values (s.1645, batch le-season-en-lecture-seule): the
  season read only shows SEASON.md as it is written (`season.text`) in its side pane, its fields closed
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
R = support(__file__, "team_form_running")
T = F.T

IN_SEASON = F.P.palette_constant("IN_SEASON")    # what the line of state says of a form read in season
SIDE = tuple(zone for zones in F.PANES.values() for zone in zones)
OPENED = F.SEASON_TABS.index("Members")         # the section `S` opens on in season
WRITTEN = ("template: seasons/files", "readers = readers")    # what SEASON.md writes, `T.FILES`
WRITES = T.script(declarations={**T.DECLARATIONS, "core-review": T.declaration(
    "core-review", [("lead", "agents/lead"), ("reviewer", "agents/reviewer")], {"budget": 1.0},
    template="teams/supervisor-workers", roles=(("make", ["lead"]),), season=T.CORE_SEASON, season_file=T.FILES,
    running=True)}, states={"core-review": [R.STATE], "ops": [T.OPS]})   # in season, SEASON.md writing `T.FILES`


def walk(form: str, tabs: list[str]) -> str:
    return ",".join([form, "boxes"] + ["ctrl+pagedown,boxes"] * (len(tabs) - 1))


def notings(text: str) -> list[list[str]]:
    """-> the zones of the side pane each noting of `boxes` shows, in the order of `SIDE`."""
    line = next((one for one in text.splitlines() if one.startswith("boxes ")), "")
    return [[zone for zone in SIDE if f"{zone}=" in noted] for noted in line[len("boxes "):].split(" | ")] if line else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-running-panes", R.script())
    for form, tabs, panes, first in (("E", F.TEAM_TABS, F.TEAM_PANES, 0), ("S", F.SEASON_TABS, F.SEASON_PANES, OPENED)):
        done = house.render("--render", "teams", *F.SIZE, "--press", walk(form, tabs))
        order = [(first + n) % len(tabs) for n in range(len(tabs))]
        wanted = [list(F.PANES[panes[n]]) for n in order]
        shown, bar = notings(done.stdout), F.tabs_row(done.stdout)
        if done.returncode == 0 and bar == tabs and shown == wanted and IN_SEASON in F.state(done.stdout):
            held(f"{form} in season: the sections and the side panes of off season",
                 "; ".join(f"{tabs[n]} {panes[n]}" for n in order))
        else:
            failures.append(f"  ✗ {form} in season{'':<17}rc={done.returncode} {bar} {shown} wanted {wanted} "
                            f"{done.stderr[-300:]!r}")

    # --- s.1645: `s` in season shows SEASON.md as it is written, its fields closed ------------------------------------
    house.use(WRITES)
    done = house.render("--render", "teams", *F.SIZE, "--press", "s,boxes")
    rows = F.zone_rows(done.stdout, "form-file")
    if done.returncode == 0 and all(any(one in row for row in rows) for one in WRITTEN) and "read only" in done.stdout:
        held("s in season shows SEASON.md as written", f"{' · '.join(WRITTEN)}, read only")
    else:
        failures.append(f"  ✗ s in season, SEASON.md       rc={done.returncode} {[row for row in rows if row]} "
                        f"{done.stderr[-300:]!r}")
    return 0
