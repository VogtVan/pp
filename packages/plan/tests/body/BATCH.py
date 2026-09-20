"""packages/plan/procs/BATCH.md -- the batch method's text: code served in touched
and dependent sections, the order as the convention, re-aligned at the landing."""
from __future__ import annotations

from tests.harness import SOURCE, kept_document


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "plan" / "procs", "BATCH").read_text(encoding="utf-8")
    for phrase in ("TOUCHED", "DEPENDENT", "the ORDER is the convention", "a line range is a CONVENIENCE that\n   scopes, never a requirement", "re-aligns the serve rows"):
        assert phrase in text, phrase
    flat = " ".join(text.split())
    for phrase in ("A law you WRITE says its SECTION",
                   "A plan document is a BLUEPRINT, not a history manual",
                   "never on the operator's world",                    # BA6: the verification's path
                   "a tool's default file under the home is not a bench"):
        assert phrase in flat, phrase
    bench.held("BATCH serves code in sections", "touched then dependent, the order a convention, re-aligned at the landing; "
               "a verification plays on a disposable path, never the operator's world (BA6)")
    return 0
