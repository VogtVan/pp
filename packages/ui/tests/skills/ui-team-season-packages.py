"""Scenario `ui-team-season-packages` -- the packages of a season, line by line (plan ui, batch l-overlay-de-saison), on
the bench's witnesses -- `core-review`'s members `lead`, `reviewer` and `scribe`, their agents saying their packages
(`agent status --json`), the team's face saying what a member may not switch off (`required`):
- `plan` switched off on `lead`'s line: `--member lead --package plan=off`, the column saying `-plan`
- `steering` switched off on `all`: one `--package steering=off` per member whose agent has it on -- `scribe`'s has none
- `team`, required: greyed in the overlay of the packages, never toggled, never composed `off`
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

SIZE = ("--size", "130x60")
TO_TABLE = "shift+tab,shift+tab"      # from the message of the first task up to the lines
TO_PACKAGES = "tab,tab,tab"           # in a profile, from the model down to the packages: effort, permissions, packages
P = T.D.PROVIDER
HEAD = f"team start core-review --budget 2 --provider {P} --model opus --effort high"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-packages", agents=T.SEASON_AGENTS)

    # --- a member's switch -----------------------------------------------------------------------------------
    member = f"S,{TO_TABLE},down,enter,{TO_PACKAGES},enter,space,enter,enter"
    shown = house.render("--render", "teams", *SIZE, "--press", member)
    lead = next((one for one in shown.stdout.split("\n") if "lead" in one and "agents/lead" in one), "")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", member + ",ctrl+s")
    wanted = f"{HEAD} --member lead --package plan=off --member reviewer --model sonnet --package plan=off"
    if shown.returncode == 0 and "-plan" in lead and done.returncode == 0 and house.gestures() == [wanted]:
        held("plan off on a member's line", f"{lead.strip(' ┃│')[:70]!r}; {wanted}")
    else:
        failures.append(f"  ✗ member switch               rc={shown.returncode},{done.returncode} {lead!r} {house.gestures()} "
                        f"{shown.stdout[-2500:]!r} {done.stderr[-400:]!r}")

    # --- a switch of `all`, member by member -------------------------------------------------------------------
    whole = f"S,{TO_TABLE},enter,{TO_PACKAGES},enter,down,space,enter,enter"
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", whole + ",ctrl+s")
    wanted = (f"{HEAD} --member lead --package steering=off --member reviewer --model sonnet --package plan=off "
              f"--package steering=off")
    if done.returncode == 0 and house.gestures() == [wanted]:
        held("steering off on all, for each member whose agent has it", wanted)
    else:
        failures.append(f"  ✗ all switch                  rc={done.returncode} {house.gestures()} {done.stdout[-2500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- `team`, required ------------------------------------------------------------------------------------
    required = f"S,{TO_TABLE},enter,{TO_PACKAGES},enter,down,down,space"
    shown = house.render("--render", "teams", *SIZE, "--press", required)
    row = next((one for one in shown.stdout.split("\n") if "team" in one and "required" in one), "")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", required + ",enter,enter,ctrl+s")
    played = " ".join(house.gestures())
    if shown.returncode == 0 and row and done.returncode == 0 and house.gestures() and "team=off" not in played:
        held("team required: greyed, never off", f"{row.strip(' ┃│')[:60]!r}; {house.gestures()}")
    else:
        failures.append(f"  ✗ required                    rc={shown.returncode},{done.returncode} {row!r} {house.gestures()} "
                        f"{shown.stdout[-2500:]!r}")
    return 0
