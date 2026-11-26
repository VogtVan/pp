"""Scenario `ui-team-tick-apart` -- `T` on the Teams tab plays the team's tick APART from the post, never under the
bound of a verb, on the bench's `pp-team` witness (cut from `ui-team-guarded`, rule 10):
- a tick that tarries past the bound of a verb (`PP_UI_TIMEOUT`) runs to its end -- the witness says `ended` once it
  comes --, and the remedy line says no `verb-timeout`
- a tick that refuses (rc 2, its refusal on stderr) has its refusal said on the remedy line once the post sees it end
"""
from __future__ import annotations

import time

from tests.harness import support

T = support(__file__, "teams")

SIZE = ("--size", "130x40")
TICK = "team tick core-review"
BOUND, TARRY = 2, 4         # the bound of a verb at the post, the seconds a slow tick takes
REFUSAL = "pp-team: team-unknown -- core-review is declared nowhere."   # what the witness's tick says on stderr


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-tick-apart", T.script(answers={"tick": {"sleep": TARRY}}))
    house.env = {**house.env, "PP_UI_TIMEOUT": str(BOUND)}

    slow = house.render("--render", "teams", *SIZE, "--press", "T,ctrl+enter")
    deadline = time.monotonic() + TARRY + 4
    while f"ended {TICK}" not in house.journal_lines() and time.monotonic() < deadline:
        time.sleep(0.2)
    remedy = T.remedy_of(slow)
    if (slow.returncode == 0 and TICK in house.journal_lines() and f"ended {TICK}" in house.journal_lines()
            and "verb-timeout" not in remedy):
        held("T ticks apart, never under a verb's bound", f"a tick of {TARRY}s under a bound of {BOUND}s ran to its "
             f"end; remedy {remedy[:60]!r}")
    else:
        failures.append(f"  ✗ tick apart                  rc={slow.returncode} {house.journal_lines()} {remedy!r}")

    house.use(T.script(answers={"tick": {"rc": 2, "err": REFUSAL + "\n"}}))
    house.clear_journal()
    refused = house.render("--render", "teams", *SIZE, "--press", "T,ctrl+enter")
    said = T.remedy_of(refused)
    if refused.returncode == 0 and TICK in house.journal_lines() and "team-unknown" in said.split():
        held("a tick apart that refuses is said", f"rc 2 on stderr: the remedy line {said[:70]!r}")
    else:
        failures.append(f"  ✗ tick refused               rc={refused.returncode} {house.journal_lines()} {said!r}")
    return 0
