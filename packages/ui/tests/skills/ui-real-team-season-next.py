"""Scenario `ui-real-team-season-next` -- the next season of a team opened from the post on the REAL verbs of `team`,
its wake-ups played by the team witness, never a provider; `essai`, its first season started by the console without
a task, the witness as its harness:
- the season stopped by the console (`team stop`, team 1.27.0): `S` opens the form on the next season, the title naming the team, its season and the next: `dev`'s
  line edited in its profile, the package `ui` -- off in the set the first season gave, silent on it -- switched on
  there
- `ctrl+s` plays it, no task with it; `n` posts its task, the post following the team to its end: the journal's second `team-started` carries the witness
  as `launch.harness` with its grammar, `dev`'s switch under `profiles` and no other member's; the face says season 2,
  `dev`'s launch with `ui=on`, T1 done, `lead` ended with its run shown on the tab; `responses.jsonl` one line; no
  witness left
Its siblings, cut by case: `ui-real-team-season` (the first season), `ui-real-team-season-stop` (the stop).
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
P = support(__file__, "dialogue")      # the readers of a capture
T = support(__file__, "teams")
SIZE = ("--size", "200x60")
WHOLE = ("--size", "200x210")        # the whole form in view, its title read above its fields
TO_LINES = "ctrl+pagedown,ctrl+pagedown,ctrl+pagedown"   # the form of SEASON.md: from its preset to its members' lines
DEV_UI_ON = f"S,{TO_LINES},down,down,enter,tab,tab,tab,enter,down,down,space,ctrl+enter,ctrl+enter"
POSTED = "n,n,e,x,t,ctrl+enter"            # a new task of the team, its message typed: the season's first task


def _flat(text: str) -> str:
    return " ".join(text.replace("┃", " ").replace("│", " ").split())


def _member(state: dict, name: str) -> dict:
    return next((one for one in state.get("members") or [] if one.get("member") == name), {})


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-season-next", {"lead": [{"body": {"done": "next"}}]})
    begun = team.call("team", "start", R.TEAM, *team.harnessed, "--no-tick")
    team.settled(lambda events: any(one.get("kind") == "team-started" for one in events))
    halted = team.call("team", "stop", R.TEAM, "--no-tick")       # off season: what the next season's form writes on
    team.settled(lambda events: any(one.get("kind") == "season-stopped" for one in events))
    first = team.state()

    # --- S off season: the next season, dev's ui switched on --------------------------------------------------------
    shown = team.render("--render", "teams", *WHOLE, "--press", DEV_UI_ON)
    title = P.title_of(shown.stdout) or [""]
    n = int((first.get("season") or {}).get("n") or 0)
    if (begun.returncode == 0 and halted.returncode == 0 and shown.returncode == 0 and n == 1 and T.in_order(title[0], R.TEAM, str(n), str(n + 1))
            and "./pp" not in shown.stdout):
        held("S opens the next season", f"{title[0]!r}, no command")
    else:
        failures.append(f"  ✗ next season shown           rc={begun.returncode},{shown.returncode} n={n} {title} "
                        f"{begun.stderr[-300:]!r} {shown.stdout[-2500:]!r} {shown.stderr[-300:]!r}")

    # --- ctrl+s: the real start of the next season, followed to its end -------------------------------------------
    played = team.render("--render", "teams", *SIZE, "--press", f"{DEV_UI_ON},ctrl+s,{POSTED}",
                         "--wait", "team:done:40")
    flat = _flat(played.stdout)
    started = team.kinds("team-started")
    launch = (started[-1].get("launch") or {}) if len(started) == 2 else {}
    profiles = (started[-1].get("profiles") or {}) if len(started) == 2 else {}
    profile = profiles.get("dev") or {}
    finished = team.kinds("done", task="T1")
    state = team.state()
    packages = (_member(state, "dev").get("launch") or {}).get("packages") or []
    lead = _member(state, "lead")
    gone = team.settled(lambda events: not team.alive(), timeout=20.0)
    if (played.returncode == 0 and launch.get("harness") == team.harness and launch.get("provider") == R.WITNESS_GRAMMAR
            and "ui=on" in str(profile.get("packages")) and list(profiles) == ["dev"]
            and (state.get("season") or {}).get("n") == 2
            and "ui=on" in str(packages) and finished and lead.get("how") == "ended" and lead.get("run")
            and lead["run"] in flat and len(team.responses()) == 1 and gone):
        held("the real season keeps the harness and dev's switch", f"team-started #2 launch.harness the witness, its "
             f"grammar beside it; profiles.dev {profile}; the face's season 2, dev's launch packages {packages}; done T1; "
             f"lead ended, run {lead['run']} on the tab; responses.jsonl 1 line; no witness left")
    else:
        failures.append(f"  ✗ real season                 rc={played.returncode} started={len(started)} launch={launch} "
                        f"profiles={profiles} season={state.get('season')} packages={packages} done={finished} lead={lead} "
                        f"responses={len(team.responses())} alive={team.alive()} {played.stdout[-2000:]!r} "
                        f"{played.stderr[-400:]!r}")
    return 0
