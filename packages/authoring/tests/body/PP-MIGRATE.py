"""packages/authoring/procs/PP-MIGRATE.md -- the text it keeps: the other doors it orients to."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document, serve_tags


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-MIGRATE").read_text(encoding="utf-8")
    assert "→ PP-MEMBER" in text
    bench.held("PP-MIGRATE orients to the other doors", "→ PP-MEMBER among them")

    sheet = kept_document(SOURCE / "packages" / "authoring", "PP_CHEATSHEET").read_text(encoding="utf-8").splitlines()
    tags = serve_tags(kept_document(SOURCE / "packages" / "authoring", "PP-MIGRATE"))
    assert tags, "the door reads the sheet by parts"
    for name, start, end in tags:
        assert name == "PP_CHEATSHEET.md", name
        assert any(line.lstrip().startswith(start) for line in sheet), start
        assert not end or any(line.lstrip().startswith(end) for line in sheet), end
    bench.held("the door's tags open a line of the sheet", " · ".join(f"{s}..{e}" for _, s, e in tags))
    return 0
