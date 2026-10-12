"""bases/kit/user/MEMBER.md -- the kit's member, placed at the instance root by the install:
it opens doors, armed by uncommenting a line."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "bases" / "kit", "MEMBER").read_text(encoding="utf-8")
    assert "uncomment a line to arm" in text
    bench.held("the kit's member arms by a comment", "uncomment a line to arm")
    return 0
