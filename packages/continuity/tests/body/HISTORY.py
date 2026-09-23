"""packages/continuity/procs/HISTORY.md -- the text it keeps: the weekly digest's promise."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "continuity", "HISTORY").read_text(encoding="utf-8")
    assert "week at a glance" in text
    bench.held("HISTORY gives the week at a glance", "the digest's promise, in its text")
    return 0
