"""packages/authoring/procs/PP-RULES.md -- the text it keeps: a rule is imperative, meta and
provable, never invented, placed on the operator's GO alone."""
from __future__ import annotations

from conductor import render
from tests.harness import SOURCE, kept_document, serve_tags


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-RULES").read_text(encoding="utf-8")
    for phrase in ("imperative, meta and provable", "on the operator's GO alone", "never invented", "rule against the bias"):
        assert phrase in text, phrase
    bench.held("PP-RULES says what a rule is", "imperative, meta and provable · rules against the biases · never invented, GO alone")
    for phrase in ("Write a constraint POSITIVE", "It lives in ONE of two sections", "names its rendering coverage",
                   "the GO that NAMES its lot", "a GO reads at its NARROWEST", "the STOP when the architecture surprises",
                   "plan › phase › lot", "write only what EVERY lot below holds", "PROOF MODE"):
        assert phrase in text, phrase
    bench.held("PP-RULES teaches the plan's acquis", "positive · two sections · the coverage a production law names · three lived rules against a bias · the scale entire")

    conductor = bench.env("body-pp-rules", packages=("authoring",)).conductor()
    conductor.start(conductor.boot("BOOT.md"))
    conductor.submit("")
    opened = render(conductor.play("PP-RULES"))
    conductor.forget()
    assert "imperative, meta and provable" in opened
    bench.held("the brief reaches the open door", "the phrase reaches the door's block")

    sheet = kept_document(SOURCE / "packages" / "authoring", "PP_CHEATSHEET").read_text(encoding="utf-8").splitlines()
    tags = serve_tags(kept_document(SOURCE / "packages" / "authoring", "PP-RULES"))
    assert tags, "the door reads the sheet by parts"
    for name, start, end in tags:
        assert name == "PP_CHEATSHEET.md", name
        assert any(line.lstrip().startswith(start) for line in sheet), start
        assert not end or any(line.lstrip().startswith(end) for line in sheet), end
    bench.held("the door's tags open a line of the sheet", " · ".join(f"{s}..{e}" for _, s, e in tags))
    return 0
