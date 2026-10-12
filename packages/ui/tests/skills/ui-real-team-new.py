"""Scenario `ui-real-team-new` -- a team born from a template at the post, on the REAL verbs of `team` (plan ui,
batch le-reel-du-centre), its wake-ups played by the team witness, never a provider:
- `N` reads the real `team templates --json`: the form opens on its first template, `supervisor-workers`; a name
  typed, `enter` plays `team new nova --template supervisor-workers` as shown -- `teams/nova/TEAM.md` written by
  team, and `team declaration nova --json` says `verdict ok`
- `S` on `nova` starts it with the harness of the post, its first task named `Boot` (`--name`): the journal's `task`
  carries the name, the supervisor answers, T1 resolved
- the Tasks tab says the task by its name
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
NEW = "./pp team new nova --template supervisor-workers"
START = "down,S,g,o,shift+tab,B,o,o,t,enter"   # its season: the message, then the first task's name


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-new", {"supervisor": [{"body": {"done": "born from a template"}}]})

    # --- N: the real templates, team new as shown ---------------------------------------------------
    shown = team.render("--render", "teams", "--size", "200x90", "--press", "N,n,o,v,a")   # the form whole
    made = team.render("--render", "teams", "--size", "200x50", "--press", "N,n,o,v,a,enter")
    written = (team.ws / "teams" / "nova" / "TEAM.md").is_file()
    declared = team.face("team", "declaration", "nova", "--json")
    if (shown.returncode == 0 and made.returncode == 0 and NEW in _flat(shown.stdout) and written
            and (declared.get("verdict") or {}).get("ok") is True):
        held("N writes a team from a real template", f"{NEW!r} shown, then played; teams/nova/TEAM.md written by team; "
             "declaration verdict ok")
    else:
        failures.append(f"  ✗ team new                    rc={shown.returncode},{made.returncode} written={written} "
                        f"declared={declared} {shown.stdout[-1500:]!r} {made.stderr[-400:]!r}")

    # --- S: the team born started, its first task named ---------------------------------------------
    started = team.render("--render", "teams", "--size", "200x50", "--press", START)
    tasks = team.kinds("task", team="nova")
    done = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events),
                        team="nova")
    if started.returncode == 0 and tasks and tasks[0].get("name") == "Boot" and done:
        held("S starts the team born, its first task named", "task T1 name 'Boot' at nova's journal; done T1")
    else:
        failures.append(f"  ✗ start                       rc={started.returncode} tasks={tasks} done={done} "
                        f"{started.stdout[-1500:]!r} {started.stderr[-400:]!r}")

    # --- the Tasks tab says it by its name ----------------------------------------------------------
    listed = team.render("--render", "tasks", "--size", "200x50", "--press",
                         "right_square_bracket,right_square_bracket,right_square_bracket")   # SHOW resolved
    row = next((one for one in listed.stdout.split("\n") if "Boot" in one), "")
    if listed.returncode == 0 and "nova" in row and not team.alive():
        held("Tasks says the task by its name", row.strip()[:80])
    else:
        failures.append(f"  ✗ named in Tasks              rc={listed.returncode} {row!r} alive={team.alive()} "
                        f"{listed.stdout[-1500:]!r}")
    return 0
