"""packages/authoring/refs/CONDUCTION.md -- the text it keeps: WHEN an author chooses each form --
what conduction carries, where work comes from, where it is played -- and the true extracts of
the models it cites."""
from __future__ import annotations

import re

from tests.harness import SOURCE, kept_document

KNOWLEDGE = ("## The five channels", "| the standing orders | the protocol |", "| MEMBER and its readings |",
             "| an overlay of TURN | a package's reflex and its offers |", "| a document at a socket |",
             "| a door, or a mount behind a skill call |",
             "**Reach** — does it arrive before the ask", "**Mass** — the characters it costs",
             "**Latency** — the calls the agent makes",
             "The reflex comes before the ask, and it is small",
             "The know-how comes behind the door the reflex opens, and it is large")
WORK = ("**Direct** work is what the operator's message asks for",
        "**Induced** work is what the direct work makes due",
        "**Background** work is due on a date or at every turn, whatever the message says",
        "Direct work plays in the turn's `WORK` step",
        "When direct work changes its method",
        "Induced and background work play in a document attached to a socket",
        "Data another document consumes enters by a mount or a payload")
TEST = ("A document that tells the agent to play a skill has a `WORK` step, or lives in the view of one",
        "An `INFER` step produces", "A mounted document serves")
MODELS = (("continuity", "TURN", "overlays"), ("continuity", "OPERATIONS", "procs"),
          ("improvement", "IMPROVE", "procs"), ("continuity", "RECALL", "procs"))


def scenario(bench) -> int:
    path = kept_document(SOURCE / "packages" / "authoring", "CONDUCTION")
    text = path.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    for phrase in KNOWLEDGE + WORK + TEST:
        assert phrase in flat, phrase
    bench.held("CONDUCTION says both halves", "the five channels, the three measures and the two laws of "
               "knowledge; the three origins of work, each defined where it appears; the four placement "
               "rules; the test of a document")

    assert len(text) <= 6000, len(text)
    for mechanism in ("overlay-carries-proc", "attach-and-mount", "::mount", "requires topology"):
        assert mechanism not in text, mechanism
    assert "PP-DESIGN" in text
    bench.held("CONDUCTION says when, never how", f"{len(text)} c under 6 000; no figure's mechanism is "
               "retold -- the guide is named for it")

    # every cited model is a TRUE extract: each indented line under a model stands in its source file
    quoted = 0
    for package, name, space in MODELS:
        source = (SOURCE / "packages" / package / space / f"{name}.md").read_text(encoding="utf-8")
        cited = re.search(rf"`{package}/{space}/{name}\.md`.*?\n\n((?:    .*\n)+)", text)
        assert cited, (package, name)
        for line in cited.group(1).splitlines():
            assert line.strip() in source, (name, line)
            quoted += 1
    bench.held("the cited models are true", f"{quoted} quoted lines of {len(MODELS)} models each found in "
               "its source file, read at run time")

    for absent in ("sw7", "procedural-prompting", ".pp/plans", "/home/"):
        assert absent not in text, absent
    bench.held("CONDUCTION names no member", "no instance, no member, no path outside the product")
    return 0
