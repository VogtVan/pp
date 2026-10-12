"""packages/steering/overlays/TURN.md -- the steering package's overlay on the kit's TURN: the
keeper offered at the work step, the initiatives managed in the steps dedicated to them, and the
vector `steering-thread:<thread id>` whose ids arrive at the session's start or in the context."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "steering", "TURN").read_text(encoding="utf-8")
    front = text.split("---")[1]
    raw_body = text.split("---", 2)[2]
    body = " ".join(raw_body.split())
    assert "+pp-steering" in front, "the overlay offers the keeper at the turn"
    for phrase in ("organises the operator's initiatives into threads and steps of work",
                   "Manage these initiatives proactively, in the steps dedicated to them",
                   "The vector `steering-thread:<thread id>`",
                   "The family `steering-thread` (id `<member>.f.<n>`)",
                   "carries the work threads to the client packages",
                   "The ids are available at the start of the session, or in the context"):
        assert phrase in body, phrase
    for absent in ("status --all", "the front shows none", "consults any guard", "Verification succeeds",
                   "NEXT states how", "reads and changes the work threads"):
        assert absent not in body, absent
    former = "<member>-" + "<n>"                 # the id form before the two dictionaries, spelled apart
    assert former not in body, "the former id form must not survive in a served text"
    bench.held("the overlay says the initiatives and the vector",
               f"`+pp-steering` offered; the initiatives managed proactively; the family `steering-thread` "
               f"and where its ids arrive -- no `status --all`, no guard, no verification ({len(raw_body)} c)")
    return 0
