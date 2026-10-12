"""packages/plan/overlays/TURN.md -- the plan mode's text: the overlay every turn
carries under the plan package."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "plan", "TURN").read_text(encoding="utf-8")
    for phrase in ("The plan mode", "carries the SYNTHESIS of", "A FRAMING choice owes no synthesis"):
        assert phrase in text, phrase
    bench.held("the overlay teaches the plan mode", "the mode, the synthesis a GO carries, a framing owes none")
    return 0
