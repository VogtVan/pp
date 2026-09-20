"""packages/authoring/procs/PP-MEMBER.md -- the text it keeps: the door's brief -- two shapes, the
encyclopedic ground, the house constraints; and that it reaches the agent when the door
opens on the shared environment."""
from __future__ import annotations

from conductor import render
from tests.harness import SOURCE, kept_document


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
    return 0
