"""Scenario `ui-real-team-season` -- the first season of a team started from the post on the REAL verbs of `team`,
its wake-ups played by the team witness, never a provider; `essai`, never started:
- `S` with a message: the form of the first season, titled by the team, no command shown; nothing is written before
  it plays
- `S`, `ctrl+s` with no message: the real `team start` writes `team-started` alone, carrying the `--harness` given
  after `--` to `./pp ui` as `launch.harness`; the face says `idle`
Its sibling, cut by case: `ui-real-team-season-next` (the next season).
"""
from __future__ import annotations

from tests.harness import support

R = support(__file__, "real_team")
P = support(__file__, "dialogue")      # the readers of a capture
SIZE = ("--size", "200x60")
WHOLE = ("--size", "200x210")        # the whole form in view, its title read above its fields
FIRST = "S,g,o"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    team = R.RealTeam(bench, "ui-real-team-season", {})

    # --- S: the first season's overlay, nothing written before it plays --------------------------------------------
    shown = team.render("--render", "teams", *WHOLE, "--press", FIRST)
    title = P.title_of(shown.stdout) or [""]
    if (shown.returncode == 0 and R.TEAM in title[0].split() and "./pp" not in shown.stdout
            and team.events() == []):
        held("S opens the first season", f"{title[0]!r}, no command; nothing written before it plays")
    else:
        failures.append(f"  ✗ first season shown          rc={shown.returncode} {shown.stdout[-1500:]!r} {shown.stderr[-300:]!r}")

    # --- ctrl+s, no message: the real start without a task -------------------------------------------------------
    bare = team.render("--render", "teams", *SIZE, "--press", "S,ctrl+s")
    team.settled(lambda events: any(one.get("kind") == "team-started" for one in events))
    kinds = [one.get("kind") for one in team.events()]
    harness = ((team.kinds("team-started")[:1] or [{}])[0].get("launch") or {}).get("harness")
    first = team.state()
    if (bare.returncode == 0 and kinds == ["team-started"] and harness == team.harness
            and first.get("state") == "idle"):
        held("the real start without a task", "team-started alone, the harness of the post as launch.harness, the face idle")
    else:
        failures.append(f"  ✗ start without a task        rc={bare.returncode} {kinds} {harness!r} {first.get('state')!r} "
                        f"{bare.stdout[-900:]!r} {bare.stderr[-300:]!r}")
    return 0
