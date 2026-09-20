"""packages/daneel/system/LAWS.md -- the Three Laws, as the package states them."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "daneel", "LAWS").read_text(encoding="utf-8")
    assert "may not injure a human being" in text
    bench.held("the first law stands", "may not injure a human being")
    return 0
