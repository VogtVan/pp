"""packages/daneel/system/SYSTEM.COMMON.md -- the package's section of the marble: the
Three Laws, then the nature it gives its member, in both conduction modes."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "daneel", "SYSTEM.COMMON").read_text(encoding="utf-8")
    assert "may not injure a human being" in text
    bench.held("the first law stands", "may not injure a human being")
    assert "calm and courteous" in text
    assert text.index("# The Laws") < text.index("# Nature")
    bench.held("the nature is calm and courteous", "as the package states it, after the Laws")
    return 0
