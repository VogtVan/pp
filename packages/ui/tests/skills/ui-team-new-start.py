"""Scenario `ui-team-new-start` -- the fields of each section of the form of TEAM.md composing their flags, what `enter`
plays and its refusal; the start passed to the form of SEASON.md: on the bench's `pp-team` witness (`_team_new`):
- `N`, the second preset chosen, its members given their paths, a role, a root, a principal, the budget changed,
  `enter`: `team declare x --template teams/lead-reviewers --member lead agents/l --member reviewer agents/r --role
  make lead --root reviewer --principal pm --budget 10 --schedule 30s`; `ctrl+s` before it plays nothing -- the form of a team starts
  nothing: the start is the season's (`ui-team-form-season`)
- a name typed and `all` ticked on a document of the list, the form written plays `team declare ram --template … --document …` -- no flag for
  a field left as it opened -- (taken from `ui-team-new`)
- a refusal of `team declare` goes to the remedy line by its code, the form open again on its values -- its name --
  (taken from `ui-team-new`)
- the first preset the verb says is the one the form opens on -- another face, `teams/lead-reviewers` first: its
  members, and `enter` plays it; `N` again opens on it (taken from `ui-team-new`, where a sort's default stood)
The refusals of a start, `declare --season` then `team start`, are `ui-team-form-season`'s.
"""
from __future__ import annotations

from tests.harness import support

N = support(__file__, "team_new")
F, T, P = N.F, N.T, N.P
REFUSAL = "pp-team: document-unknown -- teams/ram/TEAM.md: documents: `all git/branches` -- no such document.\n"
DOCUMENT = "all git/branches"         # `all` ticked on the first document of the list (batch la-liste-des-documents)
# N, ctrl+s (nothing), then the second preset (Preset), the members' paths (Members), back to Team for a role, then
# the root and a principal (Members), the budget (Limits), enter
PRESSED = N.keys("N,ctrl+s,x", N.TO_PRESET, "space,down,enter", N.F.section(1), "end," + N.typed(" agents/l"),
                 "down,end," + N.typed(" agents/r"), "ctrl+pageup,ctrl+pageup", N.TO_ROLES, N.typed("make lead"),
                 N.TO_MEMBERS, "tab," + N.typed("reviewer"), "tab," + N.typed("pm"), N.F.section(2), N.typed("10"),
                 "ctrl+enter")
FIELDS = (f"team declare x --template {N.LEAD['template']} --member lead agents/l --member reviewer agents/r "
          f"--role make lead --root reviewer --principal pm --budget 10 {N.BORN}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new-start")

    # --- every section's field composes its flag; ctrl+s plays nothing ------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *N.SIZE, "--press", PRESSED)
    if done.returncode == 0 and house.gestures() == [FIELDS]:
        held("a field changed composes its flag, ctrl+s nothing", FIELDS)
    else:
        failures.append(f"  ✗ fields                      {house.gestures()} {done.stdout[-2500:]!r} {done.stderr[-400:]!r}")

    # --- a name and a line of documents, enter: the command played, refused by its code, the form open again -----
    house.use(T.script(answers={"declare": {"rc": 2, "err": REFUSAL}}))
    house.clear_journal()
    refused = house.render("--render", "teams", *N.SIZE, "--press",
                           N.keys(N.NAMED, N.TO_DOCUMENTS, "enter", F.ALL, "ctrl+enter", F.WRITE, "boxes"))
    wanted = N.DECLARED.replace(f" {N.BORN}", f" --document '{DOCUMENT}' {N.BORN}")
    named, remedy = P.field_of(F.fields(refused.stdout), "name"), T.remedy_of(refused)
    if refused.returncode == 0 and house.gestures() == [wanted]:
        held("the form plays its fields changed", f"{wanted!r}; no flag for a field left as it opened")
    else:
        failures.append(f"  ✗ played                      {house.gestures()} {refused.stdout[-1800:]!r}")
    if refused.returncode == 0 and "document-unknown" in remedy.split() and named == ["ram"]:
        held("a refusal of team declare is said, the form open again", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     {remedy!r} {named} {refused.stdout[-1500:]!r}")

    # --- another first preset said by the verb: the form opens on it, enter plays it -----------------------------
    house.use(T.script(templates=[N.LEAD, N.FIRST]))
    house.clear_journal()
    # played, then again: its Preset
    defaulted = house.render("--render", "teams", *N.SIZE, "--press", f"N,x,ctrl+enter,N,{N.TO_PRESET},boxes")
    rows, file = F.fields(defaulted.stdout), F.zone_rows(defaulted.stdout, "form-file")
    wanted = [f"team declare x --template {N.LEAD['template']} {N.BORN}"]
    if (defaulted.returncode == 0 and house.gestures() == wanted
            and (P.field_of(rows, "preset")[:1] or [""])[0].split()[:1] == [N.LEAD["template"]]
            and all(one in file for one in N.LEAD["members"])):
        held("the form opens on the first preset said", f"{N.LEAD['template']}, its members; {wanted[0]}")
    else:
        failures.append(f"  ✗ first preset                {house.gestures()} {rows!r} {file!r}")
    return 0
