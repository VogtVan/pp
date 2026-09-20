"""packages/authoring/refs/PP_CHEATSHEET.md -- the sheet's examples, kept as written: they PLAY
through the bench, so their wording is a contract."""
from __future__ import annotations

import re

from tests.harness import SOURCE, kept_document

EXAMPLES = ("The pp cheatsheet", "your name is Compass", "you must behave like this: terse, dry humor",
            "X1  every answer closes on the ask's status.", "N1  the node's law binds every production under it.",
            "Short sentences.", "two addresses, one line", "the codes at risk")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP_CHEATSHEET").read_text(encoding="utf-8")
    for phrase in EXAMPLES:
        assert phrase in text, phrase
    bench.held("the cheatsheet's examples stand", "Compass, X1, N1, two addresses -- the examples the bench plays")
    assert re.search(r"^    constraints\.production: \|", text, re.M) and not re.search(r"^    constraints: \|", text, re.M)
    bench.held("every example carries its section", "no bare key in the sheet's examples")
    return 0
