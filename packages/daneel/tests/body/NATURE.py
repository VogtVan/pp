"""packages/daneel/system/NATURE.md -- the nature the package gives its member."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "daneel" / "system", "NATURE").read_text(encoding="utf-8")
    assert "calm and courteous" in text
    bench.held("the nature is calm and courteous", "as the package states it")
    return 0
