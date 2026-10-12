"""Scenario `ui-real-team-tasks` -- what a team does, followed in the Tasks tab on the REAL verbs of `team` (plan ui,
batch le-reel-du-centre), its wake-ups played by the team witness, never a provider:
- `n` on the Tasks tab posts a NAMED task on `essai` -- the real `post --name 'Revue PR'`, its `task` event named
- while `lead` plays its wake-up on it, the band of the task says its last action from a real step tied to it
  by its `task` (`live: lead · run …`)
- once it is done, `enter` on it under `SHOW resolved` opens its thread on the real `team log --task`, to `done`
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
SCRIPT = {"lead": {"T1": [{"body": {"done": "started"}}], "T2": [{"sleep": 2.5, "body": {"done": "reviewed"}}]}}
POST = "n,h,i,shift+tab,shift+tab,shift+tab,R,e,v,u,e,space,P,R,enter,wait:team:block"
RESOLVED = "right_square_bracket,right_square_bracket,right_square_bracket"


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-tasks", SCRIPT)
    begun = team.start("go")
    started = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))

    # --- n: a named task, its last action live --------------------------------------------------------
    posted = team.render("--render", "tasks", "--size", "200x50", "--press", POST)
    named = team.kinds("task", task="T2")
    flat = _flat(posted.stdout)
    if (begun.returncode == 0 and started and posted.returncode == 0 and named and named[0].get("name") == "Revue PR"
            and "live: lead" in flat):
        held("n names a real task, its last action live", "task T2 name 'Revue PR'; the band says live: lead · run …")
    else:
        failures.append(f"  ✗ named and live              started={started} named={named} {posted.stdout[-1500:]!r} "
                        f"{posted.stderr[-400:]!r}")

    # --- its thread, to done ------------------------------------------------------------------------
    done = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T2" for one in events),
                        timeout=40.0)
    thread = team.render("--render", "tasks", "--size", "200x50", "--press", RESOLVED + ",down,enter")
    flat = _flat(thread.stdout)
    if done and thread.returncode == 0 and "thread" in flat and "Revue PR" in flat and " done" in flat and not team.alive():
        held("the thread of the named task, to its end", "enter under SHOW resolved: the thread of T2 'Revue PR', its done")
    else:
        failures.append(f"  ✗ thread                      done={done} alive={team.alive()} {thread.stdout[-1500:]!r}")
    return 0
