"""Scenario `ui-team-responses` -- `a` on a member of the Teams tab (plan ui, batch le-membre-inspecte), on
the bench's `pp-team` witness: the responses of `reviewer` (`team responses core-review --json --agent
reviewer`) in an overlay, each with its id, its task and its whole text; none of `lead`'s; nothing written.
"""
from __future__ import annotations

from tests.harness import support

T = support(__file__, "teams")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = T.Teams(bench, "ui-team-responses")
    house.clear_journal()
    done = house.render("--render", "teams", "--size", "140x44", "--press", "tab,down,a")
    text = done.stdout
    if (done.returncode == 0 and "responses core-review reviewer" in house.journal_lines()
            and "#40" in text and "#49" in text and "the daily: nothing to say" in text and "LGTM" in text
            and "T2" in text and "lead asks" not in text and house.gestures() == []):
        held("a shows a member's responses", "#40 on T2 and #49 on T3, whole; nothing of lead; nothing written")
    else:
        failures.append(f"  ✗ responses                   rc={done.returncode} {house.journal_lines()} "
                        f"{text[-1400:]!r} {done.stderr[-400:]!r}")
    return 0
