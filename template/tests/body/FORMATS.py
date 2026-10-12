"""template/instance/FORMATS.md -- the instance's own formats, as seeded."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "template", "FORMATS").read_text(encoding="utf-8")
    assert "theme  stdin" in text and "brief  inline" in text
    bench.held("the seeded formats stand", "theme on stdin, brief inline")
    return 0
