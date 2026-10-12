"""Scenario `ui-real-team-resume` -- a task stopped and taken back from the post on the REAL verbs of `team`
(plan ui, batch le-reel-des-equipes), its wake-ups played by the team witness, never a provider:
- a task posted without a tick, nobody woken on it: `s` stops it -- `stopped` at the journal
- on the Tasks tab shown on `stopped` (`]` twice), `r` takes it back -- `resumed`, by the owner, after the stop -- and the team wakes `lead` on it again
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-resume", {"lead": {"T1": [{"body": {"done": "started"}}]}})
    begun = team.start("go")
    started = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))
    owner = team.state().get("owner")
    team.call("team", "post", R.TEAM, "--message", "second", "--no-tick")

    stopped = team.render("--render", "tasks", "--size", "200x50", "--press", "s,enter")
    stops = team.kinds("stopped", task="T2")
    resumed = team.render("--render", "tasks", "--size", "200x50", "--press",
                          "right_square_bracket,right_square_bracket,r,enter")   # SHOW stopped: T2
    resumes = team.kinds("resumed", task="T2")
    woken = team.settled(lambda events: any(one.get("kind") == "wake-intent" and one.get("task") == "T2"
                                            and one["id"] > (resumes[0]["id"] if resumes else 10 ** 9) for one in events))
    if (begun.returncode == 0 and started and stopped.returncode == 0 and resumed.returncode == 0 and len(stops) == 1
            and len(resumes) == 1 and resumes[0].get("by") == owner and resumes[0]["id"] > stops[0]["id"] and woken):
        held("s stops a task, r takes it back", f"stopped #{stops[0]['id']}, resumed #{resumes[0]['id']} by {owner}, "
             "lead woken on T2 after it")
    else:
        failures.append(f"  ✗ stop and resume             started={started} stops={stops} resumes={resumes} woken={woken} "
                        f"{stopped.stdout[-700:]!r} {resumed.stdout[-700:]!r}")
    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
