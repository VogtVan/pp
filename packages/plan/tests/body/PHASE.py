"""packages/plan/procs/PHASE.md -- the phase method's text: references served, never code."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "plan" / "procs", "PHASE").read_text(encoding="utf-8")
    assert "REFERENCES" in text and "never code" in text
    flat = " ".join(text.split())
    assert "PH5 a phase law MAY exist" in flat, "the level rule lives at the package"
    assert "SHOULD" not in text and "left without any says why" not in flat, (
        "a clause asking why the normal case happened cannot cohabit with the rule")
    for phrase in ("A written law declares its SECTION",
                   "A plan document is a BLUEPRINT, not history"):
        assert phrase in flat, phrase
    bench.held("PHASE serves references, never code",
               "the phase's rows ground the level; PH5 says when a law of the level exists, "
               "and the clause that contradicted it is gone")
    return 0
