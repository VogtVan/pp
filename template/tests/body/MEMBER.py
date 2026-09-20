"""template/instance/MEMBER.md -- the member template's text: it opens doors, armed
by uncommenting a line."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "template", "MEMBER").read_text(encoding="utf-8")
    assert "uncomment a line to arm" in text
    bench.held("the member template arms by a comment", "uncomment a line to arm")
    return 0
