"""Scenario `ui-real-team-pilot` -- the owner answers a member's question from the post, on the REAL verbs of
`team` (plan ui, batch le-reel-des-equipes), its wake-ups played by the team witness, never a provider:
- `dev` asks the owner a question (`ui-real-team-ask` shows it open in the thread)
- `m`, its overlay -- the question chosen in `reply to`, a text: the real `team post --reply` -- the journal's `post` is a `reply`
  citing the question, the question leaves `waiting`, and the team goes on to `done`
(stopping and taking back a task is `ui-real-team-resume`'s)
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
REPLY = "m,o,k,shift+tab,space,down,enter,tab,enter"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team, ask, owner, begun = R.asking(bench, "ui-real-team-pilot")

    # --- m: the reply, the team to its end ----------------------------------------------------------
    done = team.render("--render", "tasks", "--size", "200x50", "--press", REPLY, "--wait", "team:done:40")
    replies = team.kinds("post", verb="reply")
    finished = team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))
    waiting = (team.state().get("waiting") or {}).get("questions")
    if (begun and done.returncode == 0 and len(replies) == 1 and replies[0].get("reply") == ask.get("id") and replies[0].get("from") == owner
            and replies[0].get("text") == "ok" and finished and waiting == []):
        held("m replies to the question", f"post #{replies[0].get('id')} reply to #{ask.get('id')} from {owner}; done T1; "
             "waiting.questions []")
    else:
        failures.append(f"  ✗ reply                       rc={done.returncode} replies={replies} finished={finished} "
                        f"waiting={waiting} {done.stdout[-1500:]!r} {done.stderr[-300:]!r}")

    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
