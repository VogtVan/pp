"""packages/authoring/procs/PP-DESIGN.md -- the text it keeps: the author's door as a ROLE -- its
four steps in order (read the ask against the theory, choose the mechanism at the catalog, propose
the complete document, install on the GO and prove it played), what it is not; its laws PD1-PD8 and
PD11 with PD9 and PD10 gone; the catalog and the theory served whole, never retold."""
from __future__ import annotations

import re

from tests.harness import SOURCE, kept_document

STEPS = ("1. **Read the ask against the theory.**", "2. **Choose the mechanism at the catalog.**",
         "3. **Propose the complete document.**", "4. **Install on the operator's GO alone, and prove it played.**")
ROLE = ("direct, induced or background", "the seven questions", "describe the document by its forms",
        "the lighter wins", "`section set`", "`section constrain`", "`section serve`",
        "A public name wears its package's name", "`./pp -build`", "`./pp <key> -peek`", "a throwaway instance")
GONE = ("## The rules of composition", "has LINEAGE", "agent reflex", "## The catalog", "### ")
LAWS = ("PD1 ", "PD2 ", "PD3 ", "PD4 ", "PD5 ", "PD6 ", "PD7 ", "PD8 ", "PD11 ")
RETIRED = ("PD9 ", "PD10 ")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-DESIGN").read_text(encoding="utf-8")
    front, body = text.split("\n---\n", 1)
    assert all(step in body for step in STEPS)
    assert [body.index(step) for step in STEPS] == sorted(body.index(step) for step in STEPS)
    bench.held("PP-DESIGN says the four steps of the author's role, in order", "read · choose · propose · install and prove")
    assert all(phrase in body for phrase in ROLE)
    bench.held("each step names what it works with", "the origin of the work, the checklist, the forms, the cost, the writer's verbs, the naming, the build and the peek")
    assert not any(gone in body for gone in GONE) and "What this door is not" in body
    bench.held("the door carries no catalog, no rules, no lineage", "the served sheet and CONDUCTION are named for them")
    assert all(re.search(rf"^  {law}", front, re.M) for law in LAWS)
    assert not any(re.search(rf"^  {law}", front, re.M) for law in RETIRED)
    assert re.search(r"^  PD11 .*figure of the catalog.*origin of the work", front, re.M)
    bench.held("the laws frame the role", "PD1-PD8 kept, PD9 and PD10 retired, PD11 names the figure and the origin")
    assert re.search(r"^serve: \|\n  PP_CHEATSHEET\.md\n  CONDUCTION\.md$", front, re.M), "the door serves the catalog and the theory"
    bench.held("the door serves the catalog and the theory whole", "PP_CHEATSHEET.md then CONDUCTION.md ride its serve rows")
    assert "prove:` arms" not in text and "IVK" not in text and "The author's door" in front
    bench.held("the description says the role, the retired vocabulary is gone", "no prove: arming, no IVK")
    return 0
