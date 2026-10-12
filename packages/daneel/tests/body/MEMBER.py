"""packages/daneel/user/MEMBER.md -- the member the package seeds: its own law D1."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "daneel" / "user", "MEMBER").read_text(encoding="utf-8")
    assert "D1  the Three Laws govern" in text and "calm and courteous" in text
    bench.held("the seeded member carries D1", "the Three Laws govern, calm and courteous")
    return 0
