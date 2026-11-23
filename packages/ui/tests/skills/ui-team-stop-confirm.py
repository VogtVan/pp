"""Scenario `ui-team-stop-confirm` -- stopping a team is confirmed on what it stops, and the keys of the forms (batch
les-formulaires-jumeaux), on the bench's `pp-team` witness, `core-review` holding two open tasks (T3, T6), a live
recurrence (R1) and a stopped one (R2):
- `X` on the Teams tab: its overlay names each open task of `team status --json` -- its id, its name, who holds it --
  and each recurrence that goes silent -- its id, its name --, never a recurrence stopped already; `escape` plays
  nothing; `core-review` typed and `enter` play `team stop core-review` once
- the season read only (`s`): `X` opens the same confirmation over it; `escape` plays nothing; confirmed, the stop
  plays once and the form of the season stands, off season: its sections, never read only (batch
  la-saison-fermee-garde-le-formulaire)
- `E` opens the form of the team chosen, TEAM.md in its side pane, `S` the form of its season, SEASON.md; the footer of the Teams tab
  offers `N`, `E` and `S`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of the footer and of an overlay
F = support(__file__, "team_forms")    # the readers of a form: its sections, its line of state

SIZE = ("--size", "130x40")
STOP_ALL = "team stop core-review --no-tick"
TYPED = "c,o,r,e,minus,r,e,v,i,e,w,ctrl+enter"
STATE = T.RECURRING


def _said(rows: list[str]) -> tuple[list[str], list[str]]:
    """-> what the rows miss of the face: each open task -- id, name or text, every holder -- and each recurrence that
    goes silent -- id, name or text -- not on one row; each recurrence stopped or paused named on a row."""
    missing, extra = [], []
    for task in [one for one in STATE["tasks"] if one["state"] == "open"]:
        words = [task["id"], task.get("name") or task.get("text") or "", *(task.get("holders") or [])]
        if not any(row.split()[:1] == [task["id"]] and all(word in row for word in words) for row in rows):
            missing.append(task["id"])
    for one in STATE["recurrences"]:
        named = any(row.split()[:1] == [one["id"]] for row in rows)
        if one.get("stopped") is None and one.get("paused") is None:
            if not any(row.split()[:1] == [one["id"]] and (one.get("name") or one["text"]) in row for row in rows):
                missing.append(one["id"])
        elif named:
            extra.append(one["id"])
    return missing, extra


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-stop-confirm", T.script(states={"core-review": [STATE], "ops": [T.OPS]}))

    # --- X: the overlay names what it stops; escape nothing, the name typed the stop ---------------------------
    shown = house.render("--render", "teams", *SIZE, "--press", "X,escape,X")
    rows = [one for one in P.overlay_rows(shown.stdout) if one]
    missing, extra = _said(rows)
    after_escape = house.gestures()
    house.clear_journal()
    stopped = house.render("--render", "teams", *SIZE, "--press", f"X,{TYPED}")
    if shown.returncode == 0 and not missing and not extra and rows:
        held("X names what it stops", "T3 and T6 with their names and holders, R1; R2 stopped left out")
    else:
        failures.append(f"  ✗ X names                     rc={shown.returncode} missing {missing} extra {extra} {rows!r}")
    if stopped.returncode == 0 and after_escape == [] and house.gestures() == [STOP_ALL]:
        held("X confirmed plays the stop, escape nothing", f"escape: nothing; core-review typed: {STOP_ALL}")
    else:
        failures.append(f"  ✗ X plays                     {after_escape} {house.gestures()} {stopped.stdout[-900:]!r}")

    # --- s, then X: the same confirmation over the season read only --------------------------------------------
    house.clear_journal()
    season = house.render("--render", "teams", *SIZE, "--press", "s,X")
    lines = [one.strip(" ┃│") for one in season.stdout.splitlines()]
    found = [row[row.index(task):] for row in lines for task in ("T3", "T6", "R1") if task in row.split()[:3]]
    missing, extra = _said([one.strip(" ┃│") for one in found])
    house.render("--render", "teams", *SIZE, "--press", "s,X,escape")
    escaped = house.gestures()
    house.clear_journal()
    closed = house.render("--render", "teams", *SIZE, "--press", f"s,X,{TYPED},boxes")
    after = (F.tabs_row(closed.stdout), P.palette_constant("IN_SEASON") in F.state(closed.stdout))
    if (season.returncode == 0 and closed.returncode == 0 and not missing and not extra and escaped == []
            and house.gestures() == [STOP_ALL] and after == (F.SEASON_TABS, False)):
        held("s, then X: the confirmation over the season", f"T3, T6, R1 named; escape: nothing; core-review "
             f"typed: {STOP_ALL}, then the season's form off season: {after[0]}")
    else:
        failures.append(f"  ✗ s then X                    rc={season.returncode} missing {missing} extra {extra} "
                        f"{escaped} {house.gestures()} {after} {closed.stdout[-900:]!r}")

    # --- E and S: the team's section, the season's; the footer ------------------------------------------------
    team = house.render("--render", "teams", *SIZE, "--press", "E")
    start = house.render("--render", "teams", *SIZE, "--press", "S")
    panes = lambda text: {name for name in ("TEAM.md", "SEASON.md") if f"─ {name} ─" in text}
    footer = house.render("--render", "teams", *SIZE).stdout
    keys = {key: P.entry_of(footer, key) for key in ("N", "E", "S")}
    if (team.returncode == 0 and start.returncode == 0 and panes(team.stdout) == {"TEAM.md"}
            and panes(start.stdout) == {"SEASON.md"} and all(keys.values())):
        held("E opens the form of TEAM.md, S the form of SEASON.md", " · ".join(keys.values()))
    else:
        failures.append(f"  ✗ E and S                     {panes(team.stdout)} {panes(start.stdout)} {keys} "
                        f"{team.stdout[-900:]!r}")
    return 0

