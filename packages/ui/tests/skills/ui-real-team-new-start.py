"""Scenario `ui-real-team-new-start` -- a team born from a template at the post, then read and started, on the REAL
verbs of `team`, its wake-ups played by the team witness, never a provider (cut from `ui-real-team-new`, rule 10):
- `nova` declared from the real `supervisor-workers` by the console (`team declare`); its birth at the post is
  `ui-real-team-new`'s
- `e` on `nova` shows its real declaration rendered as markdown: a title, the table of its verdict, TEAM.md's keys
  in a block of code (`blocks`)
- `S` on `nova` opens the form of its season, `ctrl+s` starts it with the harness of the post and no task; `n` posts
  its first task, named `Boot` (`--name`): the journal's `task` carries the name, the supervisor answers, T1 resolved;
  the Tasks tab, its `done` waited on the watch, shows `Boot` on nova's row under `SHOW resolved`
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
TO_NAME = "shift+tab,shift+tab,shift+tab"   # in the overlay of a new task, from its message up to its name
DECLARED = "down,e,blocks,escape"     # nova chosen, its declaration read, then closed
START = f"S,ctrl+s,n,g,o,{TO_NAME},B,o,o,t,ctrl+enter"    # the season of nova started, then its first task, named
RESOLVED = R.shown("resolved")
SCRIPT = {"supervisor": [{"sleep": 2, "body": {"done": "born from a template"}}]}   # it thinks while Tasks subscribes


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-new-start", SCRIPT)

    born = team.call("team", "declare", "nova", "--template", "teams/supervisor-workers")
    declared = team.ws / "teams" / "nova" / "TEAM.md"
    text = declared.read_text(encoding="utf-8") if declared.is_file() else ""
    if born.returncode != 0 or "teams/supervisor-workers" not in text:
        failures.append(f"  ✗ nova born                   rc={born.returncode} {text[:300]!r} {born.stderr[-400:]!r}")

    # --- S: the team born started, its first task named, said by its name in Tasks ------------------
    started = team.render("--render", "teams", "--size", "200x50", "--press",
                          f"{DECLARED},{START},4,wait:team:done,{RESOLVED}")
    blocks = next((one[len("blocks "):].split(",") for one in started.stdout.splitlines()
                   if one.startswith("blocks ")), [])
    if {"MarkdownH1", "MarkdownTable", "MarkdownFence"} <= set(blocks):
        held("e renders the real declaration of nova", f"blocks {sorted(set(blocks))}")
    else:
        failures.append(f"  ✗ declaration rendered        {blocks} {started.stdout[-1500:]!r}")
    tasks = team.kinds("task", team="nova")
    done = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events),
                        team="nova")
    if started.returncode == 0 and tasks and tasks[0].get("name") == "Boot" and done:
        held("S starts the team born, n its first task named", "task T1 name 'Boot' at nova's journal; done T1")
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
