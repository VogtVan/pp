"""Scenario `ui-real-team-pause` -- a team paused and resumed from the post, on the REAL verbs of `team` (plan ui, batch
le-reel-de-la-saison), its wake-ups played by the team witness, never a provider:
- the team started and its first task done; `P`, `enter` plays the real `team pause essai`: the journal says `paused`,
  the face `state: paused`, the menu `⏸ essai` and the head `paused since … by <the owner>`
- a task posted while it is paused wakes nobody; `P`, `enter` plays `team resume essai`: `unpaused`, the member woken,
  the task done; no process of the witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
SIZE = ("--size", "160x40")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-pause", {"lead": [{"body": {"done": "first"}}, {"body": {"done": "after the pause"}}]})
    team.start("first")
    team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))
    owner = team.state().get("owner")

    # --- P: the real pause, seen at the post -------------------------------------------------------------
    paused = team.render("--render", "teams", *SIZE, "--press", "P,enter")
    seen = team.render("--render", "teams", *SIZE)
    state = team.state()
    menu = next((one for one in seen.stdout.split("\n") if "⏸ essai" in one), "")
    if (paused.returncode == 0 and team.kinds("paused") and state.get("state") == "paused" and menu
            and f"by {owner}" in seen.stdout and "paused since" in seen.stdout):
        held("P pauses the team, the post says it", f"paused by {owner} at the journal; state paused; {menu.strip()[:40]!r}")
    else:
        failures.append(f"  ✗ pause                       rc={paused.returncode} paused={team.kinds('paused')} "
                        f"state={state.get('state')} {seen.stdout[-1500:]!r} {paused.stderr[-300:]!r}")

    # --- a task posted while paused, then the resume -----------------------------------------------------
    team.call("team", "post", R.TEAM, "--message", "while paused")
    intents = len(team.kinds("wake-intent"))
    resumed = team.render("--render", "teams", *SIZE, "--press", "P,enter")
    done = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T2" for one in events))
    if (intents == 1 and resumed.returncode == 0 and team.kinds("unpaused") and done
            and team.state().get("state") in ("idle", "working", "waiting") and not team.alive()):
        held("nobody woken while paused, P resumes it", f"1 wake-intent before the resume (T1's); unpaused; T2 done; "
             "no witness left")
    else:
        failures.append(f"  ✗ resume                      intents={intents} rc={resumed.returncode} "
                        f"unpaused={team.kinds('unpaused')} done={done} alive={team.alive()} "
                        f"{resumed.stdout[-1500:]!r} {resumed.stderr[-300:]!r}")
    return 0
