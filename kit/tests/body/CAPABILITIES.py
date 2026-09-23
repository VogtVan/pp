"""kit/procs/CAPABILITIES.md -- the text it keeps: the boot's presentation step."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "kit", "CAPABILITIES").read_text(encoding="utf-8")
    assert "present yourself" in text and "say nothing else" in text
    bench.held("CAPABILITIES asks the presentation and nothing else", "present yourself · say nothing else")
    return 0
