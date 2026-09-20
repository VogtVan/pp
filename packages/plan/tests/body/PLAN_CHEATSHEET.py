"""packages/plan/refs/PLAN_CHEATSHEET.md -- the plan's doctrine on one page, served at
the turn by the plan overlay's serve row: the three levels, the frequent steps with
their mount, the laws posed last, the serve rows that live with the batch, the
plan's next move carried and never played."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "plan" / "refs", "PLAN_CHEATSHEET").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    for phrase in ("THREE levels deep, always",
                   "The depth is fixed, the width varies",
                   "The frequent steps",
                   "The laws come LAST, at every level",
                   "The serve rows of a batch LIVE with it",
                   "NEXT MOVE",
                   "never played in the turn",
                   "An ADDRESS is bare names",
                   "PREPARED",
                   "`repair` mends what is mechanical",
                   "never the operator's world"):                     # the proof's path, at the Tests row and the GO step
        assert phrase in flat, phrase
    assert "two or three" not in flat, "a plan has three levels, always"
    overlay = kept_document(SOURCE / "packages" / "plan", "TURN").read_text(encoding="utf-8")
    assert "+PLAN_CHEATSHEET.md" in overlay, "the overlay's serve row hands the doctrine to the turn"
    bench.held("the plan cheat sheet says the doctrine and the overlay serves it",
               "three levels always, the frequent steps with their mount, the laws last, the serve "
               "rows alive, the next move carried -- served by `+PLAN_CHEATSHEET.md` on the TURN overlay")
    return 0
