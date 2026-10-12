"""Scenario `ui-real-team-ring` -- a ceremony rung from the post on the REAL verbs of `team` (plan ui, batch
le-reel-des-equipes), its wake-ups played by the team witness, never a provider, the clock frozen before the
daily's hour:
- `g` opens the ceremonies, `g` again on `daily`: the real `team ring` -- the journal says `ceremony-due` under `manual-<id>`, by the
  owner, one task to `lead`
- once `dev` and `rev` answered and `lead` closed it, the Ceremonies table says `2/2` for `daily`
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
SCRIPT = {"lead": {"T1": [{"body": {"done": "started"}}], "T2": [{"body": {"done": "daily held"}}]},
          "dev": [{"body": {"done": "yesterday: tests"}}], "rev": [{"body": {"done": "yesterday: reviews"}}]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-ring", SCRIPT)
    begun = team.start("go")
    started = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))
    owner = team.state().get("owner")

    rung = team.render("--render", "teams", "--size", "200x50", "--press", "g,g")
    due = team.kinds("ceremony-due", ceremony="daily")
    period = str(due[0].get("period")) if due else ""
    task = next((one.get("task") for one in team.kinds("task") if one.get("ceremony") == "daily"), None)
    closed = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == task for one in events)
                          or any(one.get("kind") == "terminal" and one.get("agent") == "lead" and one.get("task") == task
                                 for one in events), timeout=40.0)
    if (begun.returncode == 0 and started and rung.returncode == 0 and len(due) == 1 and period == f"manual-{due[0]['id']}"
            and due[0].get("by") == owner and task and closed):
        held("g rings the ceremony at hand", f"ceremony-due daily {period} by {owner}; task {task} to lead, closed")
    else:
        failures.append(f"  ✗ ring                        rc={begun.returncode},{rung.returncode} started={started} due={due} "
                        f"task={task} closed={closed} {rung.stdout[-1200:]!r} {rung.stderr[-300:]!r}")

    shown = team.render("--render", "teams", "--size", "200x50", "--press", "c")
    row = next((one for one in shown.stdout.split("\n") if " daily " in one and "/" in one), "")
    progress = next((one.get("progress") for one in team.state().get("ceremonies") or [] if one.get("name") == "daily"), None)
    if shown.returncode == 0 and "2/2" in row and progress and all(one.get("terminal") for one in progress) and not team.alive():
        held("the progress of the ring, from the real face", f"{row.strip()[:60]!r}; progress {progress}")
    else:
        failures.append(f"  ✗ progress                    rc={shown.returncode} {row!r} {progress} alive={team.alive()} "
                        f"{shown.stdout[-1500:]!r}")
    return 0
