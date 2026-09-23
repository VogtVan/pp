"""packages/authoring/procs/PP-OFFERS.md -- the text it keeps: the harness's skills one call
away, both placements, never copied."""
from __future__ import annotations

from conductor import render
from tests.harness import SOURCE, kept_document, serve_tags


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-OFFERS").read_text(encoding="utf-8")
    for phrase in ("one call away", "Both placements", "offered-not-conductible", "Never COPY"):
        assert phrase in text, phrase
    bench.held("PP-OFFERS teaches the offer", "one call away · both placements · offered-not-conductible · never copied")

    conductor = bench.env("body-pp-offers", packages=("authoring",)).conductor()
    conductor.start(conductor.boot("BOOT.md"))
    conductor.submit("")
    opened = render(conductor.play("PP-OFFERS"))
    conductor.forget()
    assert "one call away" in opened and "Never COPY" in opened
    bench.held("the brief reaches the open door", "the phrases reach the door's block")

    sheet = kept_document(SOURCE / "packages" / "authoring", "PP_CHEATSHEET").read_text(encoding="utf-8").splitlines()
    tags = serve_tags(kept_document(SOURCE / "packages" / "authoring", "PP-OFFERS"))
    assert tags, "the door reads the sheet by parts"
    for name, start, end in tags:
        assert name == "PP_CHEATSHEET.md", name
        assert any(line.lstrip().startswith(start) for line in sheet), start
        assert not end or any(line.lstrip().startswith(end) for line in sheet), end
    bench.held("the door's tags open a line of the sheet", " · ".join(f"{s}..{e}" for _, s, e in tags))
    return 0
