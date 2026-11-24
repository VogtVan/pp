"""Scenario `ui-team-form-team` -- the form of a team writes TEAM.md by `team declare`, its changed keys alone (batch
les-formulaires-jumeaux), on the bench's `pp-team` witness replaying the faces of team 1.26.0:
- `E` on `core-review`, `readers` ticked on a document of its list of Documents (batch la-liste-des-documents), the
  hole `folder` of another typed, and a role typed back on Team (batch les-volets-par-onglet): the side pane of Team
  shows the file with the three lines in their blocks; `ctrl+enter` plays `team declare core-review --value …
  --document … --role … --json`, nothing else -- the view by member is `ui-team-form-view`'s
- the line of keys offers `palette.SEND_KEY` and its verb in a text field (the roles), whose `enter` goes to the line
  and says so (batch les-touches-du-poste); `enter` on a line (the description `E` focuses) writes nothing and goes to
  the next field, the roles, whose keys follow; `shift+tab` back to the description, `ctrl+enter` writes
Its sibling, cut by case (rule 10): `ui-team-form-team-born` (no `ctrl+s` on a team's form, `N` writes a team born).
"""
from __future__ import annotations

from tests.harness import support

F = support(__file__, "team_forms")
T, P = F.T, F.P

DOCUMENT, VALUE, ROLE = "readers review/read-commits", "folder = x", "watch lead"
EMPTIED = ",".join(["backspace"] * len("notes"))     # the hole `folder`, opened on TEAM.md's `notes`
# the list: the package's separator, then review/read-commits under the cursor, `readers` ticked on it; review/read-files
# under it, its hole typed; back to Team, a role typed under the one TEAM.md writes
TYPED = (f"E,{F.team_to('Documents')},enter,{F.FIRST_ROLE},ctrl+enter,down,tab,end,{EMPTIED},x,"
         f"ctrl+pageup,ctrl+pageup,ctrl+pageup,tab,end,enter,{F.typed(ROLE)}")
DECLARED = "team declare core-review --value folder=x --document 'readers review/read-commits' --role watch lead --json"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-team", F.script())

    # --- the side pane: the file as it will be written, the view by member -----------------------------------------
    shown = house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},boxes")
    file_rows = F.pane_rows(shown.stdout, "form-file")
    if (shown.returncode == 0 and all(one in file_rows for one in (DOCUMENT, VALUE, ROLE, "all review/read-files"))):
        held("the side pane follows the fields", f"{DOCUMENT!r}, {VALUE!r} and {ROLE!r} in the file")
    else:
        failures.append(f"  ✗ side pane                   rc={shown.returncode} {file_rows} "
                        f"{shown.stdout[-1500:]!r} {shown.stderr[-300:]!r}")

    # --- the line of keys: the key that sends, enter's new line in a text; enter on a line: the next field -----------
    house.clear_journal()
    opened = house.render("--render", "teams", *F.SIZE, "--press", "E,enter,boxes")
    typing, stepped = F.keys_row(shown.stdout), F.keys_row(opened.stdout)
    key, verb = P.send_key()
    if (key and f"[{key}] {verb}" in typing and F.NEW_LINE in typing and F.NEW_LINE in stepped
            and house.gestures() == []):
        held("ctrl+enter offered, enter on a line steps", f"the roles: {typing!r}; enter on the description, nothing "
             f"written, the roles focused: {stepped!r}")
    else:
        failures.append(f"  ✗ keys                        {typing!r} {stepped!r} {house.gestures()} {opened.stdout[-1200:]!r}")

    # --- ctrl+enter: the changed keys alone ---------------------------------------------------------------------------
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", f"{TYPED},shift+tab,ctrl+enter")
    written = house.gestures()
    if written == [DECLARED]:
        held("ctrl+enter writes the keys changed alone", DECLARED)
    else:
        failures.append(f"  ✗ ctrl+enter                  {written}")

    return 0
