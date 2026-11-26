"""Scenario `ui-team-member` -- the run of a member, read in a tab of the dialogue (plan ui, batches
le-membre-inspecte and le-suivi-des-taches), on the bench's witnesses: `pp-team` replays the team's watch while
`reviewer` and `lead` each play a wake-up, `pp-chat` the KEPT FLOW of `agents/reviewer` -- two exchanges, then the
third read again by its exchange at a step of the wake-up and at its end:
- `i` on `reviewer` opens the tab `core-review/reviewer`: its two exchanges replayed as lived turns -- the lines of
  conduction (`◇`), of a call (`⚙ … WebSearch`) and of thought (`∴`) --, then the wake-up live: its message, its
  call, its answer and its verdict; nothing of `lead` enters it; no exchanges read
- a run without a kept flow (`lead`'s) is replayed from its exchanges: `history #1`
- the mouse on the members (batch les-gestes-du-membre, s.1519): a click on the member already under the cursor
  selects it and opens nothing; a double click on another member opens its run -- `enter` opens it too, below
- the witness's watch plays the wake-up once the tab subscribed and read its kept flow: a door it did not see within
  its bound (`until-missed`) is said, red (batch les-rouges-ui-sous-charge)
- read only: a banner, no message line; no `agent chat` launched (no `open` at the witness of `agent`),
  no message, no gesture of `team`
- `x` closes the tab: the dialogue is empty again, no witness left alive
- a member without a run says so on the remedy line, and nothing is read
- the column `live` of the members says the activity of a wake-up (batch la-sequence-vivante): `⚙ Read · pp.py` once the
  watch relayed the call, after the block's frame
- one line per OPEN task of a member, each its run (batch les-runs-par-tache-au-poste, s.1402): `reviewer` at T15 and T16
  shows two lines in the order of their birth, each with the run `runs[]` keeps for that task, its state, its ctx and the
  task; `lead`, without an open task, one line; the cursor on the line of T15 puts the band on T15 and draws its
  sequence (`log core-review T15`, never T16's); `enter` there opens the run of T15, `a01389`, not the member's own
"""
from __future__ import annotations

import copy
import re

from tests.harness import support

T = support(__file__, "teams")

