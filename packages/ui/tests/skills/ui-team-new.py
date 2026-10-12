"""Scenario `ui-team-new` -- `N` gives birth to a team from a template (plan ui, batch le-formulaire-d-equipe), on the
bench's `pp-team` witness replaying `team templates --json`:
- `N` on the Teams tab opens the form of the first template, read once from `templates --json`: its members, its
  ceremony, its limits
- a name typed, the command under the fields is `./pp team new veille-ram --template supervisor-workers` -- no flag
  for a field left at its default --, and `enter` plays it word for word
- a refusal of `team new` goes to the remedy line as the verb said it, the form open again on its values
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

SIZE = ("--size", "140x110")             # the ten fields and the command under them in view
NAMED = "N," + ",".join("veille-ram")
NEW = "./pp team new veille-ram --template supervisor-workers"


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new")

    # --- N: the form of the first template ------------------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "N")
    flat = " ".join(shown.stdout.split())
    reads = [one for one in house.journal_lines() if one.startswith("templates")]
    if (shown.returncode == 0 and "a new team" in flat and "supervisor-workers" in flat and "worker-1" in flat
            and "daily every weekday 09:30" in flat and "900" in flat and reads == ["templates --json"]):
        held("N opens the form of a template", f"supervisor-workers, its members, its daily, its limits; {reads}")
    else:
        failures.append(f"  ✗ form                        rc={shown.returncode} {reads} {shown.stdout[-2500:]!r} "
                        f"{shown.stderr[-400:]!r}")

    # --- the name typed: the command shown, then played word for word -----------------------------------
    typed = house.render("--render", "teams", *SIZE, "--press", NAMED)
    preview = T.preview_in(typed, "./pp team new")
    house.clear_journal()
    played = house.render("--render", "teams", *SIZE, "--press", NAMED + ",enter")
    if typed.returncode == 0 and played.returncode == 0 and preview == NEW and house.gestures() == [NEW[5:]]:
        held("the form plays what it shows", f"{preview!r}, played as shown; no flag for a field left as it opened")
    else:
        failures.append(f"  ✗ played                      {preview!r} {house.gestures()} {typed.stdout[-1800:]!r} "
                        f"{typed.stderr[-400:]!r}")

    # --- a refusal: said on the remedy line, the form open again ------------------------------------------
    house.use(T.script(answers={"new": {"rc": 2, "err": "pp-team: team-exists -- teams/veille-ram/TEAM.md stands: a "
                                                       "template writes a new team, never over the owner's.\n"}}))
    refused = house.render("--render", "teams", *SIZE, "--press", NAMED + ",enter")
    remedy = T.remedy_of(refused)
    if refused.returncode == 0 and "team-exists" in remedy and T.preview_in(refused, "./pp team new") == NEW:
        held("a refusal of team new is said, the form open again", remedy[:90])
    else:
        failures.append(f"  ✗ refused                     {remedy!r} {refused.stdout[-1500:]!r}")
    return 0
