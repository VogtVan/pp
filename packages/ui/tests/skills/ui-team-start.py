"""Scenario `ui-team-start` -- `S` starts the team chosen (plan ui, batch les-gestes-du-pilote; its season, batch
l-overlay-de-saison), on the bench's witnesses:
- on `veille`, never started: its season, the message typed, the line `all` edited in its profile (the providers of
  `agent providers --json`) -- no budget there: a wake-up's share is team's (batch le-profil-de-lancement) --, the
  preview of the whole command under the fields; `ctrl+s` plays `team start veille --message go --provider <the
  fixture's> --model opus`, never a `--max-budget-usd`
- a name typed beside the message names the first task (`--name`)
- on `core-review`: a refusal of `team start` (`team-invalid`) goes to the remedy line as the verb said it
- the harness of the post riding `S`: `ui-team-start-harness`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

KEYS = "down,down,S,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter"   # the message, then `all`'s model in its profile
START = f"./pp team start veille --message go --provider {T.D.PROVIDER} --model opus"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-start")

    shown = house.render("--render", "teams", "--size", "130x40", "--press", KEYS)
    preview = T.preview_in(shown, "./pp team start veille --message go")   # the head says `--message …`
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", KEYS + ",ctrl+s")
    if shown.returncode == 0 and done.returncode == 0 and preview == START and house.gestures() == [START[5:]]:
        held("S starts the team with the run's parameters", START)
    else:
        failures.append(f"  ✗ start                       rc={shown.returncode},{done.returncode} {preview!r} "
                        f"{house.gestures()} {shown.stdout[-1200:]!r} {shown.stderr[-400:]!r}")

    profile = house.render("--render", "teams", "--size", "130x60", "--press", "down,down,S,shift+tab,shift+tab,enter",
                           "--wait", "none:1")
    if profile.returncode == 0 and "all the members of the season" in profile.stdout and "above 0" not in profile.stdout \
            and "max-budget-usd" not in " ".join(house.gestures()):
        held("S asks no budget", "the profile of the wake-ups has no budget field; no --max-budget-usd played")
    else:
        failures.append(f"  ✗ no budget                   rc={profile.returncode} {house.gestures()} "
                        f"{profile.stdout[-1500:]!r}")

    named = f"./pp team start veille --message go --name Nova --provider {T.D.PROVIDER} --model opus"
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "130x40", "--press", KEYS + ",tab,N,o,v,a,enter")
    if done.returncode == 0 and house.gestures() == [named[5:]]:
        held("S names the first task", named)
    else:
        failures.append(f"  ✗ named                       rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r}")

    house.use(T.script(answers={"start": {"rc": 2, "err": "pp-team: team-invalid -- teams/core-review/TEAM.md: "
                                                        "`parallel: 0` is no whole number of 1 or more.\n"}}))
    done = house.render("--render", "teams", "--size", "130x40", "--press", "S,ctrl+s")
    remedy = T.remedy_of(done)
    if done.returncode == 0 and "team-invalid -- teams/core-review/TEAM.md" in remedy:
        held("a refused start: the refusal said", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     rc={done.returncode} {remedy!r} {done.stdout[-700:]!r}")

    return 0
