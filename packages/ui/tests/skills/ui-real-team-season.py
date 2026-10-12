"""Scenario `ui-real-team-season` -- a new season of a team from the post, on the REAL verbs of `team` (plan ui, batch
le-reel-de-la-saison), its wake-ups played by the team witness, never a provider:
- the team's first season started by the console and done; `S` on `essai` opens its new season: `dev`'s line edited in
  its profile, the package `ui` switched off there -- the command shown composes `--member dev --package ui=off` and
  nothing else of a member; `ctrl+s` plays the real `team start`
- the journal's second `team-started` keeps `dev`'s switch under `profiles`, the face says the season `2` and `dev`'s
  launch with `ui=off`, the new task done; no process of the witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
SIZE = ("--size", "160x60")
DEV_UI_OFF = "S,n,e,x,t,shift+tab,shift+tab,down,down,enter,tab,tab,tab,enter,down,down,space,enter,enter"


def _flat(text: str) -> str:
    return " ".join(text.replace("┃", " ").replace("│", " ").split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-season", {"lead": [{"body": {"done": "first"}}, {"body": {"done": "second"}}]})
    first = team.start("first")
    team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T1" for one in events))

    # --- S: the new season, dev's ui switched off -------------------------------------------------------
    shown = team.render("--render", "teams", *SIZE, "--press", DEV_UI_OFF)
    flat = _flat(shown.stdout)
    composed = "--member dev --package ui=off" in flat and flat.count("--member") == 1
    if first.returncode == 0 and shown.returncode == 0 and "new season of essai" in flat and composed:
        held("S composes dev's switch alone", "new season of essai; --member dev --package ui=off, no other --member")
    else:
        failures.append(f"  ✗ season shown                rc={first.returncode},{shown.returncode} composed={composed} "
                        f"{shown.stdout[-2500:]!r} {shown.stderr[-300:]!r}")

    # --- ctrl+s: the real start of the season ---------------------------------------------------------
    played = team.render("--render", "teams", *SIZE, "--press", DEV_UI_OFF + ",ctrl+s")
    team.settled(lambda events: any(one.get("kind") == "done" and one.get("task") == "T2" for one in events))
    started = team.kinds("team-started")
    profile = ((started[-1].get("profiles") or {}).get("dev") or {}) if len(started) == 2 else {}
    state = team.state()
    dev = next((one for one in state.get("members") or [] if one.get("member") == "dev"), {})
    launch = (dev.get("launch") or {}).get("packages") or []
    if (played.returncode == 0 and len(started) == 2 and "ui=off" in str(profile.get("packages"))
            and (state.get("season") or {}).get("n") == 2 and "ui=off" in str(launch)
            and team.kinds("done", task="T2") and not team.alive()):
        held("the real season keeps dev's switch", f"team-started #2 profiles.dev {profile}; the face's season 2, dev's "
             f"launch packages {launch}; done T2; no witness left")
    else:
        failures.append(f"  ✗ real season                 rc={played.returncode} started={len(started)} profile={profile} "
                        f"season={state.get('season')} launch={launch} done={team.kinds('done', task='T2')} "
                        f"alive={team.alive()} {played.stdout[-2000:]!r} {played.stderr[-400:]!r}")
    return 0
