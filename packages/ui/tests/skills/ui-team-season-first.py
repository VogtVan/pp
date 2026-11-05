"""Scenario `ui-team-season-first` -- `S` on a team never started opens its FIRST season, shown and played, on the
bench's witnesses: `veille`, never started -- its declaration (`team declaration --json`, its `declared`: each member's
`born` and `packages`), its members' agents never played, the harness given after `--` to `./pp ui` (the agents played
before: `ui-team-season-prefilled`):
- its agents never played: an overlay titled by the team with no season number, a line per member of `declared`
  under the line `all`, nothing carried but the set the declaration says -- `all` its packages on --, nothing changed;
  the preview `./pp team start veille`, nothing more: the set a start without `--package` gives
- its agents never played, a message typed: `team start veille --message go`, nothing of the agents
- `plan` switched on on `all` in its profile: the whole set of `all` composed after the provider the profile holds,
  `--package plan=on --package steering=off --package team=on`
- the message typed and `all`'s model edited in its profile: the start carries the message, the fixture's provider
  and the model, never a `--max-budget-usd`
- a `--harness` given after `--` rides the start, shown and played; no other flag of `--` does
- a `--provider` beside it rides with it, the grammar the harness's output is read in: it replaces the provider of
  the overlay
- the harness stands before any `--member`: what follows one is that member's
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SIZE = ("--size", "130x60")
TO_TABLE = "shift+tab,shift+tab"       # from the message of the first task up to the lines: the name, the table
TO_PACKAGES = "tab,tab,tab"            # in a profile, from the model down to the packages
PROVIDER = T.D.PROVIDER
NONE, AS_ALL = (P.palette_constant(one) for one in ("NONE", "AS_ALL"))
ON = " ".join(name for name, on in T.SILENT.items() if on)     # the packages on of the set the declaration says
WHOLE = f"team start veille --provider {PROVIDER} --package plan=on --package steering=off --package team=on"

# the message typed, then `all`'s model in its profile
KEYS = "down,down,S,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter"
START = f"./pp team start veille --message go --provider {PROVIDER} --model opus"
HARNESS = ("--harness", "run me")
HARNESSED = f"{START} --harness 'run me'"

def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-first")

    # --- agents never played: the season shown bare, a message typed -------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "down,down,S")
    title = P.title_of(shown.stdout) or [""]
    lines = T.season_rows(shown.stdout, T.DECLARATIONS["veille"])
    preview = T.overlay_preview(shown, "./pp team start")
    if (shown.returncode == 0 and "veille" in title[0].split() and not re.search(r"\d", title[0])
            and len(lines) == 3 and set(lines[0][1:-1]) == {NONE} and lines[0][-1] == ON
            and all(set(one[2:]) == {AS_ALL} for one in lines[1:])
            and preview == "./pp team start veille" and house.gestures() == []):
        held("a first season shows its members and starts without a task",
             f"{title[0]!r}; {len(lines) - 1} lines of members under all, nothing carried; {preview}")
    else:
        failures.append(f"  ✗ first season shown          rc={shown.returncode} {title} {lines} {preview!r} "
                        f"{shown.stdout[-2500:]!r} {shown.stderr[-400:]!r}")

    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "down,down,S,g,o,ctrl+s")
    if done.returncode == 0 and house.gestures() == ["team start veille --message go"]:
        held("a first season of agents never played starts bare", house.gestures()[0])
    else:
        failures.append(f"  ✗ first season bare           rc={done.returncode} {house.gestures()} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press",
                        f"down,down,S,{TO_TABLE},enter,{TO_PACKAGES},enter,space,enter,enter,ctrl+s")
    if done.returncode == 0 and house.gestures() == [WHOLE]:
        held("a switch of all composes its whole set", WHOLE)
    else:
        failures.append(f"  ✗ whole set                   rc={done.returncode} {house.gestures()} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- the parameters of the run, the harness of the post ------------------------------------------------------
    shown = house.render("--render", "teams", *SIZE, "--press", KEYS, "--", *HARNESS, "--launches", "3")
    preview = T.overlay_preview(shown, "./pp team start")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", KEYS + ",ctrl+s", "--", *HARNESS, "--launches", "3")
    played = house.gestures()
    if (shown.returncode == 0 and done.returncode == 0 and preview[:len(START)] == START and len(played) == 1
            and played[0][:len(START) - 5] == START[5:] and "--max-budget-usd" not in played[0].split()):
        held("S starts the team with the run's parameters", START)
    else:
        failures.append(f"  ✗ start                       rc={shown.returncode},{done.returncode} {preview!r} {played} "
                        f"{shown.stdout[-1500:]!r} {shown.stderr[-400:]!r}")
    if preview == HARNESSED and played == [HARNESSED[5:]] and "--launches" not in played[0].split():
        held("the harness of the post rides S", f"{HARNESSED}; --launches left to agent chat")
    else:
        failures.append(f"  ✗ harness                     {preview!r} {played}")

    graded = "team start veille --message go --model opus --harness 'run me' --provider p"
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", KEYS + ",ctrl+s",
                        "--", *HARNESS, "--provider", "p", "--launches", "3")
    if done.returncode == 0 and house.gestures() == [graded]:
        held("the grammar of the harness rides S with it", f"{graded}; the overlay's provider replaced")
    else:
        failures.append(f"  ✗ grammar                     rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    ordered = (f"team start core-review --budget 2 --provider {PROVIDER} --model opus --effort high --harness 'run me' "
               "--package plan=on --package steering=on --package team=on --member reviewer --model sonnet --package plan=off")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "S,ctrl+s", "--", *HARNESS)
    if done.returncode == 0 and house.gestures() == [ordered]:
        held("the harness stands before any --member", ordered)
    else:
        failures.append(f"  ✗ harness before members      rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    return 0
