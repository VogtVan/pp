"""Scenario `ui-team-season-prefilled` -- `S` on a team never started whose members' agents played before opens its
FIRST season prefilled from them, on the bench's witnesses: `veille`, never started -- its declaration (`team
declaration --json`: `scout`, its root, and `writer`, their agents born and played, and `scribe`, its agent not born),
the agents' `status --json` (their `last`):
- the line `all` prefilled from the root's agent's `last`, a member the model its own agent last played, `·` elsewhere;
  without a message the start plays what `all` holds and what a member changes -- no `--message`, no `--name`
- the agent of a member not born is never asked: no `status agents/scribe` in the journal of `agent`
- a member not born opens its profile on the packages `declared` gives it, in their order
- `plan` switched on on that member composes `--member scribe --package plan=on`, its change of `all`'s set alone
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SIZE = ("--size", "130x60")
TO_TABLE = "shift+tab,shift+tab"       # from the message of the first task up to the lines: the name, the table
TO_PACKAGES = "tab,tab,tab"            # in a profile, from the model down to the packages
AS_ALL, SEP = (P.palette_constant(one) for one in ("AS_ALL", "SEP"))

# `veille` declares `scout`, its root, and `writer`, their agents played before, and `scribe`, its agent not born
VEILLE = T.declaration("veille", [("scout", "agents/scout"), ("writer", "agents/writer"),
                                  ("scribe", "agents/scribe", False)], {"budget": 3.0}, started=False)
SCOUT = T.SEASON_AGENTS["agents/scout"][0]["last"]
WRITER = T.SEASON_AGENTS["agents/writer"][0]["last"]["policy"]
PREFILLED = (f"team start veille --provider {SCOUT['provider']} --model {SCOUT['policy']['model']} "
             f"--effort {SCOUT['policy']['effort']} --member writer --model {WRITER['model']}")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-prefilled", T.script(declarations={**T.DECLARATIONS, "veille": VEILLE}),
                    agents=T.SEASON_AGENTS)

    # --- agents played before, a member not born ------------------------------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "down,down,S")
    lines = T.season_rows(shown.stdout, VEILLE)
    preview = T.overlay_preview(shown, "./pp team start")
    carried = [SCOUT["provider"], SCOUT["policy"]["model"], SCOUT["policy"]["effort"]]
    writer = ["writer", "agents/writer", AS_ALL, WRITER["model"], AS_ALL, AS_ALL, AS_ALL]
    if (shown.returncode == 0 and len(lines) == 4 and lines[0][2:5] == carried and lines[2] == writer
            and preview == f"./pp {PREFILLED}"):
        held("a first season prefilled from the agents' last", f"all {carried}; {lines[2]}; {preview}")
    else:
        failures.append(f"  ✗ first season prefilled      rc={shown.returncode} {lines} {preview!r} "
                        f"{shown.stdout[-2500:]!r} {shown.stderr[-400:]!r}")

    profile = f"down,down,S,{TO_TABLE},down,down,down,enter"
    shown = house.render("--render", "teams", *SIZE, "--press", profile)
    top = P.on_top(shown.stdout)
    title = P.title_of(top) or [""]
    names = [one["name"] for one in VEILLE["declared"]["agents"][2]["packages"]]
    row = next((one for one in P.overlay_rows(top) if T.in_order(one, *names)), "")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", f"{profile},{TO_PACKAGES},enter,space,enter,enter,ctrl+s")
    played = house.gestures()
    asked = [one for one in house.chat_lines() if one.startswith("status agents/")]
    words = played[0].split() if len(played) == 1 else []
    if (done.returncode == 0 and played and played[0].startswith(PREFILLED + " ") and "--message" not in words
            and "--name" not in words and "status agents/scout --json" in asked
            and "status agents/scribe --json" not in asked):
        held("a first season starts without a task", f"{PREFILLED} …; the agents asked {asked}")
    else:
        failures.append(f"  ✗ no message                  rc={done.returncode} {played} {asked} "
                        f"{done.stdout[-2000:]!r} {done.stderr[-300:]!r}")
    wanted = f"{PREFILLED} --member scribe --package plan=on"
    if (shown.returncode == 0 and "scribe" in title[0].split() and row and len(row.split(SEP)) == len(names)
            and done.returncode == 0 and played == [wanted]):
        held("a member not born has its packages", f"{row!r}; {wanted}")
    else:
        failures.append(f"  ✗ not born                    rc={shown.returncode},{done.returncode} {title} {row!r} "
                        f"{played} {top[-1500:]!r} {done.stderr[-300:]!r}")
    return 0
