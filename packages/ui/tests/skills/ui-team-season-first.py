"""Scenario `ui-team-season-first` -- `S` on a team never started opens its FIRST season, shown and played, on the
bench's witnesses: `veille`, never started -- its declaration (`team declaration --json`, its `declared`: each member's
`born` and `packages`), the agents of its members (`agent status --json`, their `last`), the harness given after `--`
to `./pp ui`:
- its agents never played: an overlay titled by the team with no season number, a line per member of `declared`
  under the line `all`, nothing carried, nothing changed; the preview `./pp team start veille`, nothing more
- its agents never played, a message typed: `team start veille --message go`, nothing of the agents
- the message typed and `all`'s model edited in its profile: the start carries the message, the fixture's provider
  and the model, never a `--max-budget-usd`
- a `--harness` given after `--` rides the start, shown and played; no other flag of `--` does
- a `--provider` beside it rides with it, the grammar the harness's output is read in: it replaces the provider of
  the overlay
- the harness stands before any `--member`: what follows one is that member's
- its agents played before: the line `all` prefilled from the root's agent's `last`, a member the model its own
  agent last played, `·` elsewhere; without a message the start plays what `all` holds and what a member changes --
  no `--message`, no `--name`
- the agent of a member not born is never asked: no `status agents/scribe` in the journal of `agent`
- a member not born opens its profile on the packages `declared` gives it, in their order
- `plan` switched off on that member composes `--member scribe --package plan=off`
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the readers of a capture and of the palette's source

SIZE = ("--size", "130x60")
TO_TABLE = "shift+tab,shift+tab"       # from the message of the first task up to the lines: the name, the table
TO_PACKAGES = "tab,tab,tab"            # in a profile, from the model down to the packages
PROVIDER = T.D.PROVIDER
NONE, AS_ALL, SEP = (P.palette_constant(one) for one in ("NONE", "AS_ALL", "SEP"))

# the message typed, then `all`'s model in its profile
KEYS = "down,down,S,g,o,shift+tab,shift+tab,enter,o,p,u,s,enter"
START = f"./pp team start veille --message go --provider {PROVIDER} --model opus"
HARNESS = ("--harness", "run me")
HARNESSED = f"{START} --harness 'run me'"

# `veille` declares `scout`, its root, and `writer`, their agents played before, and `scribe`, its agent not born
VEILLE = T.declaration("veille", [("scout", "agents/scout"), ("writer", "agents/writer"),
                                  ("scribe", "agents/scribe", T.ALL_ON, False)], {"budget": 3.0}, started=False)
SCOUT = T.SEASON_AGENTS["agents/scout"][0]["last"]
WRITER = T.SEASON_AGENTS["agents/writer"][0]["last"]["policy"]
PREFILLED = (f"team start veille --provider {SCOUT['provider']} --model {SCOUT['policy']['model']} "
             f"--effort {SCOUT['policy']['effort']} --member writer --model {WRITER['model']}")


def _agents(house, agents: dict) -> None:
    """The witness of `agent` says these agents' `status --json` from the next call on -- the faces `T.Teams` writes
    at its birth."""
    faces = {**T.MEMBER_FACES, "status": {**T.MEMBER_FACES["status"], **agents}, "providers": T.PROVIDERS}
    Path(house.env["PP_UI_CHAT_SCRIPT"]).write_text(json.dumps({"faces": faces}), encoding="utf-8")


def _lines(text: str, declared: dict) -> list[list[str]]:
    """-> the cells of the season's table: the line above the first member's, then one per member of `declared`,
    each found by its name and its path; [] when a member's line is missing."""
    rows = [T.cells_of(one) for one in P.overlay_rows(text)]
    found = []
    for one in declared["declared"]["agents"]:
        at = next((n for n, cells in enumerate(rows) if cells[:2] == [one["member"], one["path"]]), None)
        if at is None:
            return []
        found.append(rows[at])
        if len(found) == 1:
            found.insert(0, rows[at - 1])
    return found






def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-season-first")

    # --- agents never played: the season shown bare, a message typed -------------------------------------------
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "down,down,S")
    title = P.title_of(shown.stdout) or [""]
    lines = _lines(shown.stdout, T.DECLARATIONS["veille"])
    preview = T.overlay_preview(shown, "./pp team start")
    if (shown.returncode == 0 and "veille" in title[0].split() and not re.search(r"\d", title[0])
            and len(lines) == 3 and set(lines[0][1:]) == {NONE} and all(set(one[2:]) == {AS_ALL} for one in lines[1:])
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
               "--member reviewer --model sonnet --package plan=off")
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "S,ctrl+s", "--", *HARNESS)
    if done.returncode == 0 and house.gestures() == [ordered]:
        held("the harness stands before any --member", ordered)
    else:
        failures.append(f"  ✗ harness before members      rc={done.returncode} {house.gestures()} {done.stdout[-900:]!r} "
                        f"{done.stderr[-300:]!r}")

    # --- agents played before, a member not born ------------------------------------------------------------------
    _agents(house, T.SEASON_AGENTS)
    house.use(T.script(declarations={**T.DECLARATIONS, "veille": VEILLE}))
    house.clear_journal()
    shown = house.render("--render", "teams", *SIZE, "--press", "down,down,S")
    lines = _lines(shown.stdout, VEILLE)
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
    wanted = f"{PREFILLED} --member scribe --package plan=off"
    if (shown.returncode == 0 and "scribe" in title[0].split() and row and len(row.split(SEP)) == len(names)
            and done.returncode == 0 and played == [wanted]):
        held("a member not born has its packages", f"{row!r}; {wanted}")
    else:
        failures.append(f"  ✗ not born                    rc={shown.returncode},{done.returncode} {title} {row!r} "
                        f"{played} {top[-1500:]!r} {done.stderr[-300:]!r}")
    return 0
