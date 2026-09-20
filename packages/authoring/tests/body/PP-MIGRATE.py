"""packages/authoring/procs/PP-MIGRATE.md -- the text it keeps: the other doors it orients to."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-MIGRATE").read_text(encoding="utf-8")
    assert "→ PP-MEMBER" in text
    bench.held("PP-MIGRATE orients to the other doors", "→ PP-MEMBER among them")
    return 0
