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
                   "A plan document is a BLUEPRINT, not history",
                   # the convergence the phase RECOMMENDS (la-politique-de-test, 2026-10-06)
                   "not to close before the test suite of its plan's component and of the components that depend on it is green",
                   "its last batch runs that suite once"):
        assert phrase in flat, phrase
    # the project's whole suite is the plan's end, not the phase's (2026-10-06)
    assert "project's whole test suite" not in flat, "a phase converges its component, the plan the project"
    bench.held("PHASE serves references, never code",
               "the phase's rows ground the level; PH5 says when a law of the level exists, "
               "and the clause that contradicted it is gone")
    return 0
