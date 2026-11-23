"""Scenario `ui-real-team-new` -- a team born from a template at the post, on the REAL verbs of `team`:
- `N` reads the real `team templates --json`: the list of `teams` opens on its first; a name typed, and on Preset
  (batch les-volets-par-onglet) `supervisor-workers` chosen and the value `daily` it declares typed, `enter` plays
  `team declare nova --template teams/supervisor-workers --value daily=…` -- `teams/nova/TEAM.md` written by team,
  the value under `values:`, and `team declaration nova --json` says the verdict ok; `E`, then `n` in its list of
  documents and a name typed: the real `team document notes/boot --new` writes `.pp/teams/templates/notes/boot.md`
  (batch la-liste-des-documents)
Its sibling, cut by case (rule 10): `ui-real-team-new-start` (the declaration read, the season started, a first
task).
"""
from __future__ import annotations

from pathlib import Path

from tests.harness import support

R = support(__file__, "real_team")
F = support(__file__, "team_forms")    # the keys that type, the sections of the form
DAILY = "every day 08:00"
PRESETS = sorted(one.stem for one in (Path(__file__).resolve().parents[3] / "team" / "templates" / "teams").glob("*.md"))
CHOSEN = ",".join(["space"] + ["down"] * PRESETS.index("supervisor-workers") + ["enter"])     # from the first preset
BORN = f"N,n,o,v,a,{F.team_to('Preset')},{CHOSEN},tab,{F.typed(DAILY)},ctrl+enter"    # nova, its preset's `daily` typed
SCRIPT = {"supervisor": [{"sleep": 2, "body": {"done": "born from a template"}}]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-new", SCRIPT)

    # --- N: the real templates, team declare played--------------------------------------------------
    made = team.render("--render", "teams", "--size", "200x50", "--press",
                       f"{BORN},E,{F.team_to('Documents')},n,n,o,t,e,s,slash,b,o,o,t,ctrl+enter")
    path = team.ws / "teams" / "nova" / "TEAM.md"
    written = path.is_file() and f"daily = {DAILY}" in path.read_text(encoding="utf-8")
    declared = team.face("team", "declaration", "nova", "--json")
    created = (team.ws / ".pp" / "teams" / "templates" / "notes" / "boot.md").is_file()
    if made.returncode == 0 and written and (declared.get("verdict") or {}).get("ok") is True and created:
        held("N writes a team from a real template, n a house's document", f"teams/nova/TEAM.md written by team, "
             f"daily = {DAILY}; "
             "declaration verdict ok; .pp/teams/templates/notes/boot.md written by team document")
    else:
        failures.append(f"  ✗ team declare                rc={made.returncode} written={written} created={created} "
                        f"declared={declared} {path.read_text(encoding='utf-8') if path.is_file() else None!r} "
                        f"{made.stdout[-1500:]!r} {made.stderr[-400:]!r}")

    return 0
