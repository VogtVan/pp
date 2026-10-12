"""packages/authoring/procs/PP-MEMBER.md -- the text it keeps: the door's brief -- two shapes, the
encyclopedic ground, the house constraints; and that it reaches the agent when the door
opens on the shared environment."""
from __future__ import annotations

from conductor import render
from tests.harness import SOURCE, kept_document, serve_tags


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-MEMBER").read_text(encoding="utf-8")
    for phrase in ("two shapes", "encyclopedic ground", "Write the ground", "House constraints"):
        assert phrase in text, phrase
    bench.held("PP-MEMBER briefs the two shapes and the ground", "two shapes · encyclopedic ground · Write the ground · house constraints")

    conductor = bench.env("body-pp-member", packages=("authoring",)).conductor()
    conductor.start(conductor.boot("BOOT.md"))
    conductor.submit("")
    opened = render(conductor.play("PP-MEMBER"))
    conductor.forget()
    assert "two shapes" in opened and "encyclopedic ground" in opened
    bench.held("the brief reaches the open door", "the phrases reach the door's block on the shared environment")

    sheet = kept_document(SOURCE / "packages" / "authoring", "PP_CHEATSHEET").read_text(encoding="utf-8").splitlines()
    tags = serve_tags(kept_document(SOURCE / "packages" / "authoring", "PP-MEMBER"))
    assert tags, "the door reads the sheet by parts"
    for name, start, end in tags:
        assert name == "PP_CHEATSHEET.md", name
        assert any(line.lstrip().startswith(start) for line in sheet), start
        assert not end or any(line.lstrip().startswith(end) for line in sheet), end
    bench.held("the door's tags open a line of the sheet", " · ".join(f"{s}..{e}" for _, s, e in tags))
    return 0
