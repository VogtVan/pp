"""Scenario `ui-real-team-new` -- a team born from a template at the post, on the REAL verbs of `team`, its wake-ups
played by the team witness, never a provider:
- `N` reads the real `team templates --json`: the form opens on its first template, `supervisor-workers`; a name
  typed, `enter` plays `team new nova --template supervisor-workers` -- `teams/nova/TEAM.md` written by team, and
  `team declaration nova --json` says the verdict ok
- `S` on `nova` starts it with the harness of the post, its first task named `Boot` (`--name`): the journal's `task`
  carries the name, the supervisor answers, T1 resolved; the Tasks tab, its `done` waited on the watch, shows
  `Boot` on nova's row under `SHOW resolved`
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
START = "down,S,g,o,shift+tab,B,o,o,t,enter"   # its season: the message, then the first task's name
RESOLVED = "right_square_bracket,right_square_bracket,right_square_bracket"     # SHOW resolved
SCRIPT = {"supervisor": [{"sleep": 2, "body": {"done": "born from a template"}}]}   # it thinks while Tasks subscribes


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-new", SCRIPT)

    # --- N: the real templates, team new played -----------------------------------------------------
    made = team.render("--render", "teams", "--size", "200x50", "--press", "N,n,o,v,a,enter")
    written = (team.ws / "teams" / "nova" / "TEAM.md").is_file()
    declared = team.face("team", "declaration", "nova", "--json")
    if made.returncode == 0 and written and (declared.get("verdict") or {}).get("ok") is True:
        held("N writes a team from a real template", "teams/nova/TEAM.md written by team; declaration verdict ok")
    else:
        failures.append(f"  ✗ team new                    rc={made.returncode} written={written} declared={declared} "
                        f"{made.stdout[-1500:]!r} {made.stderr[-400:]!r}")

    # --- S: the team born started, its first task named, said by its name in Tasks ------------------
    started = team.render("--render", "teams", "--size", "200x50", "--press", f"{START},4,wait:team:done,{RESOLVED}")
    tasks = team.kinds("task", team="nova")
    done = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events),
                        team="nova")
    if started.returncode == 0 and tasks and tasks[0].get("name") == "Boot" and done:
        held("S starts the team born, its first task named", "task T1 name 'Boot' at nova's journal; done T1")
    else:
        failures.append(f"  ✗ start                       rc={started.returncode} tasks={tasks} done={done} "
                        f"{started.stdout[-1500:]!r} {started.stderr[-400:]!r}")
    row = next((one for one in started.stdout.split("\n") if "Boot" in one), "")
    if "nova" in row.split():
        held("Tasks says the task by its name", row.strip()[:80])
    else:
        failures.append(f"  ✗ named in Tasks              {row!r} {started.stdout[-1500:]!r}")
    if not team.settled(lambda events: not team.alive(), timeout=20.0, team="nova"):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
