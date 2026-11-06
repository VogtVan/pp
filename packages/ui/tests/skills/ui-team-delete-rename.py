"""Scenario `ui-team-delete-rename` -- `D` and `r` on the Teams tab, on the bench's `pp-team` witness (batch
les-equipes-au-poste, ui 0.60.0):
- `D` on `ops`: the agents the dry face lists as the team's alone, one line each, none checked, no command shown;
  `space` checks the first; the team's name typed and `enter` play `team delete ops --agent agents/dba --yes`, as the
  witness's journal says it
- `r` on `core-review`: one field, the new name; `enter` plays `team rename core-review <new>`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture

DELETE_ONE = "team delete ops --agent agents/dba --yes"
RENAME = "team rename core-review fresh"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-delete-rename")

    # --- D on ops: the agents in checks, none checked; space composes --agent; the name typed plays ------------
    agents = T.DELETES["ops"]["agents"]
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "down,D")
    rows = P.overlay_rows(shown.stdout)
    try:
        glyph = P.palette_constant("UNCHECKED")
    except KeyError:
        glyph = ""
    unchecked = [row for row in rows if any(one in row for one in agents) and glyph in row]
    checked = house.render("--render", "teams", "--size", "130x40", "--press", "down,D,space")
    listed = [row.strip(" ▊▎") for row in P.overlay_rows(checked.stdout) if row.startswith("▊")]   # the list's lines
    ticked = P.palette_constant("CHECKED")
    marks = {one: [ticked in row for row in listed if row.endswith(one)] for one in agents}   # the first one checked
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "down,D,space,tab,o,p,s,enter")
    if (shown.returncode == 0 and checked.returncode == 0 and done.returncode == 0 and len(unchecked) == len(agents)
            and "./pp" not in shown.stdout and marks == {agents[0]: [True], agents[1]: [False]}
            and house.gestures() == ["team delete ops --json", DELETE_ONE]):
        held("D lists the agents and composes --agent", f"{len(agents)} agents, none checked, no command; space checks "
             f"the first: {DELETE_ONE!r}, played once ops is typed")
    else:
        failures.append(f"  ✗ D with its checks           rc={shown.returncode},{checked.returncode},{done.returncode} "
                        f"unchecked={unchecked} {marks} {house.gestures()} "
                        f"{[row for row in P.overlay_rows(checked.stdout) if 'agents/' in row]!r}")

    # --- r renames the team: enter plays the field ------------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "r,f,r,e,s,h,enter")
    if done.returncode == 0 and house.gestures() == [RENAME]:
        held("r renames the team", f"{RENAME!r} played")
    else:
        failures.append(f"  ✗ rename                      rc={done.returncode} {house.gestures()} {done.stdout[-1200:]!r}")
    return 0
