"""packages/authoring/procs/PP-DESIGN.md -- the text it keeps: the proc author's guide, its forms
and its doctrine, and the cheatsheet it serves."""
from __future__ import annotations

import re

from tests.harness import SOURCE, kept_document

FORMS = ("READING", "CONTEXT", "LAW", "OFFER", "MISS", "SIGNAL", "ELECTION", "PRODUCTION", "FEED",
         "SELF-PROOF", "BLOCKED", "RECALL", "GESTURE", "DUE", "WAKE", "ASK", "VERBATIM", "GATE", "TUNING")
FIGURES = ("The conducted step", "The contributor", "The door", "The mounted step", "The overlay",
           "The payload", "The sink", "The cadence", "The check and the signal", "The package command",
           "The writer skill", "The settings fragment")
DOCTRINE = ("Describe a new proc by its forms", "Count the LLM initiatives", "intended initiative decides",
            "never in form", "load-bearing first", "The lived doctrine", "has LINEAGE",
            "mechanical or measured", "never a registered element", "Placement is law", "5 900 ok for 3 fail",
            "constraints-unsectioned", "never proven", "whole, sample or trace fact",
            "the codes at risk", "no active production law means silent checkpoint",
            "A public name wears its package's name", "name-unprefixed", "name-ambiguous")


def scenario(bench) -> int:
    text = kept_document(SOURCE / "packages" / "authoring", "PP-DESIGN").read_text(encoding="utf-8")
    assert all(form in text for form in FORMS)
    bench.held("PP-DESIGN names every interaction form", " · ".join(FORMS[:6]) + " …")
    assert "The figures — what a package makes of the forms" in text
    assert all(f"### {figure}" in text for figure in FIGURES)
    bench.held("PP-DESIGN carries the twelve figures", "two catalogs, two axes -- the forms brief, the figures didactic, real employers cited")
    assert "Three sequences of an exchange" in text and "manifest providers" not in text
    bench.held("the sequences are named for what they are", "and the manifest-provider claim is gone")
    assert all(phrase in text for phrase in DOCTRINE)
    bench.held("PP-DESIGN carries the lived doctrine", "forms first, initiatives counted, placement is law, the proof's numbers")
    front = text.split("---")[1]
    assert re.search(r"^serve: \|\n(?:  .*\n)*  CONDUCTION\.md$", front, re.M), "the door serves the theory"
    assert "The served `CONDUCTION` says WHEN to choose each figure" in text
    bench.held("the door serves the theory of conduction", "CONDUCTION.md rides the door's serve rows, "
               "and the figures open on the pointer to it")
    assert "IVK" not in text
    bench.held("the retired vocabulary is gone", "no IVK in the guide")
    assert re.search(r"^    constraints\.production: \|", text, re.M) and not re.search(r"^    constraints: \|", text, re.M)
    bench.held("every example carries its section", "no bare key in the guide's examples")
    return 0
