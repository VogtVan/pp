"""packages/plan/skills/pp-plan -- the GRAMMAR of the plans keeper, lived on a real
environment carrying the plan package: a plan born by its Context, an item prepared in
Items and born at its first section, the order guided, a log appended, a `##` refused and
a `###` kept, a section removed by its rank; the statuses DEDUCED from the writing
(Expected frames, Delivery delivers and the closing rises, a framing section rewritten on
a done node reopens, `done` checks a todo off, `block` says a stop); the next move walking
them, judged by its kind, its word and its vector; the derived list, the correctives of the keeper (Items --append, a move under a done
phase, the announce of repair), the lint that
catches a hand edit and the repair that mends what is mechanical, the titles, move and
rename. Every refusal red by its name."""
from __future__ import annotations

import json

from conductor.core import document
from tests.harness import support

P = support(__file__, "plan")
GROUND, TARGET, EXPECTED, TESTS = P.GROUND, P.TARGET, P.EXPECTED, P.TESTS


def scenario(bench) -> int:
    refuse = bench.expect_exit
    root = P.house(bench, "plan-lived").made          # the plans lived by the script alone
    drift = P.house(bench, "plan-drifted").made       # the plans a hand edits behind it
    plans = P.script(root)
    w = P.Writer(plans)
    section, framed, frame, deliver = w.section, w.framed, w.frame, w.deliver
    prepare, grow, todo = w.prepare, w.grow, w.todo

    def case(label, detail=""):
        return P.case(bench, label, detail)

    def front(path):
        return P.front(plans, path)

    def kids(path):
        return P.kids(plans, path)

    def title_line(path):
        return P.title_line(plans, path)

    def untitled(path):
        return P.untitled(plans, path)

    def clean(base, slug):
        return P.of(plans.check(base), slug) == []

    def addresses(said):
        """-> the address each line of `status` opens on, its foot left out."""
        return [one.split()[0] for one in said.splitlines() if one.strip() and not one.startswith("+")]

    demo = root / "plans" / "demo"

    # --- births: the plan by its Context, the others prepared then born ------------------
    context = "The demo plan.\n\nIts thesis, in prose."
    with case("a plan is born by its Context", "PLAN.md stands on the template, the brief under Context, no phase yet") as c:
        path, said = section(root, ["demo"], "Context", context)
        c.ok(said == ["born"] and (demo / "PLAN.md").is_file(), f"said {said}")
        body = plans.read(path)[1]
        c.ok(plans.section_text(body, "Context").strip() == context and "Items" in dict(plans.split_sections(body)),
             "Context or Items")

    refuse("section-order", lambda: section(root, ["demo"], "Items", "- survey -- Survey first"))
    bench.held("the order guides", "Items waits Target and Expected -- section-order names the missing one")

    survey_brief = "Survey first: the inventory phase"
    with case("Items prepares a child", "the entry derived `item.1: survey  todo`, no folder, no document") as c:
        prepare(root, ["demo", "survey"], survey_brief)
        c.ok(plans.children(front(demo / "PLAN.md")) == [("survey", "todo")], "the entry")
        c.ok(not (demo / "1-survey").exists(), "a folder born")

    with case("the first section births the item", "the folder indexed, the document on the template, the line's brief as Context") as c:
        path, said = section(root, ["demo", "survey"], "Ground", GROUND)
        c.ok(said == ["born", "replaced"] and path == demo / "1-survey" / "PHASE.md", f"said {said} at {path}")
        body = plans.read(path)[1]
        c.ok(plans.section_text(body, "Context").strip() == survey_brief, "the brief as Context")
        c.ok(plans.section_text(body, "Ground").strip() == GROUND, "the Ground")

    with case("the order lives in the keys", "item.1 survey, item.2 build -- the keys follow the lines") as c:
        prepare(root, ["demo", "build"], "Then build")
        c.ok([one[0] for one in plans.children(front(demo / "PLAN.md"))] == ["survey", "build"], "the order")

    with case("a batch grows under its phase", "prepared in the phase's Items, born at its Ground") as c:
        grow(root, ["demo", "survey", "map"], "Map the ground")
        c.ok([one[0] for one in plans.children(front(demo / "1-survey" / "PHASE.md"))] == ["map"], "the entry")
        c.ok((demo / "1-survey" / "1-map" / "BATCH.md").is_file(), "the batch's document")

    batch = demo / "1-survey" / "1-map" / "BATCH.md"
    with case("the todos are the batch's Items", "one line each, the entries derived, nothing else in the body") as c:
        todo(root, ["demo", "survey", "map"], "list-sources", "list the sources")
        todo(root, ["demo", "survey", "map"], "read-whole", "read them whole")
        c.ok(plans.children(front(batch)) == [("list-sources", "todo"), ("read-whole", "todo")], "the entries")
        c.ok(plans.section_text(plans.read(batch)[1], "Items").strip()
             == "- list-sources -- list the sources\n- read-whole -- read them whole", "the Items lines")

    with case("Expected frames the node", "written on a todo node it is `doing`, its parent line follows -- "
              "deduced, no verb; a second Expected moves nothing") as c:
        again = demo / "1-survey" / "2-again" / "BATCH.md"
        grow(root, ["demo", "survey", "again"], "A second batch")      # born by its Ground, todo
        section(root, ["demo", "survey", "again"], "Target", TARGET)
        c.ok(front(again)["status"] == "todo", "todo before Expected")
        _, said = section(root, ["demo", "survey", "again"], "Expected", EXPECTED)
        c.ok(P.moves(said).get("demo/survey/again", P.Move("", (), "")).status == "doing", f"said {said}")
        c.ok(front(again)["status"] == "doing" and kids(demo / "1-survey" / "PHASE.md")["again"] == "doing",
             "the document and its parent line")
        _, said = section(root, ["demo", "survey", "again"], "Expected", EXPECTED + " again")
        c.ok(P.moves(said) == {}, f"a second Expected moved {said}")

    with case("done checks a todo off", "list-sources done, read-whole untouched, the batch still doing; "
              "`done` on a node refuses -- a node closes by its work") as c:
        plans.done(root, ["demo", "survey", "map", "list-sources"])
        c.ok(plans.children(front(batch))[0][1] == "done" and front(batch)["status"] == "doing", "the statuses")
        refuse("done-invalid", lambda: plans.done(root, ["demo", "survey", "map"]))

    lines = "- list-sources -- list the sources\n- read-whole -- read them whole"
    with case("Items is rewritten, the entries follow", "a line added enters todo, a known one keeps its status, "
              "a todo line removed leaves, a delivered one refuses item-engaged -- and a Delivery over an "
              "open todo refuses items-open, naming it") as c:
        section(root, ["demo", "survey", "map"], "Items", lines + "\n- one-more -- a later step")
        c.ok(plans.children(front(batch)) == [("list-sources", "done"), ("read-whole", "todo"), ("one-more", "todo")],
             "a line added")
        section(root, ["demo", "survey", "map"], "Items", lines)
        c.ok(plans.children(front(batch)) == [("list-sources", "done"), ("read-whole", "todo")], "a line removed")
        out = refuse("item-engaged", lambda: section(root, ["demo", "survey", "map"], "Items", "- read-whole -- read them whole"))
        c.ok("list-sources" in out and "done" in out, "item-engaged names the delivered todo")
        section(root, ["demo", "survey", "map"], "Tests", TESTS)
        out = refuse("items-open", lambda: section(root, ["demo", "survey", "map"], "Delivery", "too soon"))
        c.ok("read-whole" in out, "items-open names the open todo")

    with case("a born child never leaves Items", "the entry stays while its folder stands -- item-engaged") as c:
        out = refuse("item-engaged", lambda: section(root, ["demo"], "Items", "- build -- Then build"))
        c.ok("survey" in out and "born" in out, "the born child named")

    with case("the list derives from front matters", "the open plans with their next move, the closed counted and "
              "listed by --all; a plan's nodes one line each, its todos counted, a prepared item apart; the text and "
              "the data say the same nodes; --engaged the open plans and their engaged nodes; every vector resolves; nothing "
              "written") as c:
        section(root, ["shut"], "Context", "A plan delivered.")
        w.prepare(root, ["shut", "only"], "its one phase")
        w.framed(root, ["shut", "only"])
        w.close_phase(root, ["shut", "only"])
        tree = {one: one.read_bytes() for one in sorted((root / "plans").rglob("*")) if one.is_file()}
        said = P.play(plans, ["status"])
        overview = json.loads(P.play(plans, ["status", "--json"]))
        c.ok([one["address"] for one in overview] == ["demo"], f"the open plans {overview}")
        c.ok(overview and overview[0]["children"] == {"done": 0, "open": 1, "prepared": 1}, "the progress on the born")
        c.ok(overview and overview[0]["next"] == plans.next_move(root, "demo"), "the next move")
        c.ok(addresses(said) == ["demo"] and "shut" in said.splitlines()[-1], f"the text {said!r}")
        every = json.loads(P.play(plans, ["status", "--all", "--json"]))
        c.ok([(one["address"], one["status"]) for one in every] == [("demo", "doing"), ("shut", "done")], "--all")
        c.ok(every[-1].get("next") is None, "a closed plan has no next move")
        detail = json.loads(P.play(plans, ["status", "demo", "--json"]))
        c.ok([(one["address"], one["kind"]) for one in detail] == [
            ("demo", "plan"), ("demo/survey", "phase"), ("demo/survey/map", "batch"), ("demo/survey/again", "batch"),
            ("demo/build", "phase")], f"the nodes {[one['address'] for one in detail]}")
        nodes = {one["address"]: one for one in detail}
        c.ok(nodes.get("demo/survey/map", {}).get("todos") == {"done": 1, "total": 2}, "the todos counted")
        c.ok(nodes.get("demo/build", {}).get("born") is False and nodes.get("demo/survey", {}).get("born") is True,
             "the prepared phase apart")
        c.ok(addresses(P.play(plans, ["status", "demo"])) == list(nodes), "the text and the data, one order")
        for one in detail:
            plans.verify(root, one["vector"])
        engaged = json.loads(P.play(plans, ["status", "--engaged", "--json"]))
        c.ok([one["address"] for one in engaged] == ["demo", "demo/survey", "demo/survey/map", "demo/survey/again"],
             f"--engaged {[one['address'] for one in engaged]}")
        c.ok(addresses(P.play(plans, ["status", "--engaged"])) == [one["address"] for one in engaged],
             "--engaged: the text and the data, one order")
        refuse("argument-unexpected", lambda: P.play(plans, ["status", "demo", "--engaged"]))
        c.ok({one: one.read_bytes() for one in sorted((root / "plans").rglob("*")) if one.is_file()} == tree,
             "status wrote")

    with case("check clean on a lived plan", "structure, statuses, numbering, prose all agree -- a prepared todo is no finding") as c:
        c.ok(plans.check(root) == [], "findings")

    with case("check catches the hand", "a hand-edited status reddens by name") as c:
        doc = demo / "1-survey" / "PHASE.md"
        kept = doc.read_text(encoding="utf-8")
        doc.write_text(kept.replace("doing", "cooking"), encoding="utf-8")
        c.ok(any("cooking" in one for one in plans.check(root)), "the status unnamed")
        doc.write_text(kept, encoding="utf-8")

    # --- the sections: replace, insert at rank, append, the tail, the refusals -------------
    def names():
        return [n for n, _ in plans.split_sections(plans.read(demo / "PLAN.md")[1])]

    with case("a section is replaced or inserted at its rank", "Target rewritten in place; Survey born between Context and Target") as c:
        c.ok(section(root, ["demo"], "Target", "The target, rewritten.")[1] == ["replaced"], "Target replaced")
        c.ok(section(root, ["demo"], "Survey", "The ground, seen.")[1] == ["inserted"], "Survey inserted")
        order = names()
        c.ok(order.index("Survey") == order.index("Context") + 1 and order.index("Survey") < order.index("Target"),
             f"order {order}")

    with case("a log appends, the tail is open", "Decisions grows by dated lines; a name beyond the list lands last, "
              "replaced or appended by the flag") as c:
        first, second = "- 2026-09-05 : the first word", "- 2026-09-06 : the second word"
        c.ok(section(root, ["demo"], "Decisions", first)[1] == ["inserted"], "the first log line")
        c.ok(section(root, ["demo"], "Decisions", second)[1] == ["appended"], "the second log line")
        c.ok(f"{first}\n\n{second}" in plans.section_text(plans.read(demo / "PLAN.md")[1], "Decisions"), "the log")
        c.ok(section(root, ["demo"], "Keep track", "a line of the plan's own")[1] == ["inserted"]
             and names()[-1] == "Keep track", "the tail")
        c.ok(section(root, ["demo"], "Keep track", "one more", append=True)[1] == ["appended"], "the flag")

    refuse("section-unknown", lambda: section(root, ["demo", "survey", "map"], "Todos", "- x -- y"))
    refuse("prose-missing", lambda: section(root, ["demo"], "Target", "   \n"))
    refuse("section-order", lambda: section(root, ["demo", "build"], "Target", TARGET))
    refuse("section-order", lambda: plans.write_section(root, ["demo", "build"], "Delivery", "x"))
    refuse("item-line-malformed", lambda: section(root, ["demo", "survey", "map"], "Items", "- T9 -- a tag, not a name"))
    refuse("slug-taken", lambda: section(root, ["demo", "survey", "map"], "Items", "- read-whole -- a\n- read-whole -- b"))
    bench.held("the section refusals hold", "section-unknown (Todos), prose-missing, section-order on a prepared item "
               "and on a log before the framing, item-line-malformed, slug-taken")

    # --- a subtitle inside a section: `##` refused before any write, `###` written -------
    hdoc = root / "plans" / "heads" / "PLAN.md"
    section(root, ["heads"], "Context", "A plan whose prose carries subtitles.")
    framed(root, ["heads"])
    section(root, ["heads"], "Keep track", "a line of the plan's own")
    with case("a `##` in the prose refuses before any write", "prose-heading on a section replaced, inserted, a "
              "log, the flag, a code block, a prepared item -- the bytes unchanged, no folder born") as c:
        sneaks = (("Target", "The target.\n\n## Sneaked\n\nmore", False),           # a section replaced
                  ("Protocol", "## Sneaked\n\nthe method", False),                  # a section inserted
                  ("Decisions", "- 2026-09-13 : a word\n## Sneaked", False),         # a log
                  ("Keep track", "one more\n## Sneaked", True),                     # the flag
                  ("Target", "```\n## Sneaked in a code block\n```", False))        # a code block
        for name, prose, append in sneaks:
            before = hdoc.read_bytes()
            out = refuse("prose-heading", lambda: section(root, ["heads"], name, prose, append))
            c.ok("## Sneaked" in out and "###" in out, f"{name}: the heading and the way")
            c.ok(hdoc.read_bytes() == before, f"{name}: bytes moved")
        prepare(root, ["heads", "later"], "A phase to come")
        before = hdoc.read_bytes()
        refuse("prose-heading", lambda: section(root, ["heads", "later"], "Ground", "The ground.\n## Sneaked"))
        c.ok(hdoc.read_bytes() == before and not list((root / "plans" / "heads").glob("*-later")), "a folder born")

    def headings():
        return [n for n, _ in plans.split_sections(plans.read(hdoc)[1]) if n is not None]

    counted = headings()
    with case("a `###` subtitle stays in its section", f"{len(counted)} sections before, after the write, after the "
              "rewrite -- nothing left behind; the engine's reader and check read it clean") as c:
        section(root, ["heads"], "Target", "The target.\n\n### One\n\nfirst\n\n### Two\n\nsecond")
        c.ok(headings() == counted, "a section born of a subtitle")
        section(root, ["heads"], "Target", "The target, again.\n\n### Three\n\n### Four\n\n### Five")
        c.ok(headings() == counted and "### Two" not in hdoc.read_text(encoding="utf-8"), "a subtitle left")
        c.ok(document.read(hdoc).front["slug"] == "heads" and clean(root, "heads"), "the reader or check")

    with case("check says a section twice", "a hand-doubled Target reddens by name, repair mends nothing and says the gesture; the document restored is clean") as c:
        text = hdoc.read_text(encoding="utf-8")
        hdoc.write_text(text + "\n## Target\n\nA leftover.\n", encoding="utf-8")
        found = P.of(plans.check(root), "heads")
        c.ok(any("`Target`" in one and "twice" in one for one in found), f"findings {found}")
        doubled = hdoc.read_bytes()
        mended, left = plans.repair(root)
        c.ok(P.of(mended, "heads") == [] and hdoc.read_bytes() == doubled, f"mended {mended}")
        c.ok(any("section `Target`" in one and "--remove=<n>" in one for one in P.of(left, "heads")), f"left {left}")
        hdoc.write_text(text, encoding="utf-8")
        c.ok(clean(root, "heads"), "restored")

    # --- a section removed: the occurrence the call names, and nothing else ---------------
    cdoc = root / "plans" / "cuts" / "PLAN.md"
    section(root, ["cuts"], "Context", "A plan whose documents carry leftovers.")
    framed(root, ["cuts"])
    section(root, ["cuts"], "Decisions", "- 2026-09-13 : the one word")
    with case("a section beyond the list is removed", "the document is byte for byte the one written without it") as c:
        before = cdoc.read_bytes()
        section(root, ["cuts"], "Keep track", "a line of the plan's own")
        _, said = plans.remove_section(root, ["cuts"], "Keep track", None)
        c.ok(cdoc.read_bytes() == before, "the bytes")
        c.ok("Keep track" in said and "1 of 1" in said, f"said {said}")

    text = cdoc.read_text(encoding="utf-8")
    with case("a doubled section is removed by its rank", "section-ambiguous lists each occurrence with its size "
              "and first line; --remove=1 takes the empty log, =2 the stale list, =2 a doubled Target; a rank "
              "beyond refuses section-unknown") as c:
        cdoc.write_text(text + "## Le log\n\n(à la livraison)\n\n## Le log\n\n- 2026-08-29 -- the journal\n",
                        encoding="utf-8")
        doubled = cdoc.read_bytes()
        out = refuse("section-ambiguous", lambda: plans.remove_section(root, ["cuts"], "Le log", None))
        c.ok("1:" in out and "(à la livraison)" in out and "2:" in out and "the journal" in out, f"listed {out}")
        refuse("section-unknown", lambda: plans.remove_section(root, ["cuts"], "Le log", 3))
        c.ok(cdoc.read_bytes() == doubled, "a refusal wrote")
        plans.remove_section(root, ["cuts"], "Le log", 1)
        c.ok(cdoc.read_text(encoding="utf-8") == text + "## Le log\n\n- 2026-08-29 -- the journal\n", "=1 on the log")
        cdoc.write_text(text + "## Todos\n\n- a -- the list\n\n## Todos\n\n- a -- a stale list\n", encoding="utf-8")
        plans.remove_section(root, ["cuts"], "Todos", 2)
        c.ok(cdoc.read_text(encoding="utf-8") == text + "## Todos\n\n- a -- the list\n\n", "=2 on the list")
        cdoc.write_text(text + "## Target\n\nA leftover.\n", encoding="utf-8")
        plans.remove_section(root, ["cuts"], "Target", 2)
        c.ok(cdoc.read_text(encoding="utf-8") == text, "=2 on Target")

    with case("what must stay stays", "section-kept on a listed section standing once (Target, a log), "
              "section-unknown on an absent name, path-unknown on a prepared item -- the bytes unchanged") as c:
        for name in ("Target", "Decisions"):
            refuse("section-kept", lambda: plans.remove_section(root, ["cuts"], name, None))
        refuse("section-unknown", lambda: plans.remove_section(root, ["cuts"], "Ghost", None))
        c.ok(cdoc.read_text(encoding="utf-8") == text, "the bytes")
        prepare(root, ["cuts", "later"], "A phase to come")
        before = cdoc.read_bytes()
        refuse("path-unknown", lambda: plans.remove_section(root, ["cuts", "later"], "Ground", None))
        c.ok(cdoc.read_bytes() == before, "the bytes after path-unknown")

    with case("the removal reads back clean", "the engine's reader and check after every removal; repair names "
              "`section … --remove=<n>` for a doubled section") as c:
        before = cdoc.read_bytes()
        c.ok(document.read(cdoc).front["slug"] == "cuts" and clean(root, "cuts"), "the reader or check")
        cdoc.write_text(before.decode("utf-8") + "## Target\n\nA leftover.\n", encoding="utf-8")
        _, left = plans.repair(root)
        c.ok(any("section `Target`" in one and "--remove=<n>" in one for one in P.of(left, "cuts")), f"left {left}")
        cdoc.write_bytes(before)

    with case("the address refusals teach", "a numbered folder says the bare address, an absent entry says "
              "Items, a prepared item says its first section; an absent todo") as c:
        refuse("path-unknown", lambda: section(root, ["ghost", "p1"], "Ground", GROUND))
        out = refuse("path-unknown", lambda: plans.doc_of(root, "demo", "1-survey", "1-map"))
        c.ok("FOLDER" in out and "demo/survey" in out, "the bare address")
        out = refuse("path-unknown", lambda: plans.doc_of(root, "demo", "nope"))
        c.ok("prepare it" in out, "Items said")
        refuse("path-unknown", lambda: plans.block(root, ["demo", "build"], "not yet"))
        refuse("path-unknown", lambda: plans.done(root, ["demo", "survey", "map", "ghost-step"]))

    broken = demo / "PLAN.md"
    text = broken.read_text(encoding="utf-8")
    broken.write_text(text.replace("---", "-!-", 1), encoding="utf-8")
    refuse("frontmatter-malformed", lambda: plans.read(broken))
    bench.held("frontmatter-malformed refuses", "the script trusts only what it wrote")
    broken.write_text(text, encoding="utf-8")

    # --- the next move walks the statuses, prepared items included -------------------------
    story = root / "plans" / "story"
    section(root, ["story"], "Context", "A tale of a plan.")
    with case("a prepared phase says its move", "no document yet, the entry walks: awaits its framing; framed -> create the batches") as c:
        c.ok(P.move_of(plans.next_move(root, "story")) == ("plan", "phases", "plan:story"), "no phase")
        prepare(root, ["story", "p1"], "First phase")
        c.ok(P.move_of(plans.next_move(root, "story")) == ("phase", "framing", "plan-phase:story/p1"), "prepared")
        frame(root, ["story", "p1"])
        c.ok(P.move_of(plans.next_move(root, "story")) == ("phase", "batches", "plan-phase:story/p1"), "framed")

    with case("the next move walks true", "no phase -> awaits framing -> awaits implementation -> "
              "the Delivery closes batch, phase and plan by the script -> None; every line ends with "
              "the vector of the node it names -- plan:, plan-phase:, plan-lot:") as c:
        prepare(root, ["story", "p1", "b1"], "First batch")
        c.ok(P.move_of(plans.next_move(root, "story")) == ("batch", "framing", "plan-lot:story/p1/b1"), "prepared")
        frame(root, ["story", "p1", "b1"])
        c.ok(P.move_of(plans.next_move(root, "story")) == ("batch", "implementation", "plan-lot:story/p1/b1"), "framed")
        said = P.moves(deliver(root, ["story", "p1", "b1"]))
        moved = said.get("story/p1/b1", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == ("story/p1", "story"), f"said {said}")
        c.ok(plans.next_move(root, "story") is None, "a move after the closing")

    with case("a framing section rewritten reopens", "Target on a done batch under a closed plan turns it "
              "redo and raises phase and plan with it -- the next move names the batch; a Decisions line "
              "reopens nothing") as c:
        _, said = section(root, ["story", "p1", "b1"], "Target", "reworked")
        c.ok(P.moves(said).get("story/p1/b1", P.Move("", (), "")).status == "redo", f"said {said}")
        c.ok(front(story / "1-p1" / "1-b1" / "BATCH.md")["status"] == "redo"
             and front(story / "1-p1" / "PHASE.md")["status"] == "redo"
             and front(story / "PLAN.md")["status"] == "doing", "the statuses")
        c.ok(kids(story / "1-p1" / "PHASE.md")["b1"] == "redo" and kids(story / "PLAN.md")["p1"] == "redo", "the entries")
        c.ok(P.move_of(plans.next_move(root, "story")) == ("batch", "rework", "plan-lot:story/p1/b1"), "the move")
        c.ok(clean(root, "story"), "check")
        _, said = section(root, ["story", "p1", "b1"], "Decisions", "- a dated word")
        c.ok(P.moves(said) == {}, f"a log moved {said}")

    # --- the closing rises ----------------------------------------------------------------
    casc = root / "plans" / "casc"
    with case("Delivery closes its batch", "the last todo checked off closes nothing; the Delivery does, "
              "and a sibling batch still todo stops the closing at the phase") as c:
        section(root, ["casc"], "Context", "The closing rises.")
        grow(root, ["casc", "p1"], "Phase one")
        prepare(root, ["casc", "p2"], "Phase two")
        grow(root, ["casc", "p1", "b1"], "Batch one")
        prepare(root, ["casc", "p1", "b2"], "Batch two")
        todo(root, ["casc", "p1", "b1"], "first-step", "the first step")
        todo(root, ["casc", "p1", "b1"], "last-step", "the last step")
        frame(root, ["casc", "p1", "b1"])
        plans.done(root, ["casc", "p1", "b1", "first-step"])
        plans.done(root, ["casc", "p1", "b1", "last-step"])
        c.ok(front(casc / "1-p1" / "1-b1" / "BATCH.md")["status"] == "doing", "a todo closed the batch")
        said = P.moves(deliver(root, ["casc", "p1", "b1"]))
        moved = said.get("casc/p1/b1", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == (), f"said {said}")
        c.ok(front(casc / "1-p1" / "1-b1" / "BATCH.md")["status"] == "done"
             and kids(casc / "1-p1" / "PHASE.md")["b1"] == "done", "the batch")
        c.ok(front(casc / "1-p1" / "PHASE.md")["status"] == "doing" and clean(root, "casc"), "the phase")

    with case("block says a stop, the writing lifts it", "blocked with its dated Decisions line; the next framing "
              "section lifts it (todo before Expected, doing after); the second batch delivered closes the phase") as c:
        reason = "the store is not there yet"
        b2 = casc / "1-p1" / "2-b2" / "BATCH.md"
        section(root, ["casc", "p1", "b2"], "Ground", GROUND)
        plans.block(root, ["casc", "p1", "b2"], reason)
        decisions = plans.section_text(plans.read(b2)[1], "Decisions")
        c.ok(front(b2)["status"] == "blocked" and f"blocked -- {reason}" in decisions, "the block")
        _, said = section(root, ["casc", "p1", "b2"], "Target", TARGET)
        c.ok(P.moves(said).get("casc/p1/b2", P.Move("", (), "")).status == "todo", f"lifted {said}")
        frame(root, ["casc", "p1", "b2"])
        said = P.moves(deliver(root, ["casc", "p1", "b2"]))
        c.ok(said.get("casc/p1/b2", P.Move("", (), "")).closes == ("casc/p1",), f"said {said}")
        c.ok(P.move_of(plans.next_move(root, "casc")) == ("phase", "framing", "plan-phase:casc/p2"), "the move")

    with case("the closing rises to the plan", "the Delivery of the last batch of the last phase closes "
              "batch, phase and plan in one call -- a blocked parent closes like the others, every line "
              "and document agree, check clean") as c:
        section(root, ["casc", "p2"], "Ground", GROUND)          # the prepared phase is born
        grow(root, ["casc", "p2", "b3"], "Batch three")
        todo(root, ["casc", "p2", "b3"], "only-step", "the only step")
        frame(root, ["casc", "p2", "b3"])
        plans.block(root, ["casc", "p2"], "waits the store")
        plans.done(root, ["casc", "p2", "b3", "only-step"])
        said = P.moves(deliver(root, ["casc", "p2", "b3"]))
        c.ok(said.get("casc/p2/b3", P.Move("", (), "")).closes == ("casc/p2", "casc"), f"said {said}")
        c.ok(front(casc / "PLAN.md")["status"] == "done" and kids(casc / "PLAN.md") == {"p1": "done", "p2": "done"},
             "the plan")
        c.ok(front(casc / "2-p2" / "PHASE.md")["status"] == "done" and kids(casc / "2-p2" / "PHASE.md")["b3"] == "done",
             "the phase")
        c.ok(plans.next_move(root, "casc") is None and clean(root, "casc"), "the move or check")

    with case("the rework cascades again", "a new todo in Items reopens the delivered batch and lifts the "
              "ancestry; its Delivery closes it back down to the plan -- the cycle round-trips") as c:
        todo(root, ["casc", "p2", "b3"], "one-more", "one more step")     # Items on a done batch reopens it
        c.ok(front(casc / "PLAN.md")["status"] == "doing" and kids(casc / "PLAN.md")["p2"] == "redo"
             and front(casc / "2-p2" / "1-b3" / "BATCH.md")["status"] == "redo", "the reopening")
        plans.done(root, ["casc", "p2", "b3", "one-more"])
        said = P.moves(deliver(root, ["casc", "p2", "b3"], "reworked"))
        c.ok(said.get("casc/p2/b3", P.Move("", (), "")).closes == ("casc/p2", "casc"), f"said {said}")
        c.ok(plans.next_move(root, "casc") is None and clean(root, "casc"), "the move or check")

    with case("engagement primes order", "a doing phase behind a todo phase is served; an engaged "
              "batch behind a todo batch is served; none engaged falls back to the first todo") as c:
        section(root, ["prio"], "Context", "Engagement primes order.")
        prepare(root, ["prio", "first"], "A phase never started")
        grow(root, ["prio", "second"], "A framed phase")
        frame(root, ["prio", "second"])
        c.ok(P.move_of(plans.next_move(root, "prio")) == ("phase", "batches", "plan-phase:prio/second"), "the phase")
        prepare(root, ["prio", "second", "b1"], "A batch never started")
        grow(root, ["prio", "second", "b2"], "An engaged batch")
        frame(root, ["prio", "second", "b2"])
        c.ok(P.move_of(plans.next_move(root, "prio")) == ("batch", "implementation", "plan-lot:prio/second/b2"),
             "the engaged batch")
        deliver(root, ["prio", "second", "b2"])
        c.ok(P.move_of(plans.next_move(root, "prio")) == ("batch", "framing", "plan-lot:prio/second/b1"),
             "the first todo")

    # --- check and repair: the hand behind the script ------------------------------------
    xdoc = drift / "plans" / "x" / "PLAN.md"
    with case("repair mends what is mechanical", "a broken numbering, an entry against its document, a folder "
              "without its entry -- each said; check clean after") as c:
        section(drift, ["x"], "Context", "A plan to drift.")
        grow(drift, ["x", "a"], "A phase")
        grow(drift, ["x", "b"], "Another phase")
        xdoc.write_text(xdoc.read_text(encoding="utf-8").replace("item.2:", "item.4:"), encoding="utf-8")
        c.ok(any("numbering broken" in one for one in P.of(plans.check(drift), "x")), "the numbering")
        adoc = drift / "plans" / "x" / "1-a" / "PHASE.md"
        adoc.write_text(adoc.read_text(encoding="utf-8").replace("status: todo", "status: doing"), encoding="utf-8")
        xdoc.write_text(xdoc.read_text(encoding="utf-8").replace("item.1: a  todo", "item.1: a  blocked"), encoding="utf-8")
        xdoc.write_text(xdoc.read_text(encoding="utf-8").replace("item.4: b  todo\n", ""), encoding="utf-8")
        found = P.of(plans.check(drift), "x")
        c.ok(any("has no entry" in one for one in found)
             and any("blocked" in one and "doing" in one for one in found), f"findings {found}")
        mended, left = plans.repair(drift)
        mended = P.of(mended, "x")
        c.ok(len(mended) == 2 and any("the document wins" in one for one in mended)
             and any("had no entry" in one for one in mended), f"mended {mended}")
        c.ok(P.of(left, "x") == [] and clean(drift, "x"), f"left {left}")
        c.ok(plans.children(front(xdoc)) == [("a", "doing"), ("b", "todo")], "the entries")

    with case("a clean tree repairs nothing", "no mend, nothing left") as c:
        c.ok(plans.repair(drift) == ([], []), "a mend")

    tdoc = drift / "plans" / "old" / "1-p" / "1-b" / "BATCH.md"
    with case("repair says what it leaves", "a positional tag is not mechanical -- said with its gesture, untouched") as c:
        section(drift, ["old"], "Context", "A plan of the tag era.")
        grow(drift, ["old", "p"], "A phase")
        grow(drift, ["old", "p", "b"], "A batch")
        tfront, tbody = plans.read(tdoc)
        tfront["item.1"] = "T1  todo"
        plans.write(tdoc, tfront, tbody + "\n## Todos\n\n- T1 -- an old step\n")
        c.ok(any("positional tag" in one for one in P.of(plans.check(drift), "old")), "the tag")
        mended, left = plans.repair(drift)
        left = P.of(left, "old")
        c.ok(P.of(mended, "old") == [] and len(left) == 1 and "rewrite Items with slugs" in left[0], f"left {left}")

    with case("check wants the body line", "an entry without its `- <name> -- ...` line reddens") as c:
        todo(drift, ["old", "p", "b"], "real-step", "a named step")
        tfront, tbody = plans.read(tdoc)
        plans.write(tdoc, tfront, tbody.replace("- real-step -- a named step", ""))
        c.ok(any("real-step" in one and "line in the body" in one for one in P.of(plans.check(drift), "old")),
             "the body line")

    with case("the keeper reads derived folders alone", "__pycache__, playbooks/ and campaigns/ say nothing; "
              "a `<n>-<name>` folder without its entry reddens, and repair says it") as c:
        kept = drift / "plans" / "kept"
        section(drift, ["kept"], "Context", "A plan with its own material beside its nodes.")
        grow(drift, ["kept", "p"], "A phase")
        for one in (kept / "__pycache__", kept / "playbooks", kept / "1-p" / "campaigns"):
            one.mkdir()
        c.ok(clean(drift, "kept"), "a folder of the plan's own")
        (kept / "7-orphan").mkdir()
        found = P.of(plans.check(drift), "kept")
        c.ok(len(found) == 1 and "7-orphan" in found[0] and "has no entry" in found[0], f"findings {found}")
        mended, left = plans.repair(drift)
        left = P.of(left, "kept")
        c.ok(P.of(mended, "kept") == [] and len(left) == 1 and "7-orphan" in left[0], f"left {left}")

    kdoc = root / "plans" / "proclike" / "PLAN.md"
    with case("foreign keys survive the gestures", "constraints/serve verbatim across every section write and status move, check clean") as c:
        section(root, ["proclike"], "Context", "A plan that is also a proc.")
        foreign = ("constraints.behavior: |\n  K1  the script alone writes the structure\n"
                   "serve: engine/pp.py\n")
        kdoc.write_text(kdoc.read_text(encoding="utf-8").replace(
            "---\n\n# PLAN", foreign + "---\n\n# PLAN"), encoding="utf-8")
        section(root, ["proclike"], "Survey", "Seen.")
        grow(root, ["proclike", "p1"], "A phase")
        grow(root, ["proclike", "p1", "b1"], "A batch")
        todo(root, ["proclike", "p1", "b1"], "one-step", "one step")
        frame(root, ["proclike", "p1", "b1"])
        frame(root, ["proclike"])
        c.ok(foreign in kdoc.read_text(encoding="utf-8"), "the foreign keys")
        c.ok(clean(root, "proclike"), "check")

    with case("the emit is stable", "emitting twice yields the same text -- no drift, no loss") as c:
        kfront, kbody = plans.read(kdoc)
        once = plans.emit(kfront, kbody)
        plans.write(kdoc, kfront, kbody)
        c.ok(kdoc.read_text(encoding="utf-8") == once, "a drift")

    # --- move ------------------------------------------------------------------------------
    beta = root / "plans" / "beta"
    with case("move carries a phase across plans", "entry, folders and subtree keys land; both sides renumber") as c:
        section(root, ["alpha"], "Context", "Plan A.")
        section(root, ["beta"], "Context", "Plan B.")
        grow(root, ["alpha", "one"], "Phase one")
        grow(root, ["alpha", "two"], "Phase two")
        grow(root, ["alpha", "two", "job"], "A batch")
        todo(root, ["alpha", "two", "job"], "a-step", "a step")
        grow(root, ["beta", "home"], "Target phase")
        two_doc, job_doc = (root / "plans" / "alpha" / "2-two" / "PHASE.md",
                            root / "plans" / "alpha" / "2-two" / "1-job" / "BATCH.md")
        kept = [untitled(two_doc), untitled(job_doc)]
        c.ok("`alpha`" in title_line(two_doc) and "`alpha`" in title_line(job_doc), "the titles before")
        plans.move(root, ["alpha", "two"], ["beta"], "1")
        two_doc, job_doc = beta / "1-two" / "PHASE.md", beta / "1-two" / "1-job" / "BATCH.md"
        for doc, body in ((two_doc, kept[0]), (job_doc, kept[1])):
            c.ok(title_line(doc) == plans.title_of(front(doc)) and "`beta`" in title_line(doc)
                 and "`alpha`" not in title_line(doc) and untitled(doc) == body, f"{doc.name}: title or body")
        c.ok([one[0] for one in plans.children(front(beta / "PLAN.md"))] == ["two", "home"], "the target's entries")
        jfront = front(job_doc)
        c.ok(jfront["plan"] == "beta" and jfront["phase"] == "two", "the batch's keys")
        c.ok([one[0] for one in plans.children(front(root / "plans" / "alpha" / "PLAN.md"))] == ["one"],
             "the source's entries")
        c.ok((beta / "2-home").is_dir() and clean(root, "alpha") and clean(root, "beta"), "renumbered, check")

    with case("move carries the titles", "the moved phase and its batch say the new plan, the moved batch its "
              "new phase -- the title line alone rewritten, the rest of each body byte for byte") as c:
        kept = untitled(beta / "1-two" / "1-job" / "BATCH.md")
        plans.move(root, ["beta", "two", "job"], ["beta", "home"], "1")
        job_doc = beta / "2-home" / "1-job" / "BATCH.md"
        c.ok(title_line(job_doc) == plans.title_of(front(job_doc)) and "`home`" in title_line(job_doc), "the title")
        c.ok(untitled(job_doc) == kept, "the body")

    with case("move lands a batch in another phase", "the entry leaves, the batch keys follow, check stays clean") as c:
        c.ok([one[0] for one in plans.children(front(beta / "2-home" / "PHASE.md"))] == ["job"], "the landing")
        c.ok(plans.children(front(beta / "1-two" / "PHASE.md")) == [], "the leaving")
        c.ok(clean(root, "beta"), "check")

    with case("an intra-parent move reorders", "same parent, new rank, every folder re-derived") as c:
        grow(root, ["beta", "last"], "Third phase")
        plans.move(root, ["beta", "last"], ["beta"], "1")
        c.ok([one[0] for one in plans.children(front(beta / "PLAN.md"))] == ["last", "two", "home"], "the order")
        c.ok((beta / "1-last").is_dir() and (beta / "3-home").is_dir() and clean(root, "beta"), "the folders, check")

    refuse("path-unknown", lambda: plans.move(root, ["alpha", "ghost"], ["beta"], "1"))
    refuse("target-unknown", lambda: plans.move(root, ["beta", "two"], ["gamma"], "1"))
    refuse("index-invalid", lambda: plans.move(root, ["beta", "two"], ["beta"], "9"))
    refuse("kind-mismatch", lambda: plans.move(root, ["beta", "two"], ["beta", "home"], "1"))
    grow(root, ["alpha", "home"], "A homonym")
    refuse("slug-taken", lambda: plans.move(root, ["alpha", "home"], ["beta"], "1"))
    prepare(root, ["alpha", "ready"], "A prepared phase")
    refuse("path-unknown", lambda: plans.move(root, ["alpha", "ready"], ["beta"], "1"))
    bench.held("the move refusals hold", "path-unknown, target-unknown, index-invalid, kind-mismatch, slug-taken; "
               "a prepared item moves by its parent's Items, never by move")

    # --- rename: the name is the identity every entry, folder and key carries ---------------
    gamma = root / "plans" / "gamma"
    with case("rename carries the name everywhere", "the parent's entry at its rank, its Items line, the derived "
              "folder, `slug:` and the batches' `phase:` follow in one call -- check clean; a batch alike") as c:
        section(root, ["gamma"], "Context", "Plan G.")
        grow(root, ["gamma", "one"], "Phase one")
        grow(root, ["gamma", "one", "job"], "A batch")
        todo(root, ["gamma", "one", "job"], "a-step", "a step")
        grow(root, ["gamma", "two"], "Phase two")
        kept = [untitled(gamma / "1-one" / "PHASE.md"), untitled(gamma / "1-one" / "1-job" / "BATCH.md")]
        plans.rename(root, ["gamma", "one"], "uno")
        for doc, body in ((gamma / "1-uno" / "PHASE.md", kept[0]), (gamma / "1-uno" / "1-job" / "BATCH.md", kept[1])):
            c.ok(title_line(doc) == plans.title_of(front(doc)) and "`uno`" in title_line(doc)
                 and "`one`" not in title_line(doc) and untitled(doc) == body, f"{doc.name}: title or body")
        gfront, gbody = plans.read(gamma / "PLAN.md")
        c.ok([one[0] for one in plans.children(gfront)] == ["uno", "two"], "the entry")
        c.ok(("uno", "Phase one") in plans.item_lines(plans.section_text(gbody, "Items"))
             and "one" not in dict(plans.item_lines(plans.section_text(gbody, "Items"))), "the Items line")
        c.ok((gamma / "1-uno" / "PHASE.md").is_file() and not (gamma / "1-one").exists(), "the folder")
        ufront = front(gamma / "1-uno" / "PHASE.md")
        c.ok(ufront["slug"] == "uno" and ufront["status"] == "doing", "the phase's keys")
        jfront = front(gamma / "1-uno" / "1-job" / "BATCH.md")
        c.ok(jfront["phase"] == "uno" and jfront["plan"] == "gamma" and clean(root, "gamma"), "the batch's keys, check")
        kept = untitled(gamma / "1-uno" / "1-job" / "BATCH.md")
        plans.rename(root, ["gamma", "uno", "job"], "work")
        work_doc = gamma / "1-uno" / "1-work" / "BATCH.md"
        c.ok(title_line(work_doc) == plans.title_of(front(work_doc)) and "`work`" in title_line(work_doc)
             and untitled(work_doc) == kept, "the batch's title or body")
        ufront, ubody = plans.read(gamma / "1-uno" / "PHASE.md")
        c.ok([one[0] for one in plans.children(ufront)] == ["work"]
             and ("work", "A batch") in plans.item_lines(plans.section_text(ubody, "Items")), "the batch's entry")
        wfront = front(work_doc)
        c.ok(wfront["slug"] == "work" and [one[0] for one in plans.children(wfront)] == ["a-step"]
             and clean(root, "gamma"), "the batch's keys, check")

    with case("the rename refusals hold", "kind-mismatch (a plan, a todo), name-invalid (the grammar, the same "
              "name), slug-taken, path-unknown (absent, prepared) -- nothing written") as c:
        refuse("kind-mismatch", lambda: plans.rename(root, ["gamma"], "delta"))
        refuse("kind-mismatch", lambda: plans.rename(root, ["gamma", "uno", "work", "a-step"], "b-step"))
        refuse("name-invalid", lambda: plans.rename(root, ["gamma", "two"], "Two_Phase"))
        refuse("name-invalid", lambda: plans.rename(root, ["gamma", "two"], "two"))
        refuse("slug-taken", lambda: plans.rename(root, ["gamma", "two"], "uno"))
        refuse("path-unknown", lambda: plans.rename(root, ["gamma", "ghost"], "spirit"))
        prepare(root, ["gamma", "ready"], "A prepared phase")
        refuse("path-unknown", lambda: plans.rename(root, ["gamma", "ready"], "steady"))
        c.ok(clean(root, "gamma"), "check")

    # --- the title line: check sees a wrong one, repair sets it, a free title is left ----------
    with case("check sees a title that lies, repair sets it", "a wrong plan, a doubled `# BATCH`, a missing title "
              "redden by document; repair sets the three and says them, the rest of each body byte for byte; "
              "a free title is neither judged nor touched") as c:
        section(root, ["tp"], "Context", "A plan whose titles drift.")
        grow(root, ["tp", "ph"], "A phase")
        grow(root, ["tp", "ph", "bt"], "A batch")
        grow(root, ["tp", "ph", "bare"], "A batch without title")
        tp = root / "plans" / "tp"
        tdocs = {"plan": tp / "PLAN.md", "phase": tp / "1-ph" / "PHASE.md",
                 "bt": tp / "1-ph" / "1-bt" / "BATCH.md", "bare": tp / "1-ph" / "2-bare" / "BATCH.md"}
        c.ok(clean(root, "tp"), "check before")
        kept = {name: untitled(doc) for name, doc in tdocs.items()}

        def retitle(doc, old, new):
            doc.write_text(doc.read_text(encoding="utf-8").replace(old + "\n", new, 1), encoding="utf-8")

        retitle(tdocs["plan"], title_line(tdocs["plan"]), "# TP -- a free title of the author's\n")
        free = tdocs["plan"].read_bytes()
        retitle(tdocs["phase"], title_line(tdocs["phase"]), title_line(tdocs["phase"]).replace("`tp`", "`wrong`") + "\n")
        retitle(tdocs["bt"], title_line(tdocs["bt"]), title_line(tdocs["bt"]).replace("# BATCH", "# BATCH# BATCH", 1) + "\n")
        retitle(tdocs["bare"], title_line(tdocs["bare"]), "")
        found = plans.check(root)
        c.ok(any(one.startswith("tp/1-ph:") and "`wrong`" in one for one in found), "the wrong plan")
        c.ok(any(one.startswith("tp/1-ph/1-bt:") and "# BATCH# BATCH" in one for one in found), "the doubled title")
        c.ok(any(one.startswith("tp/1-ph/2-bare:") and "no title" in one for one in found), "the missing title")
        c.ok(not any(one.startswith("tp:") for one in found), "the free title judged")
        mended, left = plans.repair(root)
        c.ok(len([one for one in P.of(mended, "tp") if "title" in one]) == 3 and P.of(left, "tp") == [],
             f"mended {mended} left {left}")
        c.ok(clean(root, "tp") and tdocs["plan"].read_bytes() == free, "check after, the free title")
        for name in ("phase", "bt"):
            c.ok(title_line(tdocs[name]) == plans.title_of(front(tdocs[name])) and untitled(tdocs[name]) == kept[name],
                 f"{name}: title or body")
        c.ok(title_line(tdocs["bare"]) == plans.title_of(front(tdocs["bare"])), "the title set")

    with case("a framing section reopens a phase, repair closes it back", "Target on a done phase turns it redo "
              "and the parent entry follows; with no batch to deliver, `repair` runs the cascade that "
              "never ran and closes it, the parent line with it") as c:
        c.ok("beta/last" in P.moves(w.close_phase(root, ["beta", "last"])).get("beta/last/closer", P.Move("", (), "")).closes,
             "beta/last closed")
        c.ok("beta/two" in P.moves(w.close_phase(root, ["beta", "two"])).get("beta/two/closer", P.Move("", (), "")).closes,
             "beta/two closed")
        _, said = section(root, ["beta", "two"], "Target", "the phase reworked")
        c.ok(P.moves(said).get("beta/two", P.Move("", (), "")).status == "redo", f"said {said}")
        c.ok(front(beta / "2-two" / "PHASE.md")["status"] == "redo" and kids(beta / "PLAN.md")["two"] == "redo",
             "the reopening")
        c.ok(P.move_of(plans.next_move(root, "beta")) == ("phase", "rework", "plan-phase:beta/two"), "the move")
        mended, left = plans.repair(root)
        c.ok("beta/2-two" in P.spots(P.of(mended, "beta")) and P.of(left, "beta") == [], f"mended {mended}")
        c.ok(front(beta / "2-two" / "PHASE.md")["status"] == "done" and kids(beta / "PLAN.md")["two"] == "done",
             "the closing")

    with case("no verb closes or reopens a node", "a log line moves nothing; `done` refuses a node -- "
              "the statuses follow the writing alone") as c:
        _, said = section(root, ["beta", "home"], "Decisions", "- a word on a phase still open")
        c.ok(P.moves(said) == {}, f"a log moved {said}")
        refuse("done-invalid", lambda: plans.done(root, ["beta", "home"]))

    with case("the check names a closed node over open work", "engaging a child under a delivered "
              "parent reddens -- the entry and its document agreed, nothing saw it before") as c:
        section(drift, ["blind"], "Context", "A closed node over open work.")
        grow(drift, ["blind", "ph"], "A phase")
        grow(drift, ["blind", "ph", "lot"], "A batch")
        frame(drift, ["blind", "ph", "lot"])
        said = P.moves(deliver(drift, ["blind", "ph", "lot"]))
        c.ok(said.get("blind/ph/lot", P.Move("", (), "")).closes == ("blind/ph", "blind"), f"said {said}")
        c.ok(clean(drift, "blind"), "check before")
        ldoc = drift / "plans" / "blind" / "1-ph" / "1-lot" / "BATCH.md"
        ldoc.write_text(ldoc.read_text(encoding="utf-8").replace("status: done", "status: doing"), encoding="utf-8")
        plans._splice_child(drift / "plans" / "blind" / "1-ph" / "PHASE.md", "lot", "doing")
        reported = P.of(plans.check(drift), "blind")
        c.ok(len(reported) == 1 and "lot" in reported[0] and "open work" in reported[0], f"findings {reported}")

    with case("the rework line names the deepest node", "a redo phase alone says itself; "
              "a redo batch beneath is said with its phase -- the full path, never the phase alone") as c:
        frame(root, ["beta", "home", "job"])
        plans.done(root, ["beta", "home", "job", "a-step"])
        said = P.moves(deliver(root, ["beta", "home", "job"]))
        c.ok("beta/home" in said.get("beta/home/job", P.Move("", (), "")).closes, f"said {said}")
        section(root, ["beta", "home"], "Target", "the phase reworked")
        c.ok(P.move_of(plans.next_move(root, "beta")) == ("phase", "rework", "plan-phase:beta/home"), "the phase")
        section(root, ["beta", "home", "job"], "Target", "the batch reworked")
        c.ok(P.move_of(plans.next_move(root, "beta")) == ("batch", "rework", "plan-lot:beta/home/job"), "the batch")

    with case("check names the legacy block", "a phases:| survivor reddens -- items are the grammar now") as c:
        section(drift, ["vintage"], "Context", "A plan of the block era.")
        rdoc = drift / "plans" / "vintage" / "PLAN.md"
        rdoc.write_text(rdoc.read_text(encoding="utf-8").replace(
            "---\n\n# PLAN", "phases: |\n  1-a  todo  old shape\n---\n\n# PLAN"), encoding="utf-8")
        c.ok(any("legacy" in one for one in P.of(plans.check(drift), "vintage")), "the legacy block")

    with case("the correctives of the keeper", "Items --append keeps the entries written and adds the fragment's, "
              "a name taken twice refuses slug-taken; a working batch moved under a done phase reopens it; repair "
              "announces every plan it mended") as c:
        section(root, ["ap"], "Context", "A plan whose Items grow.")
        prepare(root, ["ap", "p"], "the first phase")
        framed(root, ["ap", "p"])
        section(root, ["ap"], "Items", "- q -- the second phase", append=True)
        c.ok(plans.children(front(root / "plans" / "ap" / "PLAN.md")) == [("p", "doing"), ("q", "todo")],
             f"--append {plans.children(front(root / 'plans' / 'ap' / 'PLAN.md'))}")
        refuse("slug-taken", lambda: section(root, ["ap"], "Items", "- q -- the same name", append=True))
        section(root, ["mv"], "Context", "A plan whose batch moves.")
        prepare(root, ["mv", "open"], "a phase at work")
        grow(root, ["mv", "open", "job"], "a batch at work")
        framed(root, ["mv", "open", "job"])
        prepare(root, ["mv", "shut"], "a phase delivered")
        framed(root, ["mv", "shut"])
        w.close_phase(root, ["mv", "shut"])
        plans.move(root, ["mv", "open", "job"], ["mv", "shut"], "1")
        c.ok(front(root / "plans" / "mv" / "2-shut" / "PHASE.md")["status"] == "redo"
             and kids(root / "plans" / "mv" / "PLAN.md")["shut"] == "redo", "the done phase reopened")
        c.ok(clean(root, "mv"), "check after the move")
        section(root, ["rp"], "Context", "A plan repair closes back.")
        prepare(root, ["rp", "only"], "its one phase")
        framed(root, ["rp", "only"])
        w.close_phase(root, ["rp", "only"])
        section(root, ["rp", "only"], "Target", "the phase reworked")
        said = P.play(plans, ["repair"])
        c.ok(any(one[2] == "plan:rp" for one in P.pushes(said)), f"repair announces {said[-300:]}")

    return 0
