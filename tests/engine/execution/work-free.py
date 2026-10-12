"""Scenario `work-free` -- 2 case(s):
- le-travail-est-libre: WORK frees the ask's step -- the turn's own step, no sub-frame
- the card frees the work: freedom within the step, the exchange ends at FINAL or END alone
(the kit's unitary INFER -- CAPABILITIES asks ONE table -- lives at
`bases/kit/tests/engine/seeded-member.py`)
"""
from __future__ import annotations

from pathlib import Path
from conductor import Conductor, render, discovery
from tests.harness import SOURCE, body_of, kept_document, reaches


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- le-travail-est-libre: WORK frees the ask's step -------------------------------
    free_made = bench.env("freews").made
    free_engine = free_made / ".sys" / "engine" / "pp.py"
    free_member = discovery.instance_member(free_engine)

    def free_c() -> Conductor:
        return Conductor(free_member, free_engine, "t")

    free_work = free_c().resume(free_c().boot("BOOT.md"))
    if (free_work.document == "TURN" and free_work.instruction.keyword == "WORK"
            and "PROVEN_INFERENCE" not in render(free_work)):
        held("the turn inlines WORK", "no sub-frame: the ask's step is TURN's own; the stack teaches WORK")
    else:
        failures.append(f"  ✗ turn inlines WORK           {free_work.document!r} {free_work.instruction!r}")
    free_card = (free_made / ".sys" / "engine" / "refs" / "PP.md").read_text(encoding="utf-8")
    free_marble = (free_made / ".sys" / "system.md").read_text(encoding="utf-8")
    if (free_card == kept_document(SOURCE / "engine", "PP").read_text(encoding="utf-8")
            and "closing the step is not closing the exchange" not in free_card
            and "you execute that one" not in free_card
            and reaches(free_marble, body_of(kept_document(SOURCE / "engine", "SYSTEM.COMMON")))
            and "after your result" not in free_marble):

        held("the card frees the work", "freedom within the step; the exchange ends at FINAL or END alone -- the atomicity sentence is dead")
    else:
        failures.append("  ✗ card freedom                the doctrine did not turn")
    # the OPERATIONS-span case migrated RED to the continuity phase (KPS21, batch
    # la-purete-du-kit): the document left the kit with its body test.

    # the consignation-order case migrated RED to the continuity phase (KPS21, batch
    # le-turn-sans-opinion): the kit turn names no CALL -- OPERATIONS' place behind the
    # work is provable once the package attaches it at turn.end.
    return 0
