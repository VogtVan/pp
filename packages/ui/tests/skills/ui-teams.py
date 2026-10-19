"""Scenario `ui-teams` -- the Teams tab reads the teams of the house, its members, their responses and their runs, on
the bench's `pp-team` witness replaying the faces of `team` for three declared teams, `core-review` and `ops` started
and `veille` never, and its `pp-chat` witness replaying the faces of `agent`:
- the menu counts each team's wake-ups under way, its questions to the owner and its tasks done, a team never started
  counting nothing; the head of the first team says its owner and principals, its budget spent over its cap, reserved
  and left, its wake-ups against their bound, its schedule and what waits for the owner; its members each with its
  agent, its run, how it stands and its tasks; the team, its cost and its wake-ups on the status line
- `d` opens the detail of a member in an overlay titled with its team and its name: its agent, its run and how it
  stands, its tasks, what it has pending
- `c` opens the ceremonies of the team in an overlay titled with the team: each ceremony, its progress, its next ring,
  its rhythm
- a team never started shows the command that starts it and no member
- `a` on a member opens its responses in an overlay titled with its team and its name, each with its id, its task and
  its whole text; none of another member's; nothing written
- nothing of `team` is read before the tab is shown: the dialogue, then the agents
- the overlay of the runs of an agent marks the run its member holds with its team and member, `team status <name>
  --json` read for the teams started alone; another run of the agent marked with nothing
- `enter` on that run opens it in a read-only tab of the dialogue, replayed from its kept flow -- no `agent chat`
- a house without a team shows no team, and reads none
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")
SIZE = ("--size", "130x34")
CORE, REVIEWER = T.CORE, T.CORE["members"][1]


def _row(rows, *words: str) -> str:
    """-> the first row holding every word, '' when none does."""
    return next((one for one in rows if all(word in one for word in words)), "")






def _head(text: str) -> list[str]:
    """-> the rows of the head of the team chosen: the centre's rows above its first band's edge, those with text."""
    centre = T.sides_of(text)[1]
    edge = next((n for n, one in enumerate(centre) if one.strip().startswith("─")), len(centre))
    return [one.strip() for one in centre[:edge] if one.strip()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-teams")

    # --- the menu, the head, the members, the status line ----------------------------------------
    done = house.render("--render", "teams", *SIZE)
    text = done.stdout
    menu, head, status = T.sides_of(text)[0], _head(text), P.status_of(text)
    counts = {badge["team"]: [str(badge[key]) for key in ("running", "asks", "done")] for badge in T.BADGES
              if badge["started"]}
    numbers = {team: T.cells_of(_row(menu, team))[1:] for team in ("core-review", "ops")}
    veille = T.cells_of(_row(menu, "veille"))
    budget, wakes = CORE["budget"], CORE["wakes"]
    figures = (f"{budget['spent']:.2f}/{budget['cap']:.2f}", f"{budget['reserved']:.2f}", f"{budget['left']:.2f}",
               f"{wakes['launched']}/{wakes['bound']}")
    waits = [len(CORE["waiting"]["questions"]), len(CORE["waiting"]["done"])]
    members = {one["member"]: _row(text.split("\n"), one["path"]) for one in CORE["members"]}
    if (done.returncode == 0 and numbers == counts and len(veille) == 4 and not re.search(r"\d", " ".join(veille))
            and head and all(one in head[0] for one in ("core-review", CORE["owner"], *CORE["principals"]))
            and all(any(one in row for row in head) for one in figures)
            and re.findall(r"\d+", head[-2]) == [str(CORE["schedule"]["minutes"])]
            and re.findall(r"\d+", head[-1]) == [str(one) for one in waits]
            and all(all(word in members[one["member"]] for word in (one["member"], one["run"], one["how"],
                                                                     str(len(one["tasks"]))))
                    for one in CORE["members"])
            and all(one in status for one in ("core-review", f"{CORE['cost']:.2f}", figures[3]))):
        held("the teams read whole", f"the menu counts {counts}, veille nothing; the head says {', '.join(figures)}, "
             f"every {CORE['schedule']['minutes']} min, {waits} waiting; {len(members)} members; the status says "
             f"{CORE['cost']:.2f} and {figures[3]}")
    else:
        failures.append(f"  ✗ teams read                  rc={done.returncode} {numbers} {veille} {head} {members} "
                        f"{status!r} {text[-1500:]!r} {done.stderr[-400:]!r}")

    # --- the detail of a member, `d` --------------------------------------------------------------
    done = house.render("--render", "teams", *SIZE, "--press", "tab,down,d")
    title, rows = P.title_of(done.stdout), P.overlay_rows(done.stdout)
    pending = REVIEWER["pending"][0]
    if (done.returncode == 0 and title and "core-review" in title[0] and REVIEWER["member"] in title[0]
            and _row(rows, REVIEWER["member"], REVIEWER["path"]) and _row(rows, REVIEWER["run"], REVIEWER["how"])
            and _row(rows, *REVIEWER["tasks"])
            and _row(rows, f"#{pending['id']}", pending["verb"], pending["from"], pending["task"])):
        held("the overlay of a member, `d`", f"titled {title[0]!r}: its agent, its run {REVIEWER['how']}, its tasks, "
             f"#{pending['id']} pending")
    else:
        failures.append(f"  ✗ overlay d                   rc={done.returncode} {title} {rows} {done.stderr[-300:]!r}")

    # --- the ceremonies, `c` ----------------------------------------------------------------------
    done = house.render("--render", "teams", *SIZE, "--press", "c")
    title, rows = P.title_of(done.stdout), P.overlay_rows(done.stdout)
    daily, retro = CORE["ceremonies"]
    progress = f"{sum(one['answered'] for one in daily['progress'])}/{len(daily['progress'])}"
    if (done.returncode == 0 and title and "core-review" in title[0]
            and _row(rows, daily["name"], progress, daily["next_due"]) and _row(rows, retro["name"], retro["after"])
            and _row(rows, daily["name"], daily["when"]["kind"], daily["when"]["at"])):
        held("the overlay of the ceremonies, `c`", f"titled {title[0]!r}: {daily['name']} {progress} next "
             f"{daily['next_due']}, {retro['name']} after {retro['after']}, the rhythm of {daily['name']}")
    else:
        failures.append(f"  ✗ overlay c                   rc={done.returncode} {title} {rows} {done.stderr[-300:]!r}")

    # --- a team never started ---------------------------------------------------------------------
    done = house.render("--render", "teams", *SIZE, "--press", "down,down")
    command = T.preview_in(done, "./pp team start")
    if (done.returncode == 0 and command.startswith("./pp team start veille --message")
            and not any(one["path"] in done.stdout or one["run"] in done.stdout for one in CORE["members"])
            and "veille" in P.status_of(done.stdout)):
        held("a team never started says so", f"{command!r} shown, no member")
    else:
        failures.append(f"  ✗ not started                 rc={done.returncode} {command!r} {done.stdout[-1200:]!r} "
                        f"{done.stderr[-300:]!r}")

    # --- the responses of a member, `a` -----------------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE, "--press", "tab,down,a")
    title, rows = P.title_of(done.stdout), P.overlay_rows(done.stdout)
    mine = [one for one in T.RESPONSES if one["member"] == REVIEWER["member"]]
    others = [one for one in T.RESPONSES if one["member"] != REVIEWER["member"]]
    if (done.returncode == 0 and title and "core-review" in title[0] and REVIEWER["member"] in title[0]
            and str(len(mine)) in title[0]
            and f"responses core-review {REVIEWER['member']}" in house.journal_lines()
            and all(_row(rows, f"#{one['id']}", one["task"]) and _row(rows, one["response"]) for one in mine)
            and not any(f"#{one['id']}" in done.stdout or one["response"] in done.stdout for one in others)
            and house.gestures() == []):
        held("a shows a member's responses", f"{', '.join('#' + str(one['id']) + ' on ' + one['task'] for one in mine)}, "
             "whole; nothing of another member; nothing written")
    else:
        failures.append(f"  ✗ responses                   rc={done.returncode} {house.journal_lines()} {title} {rows} "
                        f"{done.stderr[-400:]!r}")

    # --- nothing of `team` before the tab is shown --------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "80x24", "--press", "2")
    if done.returncode == 0 and "agents/reviewer" in done.stdout and house.journal_lines() == []:
        held("nothing of team is read before the tab", "the dialogue, then the agents: the witness's journal empty")
    else:
        failures.append(f"  ✗ read before the tab         rc={done.returncode} {house.journal_lines()} "
                        f"{done.stdout[-800:]!r}")

    # --- the run of a member, marked in the overlay of the runs -------------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "160x40", "--press", "2,enter")
    rows = P.overlay_rows(done.stdout)
    member, other = T.cells_of(_row(rows, REVIEWER["run"])), T.cells_of(_row(rows, "a00007"))
    journal = house.journal_lines()
    if (done.returncode == 0 and len(member) > 2 and "core-review" in member[1] and REVIEWER["member"] in member[1]
            and member[2] == REVIEWER["run"] and len(other) > 2 and other[2] == "a00007"
            and not re.search(r"\w", other[1]) and "core-review" not in " ".join(other)
            and {"status", "status core-review", "status ops"} <= set(journal) and "status veille" not in journal):
        held("the run of a member is marked", f"{REVIEWER['run']} marked {member[1]!r}, a00007 marked {other[1]!r}; "
             "veille never read")
    else:
        failures.append(f"  ✗ marked                      rc={done.returncode} {member} {other} {journal} {rows}")

    # --- enter on that run: a read-only tab, its kept flow replayed ---------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "160x40", "--press", "2,enter,enter")
    chat, mark = house.chat_lines(), P.palette_constant("READ_ONLY")
    banner = _row(done.stdout.split("\n"), mark)
    tab = P.Post.tabs_of(done.stdout)
    if (done.returncode == 0 and "core-review" in tab and REVIEWER["member"] in tab
            and "core-review" in banner and REVIEWER["member"] in banner and "LGTM" in done.stdout
            and f"flow {REVIEWER['path']} {REVIEWER['run']} --json" in chat
            and not any(one.startswith("open") for one in chat)):
        held("enter on a run of a team opens it read only", f"the tab {tab.strip()!r} marked {mark}, its kept flow "
             "replayed (LGTM); no agent chat")
    else:
        failures.append(f"  ✗ opened read only            rc={done.returncode} {tab!r} {banner!r} {chat} "
                        f"{done.stdout[-1500:]!r}")

    # --- a house without a team -----------------------------------------------------------------------
    house.use(T.script(badges=[]))
    house.clear_journal()
    done = house.render("--render", "teams", *SIZE)
    head = _head(done.stdout)
    if (done.returncode == 0 and head and house.journal_lines() == ["status"]
            and not any(one["team"] in done.stdout for one in T.BADGES)):
        held("a house without a team says how to declare one", "no team in the menu nor the head; the list alone read")
    else:
        failures.append(f"  ✗ no team                     rc={done.returncode} {house.journal_lines()} {head} "
                        f"{done.stdout[-800:]!r} {done.stderr[-300:]!r}")
    return 0
