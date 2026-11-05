"""Scenario `ui-team-delete-rename` -- `D` and `r` on the Teams tab, on the bench's `pp-team` witness (batch
les-equipes-au-poste, ui 0.60.0):
- `D` on `ops`: the agents the dry face lists as the team's alone, one line each, none checked, the command `team delete
  ops --yes` under them; `space` checks the first and the command gains `--agent agents/dba`; the team's name typed and
  `enter` play the command as shown
- `r` on `core-review`: one field, the new name; the command `team rename core-review <new>` follows the typing, `enter`
  plays it as shown
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture

DELETE, DELETE_ONE = "./pp team delete ops --yes", "./pp team delete ops --agent agents/dba --yes"
RENAME = "./pp team rename core-review fresh"


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
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "down,D,space,tab,o,p,s,enter")
    if (shown.returncode == 0 and checked.returncode == 0 and done.returncode == 0 and len(unchecked) == len(agents)
            and T.preview_in(shown, "./pp team delete") == DELETE and T.preview_in(checked, "./pp team delete") == DELETE_ONE
            and house.gestures() == ["team delete ops --json", DELETE_ONE[len("./pp "):]]):
        held("D lists the agents and composes --agent", f"{len(agents)} agents, none checked, {DELETE!r}; space: "
             f"{DELETE_ONE!r}, played once ops is typed")
    else:
        failures.append(f"  ✗ D with its checks           rc={shown.returncode},{checked.returncode},{done.returncode} "
                        f"unchecked={unchecked} {T.preview_in(shown, './pp team delete')!r} "
                        f"{T.preview_in(checked, './pp team delete')!r} {house.gestures()} {shown.stdout[-1500:]!r}")

    # --- r renames the team: the command follows the field, enter plays it ------------------------------------
    shown = house.render("--render", "teams", "--size", "130x40", "--press", "r,f,r,e,s,h")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", "r,f,r,e,s,h,enter")
    if (shown.returncode == 0 and done.returncode == 0 and T.preview_in(shown, "./pp team rename") == RENAME
            and house.gestures() == [RENAME[len("./pp "):]]):
        held("r renames the team", f"{RENAME!r} shown, then played")
    else:
        failures.append(f"  ✗ rename                      rc={shown.returncode},{done.returncode} "
                        f"{T.preview_in(shown, './pp team rename')!r} {house.gestures()} {shown.stdout[-1200:]!r}")
    return 0
