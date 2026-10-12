"""packages/continuity/procs/OPERATIONS.md -- the text it keeps: what deserves the record, the
span the step covers, and when the gesture is playable, worded positively."""
from __future__ import annotations

from tests.harness import SOURCE, body_of, kept_document


def scenario(bench) -> int:
    doc = kept_document(SOURCE / "packages" / "continuity", "OPERATIONS")
    raw = doc.read_text(encoding="utf-8")
    text = " ".join(raw.split())          # a kept phrase is a sentence, never a line of it

    for phrase in ("An operation is a fact worth keeping for a later session",
                   "Each entry stands alone for a reader who was absent",
                   "recording what happened since the last consignation, including this exchange"):
        assert phrase in text, phrase
    bench.held("OPERATIONS spans the last consignation to this exchange",
               "a fact worth a later session deserves the record, and each entry stands alone")

    assert "already behind you" not in text and "never" not in body_of(doc)
    bench.held("OPERATIONS words positively", "the record looks back -- no list of nevers")

    for phrase in ("Consign while the skill is offered",
                   "If nothing qualifies, say so and leave the record as it stands"):
        assert phrase in text, phrase
    assert "retires this offer" not in text
    bench.held("OPERATIONS says when the gesture is playable",
               "the offer is alive while it stands, and a session with nothing to keep "
               "leaves the record as it is")
    return 0
