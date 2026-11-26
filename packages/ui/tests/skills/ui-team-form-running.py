"""Scenario `ui-team-form-running` -- in season the two forms are read only and the season stops from its form (batch
les-formulaires-jumeaux, team 1.27.0), on the bench's `pp-team` witness: `core-review` in season (`started.state`
`running` in `team declaration --json`), its open tasks T3 and T6, its live recurrence R1:
- `E` in season: a key typed changes nothing -- in the description, in a field of Preset (batch
  les-volets-par-onglet), shown closed --, `enter` plays nothing, the line of state says the form is read only; its
  list of documents is read, and `enter`, `n`, `e`, `d` on it open nothing and play nothing (batch
  la-liste-des-documents)
- `S` in season opens on its Members: its context, which SEASON.md does not write, is empty -- never the form's
  default 90 (todo le-context-en-pourcent)
- `S` in season: `ctrl+s` plays nothing; `X` asks the stop, naming each open task and each recurrence that goes
  silent; the team's name typed plays `team stop core-review` once, then the form of the season stands again, read
  anew off season: its sections, its side pane SEASON.md, never read only (batch la-saison-fermee-garde-le-formulaire)
- a stop refused: the form stands as it was, read only, the refusal on its line of state (todo
  le-refus-dans-le-formulaire)
- off season (`started.state` `stopped`), `E` writes: a description typed, `enter` plays `team declare`
Its sibling, cut by case (rule 10): `ui-team-form-running-panes` (the sections and the side panes in season).
"""
from __future__ import annotations

import re

from tests.harness import support

F = support(__file__, "team_forms")
R = support(__file__, "team_form_running")
T, P = F.T, F.P
STOP = "team stop core-review --no-tick"
REFUSED = "pp-team: lock-held -- teams/core-review: a tick holds the team\n"
TYPED = "c,o,r,e,minus,r,e,v,i,e,w,ctrl+enter"


def constant(name: str) -> str:
    try:
        return P.palette_constant(name)
    except KeyError:
        return f"<no {name}>"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-form-running", R.script())
    said = constant("IN_SEASON")

    # --- E in season: read only ----------------------------------------------------------------------------------
    team = house.render("--render", "teams", *F.SIZE, "--press", f"E,x,{F.team_to('Preset')},x,ctrl+enter,boxes")
    rows = F.fields(team.stdout)
    if (team.returncode == 0 and house.gestures() == [] and said in F.state(team.stdout)
            and P.field_title("daily") in rows and "x" not in P.field_of(rows, "daily")):
        held("E in season is read only", f"a key typed, enter: nothing played; {F.state(team.stdout)!r}")
    else:
        failures.append(f"  ✗ E read only                 {house.gestures()} {F.state(team.stdout)!r} "
                        f"{F.fields(team.stdout)[:12]!r}")

    house.clear_journal()
    listed = house.render("--render", "teams", *F.SIZE, "--press", f"E,{F.team_to('Documents')},enter,n,e,d,boxes")
    boxed = next((one for one in listed.stdout.splitlines() if one.startswith("boxes ")), "")
    if (listed.returncode == 0 and F.role_of(listed.stdout, "git/trunk") == "—" and "form-fields=" in boxed
            and house.gestures() == []):
        held("E in season: the list read, its keys play nothing", f"{F.document_rows(listed.stdout)}")
    else:
        failures.append(f"  ✗ list read only              {house.gestures()} {F.document_rows(listed.stdout)} {boxed} "
                        f"{listed.stdout[-1500:]!r}")

    # --- S in season: the context SEASON.md writes, none: empty, never the default ---------------------------------
    shown = house.render("--render", "teams", *F.SIZE, "--press", "S,boxes")
    context = P.field_of(F.fields(shown.stdout), "context")
    if shown.returncode == 0 and context in ([""], [P.palette_constant("SEASON_CONTEXT_EXAMPLE")]):
        held("S in season shows no context SEASON.md does not write", f"context {context}")
    else:
        failures.append(f"  ✗ context in season           {context} {F.fields(shown.stdout)[:40]!r}")

    # --- S in season: ctrl+s nothing; X names what it stops, the name typed stops the season ------------------------
    house.clear_journal()
    asked = house.render("--render", "teams", *F.SIZE, "--press", "S,ctrl+s,X")
    named = all(re.search(rf"┃\s+{task}\s", asked.stdout) for task in ("T3", "T6", "R1"))   # inside the confirmation
    nothing = house.gestures()
    house.clear_journal()
    stopped = house.render("--render", "teams", *F.SIZE, "--press", f"S,X,{TYPED},boxes")
    after = (F.tabs_row(stopped.stdout), "form-file=" in stopped.stdout, said in F.state(stopped.stdout))
    if (asked.returncode == 0 and stopped.returncode == 0 and nothing == [] and named
            and house.gestures() == [STOP] and after == (F.SEASON_TABS, True, False)):
        held("S in season stops it from its form", f"ctrl+s: nothing; X names T3, T6, R1; typed: {STOP}, then the "
             f"season's form off season: {after[0]}, SEASON.md, not read only")
    else:
        failures.append(f"  ✗ S stops                     {nothing} {named} {house.gestures()} {after} "
                        f"{stopped.stdout[-3000:]!r}")

    # --- a stop refused: the form as it was, the refusal said ----------------------------------------------------
    house.use({**R.script(), "answers": {"stop": {"rc": 2, "err": REFUSED}}})
    house.clear_journal()
    kept = house.render("--render", "teams", *F.SIZE, "--press", f"S,X,{TYPED},boxes")
    after = (F.tabs_row(kept.stdout), said in F.state(kept.stdout), "lock-held" in F.state(kept.stdout).split())
    if kept.returncode == 0 and house.gestures() == [STOP] and after == (F.SEASON_TABS, True, True):
        held("a stop refused keeps the form", f"{STOP} refused: the form read only, its line of state "
             f"{F.state(kept.stdout)[-80:]!r}")
    else:
        failures.append(f"  ✗ stop refused               {house.gestures()} {after} {kept.stdout[-3000:]!r}")

    # --- off season: E writes ---------------------------------------------------------------------------------------
    house.use(T.script())
    house.clear_journal()
    house.render("--render", "teams", *F.SIZE, "--press", "E," + F.typed("ok") + ",ctrl+enter")
    wanted = ['team declare core-review --description ok --json']
    if house.gestures() == wanted:
        held("off season E writes", wanted[0])
    else:
        failures.append(f"  ✗ off season                  {house.gestures()}")
    return 0
