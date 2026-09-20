"""packages/plan/skills/pp-plan -- the grammar of the plans keeper, lived whole on
real environments carrying the plan package: the sections written by the script (a
plan born by its Context, an item prepared in Items and born at its first section,
the order guided, a log appended), the statuses DEDUCED from the writing (Expected
frames, Delivery delivers and the closing rises, a framing section rewritten on a done
node reopens, `done` checks a todo off, `block` says a stop), the derived table, the
lint that catches a hand edit and the repair that mends what is mechanical, move,
rename, the law amended or retired by its code, the keeper reading derived folders
alone, the mount chain, the gestures' announcements, the arity of every call. Every
refusal red by its name."""
from __future__ import annotations

import contextlib
import io
import json
import sys

from tests.harness import SOURCE, load_script

GROUND = "The ground, measured on-piece."
TARGET = "What it becomes."
EXPECTED = "What is true when it closes -- the bench cited."
TESTS = "The scenario to run."


def scenario(bench) -> int:
    held = bench.held
    refuse = bench.expect_exit
    made = 0

    def instance():
        """A REAL environment carrying the plan package -- the script reads it as the
        operator's instance, never a fake."""
        nonlocal made
        made += 1
        return bench.env(f"plan{made}", ("plan",), pin=False).made

    root = instance()
    # the VENDORED copy, not the source: the skill reaches the engine's write regime
    # through its bootstrap, and the bootstrap only finds one from inside an instance
    plans = load_script(next((root / ".sys" / "vendor").glob("plan@*"))
                        / "skills" / "pp-plan" / "pp-plan.py")

    def section(base, segments, name, prose, append=False):
        path, said, moves = plans.write_section(base, segments, name, prose, append)
        return path, said + moves

    def frame(base, segments):
        """The required sections up to Expected -- the framing that makes a node `doing`."""
        framed(base, segments)

    def deliver(base, segments, log="landed"):
        """The Delivery that closes a batch -- and the closings it says."""
        _, said = section(base, segments, "Delivery", log)
        return said

    def framed(base, segments):
        """The required sections before Items, written with a word each -- what a
        framing does before it prepares its children."""
        kind = plans.KINDS[len(segments) - 1]
        if not plans.doc_of(base, *segments).is_file():        # a prepared item: its Ground births it
            section(base, segments, "Ground", GROUND)
        _, body = plans.read(plans.doc_of(base, *segments))
        for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED), ("Tests", TESTS)):
            if name in plans.SECTIONS[kind] and not plans.is_written(kind, name, body):
                section(base, segments, name, prose)
                _, body = plans.read(plans.doc_of(base, *segments))

    def items_of(base, segments):
        kind = plans.KINDS[len(segments) - 1]
        _, body = plans.read(plans.doc_of(base, *segments))
        if not plans.is_written(kind, "Items", body):
            return []
        return plans.item_lines(plans.section_text(body, "Items") or "")

    def prepare(base, segments, brief):
        """One more line in the parent's Items -- the child PREPARED, an entry, no document."""
        framed(base, segments[:-1])
        lines = items_of(base, segments[:-1]) + [(segments[-1], brief)]
        section(base, segments[:-1], "Items", "\n".join(f"- {s} -- {b}" for s, b in lines))

    def grow(base, segments, brief):
        """Prepared, then BORN by its first section -- the way a phase or a batch comes to be."""
        prepare(base, segments, brief)
        section(base, segments, "Ground", GROUND)

    def todo(base, segments, name, text):
        prepare(base, segments + [name], text)

    def title_line(path):
        return next(line for line in plans.read(path)[1].splitlines() if line.startswith("# "))

    def untitled(path):
        return "".join(line for line in plans.read(path)[1].splitlines(keepends=True)
                       if not line.startswith("# "))

    # --- births: the plan by its Context, the others prepared then born ------------------
    path, said = section(root, ["demo"], "Context", "The demo plan.\n\nIts thesis, in prose.")
    assert said == ["born"] and (root / "plans" / "demo" / "PLAN.md").is_file()
    text = path.read_text(encoding="utf-8")
    assert "## Context\n\nThe demo plan.\n\nIts thesis, in prose.\n" in text and "## Items" in text
    held("a plan is born by its Context", "PLAN.md stands on the template, the brief under Context, no phase yet")

    refuse("section-order", lambda: section(root, ["demo"], "Items", "- survey -- Survey first"))
    held("the order guides", "Items waits Target and Expected -- section-order names the missing one")

    prepare(root, ["demo", "survey"], "Survey first: the inventory phase")
    front, _ = plans.read(root / "plans" / "demo" / "PLAN.md")
    assert plans.children(front) == [("survey", "todo")]
    assert not (root / "plans" / "demo" / "1-survey").exists()
    held("Items prepares a child", "the entry derived `item.1: survey  todo`, no folder, no document")

    path, said = section(root, ["demo", "survey"], "Ground", GROUND)
    assert said == ["born", "replaced"] and path == root / "plans" / "demo" / "1-survey" / "PHASE.md"
    text = path.read_text(encoding="utf-8")
    assert "## Context\n\nSurvey first: the inventory phase\n" in text and "## Ground\n\nThe ground, measured on-piece.\n" in text
    held("the first section births the item", "the folder indexed, the document on the template, the line's brief as Context")

    prepare(root, ["demo", "build"], "Then build")
    front, _ = plans.read(root / "plans" / "demo" / "PLAN.md")
    assert [c[0] for c in plans.children(front)] == ["survey", "build"]
    held("the order lives in the keys", "item.1 survey, item.2 build -- the keys follow the lines")

    grow(root, ["demo", "survey", "map"], "Map the ground")
    front, _ = plans.read(root / "plans" / "demo" / "1-survey" / "PHASE.md")
    assert [c[0] for c in plans.children(front)] == [("map")]
    assert (root / "plans" / "demo" / "1-survey" / "1-map" / "BATCH.md").is_file()
    held("a batch grows under its phase", "prepared in the phase's Items, born at its Ground")

    todo(root, ["demo", "survey", "map"], "list-sources", "list the sources")
    todo(root, ["demo", "survey", "map"], "read-whole", "read them whole")
    btext = (root / "plans" / "demo" / "1-survey" / "1-map" / "BATCH.md").read_text(encoding="utf-8")
    assert "item.1: list-sources  todo" in btext and "item.2: read-whole  todo" in btext
    assert "## Items\n\n- list-sources -- list the sources\n- read-whole -- read them whole\n" in btext
    held("the todos are the batch's Items", "one line each, the entries derived, nothing else in the body")

    grow(root, ["demo", "survey", "again"], "A second batch")      # born by its Ground, todo
    section(root, ["demo", "survey", "again"], "Target", TARGET)
    afront, _ = plans.read(root / "plans" / "demo" / "1-survey" / "2-again" / "BATCH.md")
    assert afront["status"] == "todo"
    _, said = section(root, ["demo", "survey", "again"], "Expected", EXPECTED)
    assert "pp-plan: demo/survey/again -> doing" in said
    afront, _ = plans.read(root / "plans" / "demo" / "1-survey" / "2-again" / "BATCH.md")
    pfront, _ = plans.read(root / "plans" / "demo" / "1-survey" / "PHASE.md")
    assert afront["status"] == "doing" and dict(plans.children(pfront))["again"] == "doing"
    _, said = section(root, ["demo", "survey", "again"], "Expected", EXPECTED + " again")
    assert not any("->" in one for one in said)
    held("Expected frames the node", "written on a todo node it is `doing`, its parent line follows -- "
         "deduced, no verb; a second Expected moves nothing")

    plans.done(root, ["demo", "survey", "map", "list-sources"])
    bfront, _ = plans.read(root / "plans" / "demo" / "1-survey" / "1-map" / "BATCH.md")
    assert plans.children(bfront)[0][1] == "done" and bfront["status"] == "doing"
    refuse("done-invalid", lambda: plans.done(root, ["demo", "survey", "map"]))
    held("done checks a todo off", "list-sources done, read-whole untouched, the batch still doing; "
         "`done` on a node refuses -- a node closes by its work")

    section(root, ["demo", "survey", "map"], "Items", "- list-sources -- list the sources\n- read-whole -- read them whole\n- one-more -- a later step")
    bfront, _ = plans.read(root / "plans" / "demo" / "1-survey" / "1-map" / "BATCH.md")
    assert plans.children(bfront) == [("list-sources", "done"), ("read-whole", "todo"), ("one-more", "todo")]
    section(root, ["demo", "survey", "map"], "Items", "- list-sources -- list the sources\n- read-whole -- read them whole")
    bfront, _ = plans.read(root / "plans" / "demo" / "1-survey" / "1-map" / "BATCH.md")
    assert plans.children(bfront) == [("list-sources", "done"), ("read-whole", "todo")]
    out = refuse("item-engaged", lambda: section(root, ["demo", "survey", "map"], "Items", "- read-whole -- read them whole"))
    assert "list-sources" in out and "done" in out
    section(root, ["demo", "survey", "map"], "Tests", TESTS)
    out = refuse("items-open", lambda: section(root, ["demo", "survey", "map"], "Delivery", "too soon"))
    assert "read-whole" in out
    held("Items is rewritten, the entries follow", "a line added enters todo, a known one keeps its status, "
         "a todo line removed leaves, a delivered one refuses item-engaged -- and a Delivery over an "
         "open todo refuses items-open, naming it")

    out = refuse("item-engaged", lambda: section(root, ["demo"], "Items", "- build -- Then build"))
    assert "survey" in out and "born" in out
    held("a born child never leaves Items", "the entry stays while its folder stands -- item-engaged")

    table = plans.status_table(root, None)
    assert "| demo |" in table
    detail = plans.status_table(root, "demo")
    assert "demo/survey/map/read-whole" in detail and "| demo/build | phase | todo |" in detail
    held("the table derives from front matters", "overview and full tree, the prepared child shown, nothing stored")

    assert plans.check(root) == []
    held("check clean on a lived plan", "structure, statuses, numbering, prose all agree -- a prepared todo is no finding")

    doc = root / "plans" / "demo" / "1-survey" / "PHASE.md"
    doc.write_text(doc.read_text(encoding="utf-8").replace("doing", "cooking"), encoding="utf-8")
    findings = plans.check(root)
    assert any("cooking" in f for f in findings)
    held("check catches the hand", "a hand-edited status reddens by name")
    doc.write_text(doc.read_text(encoding="utf-8").replace("cooking", "doing"), encoding="utf-8")

    # --- the sections: replace, insert at rank, append, the tail, the refusals -------------
    _, said = section(root, ["demo"], "Target", "The target, rewritten.")
    assert said == ["replaced"]
    _, said = section(root, ["demo"], "Survey", "The ground, seen.")
    assert said == ["inserted"]
    body = plans.read(root / "plans" / "demo" / "PLAN.md")[1]
    names = [n for n, _ in plans.split_sections(body)]
    assert names.index("Survey") == names.index("Context") + 1 and names.index("Survey") < names.index("Target")
    held("a section is replaced or inserted at its rank", "Target rewritten in place; Survey born between Context and Target")

    _, said = section(root, ["demo"], "Decisions", "- 2026-09-05 : the first word")
    assert said == ["inserted"]
    _, said = section(root, ["demo"], "Decisions", "- 2026-09-06 : the second word")
    assert said == ["appended"]
    body = plans.read(root / "plans" / "demo" / "PLAN.md")[1]
    assert "the first word\n\n- 2026-09-06 : the second word" in plans.section_text(body, "Decisions")
    _, said = section(root, ["demo"], "Keep track", "a line of the plan's own")
    assert said == ["inserted"] and [n for n, _ in plans.split_sections(plans.read(root / "plans" / "demo" / "PLAN.md")[1])][-1] == "Keep track"
    _, said = section(root, ["demo"], "Keep track", "one more", append=True)
    assert said == ["appended"]
    held("a log appends, the tail is open", "Decisions grows by dated lines; a name beyond the list lands last, "
         "replaced or appended by the flag")

    refuse("section-unknown", lambda: section(root, ["demo", "survey", "map"], "Todos", "- x -- y"))
    refuse("prose-missing", lambda: section(root, ["demo"], "Target", "   \n"))
    refuse("section-order", lambda: section(root, ["demo", "build"], "Target", TARGET))
    refuse("section-order", lambda: section(root, ["demo", "survey", "map"], "Delivery", "landed") if False else plans.write_section(root, ["demo", "build"], "Delivery", "x"))
    refuse("item-line-malformed", lambda: section(root, ["demo", "survey", "map"], "Items", "- T9 -- a tag, not a name"))
    refuse("slug-taken", lambda: section(root, ["demo", "survey", "map"], "Items", "- read-whole -- a\n- read-whole -- b"))
    held("the section refusals hold", "section-unknown (Todos), prose-missing, section-order on a prepared item "
         "and on a log before the framing, item-line-malformed, slug-taken")

    # --- a subtitle inside a section: `##` refused before any write, `###` written -------
    heads = instance()
    section(heads, ["heads"], "Context", "A plan whose prose carries subtitles.")
    framed(heads, ["heads"])
    section(heads, ["heads"], "Keep track", "a line of the plan's own")
    hdoc = heads / "plans" / "heads" / "PLAN.md"
    sneaks = (("Target", "The target.\n\n## Sneaked\n\nmore", False),           # a section replaced
              ("Protocol", "## Sneaked\n\nthe method", False),                  # a section inserted
              ("Decisions", "- 2026-09-13 : a word\n## Sneaked", False),         # a log
              ("Keep track", "one more\n## Sneaked", True),                     # the flag
              ("Target", "```\n## Sneaked in a code block\n```", False))        # a code block
    for name, prose, append in sneaks:
        before = hdoc.read_bytes()
        out = refuse("prose-heading", lambda: section(heads, ["heads"], name, prose, append))
        assert "## Sneaked" in out and "###" in out
        assert hdoc.read_bytes() == before, name
    prepare(heads, ["heads", "later"], "A phase to come")
    before = hdoc.read_bytes()
    refuse("prose-heading", lambda: section(heads, ["heads", "later"], "Ground", "The ground.\n## Sneaked"))
    assert hdoc.read_bytes() == before and not list((heads / "plans" / "heads").glob("*-later"))
    held("a `##` in the prose refuses before any write", "prose-heading on a section replaced, inserted, a "
         "log, the flag, a code block, a prepared item -- the bytes unchanged, no folder born")

    def headings():
        return [n for n, _ in plans.split_sections(plans.read(hdoc)[1]) if n is not None]

    counted = headings()
    section(heads, ["heads"], "Target", "The target.\n\n### One\n\nfirst\n\n### Two\n\nsecond")
    assert headings() == counted
    section(heads, ["heads"], "Target", "The target, again.\n\n### Three\n\n### Four\n\n### Five")
    assert headings() == counted and "### Two" not in hdoc.read_text(encoding="utf-8")
    from conductor.core import document
    assert document.read(hdoc).front["slug"] == "heads" and plans.check(heads) == []
    held("a `###` subtitle stays in its section", f"{len(counted)} sections before, after the write, after the "
         "rewrite -- nothing left behind; the engine's reader and check read it clean")

    text = hdoc.read_text(encoding="utf-8")
    hdoc.write_text(text + "\n## Target\n\nA leftover.\n", encoding="utf-8")
    findings = plans.check(heads)
    assert any("section `Target` appears twice" in f for f in findings), findings
    doubled = hdoc.read_bytes()
    mended, left = plans.repair(heads)
    assert mended == [] and hdoc.read_bytes() == doubled
    assert any("section `Target`" in f and "--remove=<n>" in f for f in left), left
    hdoc.write_text(text, encoding="utf-8")
    assert plans.check(heads) == []
    held("check says a section twice", "a hand-doubled Target reddens by name, repair mends nothing and says the gesture; the document restored is clean")

    # --- a section removed: the occurrence the call names, and nothing else ---------------
    cuts = instance()
    section(cuts, ["cuts"], "Context", "A plan whose documents carry leftovers.")
    framed(cuts, ["cuts"])
    section(cuts, ["cuts"], "Decisions", "- 2026-09-13 : the one word")
    cdoc = cuts / "plans" / "cuts" / "PLAN.md"
    clean = cdoc.read_bytes()
    section(cuts, ["cuts"], "Keep track", "a line of the plan's own")
    _, said = plans.remove_section(cuts, ["cuts"], "Keep track", None)
    assert cdoc.read_bytes() == clean and "Keep track" in said and "1 of 1" in said, said
    held("a section beyond the list is removed", "the document is byte for byte the one written without it")

    text = cdoc.read_text(encoding="utf-8")
    cdoc.write_text(text + "## Le log\n\n(à la livraison)\n\n## Le log\n\n- 2026-08-29 -- the journal\n",
                    encoding="utf-8")
    doubled = cdoc.read_bytes()
    out = refuse("section-ambiguous", lambda: plans.remove_section(cuts, ["cuts"], "Le log", None))
    assert "1:" in out and "(à la livraison)" in out and "2:" in out and "the journal" in out, out
    refuse("section-unknown", lambda: plans.remove_section(cuts, ["cuts"], "Le log", 3))
    assert cdoc.read_bytes() == doubled
    plans.remove_section(cuts, ["cuts"], "Le log", 1)
    assert cdoc.read_text(encoding="utf-8") == text + "## Le log\n\n- 2026-08-29 -- the journal\n"
    cdoc.write_text(text + "## Todos\n\n- a -- the list\n\n## Todos\n\n- a -- a stale list\n", encoding="utf-8")
    plans.remove_section(cuts, ["cuts"], "Todos", 2)
    assert cdoc.read_text(encoding="utf-8") == text + "## Todos\n\n- a -- the list\n\n"
    cdoc.write_text(text + "## Target\n\nA leftover.\n", encoding="utf-8")
    plans.remove_section(cuts, ["cuts"], "Target", 2)
    assert cdoc.read_text(encoding="utf-8") == text
    held("a doubled section is removed by its rank", "section-ambiguous lists each occurrence with its size "
         "and first line; --remove=1 takes the empty log, =2 the stale list, =2 a doubled Target; a rank "
         "beyond refuses section-unknown")

    for name in ("Target", "Decisions"):
        refuse("section-kept", lambda: plans.remove_section(cuts, ["cuts"], name, None))
    refuse("section-unknown", lambda: plans.remove_section(cuts, ["cuts"], "Ghost", None))
    assert cdoc.read_text(encoding="utf-8") == text
    prepare(cuts, ["cuts", "later"], "A phase to come")
    before = cdoc.read_bytes()
    refuse("path-unknown", lambda: plans.remove_section(cuts, ["cuts", "later"], "Ground", None))
    assert cdoc.read_bytes() == before
    held("what must stay stays", "section-kept on a listed section standing once (Target, a log), "
         "section-unknown on an absent name, path-unknown on a prepared item -- the bytes unchanged")

    assert document.read(cdoc).front["slug"] == "cuts" and plans.check(cuts) == []
    cdoc.write_text(before.decode("utf-8") + "## Target\n\nA leftover.\n", encoding="utf-8")
    _, left = plans.repair(cuts)
    assert any("section `Target`" in f and "--remove=<n>" in f for f in left), left
    cdoc.write_bytes(before)
    held("the removal reads back clean", "the engine's reader and check after every removal; repair names "
         "`section … --remove=<n>` for a doubled section")

    refuse("path-unknown", lambda: section(root, ["ghost", "p1"], "Ground", GROUND))
    out = refuse("path-unknown", lambda: plans.doc_of(root, "demo", "1-survey", "1-map"))
    assert "FOLDER" in out and "demo/survey" in out
    out = refuse("path-unknown", lambda: plans.doc_of(root, "demo", "nope"))
    assert "prepare it" in out
    refuse("path-unknown", lambda: plans.block(root, ["demo", "build"], "not yet"))
    refuse("path-unknown", lambda: plans.done(root, ["demo", "survey", "map", "ghost-step"]))
    held("the address refusals teach", "a numbered folder says the bare address, an absent entry says "
         "Items, a prepared item says its first section; an absent todo")

    broken = root / "plans" / "demo" / "PLAN.md"
    text = broken.read_text(encoding="utf-8")
    broken.write_text(text.replace("---", "-!-", 1), encoding="utf-8")
    refuse("frontmatter-malformed", lambda: plans.read(broken))
    held("frontmatter-malformed refuses", "the script trusts only what it wrote")
    broken.write_text(text, encoding="utf-8")

    # --- the next move walks the statuses, prepared items included -------------------------
    root2 = instance()
    section(root2, ["story"], "Context", "A tale of a plan.")
    assert plans.next_move(root2, "story") == "the plan has no phase yet -- its phases come on the operator's GO (one GO creates and frames them) (plan:story)"
    prepare(root2, ["story", "p1"], "First phase")
    assert plans.next_move(root2, "story") == ("the phase p1 awaits its framing"
                                              " -- its batches come on the operator's GO (plan-phase:story/p1)")
    frame(root2, ["story", "p1"])
    assert plans.next_move(root2, "story") == "the phase p1 awaits its batches -- their creation awaits the operator's GO (plan-phase:story/p1)"
    held("a prepared phase says its move", "no document yet, the entry walks: awaits its framing; framed -> create the batches")
    prepare(root2, ["story", "p1", "b1"], "First batch")
    assert plans.next_move(root2, "story") == "the batch p1/b1 awaits its framing (plan-lot:story/p1/b1)"
    frame(root2, ["story", "p1", "b1"])
    assert plans.next_move(root2, "story") == "the batch p1/b1 awaits its implementation -- on the GO that names it (plan-lot:story/p1/b1)"
    said = deliver(root2, ["story", "p1", "b1"])
    assert "pp-plan: story/p1/b1 -> done -- closes story/p1, story" in said
    assert plans.next_move(root2, "story") is None
    held("the next move walks true", "no phase -> awaits framing -> awaits implementation -> "
         "the Delivery closes batch, phase and plan by the script -> None; every line ends with "
         "the vector of the node it names -- plan:, plan-phase:, plan-lot:")

    _, said = section(root2, ["story", "p1", "b1"], "Target", "reworked")
    assert "pp-plan: story/p1/b1 -> redo -- the rework is open" in said
    cfront, _ = plans.read(root2 / "plans" / "story" / "PLAN.md")
    qfront, _ = plans.read(root2 / "plans" / "story" / "1-p1" / "PHASE.md")
    lfront2, _ = plans.read(root2 / "plans" / "story" / "1-p1" / "1-b1" / "BATCH.md")
    assert (lfront2["status"] == "redo" and qfront["status"] == "redo"
            and cfront["status"] == "doing")
    assert (dict(plans.children(qfront))["b1"] == "redo"
            and dict(plans.children(cfront))["p1"] == "redo")
    assert plans.next_move(root2, "story") == "the batch p1/b1 is reopened -- its rework awaits the operator's GO (plan-lot:story/p1/b1)"
    assert plans.check(root2) == []
    _, said = section(root2, ["story", "p1", "b1"], "Decisions", "- a dated word")
    assert not any("->" in one for one in said)
    held("a framing section rewritten reopens", "Target on a done batch under a closed plan turns it "
         "redo and raises phase and plan with it -- the next move names the batch; a Decisions line "
         "reopens nothing")

    # --- the closing rises ----------------------------------------------------------------
    casc = instance()
    section(casc, ["casc"], "Context", "The closing rises.")
    grow(casc, ["casc", "p1"], "Phase one")
    prepare(casc, ["casc", "p2"], "Phase two")
    grow(casc, ["casc", "p1", "b1"], "Batch one")
    prepare(casc, ["casc", "p1", "b2"], "Batch two")
    todo(casc, ["casc", "p1", "b1"], "first-step", "the first step")
    todo(casc, ["casc", "p1", "b1"], "last-step", "the last step")
    frame(casc, ["casc", "p1", "b1"])
    plans.done(casc, ["casc", "p1", "b1", "first-step"])
    plans.done(casc, ["casc", "p1", "b1", "last-step"])
    b1front, _ = plans.read(casc / "plans" / "casc" / "1-p1" / "1-b1" / "BATCH.md")
    assert b1front["status"] == "doing"
    said = deliver(casc, ["casc", "p1", "b1"])
    assert "pp-plan: casc/p1/b1 -> done" in said and not any("closes" in one for one in said)
    b1front, _ = plans.read(casc / "plans" / "casc" / "1-p1" / "1-b1" / "BATCH.md")
    p1front, _ = plans.read(casc / "plans" / "casc" / "1-p1" / "PHASE.md")
    assert b1front["status"] == "done" and dict(plans.children(p1front))["b1"] == "done"
    assert p1front["status"] == "doing" and plans.check(casc) == []
    held("Delivery closes its batch", "the last todo checked off closes nothing; the Delivery does, "
         "and a sibling batch still todo stops the closing at the phase")

    section(casc, ["casc", "p1", "b2"], "Ground", GROUND)
    plans.block(casc, ["casc", "p1", "b2"], "the store is not there yet")
    b2front, b2body = plans.read(casc / "plans" / "casc" / "1-p1" / "2-b2" / "BATCH.md")
    assert b2front["status"] == "blocked" and "blocked -- the store is not there yet" in plans.section_text(b2body, "Decisions")
    _, said = section(casc, ["casc", "p1", "b2"], "Target", TARGET)
    assert "pp-plan: casc/p1/b2 -> todo -- the block is lifted" in said
    frame(casc, ["casc", "p1", "b2"])
    said = deliver(casc, ["casc", "p1", "b2"])
    assert "pp-plan: casc/p1/b2 -> done -- closes casc/p1" in said
    assert plans.next_move(casc, "casc") == "the phase p2 awaits its framing -- its batches come on the operator's GO (plan-phase:casc/p2)"
    held("block says a stop, the writing lifts it", "blocked with its dated Decisions line; the next framing "
         "section lifts it (todo before Expected, doing after); the second batch delivered closes the phase")

    section(casc, ["casc", "p2"], "Ground", GROUND)          # the prepared phase is born
    grow(casc, ["casc", "p2", "b3"], "Batch three")
    todo(casc, ["casc", "p2", "b3"], "only-step", "the only step")
    frame(casc, ["casc", "p2", "b3"])
    plans.block(casc, ["casc", "p2"], "waits the store")
    plans.done(casc, ["casc", "p2", "b3", "only-step"])
    said = deliver(casc, ["casc", "p2", "b3"])
    assert "pp-plan: casc/p2/b3 -> done -- closes casc/p2, casc" in said
    cfront, _ = plans.read(casc / "plans" / "casc" / "PLAN.md")
    p2front, _ = plans.read(casc / "plans" / "casc" / "2-p2" / "PHASE.md")
    assert cfront["status"] == "done" and dict(plans.children(cfront)) == {"p1": "done", "p2": "done"}
    assert p2front["status"] == "done" and dict(plans.children(p2front))["b3"] == "done"
    assert plans.next_move(casc, "casc") is None and plans.check(casc) == []
    held("the closing rises to the plan", "the Delivery of the last batch of the last phase closes "
         "batch, phase and plan in one call -- a blocked parent closes like the others, every line "
         "and document agree, check clean")

    todo(casc, ["casc", "p2", "b3"], "one-more", "one more step")     # Items on a done batch reopens it
    cfront, _ = plans.read(casc / "plans" / "casc" / "PLAN.md")
    b3front, _ = plans.read(casc / "plans" / "casc" / "2-p2" / "1-b3" / "BATCH.md")
    assert cfront["status"] == "doing" and dict(plans.children(cfront))["p2"] == "redo" and b3front["status"] == "redo"
    plans.done(casc, ["casc", "p2", "b3", "one-more"])
    said = deliver(casc, ["casc", "p2", "b3"], "reworked")
    assert "pp-plan: casc/p2/b3 -> done -- closes casc/p2, casc" in said
    assert plans.next_move(casc, "casc") is None and plans.check(casc) == []
    held("the rework cascades again", "a new todo in Items reopens the delivered batch and lifts the "
         "ancestry; its Delivery closes it back down to the plan -- the cycle round-trips")

    prio = instance()
    section(prio, ["prio"], "Context", "Engagement primes order.")
    prepare(prio, ["prio", "first"], "A phase never started")
    grow(prio, ["prio", "second"], "A framed phase")
    frame(prio, ["prio", "second"])
    assert plans.next_move(prio, "prio") == "the phase second awaits its batches -- their creation awaits the operator's GO (plan-phase:prio/second)"
    prepare(prio, ["prio", "second", "b1"], "A batch never started")
    grow(prio, ["prio", "second", "b2"], "An engaged batch")
    frame(prio, ["prio", "second", "b2"])
    assert plans.next_move(prio, "prio") == "the batch second/b2 awaits its implementation -- on the GO that names it (plan-lot:prio/second/b2)"
    deliver(prio, ["prio", "second", "b2"])
    assert plans.next_move(prio, "prio") == "the batch second/b1 awaits its framing (plan-lot:prio/second/b1)"
    held("engagement primes order", "a doing phase behind a todo phase is served; an engaged "
         "batch behind a todo batch is served; none engaged falls back to the first todo")

    # --- check and repair ---------------------------------------------------------------
    drift = instance()
    section(drift, ["x"], "Context", "A plan to drift.")
    grow(drift, ["x", "a"], "A phase")
    grow(drift, ["x", "b"], "Another phase")
    xdoc = drift / "plans" / "x" / "PLAN.md"
    xdoc.write_text(xdoc.read_text(encoding="utf-8").replace("item.2:", "item.4:"), encoding="utf-8")
    assert any("numbering broken" in f for f in plans.check(drift))
    adoc = drift / "plans" / "x" / "1-a" / "PHASE.md"
    adoc.write_text(adoc.read_text(encoding="utf-8").replace("status: todo", "status: doing"), encoding="utf-8")
    xdoc.write_text(xdoc.read_text(encoding="utf-8").replace("item.1: a  todo", "item.1: a  blocked"), encoding="utf-8")
    plans.birth(drift, ["x", "b"], "orphan") if False else None
    xtext = xdoc.read_text(encoding="utf-8")
    xdoc.write_text(xtext.replace("item.4: b  todo\n", ""), encoding="utf-8")
    findings = plans.check(drift)
    assert any("has no entry" in f for f in findings) and any("says blocked, the document says doing" in f for f in findings)
    mended, left = plans.repair(drift)
    assert len(mended) == 2 and any("the document wins" in m for m in mended) and any("had no entry" in m for m in mended)
    assert left == [] and plans.check(drift) == []
    xfront, _ = plans.read(xdoc)
    assert plans.children(xfront) == [("a", "doing"), ("b", "todo")]
    held("repair mends what is mechanical", "a broken numbering, an entry against its document, a folder "
         "without its entry -- each said; check clean after")

    mended, left = plans.repair(drift)
    assert mended == [] and left == []
    held("a clean tree repairs nothing", "no mend, nothing left")

    tagged = instance()
    section(tagged, ["old"], "Context", "A plan of the tag era.")
    grow(tagged, ["old", "p"], "A phase")
    grow(tagged, ["old", "p", "b"], "A batch")
    tdoc = tagged / "plans" / "old" / "1-p" / "1-b" / "BATCH.md"
    tfront, tbody = plans.read(tdoc)
    tfront["item.1"] = "T1  todo"
    plans.write(tdoc, tfront, tbody + "\n## Todos\n\n- T1 -- an old step\n")
    assert any("positional tag" in f for f in plans.check(tagged))
    mended, left = plans.repair(tagged)
    assert mended == [] and len(left) == 1 and "rewrite Items with slugs" in left[0]
    held("repair says what it leaves", "a positional tag is not mechanical -- said with its gesture, untouched")

    todo(tagged, ["old", "p", "b"], "real-step", "a named step")
    tfront, tbody = plans.read(tdoc)
    plans.write(tdoc, tfront, tbody.replace("- real-step -- a named step", ""))
    assert any("real-step" in f and "line in the body" in f for f in plans.check(tagged))
    held("check wants the body line", "an entry without its `- <name> -- ...` line reddens")

    dirs = instance()
    section(dirs, ["kept"], "Context", "A plan with its own material beside its nodes.")
    grow(dirs, ["kept", "p"], "A phase")
    (dirs / "plans" / "kept" / "__pycache__").mkdir()
    (dirs / "plans" / "kept" / "playbooks").mkdir()
    (dirs / "plans" / "kept" / "1-p" / "campaigns").mkdir()
    assert plans.check(dirs) == []
    (dirs / "plans" / "kept" / "7-orphan").mkdir()
    findings = plans.check(dirs)
    assert len(findings) == 1 and "7-orphan" in findings[0] and "has no entry" in findings[0]
    mended, left = plans.repair(dirs)
    assert mended == [] and len(left) == 1 and "7-orphan" in left[0]
    held("the keeper reads derived folders alone", "__pycache__, playbooks/ and campaigns/ say nothing; "
         "a `<n>-<name>` folder without its entry reddens, and repair says it")

    keeper = instance()
    section(keeper, ["proclike"], "Context", "A plan that is also a proc.")
    kdoc = keeper / "plans" / "proclike" / "PLAN.md"
    foreign = ("constraints.behavior: |\n  K1  the script alone writes the structure\n"
               "serve: engine/pp.py\n")
    kdoc.write_text(kdoc.read_text(encoding="utf-8").replace(
        "---\n\n# PLAN", foreign + "---\n\n# PLAN"), encoding="utf-8")
    section(keeper, ["proclike"], "Survey", "Seen.")
    grow(keeper, ["proclike", "p1"], "A phase")
    grow(keeper, ["proclike", "p1", "b1"], "A batch")
    todo(keeper, ["proclike", "p1", "b1"], "one-step", "one step")
    frame(keeper, ["proclike", "p1", "b1"])
    frame(keeper, ["proclike"])
    assert foreign in kdoc.read_text(encoding="utf-8")
    assert plans.check(keeper) == []
    held("foreign keys survive the gestures", "constraints/serve verbatim across every section write and status move, check clean")

    kfront, kbody = plans.read(kdoc)
    once = plans.emit(kfront, kbody)
    plans.write(kdoc, kfront, kbody)
    assert kdoc.read_text(encoding="utf-8") == once
    held("the emit is stable", "emitting twice yields the same text -- no drift, no loss")

    # --- move ------------------------------------------------------------------------------
    mover = instance()
    section(mover, ["alpha"], "Context", "Plan A.")
    section(mover, ["beta"], "Context", "Plan B.")
    grow(mover, ["alpha", "one"], "Phase one")
    grow(mover, ["alpha", "two"], "Phase two")
    grow(mover, ["alpha", "two", "job"], "A batch")
    todo(mover, ["alpha", "two", "job"], "a-step", "a step")
    grow(mover, ["beta", "home"], "Target phase")

    two_doc, job_doc = (mover / "plans" / "alpha" / "2-two" / "PHASE.md",
                        mover / "plans" / "alpha" / "2-two" / "1-job" / "BATCH.md")
    kept = [untitled(two_doc), untitled(job_doc)]
    assert "`alpha`" in title_line(two_doc) and "`alpha`" in title_line(job_doc)
    plans.move(mover, ["alpha", "two"], ["beta"], "1")
    two_doc, job_doc = (mover / "plans" / "beta" / "1-two" / "PHASE.md",
                        mover / "plans" / "beta" / "1-two" / "1-job" / "BATCH.md")
    for doc, body in ((two_doc, kept[0]), (job_doc, kept[1])):
        assert title_line(doc) == plans.title_of(plans.read(doc)[0]) and "`beta`" in title_line(doc), doc
        assert "`alpha`" not in title_line(doc) and untitled(doc) == body, doc
    bfront, _ = plans.read(mover / "plans" / "beta" / "PLAN.md")
    assert [c[0] for c in plans.children(bfront)] == ["two", "home"]
    jfront, _ = plans.read(mover / "plans" / "beta" / "1-two" / "1-job" / "BATCH.md")
    assert jfront["plan"] == "beta" and jfront["phase"] == "two"
    afront, _ = plans.read(mover / "plans" / "alpha" / "PLAN.md")
    assert [c[0] for c in plans.children(afront)] == ["one"]
    assert (mover / "plans" / "beta" / "2-home").is_dir()
    assert plans.check(mover) == []
    held("move carries a phase across plans", "entry, folders and subtree keys land; both sides renumber")

    kept = untitled(job_doc)
    plans.move(mover, ["beta", "two", "job"], ["beta", "home"], "1")
    job_doc = mover / "plans" / "beta" / "2-home" / "1-job" / "BATCH.md"
    assert title_line(job_doc) == plans.title_of(plans.read(job_doc)[0]) and "`home`" in title_line(job_doc)
    assert untitled(job_doc) == kept
    held("move carries the titles", "the moved phase and its batch say the new plan, the moved batch its "
         "new phase -- the title line alone rewritten, the rest of each body byte for byte")
    hfront, _ = plans.read(mover / "plans" / "beta" / "2-home" / "PHASE.md")
    assert [c[0] for c in plans.children(hfront)] == ["job"]
    tfront, _ = plans.read(mover / "plans" / "beta" / "1-two" / "PHASE.md")
    assert plans.children(tfront) == []
    assert plans.check(mover) == []
    held("move lands a batch in another phase", "the entry leaves, the batch keys follow, check stays clean")

    grow(mover, ["beta", "last"], "Third phase")
    plans.move(mover, ["beta", "last"], ["beta"], "1")
    bfront, _ = plans.read(mover / "plans" / "beta" / "PLAN.md")
    assert [c[0] for c in plans.children(bfront)] == ["last", "two", "home"]
    assert (mover / "plans" / "beta" / "1-last").is_dir() and (mover / "plans" / "beta" / "3-home").is_dir()
    assert plans.check(mover) == []
    held("an intra-parent move reorders", "same parent, new rank, every folder re-derived")

    refuse("path-unknown", lambda: plans.move(mover, ["alpha", "ghost"], ["beta"], "1"))
    refuse("target-unknown", lambda: plans.move(mover, ["beta", "two"], ["gamma"], "1"))
    refuse("index-invalid", lambda: plans.move(mover, ["beta", "two"], ["beta"], "9"))
    refuse("kind-mismatch", lambda: plans.move(mover, ["beta", "two"], ["beta", "home"], "1"))
    grow(mover, ["alpha", "home"], "A homonym")
    refuse("slug-taken", lambda: plans.move(mover, ["alpha", "home"], ["beta"], "1"))
    prepare(mover, ["alpha", "ready"], "A prepared phase")
    refuse("path-unknown", lambda: plans.move(mover, ["alpha", "ready"], ["beta"], "1"))
    held("the move refusals hold", "path-unknown, target-unknown, index-invalid, kind-mismatch, slug-taken; "
         "a prepared item moves by its parent's Items, never by move")

    # --- rename: the name is the identity every entry, folder and key carries ---------------
    namer = instance()
    section(namer, ["gamma"], "Context", "Plan G.")
    grow(namer, ["gamma", "one"], "Phase one")
    grow(namer, ["gamma", "one", "job"], "A batch")
    todo(namer, ["gamma", "one", "job"], "a-step", "a step")
    grow(namer, ["gamma", "two"], "Phase two")
    kept = [untitled(namer / "plans" / "gamma" / "1-one" / "PHASE.md"),
            untitled(namer / "plans" / "gamma" / "1-one" / "1-job" / "BATCH.md")]
    plans.rename(namer, ["gamma", "one"], "uno")
    for doc, body in ((namer / "plans" / "gamma" / "1-uno" / "PHASE.md", kept[0]),
                      (namer / "plans" / "gamma" / "1-uno" / "1-job" / "BATCH.md", kept[1])):
        assert title_line(doc) == plans.title_of(plans.read(doc)[0]) and "`uno`" in title_line(doc), doc
        assert "`one`" not in title_line(doc) and untitled(doc) == body, doc
    gfront, gbody = plans.read(namer / "plans" / "gamma" / "PLAN.md")
    assert [c[0] for c in plans.children(gfront)] == ["uno", "two"]
    assert "- uno -- Phase one" in gbody and "- one --" not in gbody
    assert (namer / "plans" / "gamma" / "1-uno" / "PHASE.md").is_file()
    assert not (namer / "plans" / "gamma" / "1-one").exists()
    ufront, _ = plans.read(namer / "plans" / "gamma" / "1-uno" / "PHASE.md")
    assert ufront["slug"] == "uno" and ufront["status"] == "doing"
    jfront, _ = plans.read(namer / "plans" / "gamma" / "1-uno" / "1-job" / "BATCH.md")
    assert jfront["phase"] == "uno" and jfront["plan"] == "gamma"
    assert plans.check(namer) == []
    kept = untitled(namer / "plans" / "gamma" / "1-uno" / "1-job" / "BATCH.md")
    plans.rename(namer, ["gamma", "uno", "job"], "work")
    work_doc = namer / "plans" / "gamma" / "1-uno" / "1-work" / "BATCH.md"
    assert title_line(work_doc) == plans.title_of(plans.read(work_doc)[0]) and "`work`" in title_line(work_doc)
    assert untitled(work_doc) == kept
    ufront, ubody = plans.read(namer / "plans" / "gamma" / "1-uno" / "PHASE.md")
    assert [c[0] for c in plans.children(ufront)] == ["work"] and "- work -- A batch" in ubody
    wfront, _ = plans.read(namer / "plans" / "gamma" / "1-uno" / "1-work" / "BATCH.md")
    assert wfront["slug"] == "work" and [c[0] for c in plans.children(wfront)] == ["a-step"]
    assert plans.check(namer) == []
    held("rename carries the name everywhere", "the parent's entry at its rank, its Items line, the derived "
         "folder, `slug:` and the batches' `phase:` follow in one call -- check clean; a batch alike")

    refuse("kind-mismatch", lambda: plans.rename(namer, ["gamma"], "delta"))
    refuse("kind-mismatch", lambda: plans.rename(namer, ["gamma", "uno", "work", "a-step"], "b-step"))
    refuse("name-invalid", lambda: plans.rename(namer, ["gamma", "two"], "Two_Phase"))
    refuse("name-invalid", lambda: plans.rename(namer, ["gamma", "two"], "two"))
    refuse("slug-taken", lambda: plans.rename(namer, ["gamma", "two"], "uno"))
    refuse("path-unknown", lambda: plans.rename(namer, ["gamma", "ghost"], "spirit"))
    prepare(namer, ["gamma", "ready"], "A prepared phase")
    refuse("path-unknown", lambda: plans.rename(namer, ["gamma", "ready"], "steady"))
    assert plans.check(namer) == []
    held("the rename refusals hold", "kind-mismatch (a plan, a todo), name-invalid (the grammar, the same "
         "name), slug-taken, path-unknown (absent, prepared) -- nothing written")

    # --- the title line: check sees a wrong one, repair sets it, a free title is left ----------
    titles = instance()
    section(titles, ["tp"], "Context", "A plan whose titles drift.")
    grow(titles, ["tp", "ph"], "A phase")
    grow(titles, ["tp", "ph", "bt"], "A batch")
    grow(titles, ["tp", "ph", "bare"], "A batch without title")
    tdocs = {"plan": titles / "plans" / "tp" / "PLAN.md", "phase": titles / "plans" / "tp" / "1-ph" / "PHASE.md",
             "bt": titles / "plans" / "tp" / "1-ph" / "1-bt" / "BATCH.md",
             "bare": titles / "plans" / "tp" / "1-ph" / "2-bare" / "BATCH.md"}
    assert plans.check(titles) == []
    kept = {name: untitled(doc) for name, doc in tdocs.items()}

    def retitle(doc, old, new):
        doc.write_text(doc.read_text(encoding="utf-8").replace(old + "\n", new, 1), encoding="utf-8")

    retitle(tdocs["plan"], title_line(tdocs["plan"]), "# TP -- a free title of the author's\n")
    free = tdocs["plan"].read_bytes()
    retitle(tdocs["phase"], title_line(tdocs["phase"]), title_line(tdocs["phase"]).replace("`tp`", "`wrong`") + "\n")
    retitle(tdocs["bt"], title_line(tdocs["bt"]), title_line(tdocs["bt"]).replace("# BATCH", "# BATCH# BATCH", 1) + "\n")
    retitle(tdocs["bare"], title_line(tdocs["bare"]), "")
    findings = plans.check(titles)
    assert any(f.startswith("tp/1-ph:") and "`wrong`" in f for f in findings), findings
    assert any(f.startswith("tp/1-ph/1-bt:") and "# BATCH# BATCH" in f for f in findings), findings
    assert any(f.startswith("tp/1-ph/2-bare:") and "no title" in f for f in findings), findings
    assert not any(f.startswith("tp:") for f in findings), findings
    mended, left = plans.repair(titles)
    assert len([m for m in mended if "title" in m]) == 3 and left == [], (mended, left)
    assert plans.check(titles) == [] and tdocs["plan"].read_bytes() == free
    for name in ("phase", "bt"):
        assert title_line(tdocs[name]) == plans.title_of(plans.read(tdocs[name])[0]) and untitled(tdocs[name]) == kept[name]
    assert title_line(tdocs["bare"]) == plans.title_of(plans.read(tdocs["bare"])[0])
    held("check sees a title that lies, repair sets it", "a wrong plan, a doubled `# BATCH`, a missing title "
         "redden by document; repair sets the three and says them, the rest of each body byte for byte; "
         "a free title is neither judged nor touched")

    def close_phase(base, segments):
        """A phase closes by a delivered batch -- one prepared, framed and delivered under it."""
        grow(base, segments + ["closer"], "the batch that closes the phase")
        frame(base, segments + ["closer"])
        return deliver(base, segments + ["closer"])

    assert "closes beta/last" in " ".join(close_phase(mover, ["beta", "last"]))
    assert "closes beta/two" in " ".join(close_phase(mover, ["beta", "two"]))
    _, said = section(mover, ["beta", "two"], "Target", "the phase reworked")
    assert "pp-plan: beta/two -> redo -- the rework is open" in said
    rfront, _ = plans.read(mover / "plans" / "beta" / "2-two" / "PHASE.md")
    bfront, _ = plans.read(mover / "plans" / "beta" / "PLAN.md")
    assert rfront["status"] == "redo" and dict(plans.children(bfront))["two"] == "redo"
    assert plans.next_move(mover, "beta") == "the phase two is reopened -- its rework awaits the operator's GO (plan-phase:beta/two)"
    mended, left = plans.repair(mover)
    assert any("beta/2-two: open over children all done -- closed" in m for m in mended) and left == []
    rfront, _ = plans.read(mover / "plans" / "beta" / "2-two" / "PHASE.md")
    bfront, _ = plans.read(mover / "plans" / "beta" / "PLAN.md")
    assert rfront["status"] == "done" and dict(plans.children(bfront))["two"] == "done"
    held("a framing section reopens a phase, repair closes it back", "Target on a done phase turns it redo "
         "and the parent entry follows; with no batch to deliver, `repair` runs the cascade that "
         "never ran and closes it, the parent line with it")

    _, said = section(mover, ["beta", "home"], "Decisions", "- a word on a phase still open")
    assert not any("->" in one for one in said)
    refuse("done-invalid", lambda: plans.done(mover, ["beta", "home"]))
    held("no verb closes or reopens a node", "a log line moves nothing; `done` refuses a node -- "
         "the statuses follow the writing alone")

    blind = instance()
    section(blind, ["blind"], "Context", "A closed node over open work.")
    grow(blind, ["blind", "ph"], "A phase")
    grow(blind, ["blind", "ph", "lot"], "A batch")
    frame(blind, ["blind", "ph", "lot"])
    assert "pp-plan: blind/ph/lot -> done -- closes blind/ph, blind" in deliver(blind, ["blind", "ph", "lot"])
    assert plans.check(blind) == []
    ldoc = blind / "plans" / "blind" / "1-ph" / "1-lot" / "BATCH.md"
    ldoc.write_text(ldoc.read_text(encoding="utf-8").replace("status: done", "status: doing"), encoding="utf-8")
    plans._splice_child(blind / "plans" / "blind" / "1-ph" / "PHASE.md", "lot", "doing")
    reported = plans.check(blind)
    assert len(reported) == 1 and "lot" in reported[0] and "open work" in reported[0]
    held("the check names a closed node over open work", "engaging a child under a delivered "
         "parent reddens -- the entry and its document agreed, nothing saw it before")

    frame(mover, ["beta", "home", "job"])
    plans.done(mover, ["beta", "home", "job", "a-step"])
    assert "closes beta/home" in " ".join(deliver(mover, ["beta", "home", "job"]))
    section(mover, ["beta", "home"], "Target", "the phase reworked")
    assert plans.next_move(mover, "beta") == "the phase home is reopened -- its rework awaits the operator's GO (plan-phase:beta/home)"
    section(mover, ["beta", "home", "job"], "Target", "the batch reworked")
    assert plans.next_move(mover, "beta") == "the batch home/job is reopened -- its rework awaits the operator's GO (plan-lot:beta/home/job)"
    held("the rework line names the deepest node", "a redo phase alone says itself; "
         "a redo batch beneath is said with its phase -- the full path, never the phase alone")

    relic = instance()
    section(relic, ["vintage"], "Context", "A plan of the block era.")
    rdoc = relic / "plans" / "vintage" / "PLAN.md"
    rtext = rdoc.read_text(encoding="utf-8")
    rdoc.write_text(rtext.replace("---\n\n# PLAN",
                                  "phases: |\n  1-a  todo  old shape\n---\n\n# PLAN"),
                    encoding="utf-8")
    assert any("legacy" in f for f in plans.check(relic))
    held("check names the legacy block", "a phases:| survivor reddens -- items are the grammar now")

    # --- the console: the arity, the paths, the announcements -------------------------------
    root3 = instance()
    plans.home = lambda: root3

    def played(argv, stdin=None):
        if stdin is not None:
            sys.stdin = io.StringIO(stdin)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            plans.main(argv)
        return out.getvalue()

    # --- the plan's CRITICAL SECTION: a writing verb waits while the lock is held ----
    import subprocess
    guarded_root = instance()
    plans.home = lambda: guarded_root
    spot0 = sys.stdin
    try:
        sys.stdin = io.StringIO("Prose.")
        with contextlib.redirect_stdout(io.StringIO()):
            plans.main(["section", "locked", "Context"])
    finally:
        sys.stdin = spot0
    # the VENDORED script again: a second PROCESS, the way another session would come
    script = (next((guarded_root / ".sys" / "vendor").glob("plan@*"))
              / "skills" / "pp-plan" / "pp-plan.py")
    call = [sys.executable, str(script), "section", "locked", "Target"]
    with plans.regime().held(guarded_root / "plans" / "locked"):
        try:
            subprocess.run(call, input=TARGET, capture_output=True, text=True, timeout=2)
            waited = False          # it went through: no critical section
        except subprocess.TimeoutExpired:
            waited = True           # it BLOCKED on the lock, as a verb must
    freed = subprocess.run(call, input=TARGET, capture_output=True, text=True, timeout=20)
    if waited and freed.returncode == 0 and "Target replaced on locked" in freed.stdout:
        held("a writing verb waits for the plan's lock", "blocked while another session "
             "holds it, through once released -- the read-modify-write span is closed")
    else:
        bench.failures.append(f"  ✗ plan lock                     waited={waited} "
                              f"rc={freed.returncode} said={freed.stdout.strip()[:60]}")

    plans.home = lambda: root3
    spot = sys.stdin
    try:
        said = played(["section", "saga", "Context"], stdin="Prose.")
        assert f"pp-plan: Context born on saga -- {root3.name}/plans/saga/PLAN.md" in said
        assert ("::push plan-next-move plan:saga the plan has no phase yet"
                " -- its phases come on the operator's GO (one GO creates and frames them)") in said
        played(["section", "saga", "Target", "-"], stdin=TARGET)
        played(["section", "saga", "Expected"], stdin=EXPECTED)
        said = played(["section", "saga", "Items"], stdin="- p1 -- Phase one\n")
        assert "pp-plan: Items replaced on saga" in said
        assert ("::push plan-next-move plan:saga the phase p1 awaits its framing"
                " -- its batches come on the operator's GO") in said
        said = played(["section", "saga/p1", "Ground"], stdin=GROUND)
        assert f"pp-plan: Ground born and replaced on saga/p1 -- {root3.name}/plans/saga/1-p1/PHASE.md" in said
        played(["section", "saga/p1", "Target"], stdin=TARGET)
        said = played(["section", "saga/p1", "Expected"], stdin=EXPECTED)
        assert "pp-plan: saga/p1 -> doing" in said
        played(["section", "saga/p1", "Items"], stdin="- b -- the batch\n")
        for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED), ("Tests", TESTS)):
            played(["section", "saga/p1/b", name], stdin=prose)
        said = played(["section", "saga/p1/b", "Delivery"], stdin="landed")
        assert "pp-plan: saga/p1/b -> done -- closes saga/p1, saga" in said
        assert "::clear plan-next-move plan:saga" in said
        played(["section", "chain", "Context"], stdin="Prose.")
        played(["section", "chain", "Target"], stdin=TARGET)
        played(["section", "chain", "Expected"], stdin=EXPECTED)
        played(["section", "chain", "Items"], stdin="- p -- P.\n")
        for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED)):
            played(["section", "chain/p", name], stdin=prose)
        played(["section", "chain/p", "Items"], stdin="- b -- B.\n")
        for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED), ("Tests", TESTS)):
            played(["section", "chain/p/b", name], stdin=prose)
        played(["section", "chain/p/b", "Items"], stdin="- the-step -- the step\n")
        said = played(["done", "chain/p/b/the-step"])
        assert "pp-plan: chain/p/b/the-step -> done" in said and "closes" not in said
        said = played(["block", "chain/p/b", "waits", "a", "word"])
        assert "pp-plan: chain/p/b -> blocked -- waits a word" in said
        said = played(["section", "chain/p/b", "Delivery"], stdin="landed")
        assert "pp-plan: chain/p/b -> done -- closes chain/p, chain" in said
        assert "::clear plan-next-move plan:chain" in said
    finally:
        sys.stdin = spot
    held("the gestures announce", "a birth says the path from the repo root; Expected says doing, "
         "Delivery says done and what it closed, deepest first; the push follows each move, the "
         "closed plan clears")

    out = refuse("argument-unexpected", lambda: played(["section", "saga", "Target", "extra"], stdin="x"))
    assert "section <address> <Name>" in out and "DETERMINISTIC" not in out
    out = refuse("argument-missing", lambda: played(["done"]))
    assert "done <slug>/<phase>/<batch>/<todo>" in out
    out = refuse("argument-missing", lambda: played(["rename", "saga/p1"]))
    assert "rename <address> <new-name>" in out
    out = refuse("verb-unknown", lambda: played(["frobnicate"]))
    assert "section, done, block, move" in out
    refuse("verb-unknown", lambda: played(["set", "saga", "done"]))
    refuse("verb-unknown", lambda: played(["reopen", "saga/p1"]))
    out = refuse("argument-unexpected", lambda: played(["section", "saga", "Target", "--frob"], stdin="x"))
    assert "--append" in out
    held("a malformed call refuses by name", "argument-unexpected, argument-missing, verb-unknown -- one "
         "sentence with the verb's usage, never the docstring; a trailing `-` is the stdin marker; "
         "`set` and `reopen` are verbs no more")

    docs3 = [root3 / "plans" / "saga" / "PLAN.md", root3 / "plans" / "saga" / "1-p1" / "PHASE.md",
             root3 / "plans" / "saga" / "1-p1" / "1-b" / "BATCH.md"]
    fronts = [plans.read(one)[0] for one in docs3]
    assert [one["status"] for one in fronts] == ["done", "done", "done"]
    btext = docs3[2].read_text(encoding="utf-8")
    docs3[2].write_text(btext + "## Le log\n\n(à la livraison)\n\n## Le log\n\nthe journal\n", encoding="utf-8")
    doubled = docs3[2].read_bytes()
    for flags in (["--remove", "--append"], ["--remove=x"], ["--remove=0"]):
        refuse("argument-unexpected", lambda: played(["section", "saga/p1/b", "Le log"] + flags, stdin=""))
        assert docs3[2].read_bytes() == doubled, flags
    unread = io.StringIO("## a prose the removal never reads")
    spot = sys.stdin
    try:
        sys.stdin = unread
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            plans.main(["section", "saga/p1/b", "Le log", "--remove=1"])
    finally:
        sys.stdin = spot
    assert unread.tell() == 0 and "pp-plan: Le log (1 of 2" in out.getvalue(), out.getvalue()
    assert docs3[2].read_text(encoding="utf-8") == btext + "## Le log\n\nthe journal\n"
    assert [plans.read(one)[0] for one in docs3] == fronts
    held("the console removes by its flag", "section … --remove=1 plays without reading stdin, says the "
         "occurrence it took; a done batch, its phase and its plan keep their fronts; --remove with "
         "--append, a rank that is no positive integer refuse argument-unexpected")

    vend = instance()
    vendor = next((vend / ".sys" / "vendor").glob("plan@*"))      # the package, as installed
    vplans = load_script(vendor / "skills" / "pp-plan" / "pp-plan.py")
    vplans.write_section(vend, ["job"], "Context", "A plan to mount.")
    vplans.write_section(vend, ["job"], "Target", TARGET)
    vplans.write_section(vend, ["job"], "Expected", EXPECTED)
    vplans.write_section(vend, ["job"], "Items", "- ph -- A phase\n- ph2 -- A prepared phase")
    vplans.write_section(vend, ["job", "ph"], "Ground", GROUND)
    vplans.write_section(vend, ["job", "ph"], "Target", TARGET)
    vplans.write_section(vend, ["job", "ph"], "Expected", EXPECTED)
    vplans.write_section(vend, ["job", "ph"], "Items", "- bt -- A batch\n- bt2 -- A prepared batch")
    vplans.write_section(vend, ["job", "ph", "bt"], "Ground", GROUND)
    before_mount = {p: p.read_bytes() for p in (vend / "plans").rglob("*.md")}
    two = vplans.mount_chain(vend, ["job"])
    four = vplans.mount_chain(vend, ["job", "ph"])
    six = vplans.mount_chain(vend, ["job", "ph", "bt"])
    three = vplans.mount_chain(vend, ["job", "ph2"])
    five = vplans.mount_chain(vend, ["job", "ph", "bt2"])
    ahead = vplans.mount_chain(vend, ["job", "ph", "not-yet"])      # not even prepared
    after_mount = {p: p.read_bytes() for p in (vend / "plans").rglob("*.md")}
    assert [len(two), len(four), len(six), len(three), len(five), len(ahead)] == [2, 4, 6, 3, 5, 5]
    assert two[0]["scope"] == "nested" and two[0]["body"] is True
    assert two[1]["scope"] == "stacked" and two[1]["body"] is True
    assert six[4]["doc"].startswith(".sys/vendor") and six[5]["doc"].startswith("plans/")
    assert three[2]["doc"].endswith("PHASE.md") and three[2]["scope"] == "nested"
    assert five[4]["doc"].endswith("BATCH.md") and five[4]["scope"] == "nested"
    assert all((vend / one["doc"]).is_file() for one in six)
    assert before_mount == after_mount
    held("the mount chain grows by level", "2 for a plan, 4 for a phase, 6 for a batch -- method nested, "
         "node stacked, both with their body; a PREPARED item, or one to come under a born parent, "
         "mounts its method ahead (3, 5); plans/ intact")

    # --- the node at work mounts WHOLE, its ancestors by a selection of their sections -------
    def bodies(chain):
        return [one["body"] for one in chain if one["doc"].startswith("plans/")]
    vplans.write_section(vend, ["job"], "Arbitrations", "None.")
    vplans.write_section(vend, ["job", "ph"], "Arbitrations", "None.")
    plan_shown, phase_shown = ["## Target..## Arbitrations"], ["## Target..## Items"]
    assert bodies(vplans.mount_chain(vend, ["job"])) == [True]
    assert bodies(vplans.mount_chain(vend, ["job", "ph"])) == [plan_shown, True]
    assert bodies(vplans.mount_chain(vend, ["job", "ph", "bt"])) == [plan_shown, phase_shown, True]
    assert bodies(vplans.mount_chain(vend, ["job", "ph", "bt2"])) == [plan_shown, True]    # prepared
    assert bodies(vplans.mount_chain(vend, ["job", "ph", "not-yet"])) == [plan_shown, True]  # to come
    assert bodies(vplans.mount_chain(vend, ["job", "ph2"])) == [True]
    # a section the ancestor lacks says nothing: the couples follow what stands
    assert vplans.shown("phase", "# T\n\n## Context\nc\n## Target\nt\n## Items\n- a -- b\n") == ["## Target..## Items"]
    assert vplans.shown("plan", "## Context\nc\n## Target\nt\n## Protocol\np\n## Expected\ne\n") \
        == ["## Target..## Protocol", "## Expected.."]
    assert vplans.shown("plan", "## Context\nc\n") == []
    # a heading that is no section of the kind stays with the section it details
    legacy = vend / "plans" / "job" / "PLAN.md"
    legacy.write_text(legacy.read_text(encoding="utf-8").replace(
        "## Expected", "## An older heading\n\nkept with the target\n\n## Expected"), encoding="utf-8")
    assert bodies(vplans.mount_chain(vend, ["job", "ph"])) == [plan_shown, True]
    # --whole hands the former chain back, every body whole
    whole = vplans.mount_chain(vend, ["job", "ph", "bt"], whole=True)
    former = [{**one, "body": True} for one in six]      # every body whole, as the chain was
    assert bodies(whole) == [True, True, True] and whole == former
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        assert vplans.main(["mount", "job/ph/bt", "--whole"]) == 0
    assert json.loads(said.getvalue().splitlines()[0].removeprefix("::mount ")) == former
    refuse("argument-unexpected", lambda: vplans.main(["mount", "job/ph/bt", "--all"]))
    held("the node at work mounts whole, its ancestors by selection",
         "a plan, a phase, a batch, a prepared and a to-come batch: the last document whole, each "
         "ancestor from Target to Items; a section missing says nothing, an older heading stays "
         "with its section; `--whole` hands the former chain back")

    refuse("path-unknown", lambda: vplans.mount_chain(vend, ["job", "ph2", "x"]))
    refuse("path-unknown", lambda: vplans.mount_chain(vend, ["unborn"]))
    # the SOURCE copy, loaded only here: a script outside its vendored home has no procs/
    outside = load_script(SOURCE / "packages" / "plan" / "skills" / "pp-plan" / "pp-plan.py")
    refuse("method-missing", lambda: outside.mount_chain(root, ["demo"]))
    held("the mount refusals hold", "a child of a prepared item and an unborn plan refuse; "
         "a script outside its vendored home says it")

    # --- the framing writes its OWN sections, with no author's package anywhere -------
    vplans.write_section(vend, ["le-mur"], "Context", "The wall.")

    @contextlib.contextmanager
    def fed(text: str):
        spot, sys.stdin = sys.stdin, io.StringIO(text)
        try:
            yield
        finally:
            sys.stdin = spot

    with fed("chaque pierre porte son mortier et le dit\n"):
        assert vplans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0
    assert vplans.main(["serve", "le-mur", "reference:", "README.md"]) == 0
    written = (vend / "plans" / "le-mur" / "PLAN.md").read_text(encoding="utf-8")
    assert "KMU1  chaque pierre porte son mortier et le dit" in written
    assert "serve: |\n  reference: README.md" in written
    assert "# PLAN `le-mur`" in written and "The wall." in written
    held("the framing writes its own sections",
         "`constrain` and `serve` land on a plan document through the engine's writer, "
         "imported by the vendored bootstrap -- the composition carries no author's package, "
         "and the body is untouched")

    # --- a law amends and retires BY ITS CODE; a retired code never returns ------------------
    mur = vend / "plans" / "le-mur" / "PLAN.md"
    with fed("KMU1  chaque pierre porte son mortier, et le dit\nla toiture suit\n"):
        assert vplans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0
    written = mur.read_text(encoding="utf-8")
    assert "  KMU1  chaque pierre porte son mortier, et le dit\n  KMU2  la toiture suit\n" in written
    assert written.count("KMU1") == 1
    with fed("KZZ9  nulle part\n"):
        refuse("code-unknown", lambda: vplans.main(["constrain", "le-mur", "--section", "production"]))
    assert vplans.main(["constrain", "le-mur", "--retire", "KMU1"]) == 0
    written = mur.read_text(encoding="utf-8")
    laws, kept = written.split("retired: |", 1)
    assert "KMU1" not in laws and "  KMU2  la toiture suit" in laws
    assert kept.startswith("\n  KMU1  retired ") and "-- chaque pierre porte son mortier, et le dit" in kept
    with fed("le sol tient\n"):
        assert vplans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0
    written = mur.read_text(encoding="utf-8")
    assert "  KMU3  le sol tient" in written and "KMU1  le sol" not in written
    assert vplans.main(["constrain", "le-mur", "--retire", "KMU2"]) == 0
    assert vplans.main(["constrain", "le-mur", "--retire", "KMU3"]) == 0
    written = mur.read_text(encoding="utf-8")
    assert "KMU2  la toiture" not in written.split("retired:")[0] and written.count("  retired ") == 3
    with fed("la nuit tombe\n"):
        assert vplans.main(["constrain", "le-mur", "KMU", "--section", "behavior"]) == 0
    written = mur.read_text(encoding="utf-8")
    assert "constraints.behavior: |\n  KMU4  la nuit tombe" in written
    assert vplans.main(["constrain", "le-mur", "--retire", "KMU4"]) == 0
    written = mur.read_text(encoding="utf-8")
    assert "constraints.behavior" not in written and written.count("  retired ") == 4
    with fed("encore\n"):
        assert vplans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0
    written = mur.read_text(encoding="utf-8")
    assert "  KMU5  encore" in written and "serve: |\n  reference: README.md" in written
    refuse("code-unknown", lambda: vplans.main(["constrain", "le-mur", "--retire", "KMU1"]))
    refuse("argument-missing", lambda: vplans.main(["constrain", "le-mur", "--retire"]))
    refuse("argument-unexpected", lambda: vplans.main(["constrain", "le-mur", "KMU", "--retire", "KMU4"]))
    assert vplans.check(vend) == []
    held("a law amends and retires by its code",
         "a piped line opening on a posed code replaces that law in place, a bare line derives the "
         "next code; `--retire` takes the law out (the emptied block with it) and keeps the code "
         "under `retired:` with its date and text -- KMU1 to KMU4 retired, the emptied behavior "
         "block gone with its key, the next code is KMU5; an unknown code refuses; the serve rows untouched")

    # --- a row is written the same by argv and by stdin, blanks inside brackets kept -------
    vreading = sys.modules["conductor"].reading
    tagged = ["reference:", "W.md[## Beta..## Gamma]", "NOTE.md"]
    vplans.write_section(vend, ["le-toit"], "Context", "The roof.")
    toit = vend / "plans" / "le-toit" / "PLAN.md"
    with fed(" ".join(tagged) + "\n"):
        assert vplans.main(["serve", "le-mur", "-"]) == 0
    assert vplans.main(["serve", "le-toit", *tagged]) == 0
    block = "serve: |\n  " + " ".join(tagged) + "\n"
    assert block in mur.read_text(encoding="utf-8") and block in toit.read_text(encoding="utf-8")
    assert vreading.serve_sections(vreading.read(mur)) == ((tuple(tagged),),)
    before = mur.read_bytes()
    with fed("reference: W.md[## Beta NOTE.md\n"):
        refuse("serve-range-malformed", lambda: vplans.main(["serve", "le-mur", "-"]))
    assert mur.read_bytes() == before
    said = io.StringIO()
    with contextlib.redirect_stdout(said), fed("code: x.py[10-40] x.py[def a..def b]\n"):
        assert vplans.main(["serve", "le-toit", "-"]) == 0
    assert said.getvalue().count("x.py[10-40]") == 1 and "x.py[def a" not in said.getvalue()
    assert vplans.check(vend) == []
    held("a row is written the same by argv and by stdin",
         "a piped token keeps the blanks inside its brackets: the same block by both ways, read "
         "back by the engine's reader in as many tokens; an open bracket refuses and leaves the "
         "bytes; the answer names the line range alone")

    # --- a plan is BORN with the blueprint law, under a code of its own ---------------
    born = instance()
    plans.write_section(born, ["le-mur-du-jardin"], "Context", "The wall.")
    plans.write_section(born, ["la-toiture"], "Context", "The roof.")
    first = (born / "plans" / "le-mur-du-jardin" / "PLAN.md").read_text(encoding="utf-8")
    second = (born / "plans" / "la-toiture" / "PLAN.md").read_text(encoding="utf-8")
    codes = [one.split()[0] for text in (first, second)
             for one in text.splitlines() if "BLUEPRINT, never a history manual" in one]
    assert "constraints.production: |" in first and "constraints.production: |" in second
    assert len(codes) == 2 and codes[0] != codes[1], codes
    assert codes == ["KLMD1", "KLT1"], codes
    held("a plan is born with its blueprint law",
         "the template carries the rule and the script derives its code from the slug -- "
         f"{codes[0]} and {codes[1]}: two plans of one instance never declare the same code")

    # --- the verifier: plan's own families, an ADDRESS that resolves (batch
    # plan-declare-ses-vecteurs) -- a born plan, a born phase, a PREPARED batch pass; an
    # unknown address, a depth that does not fit its family, a foreign family refuse
    vroot = instance()
    vp = load_script(next((vroot / ".sys" / "vendor").glob("plan@*")) / "skills" / "pp-plan" / "pp-plan.py")
    for name, prose in (("Context", "A plan to verify."), ("Target", "Its target."),
                        ("Expected", "What it frames."), ("Items", "- socle -- the base course\n")):
        vp.write_section(vroot, ["verif"], name, prose)
    for name, prose in (("Ground", "The ground of the base."), ("Target", "Its target."),
                        ("Expected", "What it frames."), ("Items", "- b1 -- the first batch\n")):
        vp.write_section(vroot, ["verif", "socle"], name, prose)
    for vector in ("plan:verif", "plan-phase:verif/socle", "plan-lot:verif/socle/b1"):
        with fed(vector + "\n"):
            assert vp.main(["verify"]) == 0, vector
    with fed("plan:nulle-part\n"):
        refuse("path-unknown", lambda: vp.main(["verify"]))
    with fed("plan-lot:verif/socle/nowhere\n"):
        refuse("path-unknown", lambda: vp.main(["verify"]))
    with fed("plan-phase:verif\n"):
        refuse("address-depth", lambda: vp.main(["verify"]))
    with fed("thread:piscine\n"):
        refuse("family-foreign", lambda: vp.main(["verify"]))
    refuse("argument-unexpected", lambda: vp.main(["verify", "verif"]))
    held("the verifier answers for plan's own families",
         "plan:, plan-phase: and plan-lot: are ADDRESSES: a born plan, a born phase and a batch merely "
         "PREPARED in its parent's Items pass; an unknown address refuses with the resolver's "
         "reason, a depth that does not fit its family and a foreign family refuse by name -- "
         "read-only, the vector on stdin, no argument")

    return 0
