"""packages/authoring/refs/CONDUCTION.md -- the text it keeps: the theory of conduction -- WHY a
reading goes where it goes and WHEN an author chooses each form: what conduction carries, what a
reading founds, where work comes from and where it is played, the law of inference, how a
placement is judged, the author's three documents -- and the true extracts of the models it cites."""
from __future__ import annotations

import re

from tests.harness import SOURCE, kept_document

WHY = ("The documents of an instance exist to give the agent a knowledge",
       "play the right proc at the right moment", "Conduction is the art of that transport",
       "Serving everything at the turn is brute force", "A door costs a call",
       "The readings found both the proof and the production",
       "do not replace a well-scaffolded context", "The boot is paid once",
       "a figure of COST, never of return")
KNOWLEDGE = ("## The five channels", "| the standing orders | the protocol |", "| MEMBER and its readings |",
             "| an overlay of TURN | a package's reflex and its offers |", "| a document at a socket |",
             "| a door, or a mount behind a skill call |",
             "**Reach** — does it arrive before the ask", "**Mass** — the characters it costs",
             "**Latency** — the calls the agent makes", "Mass has a grain and a place",
             "a context has a diminishing return",
             "The context precedes the ask", "in grain and in moment", "Served is not applied",
             "The reflex", "comes before the ask, and it is small",
             "comes behind the door the reflex opens, and it is large",
             "The boot keeps what founds EVERY ask", "A placement fails in two directions",
             "the description says WHEN", "the reflex and the offer in one paragraph",
             "the reference lives behind the door or the mount",
             "A tool must not arrive without its rules", "the first turn can carry work",
             "after a summary of the conversation", "three useful sentences")
WORK = ("**Direct** work is what the operator's message asks for",
        "**Induced** work is what the direct work makes due",
        "**Background** work is due on a date or at every turn, whatever the message says",
        "Direct work plays in the turn's `WORK` step",
        "When direct work changes its method",
        "Induced and background work play in a document attached to a socket",
        "Data another document consumes enters by a mount or a payload")
INFERENCE = ("Orchestration is probabilistic, execution is deterministic",
             "Everything that can be scripted is scripted", "never asked of the agent",
             "Inference is for constrained judgment", "chains scripts by its `WORK` steps",
             "on its contract", "never by reading its code",
             "the skill does, the proc judges")
TEST = ("A document that tells the agent to play a skill has a `WORK` step, or lives in the view of one",
        "An `INFER` step produces", "A mounted document serves",
        "what a script would render is misplaced", "This test has to be mechanical",
        "the nearest and most precise instruction", "a rule that counts is held by the engine")
USAGE = ("Usage is never declared by the agent", "**cited**", "**taken up**", "**ablation**",
         "never cited nor taken up, is a candidate to leave its channel")
AUTHOR = ("`CONDUCTION`, this page, is the theory", "`PP_CHEATSHEET` is the catalog",
          "`PP-DESIGN` is the door", "its body says what is expected of the agent",
          "its laws frame that expectation and add the policy", "its `serve:` rows give the reference")
MODELS = (("continuity", "TURN", "overlays"), ("steering", "TURN", "overlays"),
          ("continuity", "OPERATIONS", "procs"), ("improvement", "IMPROVE", "procs"),
          ("continuity", "RECALL", "procs"))
PARTS = 14
CHECKS = 7


def scenario(bench) -> int:
    path = kept_document(SOURCE / "packages" / "authoring", "CONDUCTION")
    text = path.read_text(encoding="utf-8")
    flat = " ".join(text.split())
    for phrase in WHY + KNOWLEDGE + WORK + INFERENCE + TEST + USAGE + AUTHOR:
        assert phrase in flat, phrase
    parts = re.findall(r"^## ", text, re.M)
    assert len(parts) == PARTS, len(parts)
    checklist = text.split("## A checklist for the author")[1]
    assert len(re.findall(r"^\d+\. ", checklist, re.M)) == CHECKS, checklist
    bench.held("CONDUCTION says the whole theory", f"{PARTS} parts: why conduction and what it carries; the "
               "five channels, the three measures with their grain, what a reading founds, the two laws "
               "with the boot rule and the two directions, the offer; the three origins of work and the "
               "four placement rules; the law of inference; the test and why it is mechanical; the three "
               f"signals of usage; the author's three documents; a checklist of {CHECKS}")

    mass = len(path.read_bytes())
    assert mass <= 10000, mass
    for mechanism in ("overlay-carries-proc", "attach-and-mount", "::mount", "requires topology"):
        assert mechanism not in text, mechanism
    assert "PP-DESIGN" in text and "PP_CHEATSHEET" in text
    bench.held("CONDUCTION says why and when, never how", f"{mass} bytes under 10 000 (wc -c); no "
               "figure's mechanism is retold -- the guide and the catalog are named for it")

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