OPEN = "3,tab,down,i,wait:team:wake-ended"      # the end of reviewer's wake-up, its exchange read again
MISSED = "until-missed "                         # the witness's watch never saw the line it waited for
MEMBER_Y = 2                                     # the row of the first member in its framed table: the edge, the header


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-member", T.script(watch={"core-review": T.MEMBER_WATCH}))

    # --- the tab of the member: its history, then its wake-up live -------------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "140x90", "--press", OPEN)   # the three exchanges in view
    text = done.stdout
    chat = house.chat_lines()
    flows = [one for one in chat if one.startswith("flow agents/reviewer a01389")]
    missed = [one for one in house.journal_lines() if one.startswith(MISSED)]
    if missed:
        failures.append(f"  ✗ member tab                  the watch's door was not seen: {missed}")
    elif (done.returncode == 0 and "core-review/reviewer" in text and "read only" in text
            and text.count("◇ ") >= 3 and "WebSearch" in text and "∴ " in text and "412 held" in text and "merged" in text
            and "step(s)" in text and "refused" not in text and "lead-only" not in text
            and "parked" in text and not any(one.startswith(("open", "message", "exchanges")) for one in chat)
            and flows.count("flow agents/reviewer a01389 --json") == 1
            and any("--exchange 3" in one for one in flows) and house.gestures() == []):
        held("the run of a member, read in a tab", f"two exchanges replayed from the kept flow ({text.count('◇ ')} ◇, "
             "a ⚙ WebSearch, a ∴), the third live (412 held, merged, parked); nothing of lead; "
             f"{len(flows)} flow reading(s), no exchanges, no agent chat, no message, no gesture")
    else:
        failures.append(f"  ✗ member tab                  rc={done.returncode} {chat} {house.gestures()} "
                        f"{text[-2600:]!r} {done.stderr[-500:]!r}")

    # --- read only: no message line; x closes the tab ----------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "140x44", "--press", OPEN + ",x")
    missed = [one for one in house.journal_lines() if one.startswith(MISSED)]
    if missed:
        failures.append(f"  ✗ close                       the watch's door was not seen: {missed}")
    elif (done.returncode == 0 and "no conversation open" in done.stdout and not house.alive()
            and "message to" not in done.stdout):
        held("x closes the tab of the member", "the dialogue empty again, no witness left alive")
    else:
        failures.append(f"  ✗ close                       rc={done.returncode} alive={house.alive()} "
                        f"{done.stdout[-900:]!r}")

    # --- a run without a kept flow: its exchanges ------------------------------------------------------
    house.use(T.script())
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "140x44", "--press", "3,tab,i")
    chat = house.chat_lines()
    if (done.returncode == 0 and "core-review/lead" in done.stdout and "history #1" in done.stdout
            and "flow agents/lead a77f10 --json" in chat and "exchanges agents/lead a77f10 --json" in chat):
        held("a run without a kept flow is replayed from its exchanges", "core-review/lead, history #1; the flow read "
             "empty, then the exchanges")
    else:
        failures.append(f"  ✗ no flow                     rc={done.returncode} {chat} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- a click selects, a double click opens (s.1519) -------------------------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "140x44", "--press",
                        f"3,tab,down,click:#teams-members:3:{MEMBER_Y + 1},double:#teams-members:3:{MEMBER_Y}")
    flows = [one for one in house.chat_lines() if one.startswith("flow ")]
    if (done.returncode == 0 and flows == ["flow agents/lead a77f10 --json"] and "core-review/lead" in done.stdout
            and "core-review/reviewer" not in done.stdout):
        held("a click selects, a double click opens", f"a click on reviewer under the cursor: nothing read; a double "
             f"click on lead: {flows}")
    else:
        failures.append(f"  ✗ mouse                       rc={done.returncode} {flows} {done.stdout[-1500:]!r} "
                        f"{done.stderr[-400:]!r}")

    # --- a member without a run ------------------------------------------------------------------------
    unborn = copy.deepcopy(T.CORE)
    unborn["members"][1]["run"] = None
    house.use(T.script(states={"core-review": [unborn], "veille": [{"team": "veille", "started": None}]}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "140x44", "--press", "tab,down,i")
    remedy = T.remedy_of(done)
    if (done.returncode == 0 and "reviewer has no run to inspect" in remedy
            and not any(one.startswith("exchanges") for one in house.chat_lines())):
        held("a member without a run says so", remedy)
    else:
        failures.append(f"  ✗ no run                      {remedy!r} {house.chat_lines()} {done.stdout[-700:]!r}")

    # --- the live column says the activity ----------------------------------------------------------
    house.use(T.script(watch={"core-review": [{"sleep": 0.5}, T.STEP, {"sleep": 0.2}, T.ACT_TOOL]}))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "170x44", "--wait", "team:activity")   # the season and ctx columns, the frame's two sides
    row = next((one for one in done.stdout.split("\n") if "reviewer" in one and "agents/reviewer" in one), "")
    frame = T.STEP["stack"].split("▸")[-1].strip()
    if done.returncode == 0 and T.in_order(row, frame, T.ACT_TOOL["name"], T.ACT_TOOL["title"]):
        held("the live column says the activity", f"{row.strip()[-60:]!r}")
    else:
        failures.append(f"  ✗ live column                 rc={done.returncode} {row!r} {done.stdout[-1200:]!r}")

    # --- one line per open task, each its run (s.1402) ------------------------------------------------
    log = {**T.script()["log"], "core-review/T15": T.T15_LOG, "core-review/T16": T.T16_LOG}
    house.use(T.script(states={"core-review": [T.BY_TASK], "veille": [{"team": "veille", "started": None}]}, log=log))
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "170x44")
    rows = T.sides_of(done.stdout)[1]
    mine = [T.cells_of(one) for one in rows if "agents/reviewer" in one]
    lead = [T.cells_of(one) for one in rows if "agents/lead" in one]
    said = [one[3:7] for one in mine if len(one) > 6]
    wanted = [["a01389", "31%", "parked", "T15"], ["a00007", "44%", "running", "T16"]]
    if done.returncode == 0 and said == wanted and len(lead) == 1 and lead[0][3:7] == ["a77f10", "26%", "ended", "2"]:
        held("one line per open task, each its run", f"reviewer: {said}; lead, no open task: one line {lead[0][3:7]}")
    else:
        failures.append(f"  ✗ lines by task               rc={done.returncode} {said} {lead} {done.stdout[-1800:]!r}")

    # --- the cursor on the line of T15: its sequence; enter: its run ----------------------------------
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "160x50", "--press", "3,tab,down")
    reads = [one for one in house.journal_lines() if one.startswith("log core-review T1")]
    if (done.returncode == 0 and re.search(r"\[T15 ", done.stdout) and "which port?" in done.stdout
            and "log core-review T15" in reads and "log core-review T16" not in reads):
        held("the cursor on the line of T15 draws its sequence", f"the band on T15, its ask in the sequence; {reads}")
    else:
        failures.append(f"  ✗ line's sequence             rc={done.returncode} {reads} {done.stdout[-2400:]!r}")
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "140x44", "--press", "3,tab,down,enter")
    flows = [one for one in house.chat_lines() if one.startswith("flow ")]
    if (done.returncode == 0 and "core-review/reviewer" in done.stdout and "flow agents/reviewer a01389 --json" in flows
            and not any("a00007" in one for one in flows)):
        held("enter on the line of T15 opens its run", f"core-review/reviewer read on a01389: {flows}")
    else:
        failures.append(f"  ✗ line's run                  rc={done.returncode} {flows} {done.stdout[-1500:]!r}")
    return 0
