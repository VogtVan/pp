"""Scenario `ui-real-team-season` -- the seasons of a team started from the post on the REAL verbs of `team`, its
wake-ups played by the team witness, never a provider; `essai`, never started:
- `S` with a message: the first season's command carries the `--harness` given after `--` to `./pp ui`; nothing is
  written before it plays
- `S`, `ctrl+s` with no message: the real `team start` writes `team-started` alone, the face says `idle`
- `S` again opens the next season, the title naming the team, its season and the next: a message typed, `dev`'s line
  edited in its profile, the package `ui` switched off there -- the command composes `--member dev --package ui=off`
  and nothing else of a member
- `ctrl+s` plays it, the post following the team to its end: the journal's second `team-started` carries the witness
  as `launch.harness` with its grammar, `dev`'s switch under `profiles`; the face says season 2, `dev`'s launch with
  `ui=off`, T1 done, `lead` ended with its run shown on the tab; `responses.jsonl` one line; no witness left
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
P = support(__file__, "dialogue")      # the readers of a capture
T = support(__file__, "teams")
SIZE = ("--size", "200x60")
FIRST = "S,g,o"
DEV_UI_OFF = "S,n,e,x,t,shift+tab,shift+tab,down,down,enter,tab,tab,tab,enter,down,down,space,enter,enter"


def _flat(text: str) -> str:
    return " ".join(text.replace("┃", " ").replace("│", " ").split())


def _member(state: dict, name: str) -> dict:
    return next((one for one in state.get("members") or [] if one.get("member") == name), {})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-season", {"lead": [{"body": {"done": "next"}}]})

    # --- S: the first season's command, the harness of the post ---------------------------------------------------
    shown = team.render("--render", "teams", *SIZE, "--press", FIRST)
    flat = _flat(shown.stdout)
    if shown.returncode == 0 and "./pp team start essai --message go" in flat and "--harness" in flat and team.events() == []:
        held("S shows the first season with the harness of the post", "./pp team start essai --message go … --harness "
             "<the witness>; nothing written before it plays")
    else:
        failures.append(f"  ✗ first season shown          rc={shown.returncode} {shown.stdout[-1500:]!r} {shown.stderr[-300:]!r}")

    # --- ctrl+s, no message: the real start without a task -------------------------------------------------------
    bare = team.render("--render", "teams", *SIZE, "--press", "S,ctrl+s")
    team.settled(lambda events: any(one.get("kind") == "team-started" for one in events))
    kinds = [one.get("kind") for one in team.events()]
    first = team.state()
    if bare.returncode == 0 and kinds == ["team-started"] and first.get("state") == "idle":
        held("the real start without a task", "team-started alone, the face idle")
    else:
        failures.append(f"  ✗ start without a task        rc={bare.returncode} {kinds} {first.get('state')!r} "
                        f"{bare.stdout[-900:]!r} {bare.stderr[-300:]!r}")

    # --- S: the next season, dev's ui switched off ----------------------------------------------------------------
    shown = team.render("--render", "teams", *SIZE, "--press", DEV_UI_OFF)
    flat = _flat(shown.stdout)
    title = P.title_of(shown.stdout) or [""]
    n = int((first.get("season") or {}).get("n") or 0)
    composed = "--member dev --package ui=off" in flat and flat.count("--member") == 1
    if shown.returncode == 0 and n == 1 and T.in_order(title[0], R.TEAM, str(n), str(n + 1)) and composed:
        held("S composes dev's switch alone", f"{title[0]!r}; --member dev --package ui=off, no other --member")
    else:
        failures.append(f"  ✗ next season shown           rc={shown.returncode} n={n} {title} composed={composed} "
                        f"{shown.stdout[-2500:]!r} {shown.stderr[-300:]!r}")

    # --- ctrl+s: the real start of the next season, followed to its end -------------------------------------------
    played = team.render("--render", "teams", *SIZE, "--press", DEV_UI_OFF + ",ctrl+s", "--wait", "team:done:40")
    flat = _flat(played.stdout)
    started = team.kinds("team-started")
    launch = (started[-1].get("launch") or {}) if len(started) == 2 else {}
    profile = ((started[-1].get("profiles") or {}).get("dev") or {}) if len(started) == 2 else {}
    finished = team.kinds("done", task="T1")
    state = team.state()
    packages = (_member(state, "dev").get("launch") or {}).get("packages") or []
    lead = _member(state, "lead")
    gone = team.settled(lambda events: not team.alive(), timeout=20.0)
    if (played.returncode == 0 and launch.get("harness") == team.harness and launch.get("provider") == R.WITNESS_GRAMMAR
            and "ui=off" in str(profile.get("packages")) and (state.get("season") or {}).get("n") == 2
            and "ui=off" in str(packages) and finished and lead.get("how") == "ended" and lead.get("run")
            and lead["run"] in flat and len(team.responses()) == 1 and gone):
        held("the real season keeps the harness and dev's switch", f"team-started #2 launch.harness the witness, its "
             f"grammar beside it; profiles.dev {profile}; the face's season 2, dev's launch packages {packages}; done T1; "
             f"lead ended, run {lead['run']} on the tab; responses.jsonl 1 line; no witness left")
    else:
        failures.append(f"  ✗ real season                 rc={played.returncode} started={len(started)} launch={launch} "
                        f"profile={profile} season={state.get('season')} packages={packages} done={finished} lead={lead} "
                        f"responses={len(team.responses())} alive={team.alive()} {played.stdout[-2000:]!r} "
                        f"{played.stderr[-400:]!r}")
    return 0
