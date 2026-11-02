"""Scenario `ui-real-team-tasks` -- what a team does, followed and steered from the post on the REAL verbs of `team`,
its wake-ups played by the team witness, never a provider; `essai` started once, T1 done --
- `n` on the Tasks tab posts a NAMED task, the real `post --name 'Revue PR'`: its `task` event named; while `lead`
  plays its wake-up on it, the band says `lead` live on it, from a real step tied to it by its `task`
- once it is done, `enter` on it under `SHOW resolved` -- the newest first -- opens its thread on the real `team log --task`, to its `done`
- a task posted without a tick, nobody woken on it: `s` stops it -- `stopped` at the journal; under `SHOW stopped`
  `r` takes it back -- `resumed`, by the owner, after the stop -- and the team wakes `lead` on it again; no process
  of the witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
P = support(__file__, "dialogue")      # the readers of an overlay and of the palette's source
SIZE = ("--size", "200x50")
SCRIPT = {"lead": {"T1": [{"body": {"done": "started"}}], "T2": [{"sleep": 4.0, "body": {"done": "reviewed"}}],
                   "T3": [{"body": {"done": "taken back"}}]}}
POST = "n,h,i,shift+tab,shift+tab,shift+tab,R,e,v,u,e,space,P,R,enter,wait:team:wake-launched,rest:1"
NAME = "Revue PR"
RESOLVED = "right_square_bracket,right_square_bracket,right_square_bracket,right_square_bracket"
STOPPED = "right_square_bracket,right_square_bracket,right_square_bracket"
WAKE = P.palette_constant("WAKE")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _done(task):
    return lambda events: any(one.get("kind") == "done" and one.get("task") == task for one in events)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-tasks", SCRIPT)
    begun = team.start("go")
    started = team.settled(_done("T1"))
    owner = team.state().get("owner")

    # --- n: a named task, its last action live -------------------------------------------------------
    posted = team.render("--render", "tasks", *SIZE, "--press", POST)
    named = team.kinds("task", task="T2")
    if (begun.returncode == 0 and started and posted.returncode == 0 and named and named[0].get("name") == NAME
            and f"{WAKE} lead" in _flat(posted.stdout)):
        held("n names a real task, its last action live", f"task T2 name {NAME!r}; its sequence: {WAKE} lead")
    else:
        failures.append(f"  ✗ named and live              started={started} named={named} {posted.stdout[-1500:]!r} "
                        f"{posted.stderr[-400:]!r}")

    # --- its thread, to done -------------------------------------------------------------------------
    done = team.settled(_done("T2"), timeout=40.0)
    thread = team.render("--render", "tasks", *SIZE, "--press", RESOLVED + ",enter")   # T2, the newest, first
    title, rows = " ".join(P.title_of(thread.stdout)), P.overlay_rows(thread.stdout)
    if done and thread.returncode == 0 and R.TEAM in title and NAME in title and any("done" in row.split() for row in rows):
        held("the thread of the named task, to its end", f"under SHOW resolved: {title!r}, its done")
    else:
        failures.append(f"  ✗ thread                      done={done} {title!r} {thread.stdout[-1500:]!r}")

    # --- s stops a task, r takes it back -------------------------------------------------------------
    team.call("team", "post", R.TEAM, "--message", "second", "--no-tick")
    steered = team.render("--render", "tasks", *SIZE, "--press", f"s,enter,wait:team:stopped,{STOPPED},r,enter")
    stops, resumes = team.kinds("stopped", task="T3"), team.kinds("resumed", task="T3")
    woken = team.settled(lambda events: any(one.get("kind") == "wake-intent" and one.get("task") == "T3"
                                            and one["id"] > (resumes[0]["id"] if resumes else 10 ** 9) for one in events))
    if (steered.returncode == 0 and len(stops) == 1 and len(resumes) == 1
            and resumes[0].get("by") == owner and resumes[0]["id"] > stops[0]["id"] and woken):
        held("s stops a task, r takes it back", f"stopped #{stops[0]['id']}, resumed #{resumes[0]['id']} by {owner}, "
             "lead woken on T3 after it")
    else:
        failures.append(f"  ✗ stop and resume             stops={stops} resumes={resumes} woken={woken} "
                        f"{steered.stdout[-1200:]!r} {steered.stderr[-300:]!r}")
    team.settled(_done("T3"))
    if not team.settled(lambda events: not team.alive(), timeout=20.0):
        failures.append(f"  ✗ witness left                {team.alive()}")
    return 0
