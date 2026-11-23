"""Scenario `ui-team-season-harness` -- `S` plays the parameters of the run and the harness given to the post, on the
bench's witnesses: `veille`, never started, SEASON.md writing nothing of its season; `core-review`, its season written;
the harness given after `--` to `./pp ui`; what plays read from the witness's journal:
- `all`'s model edited in its profile: the `declare --season` of `ctrl+s` carries the season's context at the form's
  default, the fixture's provider and the model, never a `--max-budget-usd`; then `team start` without a flag of the
  season
- a `--harness` given after `--` rides that declare; no other flag of `--` does
- a `--provider` beside it rides with it, the grammar the harness's output is read in: it replaces the provider of
  the overlay
- the harness stands before any `--member`: what follows one is that member's -- `lead`'s model, edited
Its sibling, cut by case: `ui-team-season-first` (the first season of a team).
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

SIZE = T.SEASON_SMALL
PROVIDER = T.D.PROVIDER

# `all`'s model in its profile
KEYS = f"down,down,S,{T.TO_LINES},enter,o,p,u,s,ctrl+enter"
START = f"team declare veille --season --context 90 --provider {PROVIDER} --model opus"
HARNESS = ("--harness", "run me")
STARTED = "team start veille --no-tick"      # the season SEASON.md writes once declared: no flag of the season
HARNESSED = [f"{START} --harness 'run me' --json", STARTED]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-harness")

    # --- the parameters of the run, the harness of the post ------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", KEYS + ",ctrl+s", "--", *HARNESS, "--launches", "3")
    played = house.gestures()
    if (done.returncode == 0 and len(played) == 2 and played[1] == STARTED
            and played[0][:len(START)] == START and "--max-budget-usd" not in played[0].split()):
        held("S starts the team with the run's parameters", START)
    else:
        failures.append(f"  ✗ start                       rc={done.returncode} {played} "
                        f"{done.stdout[-1500:]!r} {done.stderr[-400:]!r}")
    if played == HARNESSED and "--launches" not in played[0].split():
        held("the harness of the post rides S", f"{HARNESSED[0]}; --launches left to agent chat")
    else:
        failures.append(f"  ✗ harness                     {played}")

    graded = ["team declare veille --season --context 90 --model opus --harness 'run me' --provider p --json", STARTED]
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", KEYS + ",ctrl+s",
                        "--", *HARNESS, "--provider", "p", "--launches", "3")
    if done.returncode == 0 and house.gestures() == graded:
        held("the grammar of the harness rides S with it", f"{graded}; the overlay's provider replaced")
    else:
        failures.append(f"  ✗ grammar                     rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    ordered = ["team declare core-review --season --context 90 --harness 'run me' --member lead --model haiku --json",
               T.NEXT]
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", f"S,{T.TO_LINES},down,enter,h,a,i,k,u,ctrl+enter,ctrl+s",
                        "--", *HARNESS)
    if done.returncode == 0 and house.gestures() == ordered:
        held("the harness stands before any --member", ordered[0])
    else:
        failures.append(f"  ✗ harness before members      rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    return 0
