"""Scenario `ui-team-member` -- the run of a member, read in a tab of the dialogue (plan ui, batches
le-membre-inspecte and le-suivi-des-taches), on the bench's witnesses: `pp-team` replays the team's watch while
`reviewer` and `lead` each play a wake-up, `pp-chat` the KEPT FLOW of `agents/reviewer` -- two exchanges, then the
third read again by its exchange at a step of the wake-up and at its end:
- `i` on `reviewer` opens the tab `core-review/reviewer`: its two exchanges replayed as lived turns -- the lines of
  conduction (`◇`), of a call (`⚙ … WebSearch`) and of thought (`∴`) --, then the wake-up live: its message, its
  call, its answer and its verdict; nothing of `lead` enters it; no exchanges read
- a run without a kept flow (`lead`'s) is replayed from its exchanges: `history #1`
- read only: a banner, no message line; no `agent chat` launched (no `open` at the witness of `agent`),
  no message, no gesture of `team`
- `x` closes the tab: the dialogue is empty again, no witness left alive
- a member without a run says so on the remedy line, and nothing is read
"""
from __future__ import annotations

import copy

from tests.harness import support

T = support(__file__, "teams")

OPEN = "3,tab,down,i,wait:team:wake-ended"      # the end of reviewer's wake-up, its exchange read again


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-member", T.script(watch={"core-review": T.MEMBER_WATCH}))

    # --- the tab of the member: its history, then its wake-up live -------------------------------------
    house.clear_journal()
    done = house.render("--render", "dialogue", "--size", "140x90", "--press", OPEN)   # the three exchanges in view
    text = done.stdout
    chat = house.chat_lines()
    flows = [one for one in chat if one.startswith("flow agents/reviewer a01389")]
    if (done.returncode == 0 and "core-review/reviewer" in text and "read only" in text
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
    if (done.returncode == 0 and "no conversation open" in done.stdout and not house.alive()
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

    return 0
