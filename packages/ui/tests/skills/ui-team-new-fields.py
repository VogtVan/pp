"""Scenario `ui-team-new-fields` -- the fields of `N` compose their flags (plan ui, batch le-formulaire-d-equipe), on
the bench's `pp-team` witness:
- another template (`lead-reviewers`), its members changed -- each line `<name> <path>` --, a root chosen, a
  principal, the budget changed: `--member lead agents/l --member reviewer agents/r --root reviewer --principal pm
  --budget 10`, in the order the command shows, played word for word
- the ceremony of `supervisor-workers` unchecked: `--no-ceremony`
- what cannot play plays nothing and says why: no name; a member without its path
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")

SIZE = ("--size", "140x110")             # the ten fields and the command under them in view


def typed(text: str) -> str:
    """-> the keys that type `text`, a blank as `space`."""
    return ",".join("space" if char == " " else char for char in text)


NAME = "N,x"
TO_LEAD = "shift+tab,down,down,enter"                       # from the name: the template list, its second line
MEMBERS = "tab,tab,end," + typed(" agents/l") + ",down,end," + typed(" agents/r")
ROOT = "tab,down,down,down,enter"                           # the blank, lead, reviewer
REST = "tab," + typed("pm") + ",tab,tab," + typed("10")
FIELDS = "./pp team new x --template lead-reviewers --member lead agents/l --member reviewer agents/r --root reviewer " \
    "--principal pm --budget 10"


def keys(*parts: str) -> str:
    return ",".join(parts)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-new-fields")

    # --- another template, its fields changed: each flag composed -----------------------------------------
    house.clear_journal()
    press = keys(NAME, TO_LEAD, MEMBERS, ROOT, REST)
    shown = house.render("--render", "teams", *SIZE, "--press", press)
    preview = T.preview_folded(shown, "./pp team new")
    played = house.render("--render", "teams", *SIZE, "--press", press + ",enter")
    if shown.returncode == 0 and played.returncode == 0 and preview == FIELDS and house.gestures() == [FIELDS[5:]]:
        held("a field changed composes its flag", FIELDS)
    else:
        failures.append(f"  ✗ fields                      {preview!r} {house.gestures()} {shown.stdout[-2500:]!r} "
                        f"{shown.stderr[-400:]!r}")

    # --- the ceremony unchecked ------------------------------------------------------------------------------
    house.clear_journal()
    off = house.render("--render", "teams", *SIZE, "--press", "N,x,tab,tab,tab,tab,down,down,enter,enter")
    if off.returncode == 0 and house.gestures() == ["team new x --template supervisor-workers --no-ceremony"]:
        held("the ceremony unchecked composes --no-ceremony", house.gestures()[0])
    else:
        failures.append(f"  ✗ ceremony                    {house.gestures()} {off.stdout[-2000:]!r}")

    # --- what cannot play: no name; a member without its path ------------------------------------------------
    house.clear_journal()
    nameless = house.render("--render", "teams", *SIZE, "--press", "N,enter")
    pathless = house.render("--render", "teams", *SIZE, "--press", keys(NAME, "tab,end," + typed(" agents/s")
                                                                        + ",down,end,space", "enter"))
    flat_n, flat_p = " ".join(nameless.stdout.split()), " ".join(pathless.stdout.split())
    if (nameless.returncode == 0 and pathless.returncode == 0 and house.gestures() == []
            and "a name for the team" in flat_n and "<name> <path>" in flat_p):
        held("what cannot play plays nothing and says why", "no name: `a name for the team`; a member without its path: "
             "`<name> <path>`; nothing in the witness's journal")
    else:
        failures.append(f"  ✗ nothing played              {house.gestures()} {nameless.stdout[-1200:]!r} "
                        f"{pathless.stdout[-1200:]!r}")
    return 0
