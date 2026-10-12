"""Scenario `ui-teams` -- the Teams tab reads the teams of the house (plan ui, batches le-volet-des-equipes and
les-deux-onglets), on the bench's `pp-team` witness replaying the faces of `team` for three declared teams,
`core-review` and `ops` started and `veille` never:
- the menu (the wake-ups under way and the questions to the owner the face counts, `-` for a team never started),
  titled with the hour of its reading; the head of the first team -- its budget `spent/cap · reserved · left`, its
  wake-ups against their bound, its net, what waits for the owner counted on one line --; its members, each with
  its agent, its run, how it stands and its tasks; the team on the status line
- the detail of a member (`d`) and the ceremonies (`c`), each in an overlay
- a team never started says so and the command that starts it; a house without a team says how to declare one
- the frame holds at 80x24 and 200x50
- nothing of `team` is read before the tab is shown
"""
from __future__ import annotations

import re

from tests.harness import support

T = support(__file__, "teams")
P = support(__file__, "dialogue")      # the footer's keys, read on any number of lines
HOUR = r"\d\d:\d\d:\d\d"


def _flat(text: str) -> str:
    return " ".join(text.split())


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-teams")

    # --- the menu, the head, the members, the status line ----------------------------------------
    done = house.render("--render", "teams", "--size", "130x34")
    text, flat = done.stdout, _flat(done.stdout)
    status = text.rstrip("\n").split("\n")[-1]
    titles = [name for name in ("Teams", "Members") if re.search(rf"{name} · {HOUR}", text)]
    veille = next((line for line in text.split("\n") if "veille" in line), "")
    reviewer = next((line for line in text.split("\n") if "agents/reviewer" in line), "")
    if (done.returncode == 0 and len(titles) == 2 and "core-review" in text and "ops" in text
            and re.search(r"veille\s+-\s+-", veille)
            and "budget 1.84/2.00 USD · reserved 0.10 · left 0.06 · wakes 7/40" in flat
            and "schedule every 5 min laid" in flat and "for you: 1 question · 1 task done" in flat
            and all(one in reviewer for one in ("reviewer", "a01389", "running", "2"))
            and "cost 1.84 USD" in status and "wakes 7/40" in status):
        held("the teams read whole", f"the menu and the members titled with their hour, `veille` never started (-), "
             f"the head with its budget and 'for you' counted; status {status.strip()[:80]!r}")
    else:
        failures.append(f"  ✗ teams read                  rc={done.returncode} titles={titles} {veille!r} {reviewer!r} "
                        f"{status!r} {text[-1500:]!r} {done.stderr[-400:]!r}")

    # --- the detail of a member, the ceremonies, each in an overlay --------------------------------
    for keys, said, what in (("tab,down,d", ("reviewer · agents/reviewer", "running", "#46 reply from lead on T3"),
                              "a member, `d`"),
                             ("c", ("ceremonies of core-review", "daily", "retro", "every weekday 09:30"),
                              "the ceremonies, `c`")):
        done = house.render("--render", "teams", "--size", "130x34", "--press", keys)
        flat = _flat(done.stdout)
        if done.returncode == 0 and all(one in flat for one in said):
            held(f"the overlay of {what}", f"--press {keys}: {', '.join(said)}")
        else:
            failures.append(f"  ✗ overlay {what:<20} rc={done.returncode} {said} {done.stdout[-1500:]!r} "
                            f"{done.stderr[-300:]!r}")

    # --- a team never started, a house without a team -----------------------------------------------
    done = house.render("--render", "teams", "--size", "130x34", "--press", "down,down")
    flat = _flat(done.stdout)
    if (done.returncode == 0 and "veille · not started" in flat and "./pp team start veille --message" in flat
            and "a01389" not in flat):
        held("a team never started says so", "veille: not started, the command that starts it, no member shown")
    else:
        failures.append(f"  ✗ not started                 rc={done.returncode} {done.stdout[-1200:]!r} "
                        f"{done.stderr[-300:]!r}")
    house.use(T.script(badges=[]))
    done = house.render("--render", "teams", "--size", "130x34")
    if done.returncode == 0 and "no team declared" in _flat(done.stdout) and "teams/<name>/TEAM.md" in done.stdout:
        held("a house without a team says how to declare one", "no team declared: teams/<name>/TEAM.md declares one")
    else:
        failures.append(f"  ✗ no team                     rc={done.returncode} {done.stdout[-800:]!r} "
                        f"{done.stderr[-300:]!r}")
    house.use(T.script())

    # --- the frame holds at two sizes ---------------------------------------------------------------
    for width, height in ((80, 24), (200, 50)):
        done = house.render("--render", "teams", "--size", f"{width}x{height}")
        lines = done.stdout.rstrip("\n").split("\n")
        if (done.returncode == 0 and len(lines) == height and max(len(one) for one in lines) <= width
                and "3·Teams" in lines[1] and "4·Tasks" in lines[1] and "[q] quit" in P.keys_of(done.stdout)
                and re.search(rf"Teams · {HOUR}", done.stdout) and "Members" in done.stdout):
            held(f"the frame holds at {width}x{height}", "header, tabs, the menu and the bands, the footer")
        else:
            failures.append(f"  ✗ frame {width}x{height}            rc={done.returncode} lines={len(lines)} "
                            f"{done.stdout!r} {done.stderr[-300:]!r}")

    # --- nothing of `team` before the tab is shown -------------------------------------------------
    house.clear_journal()
    first = house.render("--render", "dialogue", "--size", "80x24")
    second = house.render("--render", "agents", "--size", "80x24")
    journal = house.journal_lines()
    if first.returncode == 0 and second.returncode == 0 and journal == []:
        held("nothing of team is read before the tab", "a render of dialogue then agents: the witness's journal empty")
    else:
        failures.append(f"  ✗ read before the tab         rc={first.returncode},{second.returncode} {journal}")
    return 0
