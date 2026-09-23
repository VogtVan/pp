"""packages/plan/procs/PLAN.md -- the plan method's text: references served, never code."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "plan" / "procs", "PLAN").read_text(encoding="utf-8")
    assert "REFERENCES" in text and "never code" in text
    flat = " ".join(text.split())
    assert "PN12 a plan law MAY exist" in flat, "the level rule lives at the package"
    assert "SHOULD" not in text, "a SHOULD cannot cohabit with a MAY that says when"
    assert "MUST on a batch, MAY on a plan or phase" in flat
    for phrase in ("A written law declares its SECTION",
                   "A plan document is a BLUEPRINT, not history",
                   "PN14 the body of a plan document is written by the script alone",
                   "pp-plan section <slug> Context",
                   "PREPARES the phases"):
        assert phrase in flat, phrase
    bench.held("PLAN serves references, never code",
               "the plan's rows ground the level; PN12 says when a law of the level exists, "
               "a written law says its section, the document is a blueprint, its body is the "
               "script's (PN14) and the phases are prepared, not created")
    return 0
