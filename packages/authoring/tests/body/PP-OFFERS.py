"""packages/authoring/procs/PP-OFFERS.md -- the text it keeps: the harness's skills one call
away, both placements, never copied."""
from __future__ import annotations

from conductor import render
from tests.harness import SOURCE, kept_document


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
    return 0
