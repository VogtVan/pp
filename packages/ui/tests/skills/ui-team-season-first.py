"""Scenario `ui-team-season-first` -- `S` on a team never started opens its FIRST season and plays it, on the
bench's witnesses: `veille`, never started -- its declaration (`team declaration --json`, its `declared`: each member's
`born` and `packages`; its season, SEASON.md writing none: no launch, the set a start without `--package` gives) --,
the harness given after `--` to `./pp ui` (a season SEASON.md writes: `ui-team-season-prefilled`):
- its season unwritten: an overlay titled by the team with no season number, a line per member of `declared` under
  the line `all`, nothing carried but the set the declaration says -- `all` its packages on --, nothing changed, no
  command shown
- `ctrl+s` on the form left as it is: `team declare veille --season --context 90` -- its context at the form's
  default --, then `team start veille`, nothing more -- the season SEASON.md writes, no task (what plays read from the witness's journal)
- `plan` switched on on `all` in its profile: that package alone composed, after the provider the profile holds --
  the season SEASON.md writes keeps the rest
Its sibling, cut by case: `ui-team-season-harness` (the parameters of the run, the harness of the post).
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SIZE = T.SEASON_SMALL
TO_PACKAGES = "tab,tab,tab"            # in a profile, from the model down to the packages
PROVIDER = T.D.PROVIDER
NONE, AS_ALL = (P.palette_constant(one) for one in ("NONE", "AS_ALL"))
ON = " ".join(name for name, on in T.SILENT.items() if on)     # the packages on of the set the declaration says
WHOLE = [f"team declare veille --season --context 90 --provider {PROVIDER} --package plan=on --json",
         "team start veille --no-tick"]

BARE = ["team declare veille --season --context 90 --json", "team start veille --no-tick"]   # SEASON.md writes
#                                                 nothing of a first season: its context at the form's default

def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-first")

    # --- agents never played: the season shown bare, started bare -------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *T.SEASON_SIZE, "--press", f"down,down,S,{T.TO_LINES},boxes")
    title = P.title_of(shown.stdout) or [""]
    lines = T.season_rows(shown.stdout, T.DECLARATIONS["veille"])
    if (shown.returncode == 0 and "veille" in title[0].split() and not re.search(r"\d", title[0])
            and len(lines) == 3 and set(lines[0][1:-1]) == {NONE} and lines[0][-1] == ON
            and all(set(one[2:]) == {AS_ALL} for one in lines[1:])
            and "./pp" not in shown.stdout and house.gestures() == []):
        held("a first season shows its members, nothing carried",
             f"{title[0]!r}; {len(lines) - 1} lines of members under all, nothing carried, no command")
    else:
        failures.append(f"  ✗ first season shown          rc={shown.returncode} {title} {lines} "
                        f"{shown.stdout[-2500:]!r} {shown.stderr[-400:]!r}")

    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "down,down,S,ctrl+s")
    if done.returncode == 0 and house.gestures() == BARE:
        held("a first season SEASON.md writes nothing of starts bare", " ; ".join(BARE))
    else:
        failures.append(f"  ✗ first season bare           rc={done.returncode} {house.gestures()} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press",
                        f"down,down,S,{T.TO_LINES},enter,{TO_PACKAGES},enter,space,ctrl+enter,ctrl+enter,ctrl+s")
    if done.returncode == 0 and house.gestures() == WHOLE:
        held("a switch of all composes that package alone", " ; ".join(WHOLE))
    else:
        failures.append(f"  ✗ whole set                   rc={done.returncode} {house.gestures()} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    return 0
