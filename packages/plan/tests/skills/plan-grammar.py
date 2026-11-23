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
GROUND, EXPECTED, TESTS, CHOICES = P.GROUND, P.EXPECTED, P.TESTS, P.CHOICES


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

    def wanted(path):
        """-> the title the node's template gives it, its parent read from its address."""
        address = plans.address_of(root / "plans", path)
        return plans.title_of(root, front(path), address[-2] if len(address) > 1 else "")

    def clean(base, slug):
        return P.of(plans.check(base), slug) == []

    def addresses(said):
        """-> the address each line of `status` opens on, its foot left out."""
        return [one.split()[0] for one in said.splitlines() if one.strip() and not one.startswith("+")]

    demo = root / "plans" / "demo"

    # --- births: the plan by its Context, the others prepared then born ------------------
    context = "The demo plan.\n\nIts thesis, in prose."
    with case("a plan is born by its Context", "PLAN.md stands with its title and its Context, nothing else of the "
              "template's body, no phase yet") as c:
        path, said = section(root, ["demo"], "Context", context)
        c.ok(said == ["born"] and (demo / "PLAN.md").is_file(), f"said {said}")
        body = plans.read(path)[1]
        c.ok(plans.section_text(body, "Context").strip() == context
             and [one for one, _ in plans.split_sections(body) if one] == ["Context"], "Context alone")

    survey_brief = "Survey first: the inventory phase"
    with case("Items prepares a child", "the entry derived `item.1: survey  todo`, no folder, no document") as c:
        prepare(root, ["demo", "survey"], survey_brief)
        c.ok(plans.children(front(demo / "PLAN.md")) == [("survey", "todo")], "the entry")
        c.ok(not (demo / "1-survey").exists(), "a folder born")

    with case("the first section births the item", "the folder indexed, the document on the template, its title "
              "and the section written alone -- the Items line is not copied; a phase carries no Context") as c:
        refuse("section-unknown", lambda: section(root, ["demo", "survey"], "Context", "a brief"))
        c.ok(not (demo / "1-survey").exists(), "nothing born by a refusal")
        path, said = section(root, ["demo", "survey"], "Ground", GROUND)
        c.ok(said == ["born", "inserted"] and path == demo / "1-survey" / "PHASE.md", f"said {said} at {path}")
        body = plans.read(path)[1]
        c.ok([one for one, _ in plans.split_sections(body) if one] == ["Ground"], f"Ground alone {body!r}")
        c.ok(survey_brief not in body and plans.section_text(body, "Ground").strip() == GROUND, "the brief left out")

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

    with case("Choices frames the node", "Expected and Tests written on a todo node leave it todo; Choices makes "
              "it `doing`, its parent line follows -- deduced, no verb; a second Choices moves nothing; Target "
              "refuses section-unknown") as c:
        again = demo / "1-survey" / "2-again" / "BATCH.md"
        grow(root, ["demo", "survey", "again"], "A second batch")      # born by its Ground, todo
        section(root, ["demo", "survey", "again"], "Expected", EXPECTED)
        section(root, ["demo", "survey", "again"], "Tests", TESTS)
        c.ok(front(again)["status"] == "todo", "todo before Choices")
        refuse("section-unknown", lambda: section(root, ["demo", "survey", "again"], "Target", "the target"))
        _, said = section(root, ["demo", "survey", "again"], "Choices", CHOICES)
        c.ok(P.moves(said).get("demo/survey/again", P.Move("", (), "")).status == "doing", f"said {said}")
        c.ok(front(again)["status"] == "doing" and kids(demo / "1-survey" / "PHASE.md")["again"] == "doing",
             "the document and its parent line")
        _, said = section(root, ["demo", "survey", "again"], "Choices", CHOICES + " again")
        c.ok(P.moves(said) == {}, f"a second Choices moved {said}")

    with case("done checks a todo off", "list-sources done, read-whole untouched, the batch still doing") as c:
        plans.done(root, ["demo", "survey", "map", "list-sources"])
        c.ok(plans.children(front(batch))[0][1] == "done" and front(batch)["status"] == "doing", "the statuses")

    lines = "- list-sources -- list the sources\n- read-whole -- read them whole"
    with case("Items is rewritten, the entries follow", "a line added enters todo, a known one keeps its status, "
              "a todo line removed leaves, a delivered one refuses item-engaged -- and a leaf's Delivery "
              "without its item refuses item-missing") as c:
        section(root, ["demo", "survey", "map"], "Items", lines + "\n- one-more -- a later step")
        c.ok(plans.children(front(batch)) == [("list-sources", "done"), ("read-whole", "todo"), ("one-more", "todo")],
             "a line added")
        section(root, ["demo", "survey", "map"], "Items", lines)
        c.ok(plans.children(front(batch)) == [("list-sources", "done"), ("read-whole", "todo")], "a line removed")
        out = refuse("item-engaged", lambda: section(root, ["demo", "survey", "map"], "Items", "- read-whole -- read them whole"))
        c.ok("list-sources" in out and "done" in out, "item-engaged names the delivered todo")
        section(root, ["demo", "survey", "map"], "Tests", TESTS)
        out = refuse("item-missing", lambda: section(root, ["demo", "survey", "map"], "Delivery", "too soon"))
        c.ok("--item" in out, "item-missing names the flag")

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
        c.ok(overview and overview[0]["children"] == {"template": "phase", "done": 0, "open": 1, "prepared": 1}, "the progress on the born")
        c.ok(overview and overview[0]["next"] == plans.next_move(root, "demo"), "the next move")
        c.ok(addresses(said) == ["demo"] and "shut" in said.splitlines()[-1], f"the text {said!r}")
        every = json.loads(P.play(plans, ["status", "--all", "--json"]))
        c.ok([(one["address"], one["status"]) for one in every] == [("demo", "doing"), ("shut", "done")], "--all")
        c.ok(every[-1].get("next") is None, "a closed plan has no next move")
        detail = json.loads(P.play(plans, ["status", "demo", "--json"]))
        c.ok([(one["address"], one["template"]) for one in detail] == [
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

    with case("a section is replaced or inserted at its rank", "Expected rewritten in place; on a plan born by its "
              "Context, Choices then Ground inserted -- Ground between Context and Choices") as c:
        c.ok(section(root, ["demo"], "Expected", "The expected, rewritten.")[1] == ["replaced"], "Expected replaced")
        section(root, ["ranks"], "Context", "A plan whose sections come out of order.")
        c.ok(section(root, ["ranks"], "Choices", CHOICES)[1][:1] == ["inserted"], "Choices inserted")
        c.ok(section(root, ["ranks"], "Ground", "The ground, seen.")[1] == ["inserted"], "Ground inserted")
        order = [n for n, _ in plans.split_sections(plans.read(root / "plans" / "ranks" / "PLAN.md")[1]) if n]
        c.ok(order == ["Context", "Ground", "Choices"], f"order {order}")

    with case("a section appends by the flag, the template closes the list", "Delivery, the plan's journal, "
              "inserted at its rank then appended; Choices appended by the flag; a name the template does not "
              "carry refuses -- Decisions among them") as c:
        first, second = "- 2026-09-05 : the first word", "- 2026-09-06 : the second word"
        c.ok(section(root, ["demo"], "Delivery", first)[1] == ["inserted"], "the first line")
        c.ok(section(root, ["demo"], "Delivery", second)[1] == ["appended"], "the journal appends")
        c.ok(f"{first}\n\n{second}" in plans.section_text(plans.read(demo / "PLAN.md")[1], "Delivery"), "the lines")
        c.ok(section(root, ["demo"], "Choices", "One more choice.", append=True)[1] == ["appended"], "the flag")
        c.ok(names()[-1] == "Delivery", f"the journal last {names()}")
        refuse("section-unknown", lambda: section(root, ["demo"], "Decisions", first))
    refuse("section-unknown", lambda: section(root, ["demo"], "Keep track", "a line of the plan's own"))

    refuse("section-unknown", lambda: section(root, ["demo", "survey", "map"], "Todos", "- x -- y"))
    refuse("prose-missing", lambda: section(root, ["demo"], "Expected", "   \n"))
    refuse("node-unframed", lambda: plans.write_section(root, ["demo", "build"], "Delivery", "x"))
    refuse("item-line-malformed", lambda: section(root, ["demo", "survey", "map"], "Items", "- T9 -- a tag, not a name"))
    refuse("slug-taken", lambda: section(root, ["demo", "survey", "map"], "Items", "- read-whole -- a\n- read-whole -- b"))
    bench.held("the section refusals hold", "section-unknown (Todos), prose-missing, node-unframed on a prepared "
               "item, item-line-malformed, slug-taken")

    # --- a subtitle inside a section: `##` refused before any write, `###` written -------
    hdoc = root / "plans" / "heads" / "PLAN.md"
    section(root, ["heads"], "Context", "A plan whose prose carries subtitles.")
    framed(root, ["heads"])
    section(root, ["heads"], "Delivery", "- 2026-09-12 : a first word")
    with case("a `##` in the prose refuses before any write", "prose-heading on a section replaced, inserted, a "
              "log, the flag, a code block, a prepared item -- the bytes unchanged, no folder born") as c:
        sneaks = (("Expected", "The expected.\n\n## Sneaked\n\nmore", False),       # a section replaced
                  ("Items", "## Sneaked\n\n- p -- a phase", False),                # a section inserted
                  ("Delivery", "- 2026-09-13 : a word\n## Sneaked", False),          # a log
                  ("Choices", "one more\n## Sneaked", True),                        # the flag
                  ("Expected", "```\n## Sneaked in a code block\n```", False))      # a code block
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
        section(root, ["heads"], "Expected", "The expected.\n\n### One\n\nfirst\n\n### Two\n\nsecond")
        c.ok(headings() == counted, "a section born of a subtitle")
        section(root, ["heads"], "Expected", "The expected, again.\n\n### Three\n\n### Four\n\n### Five")
        c.ok(headings() == counted and "### Two" not in hdoc.read_text(encoding="utf-8"), "a subtitle left")
        c.ok(document.read(hdoc).front["slug"] == "heads" and clean(root, "heads"), "the reader or check")

    with case("check says a section twice", "a hand-doubled Expected reddens by name, repair mends nothing and says the gesture; the document restored is clean") as c:
        text = hdoc.read_text(encoding="utf-8")
        hdoc.write_text(text + "\n## Expected\n\nA leftover.\n", encoding="utf-8")
        found = P.of(plans.check(root), "heads")
        c.ok(any("`Expected`" in one and "twice" in one for one in found), f"findings {found}")
        doubled = hdoc.read_bytes()
        mended, left = plans.repair(root)
        c.ok(P.of(mended, "heads") == [] and hdoc.read_bytes() == doubled, f"mended {mended}")
        c.ok(any("section `Expected`" in one and "--remove=<n>" in one for one in P.of(left, "heads")), f"left {left}")
        hdoc.write_text(text, encoding="utf-8")
        c.ok(clean(root, "heads"), "restored")

    # --- a section removed: the occurrence the call names, and nothing else ---------------
    cdoc = root / "plans" / "cuts" / "PLAN.md"
    section(root, ["cuts"], "Context", "A plan whose documents carry leftovers.")
    framed(root, ["cuts"])
    section(root, ["cuts"], "Delivery", "- 2026-09-13 : the one word")
    with case("a section beyond the template is removed", "a section a hand wrote, the template not carrying it: "
              "the document is byte for byte the one written without it") as c:
        before = cdoc.read_bytes()
        cdoc.write_bytes(before + b"## Keep track\n\na line of the plan's own\n\n")
        _, said = plans.remove_section(root, ["cuts"], "Keep track", None)
        c.ok(cdoc.read_bytes() == before, "the bytes")
        c.ok("Keep track" in said and "1 of 1" in said, f"said {said}")

    text = cdoc.read_text(encoding="utf-8")
    with case("a doubled section is removed by its rank", "section-ambiguous lists each occurrence with its size "
              "and first line; --remove=1 takes the empty log, =2 the stale list, =2 a doubled Expected; a rank "
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
        cdoc.write_text(text + "## Expected\n\nA leftover.\n", encoding="utf-8")
        plans.remove_section(root, ["cuts"], "Expected", 2)
        c.ok(cdoc.read_text(encoding="utf-8") == text, "=2 on Expected")

    with case("what must stay stays", "section-kept on a listed section standing once (Expected, a log), "
              "section-unknown on an absent name, path-unknown on a prepared item -- the bytes unchanged") as c:
        for name in ("Expected", "Delivery"):
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
        cdoc.write_text(before.decode("utf-8") + "## Expected\n\nA leftover.\n", encoding="utf-8")
        _, left = plans.repair(root)
        c.ok(any("section `Expected`" in one and "--remove=<n>" in one for one in P.of(left, "cuts")), f"left {left}")
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
        c.ok(P.move_of(plans.next_move(root, "story")) == ("phase", "framing", "plan:story/p1"), "prepared")
        frame(root, ["story", "p1"])
        c.ok(P.move_of(plans.next_move(root, "story")) == ("phase", "batches", "plan:story/p1"), "framed")

    with case("the next move walks true", "no phase -> awaits framing -> awaits implementation -> "
              "the Delivery closes batch, phase and plan by the script -> None; every line ends with "
              "the vector of the node it names -- plan:<address>, at every depth") as c:
        prepare(root, ["story", "p1", "b1"], "First batch")
        c.ok(P.move_of(plans.next_move(root, "story")) == ("batch", "framing", "plan:story/p1/b1"), "prepared")
        frame(root, ["story", "p1", "b1"])
        c.ok(P.move_of(plans.next_move(root, "story")) == ("batch", "implementation", "plan:story/p1/b1"), "framed")
        said = P.moves(deliver(root, ["story", "p1", "b1"]))
        moved = said.get("story/p1/b1", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == ("story/p1", "story"), f"said {said}")
        c.ok(plans.next_move(root, "story") is None, "a move after the closing")

    with case("a framing section rewritten reopens", "Expected on a done batch under a closed plan turns it "
              "redo and raises phase and plan with it -- the next move names the batch; a line of the plan's "
              "journal moves nothing") as c:
        _, said = section(root, ["story", "p1", "b1"], "Expected", "reworked")
        c.ok(P.moves(said).get("story/p1/b1", P.Move("", (), "")).status == "redo", f"said {said}")
        c.ok(front(story / "1-p1" / "1-b1" / "BATCH.md")["status"] == "redo"
             and front(story / "1-p1" / "PHASE.md")["status"] == "redo"
             and front(story / "PLAN.md")["status"] == "redo", "the statuses")
        c.ok(kids(story / "1-p1" / "PHASE.md")["b1"] == "redo" and kids(story / "PLAN.md")["p1"] == "redo", "the entries")
        c.ok(P.move_of(plans.next_move(root, "story")) == ("batch", "rework", "plan:story/p1/b1"), "the move")
        c.ok(clean(root, "story"), "check")
        _, said = section(root, ["story"], "Delivery", "- a dated word")
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
        c.ok(front(casc / "1-p1" / "1-b1" / "BATCH.md")["status"] == "doing", "a todo left open keeps the batch")
        closed = plans.done(root, ["casc", "p1", "b1", "last-step"])
        c.ok(closed == ["casc/p1/b1"], f"the last todo closes the batch alone {closed}")
        c.ok(front(casc / "1-p1" / "1-b1" / "BATCH.md")["status"] == "done"
             and kids(casc / "1-p1" / "PHASE.md")["b1"] == "done", "the batch")
        c.ok(front(casc / "1-p1" / "PHASE.md")["status"] == "doing" and clean(root, "casc"), "the phase")

    with case("block says a stop, the writing lifts it", "blocked with its dated Delivery line; the next section "
              "written lifts it (todo before Choices, doing after); the second batch delivered closes the phase") as c:
        reason = "the store is not there yet"
        b2 = casc / "1-p1" / "2-b2" / "BATCH.md"
        section(root, ["casc", "p1", "b2"], "Ground", GROUND)
        plans.block(root, ["casc", "p1", "b2"], reason)
        logged = plans.section_text(plans.read(b2)[1], "Delivery") or ""
        c.ok(front(b2)["status"] == "blocked" and f"blocked -- {reason}" in logged, "the block")
        _, said = section(root, ["casc", "p1", "b2"], "Expected", EXPECTED)
        c.ok(P.moves(said).get("casc/p1/b2", P.Move("", (), "")).status == "todo", f"lifted {said}")
        frame(root, ["casc", "p1", "b2"])
        said = P.moves(deliver(root, ["casc", "p1", "b2"]))
        c.ok(said.get("casc/p1/b2", P.Move("", (), "")).closes == ("casc/p1",), f"said {said}")
        c.ok(P.move_of(plans.next_move(root, "casc")) == ("phase", "framing", "plan:casc/p2"), "the move")

    with case("the closing rises to the plan", "the Delivery of the last batch of the last phase closes "
              "batch, phase and plan in one call -- a blocked parent closes like the others, every line "
              "and document agree, check clean") as c:
        section(root, ["casc", "p2"], "Ground", GROUND)          # the prepared phase is born
        grow(root, ["casc", "p2", "b3"], "Batch three")
        todo(root, ["casc", "p2", "b3"], "only-step", "the only step")
        frame(root, ["casc", "p2", "b3"])
        plans.block(root, ["casc", "p2"], "waits the store")
        _, written, moves = plans.write_section(root, ["casc", "p2", "b3"], "Delivery", "landed", item="only-step")
        said = P.moves(written + moves)
        c.ok(said.get("casc/p2/b3", P.Move("", (), "")).closes == ("casc/p2", "casc"), f"said {said}")
        c.ok(front(casc / "PLAN.md")["status"] == "done" and kids(casc / "PLAN.md") == {"p1": "done", "p2": "done"},
             "the plan")
        c.ok(front(casc / "2-p2" / "PHASE.md")["status"] == "done" and kids(casc / "2-p2" / "PHASE.md")["b3"] == "done",
             "the phase")
        c.ok(plans.next_move(root, "casc") is None and clean(root, "casc"), "the move or check")

    with case("the rework cascades again", "a new todo in Items reopens the delivered batch and lifts the "
              "ancestry, the plan `redo` too; its delivered todo closes it back up to the plan -- the cycle "
              "round-trips") as c:
        todo(root, ["casc", "p2", "b3"], "one-more", "one more step")     # Items on a done batch reopens it
        c.ok(front(casc / "PLAN.md")["status"] == "redo" and kids(casc / "PLAN.md")["p2"] == "redo"
             and front(casc / "2-p2" / "1-b3" / "BATCH.md")["status"] == "redo", "the reopening")
        said = P.moves(deliver(root, ["casc", "p2", "b3"], "reworked"))
        c.ok(said.get("casc/p2/b3", P.Move("", (), "")).closes == ("casc/p2", "casc"), f"said {said}")
        c.ok(plans.next_move(root, "casc") is None and clean(root, "casc"), "the move or check")

    with case("engagement primes order", "a doing phase behind a todo phase is served; an engaged "
              "batch behind a todo batch is served; none engaged falls back to the first todo") as c:
        section(root, ["prio"], "Context", "Engagement primes order.")
        prepare(root, ["prio", "first"], "A phase never started")
        grow(root, ["prio", "second"], "A framed phase")
        frame(root, ["prio", "second"])
        c.ok(P.move_of(plans.next_move(root, "prio")) == ("phase", "batches", "plan:prio/second"), "the phase")
        prepare(root, ["prio", "second", "b1"], "A batch never started")
        grow(root, ["prio", "second", "b2"], "An engaged batch")
        frame(root, ["prio", "second", "b2"])
        c.ok(P.move_of(plans.next_move(root, "prio")) == ("batch", "implementation", "plan:prio/second/b2"),
             "the engaged batch")
        deliver(root, ["prio", "second", "b2"])
        c.ok(P.move_of(plans.next_move(root, "prio")) == ("batch", "framing", "plan:prio/second/b1"),
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
        section(root, ["proclike"], "Ground", "Seen.")
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
            c.ok(title_line(doc) == wanted(doc) and "`beta`" in title_line(doc)
                 and "`alpha`" not in title_line(doc) and untitled(doc) == body, f"{doc.name}: title or body")
        c.ok([one[0] for one in plans.children(front(beta / "PLAN.md"))] == ["two", "home"], "the target's entries")
        jfront = front(job_doc)
        c.ok(jfront["plan"] == "beta" and "phase" not in jfront, "the batch's keys")
        c.ok([one[0] for one in plans.children(front(root / "plans" / "alpha" / "PLAN.md"))] == ["one"],
             "the source's entries")
        c.ok((beta / "2-home").is_dir() and clean(root, "alpha") and clean(root, "beta"), "renumbered, check")

    with case("move carries the titles", "the moved phase and its batch say the new plan, the moved batch its "
              "new phase -- the title line alone rewritten, the rest of each body byte for byte") as c:
        kept = untitled(beta / "1-two" / "1-job" / "BATCH.md")
        plans.move(root, ["beta", "two", "job"], ["beta", "home"], "1")
        job_doc = beta / "2-home" / "1-job" / "BATCH.md"
        c.ok(title_line(job_doc) == wanted(job_doc) and "`home`" in title_line(job_doc), "the title")
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
            c.ok(title_line(doc) == wanted(doc) and "`uno`" in title_line(doc)
                 and "`one`" not in title_line(doc) and untitled(doc) == body, f"{doc.name}: title or body")
        gfront, gbody = plans.read(gamma / "PLAN.md")
        c.ok([one[0] for one in plans.children(gfront)] == ["uno", "two"], "the entry")
        c.ok(("uno", "Phase one") in plans.item_lines(plans.section_text(gbody, "Items"))
             and "one" not in dict(plans.item_lines(plans.section_text(gbody, "Items"))), "the Items line")
        c.ok((gamma / "1-uno" / "PHASE.md").is_file() and not (gamma / "1-one").exists(), "the folder")
        ufront = front(gamma / "1-uno" / "PHASE.md")
        c.ok(ufront["slug"] == "uno" and ufront["status"] == "doing", "the phase's keys")
        jfront = front(gamma / "1-uno" / "1-job" / "BATCH.md")
        c.ok("phase" not in jfront and jfront["plan"] == "gamma" and clean(root, "gamma"), "the batch's keys, check")
        kept = untitled(gamma / "1-uno" / "1-job" / "BATCH.md")
        plans.rename(root, ["gamma", "uno", "job"], "work")
        work_doc = gamma / "1-uno" / "1-work" / "BATCH.md"
        c.ok(title_line(work_doc) == wanted(work_doc) and "`work`" in title_line(work_doc)
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
            c.ok(title_line(tdocs[name]) == wanted(tdocs[name]) and untitled(tdocs[name]) == kept[name],
                 f"{name}: title or body")
        c.ok(title_line(tdocs["bare"]) == wanted(tdocs["bare"]), "the title set")

    with case("a framing section reopens a phase, repair closes it back", "Expected on a done phase turns it redo "
              "and the parent entry follows; with no batch to deliver, `repair` runs the cascade that "
              "never ran and closes it, the parent line with it") as c:
        c.ok("beta/last" in P.moves(w.close_phase(root, ["beta", "last"])).get("beta/last/closer", P.Move("", (), "")).closes,
             "beta/last closed")
        c.ok("beta/two" in P.moves(w.close_phase(root, ["beta", "two"])).get("beta/two/closer", P.Move("", (), "")).closes,
             "beta/two closed")
        _, said = section(root, ["beta", "two"], "Expected", "the phase reworked")
        c.ok(P.moves(said).get("beta/two", P.Move("", (), "")).status == "redo", f"said {said}")
        c.ok(front(beta / "2-two" / "PHASE.md")["status"] == "redo" and kids(beta / "PLAN.md")["two"] == "redo",
             "the reopening")
        c.ok(P.move_of(plans.next_move(root, "beta")) == ("phase", "rework", "plan:beta/two"), "the move")
        mended, left = plans.repair(root)
        c.ok("beta/2-two" in P.spots(P.of(mended, "beta")) and P.of(left, "beta") == [], f"mended {mended}")
        c.ok(front(beta / "2-two" / "PHASE.md")["status"] == "done" and kids(beta / "PLAN.md")["two"] == "done",
             "the closing")

    with case("no section closes a node, the hand closes no work in progress", "a log line moves nothing; "
              "`done` on a node whose item is under way refuses item-engaged") as c:
        frame(root, ["beta", "home"])
        _, said = section(root, ["beta", "home"], "Delivery", "- a word on a phase still open")
        c.ok(P.moves(said) == {}, f"a log moved {said}")
        refuse("item-engaged", lambda: plans.done(root, ["beta", "home"]))

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
        closed = plans.done(root, ["beta", "home", "job", "a-step"])
        c.ok("beta/home" in closed, f"closed {closed}")
        section(root, ["beta", "home"], "Expected", "the phase reworked")
        c.ok(P.move_of(plans.next_move(root, "beta")) == ("phase", "rework", "plan:beta/home"), "the phase")
        section(root, ["beta", "home", "job"], "Expected", "the batch reworked")
        c.ok(P.move_of(plans.next_move(root, "beta")) == ("batch", "rework", "plan:beta/home/job"), "the batch")

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
        section(root, ["rp", "only"], "Expected", "the phase reworked")
        said = P.play(plans, ["repair"])
        c.ok(any(one[2] == "plan:rp" for one in P.pushes(said)), f"repair announces {said[-300:]}")

    # --- the templates: the tree's own read first, the structure from its front alone ---------
    own = root / "plans" / plans.TREE_TEMPLATES / "batch.md"
    with case("the tree's template replaces the product's", "its sections, its rank and its `doing` read from its "
              "front: Security written lands between Ground and Expected and frames the batch; Items and Delivery "
              "added last; Notes and Tests refuse section-unknown") as c:
        own.parent.mkdir(parents=True, exist_ok=True)
        own.write_text("---\nname: batch\ndescription: a batch with its security\nleaf: yes\nsections: |\n  Context\n  Ground\n"
                       "  Expected\n  Security\nstatuses: |\n  doing  Security\n  redo  Ground\n---\n\n"
                       "# BATCH `{slug}` -- phase `{phase}`, plan `{plan}`\n\n## Context\n", encoding="utf-8")
        section(root, ["tpl"], "Context", "A plan whose batches carry their security.")
        prepare(root, ["tpl", "ph"], "its phase")
        framed(root, ["tpl", "ph"])
        prepare(root, ["tpl", "ph", "safe"], "a batch with its security")
        path, _ = section(root, ["tpl", "ph", "safe"], "Ground", GROUND)
        c.ok(front(path)["template"] == "batch" and front(path)["status"] == "todo", "born on the template")
        section(root, ["tpl", "ph", "safe"], "Expected", EXPECTED)
        c.ok(front(path)["status"] == "todo", "Expected frames nothing here")
        _, said = section(root, ["tpl", "ph", "safe"], "Security", "the surfaces and their proof")
        c.ok(P.moves(said).get("tpl/ph/safe", P.Move("", (), "")).status == "doing", f"Security frames {said}")
        order = [n for n, _ in plans.split_sections(plans.read(path)[1]) if n is not None]
        c.ok(order == ["Ground", "Expected", "Security"], f"order {order}")
        c.ok(plans.level(root, "batch").sections[-2:] == ("Items", "Delivery"), "Items and Delivery last")
        for name in ("Notes", "Tests"):
            refuse("section-unknown", lambda: section(root, ["tpl", "ph", "safe"], name, "x"))
        c.ok(clean(root, "tpl"), "check")

    with case("a template that cannot serve refuses", "template-invalid for a status other than doing and redo, a "
              "status naming a section not carried, Delivery among the statuses, no section; template-unknown for "
              "a name no tree carries -- nothing written") as c:
        good = own.read_text(encoding="utf-8")
        doc = root / "plans" / "tpl" / "1-ph" / "1-safe" / "BATCH.md"
        for wrong in (good.replace("  redo  Ground", "  closed  Ground"),
                      good.replace("  redo  Ground", "  redo  Ghost"),
                      good.replace("  redo  Ground", "  redo  Delivery"),
                      good.replace("  Context\n  Ground\n  Expected\n  Security\n", "")):
            own.write_text(wrong, encoding="utf-8")
            before = doc.read_bytes()
            refuse("template-invalid", lambda: section(root, ["tpl", "ph", "safe"], "Ground", GROUND))
            c.ok(doc.read_bytes() == before, "bytes moved")
        own.write_text(good, encoding="utf-8")
        doc.write_text(doc.read_text(encoding="utf-8").replace("template: batch", "template: ghost"), encoding="utf-8")
        refuse("template-unknown", lambda: section(root, ["tpl", "ph", "safe"], "Ground", GROUND))
        c.ok(any("template-unknown" in one for one in P.of(plans.check(root), "tpl")), "check says it")
        doc.write_text(doc.read_text(encoding="utf-8").replace("template: ghost", "template: batch"), encoding="utf-8")
        own.unlink()

    with case("repair leaves the form before the templates", "a node carrying `kind:` is said by check and "
              "refuses template-missing, a batch carrying `phase:` is said too; repair mends neither and says each "
              "with its gesture, every byte kept -- the migration script rewrites them") as c:
        doc = root / "plans" / "tpl" / "1-ph" / "PHASE.md"
        written = doc.read_text(encoding="utf-8")
        doc.write_text(written.replace("template: phase", "kind: phase"), encoding="utf-8")
        under = root / "plans" / "tpl" / "1-ph" / "1-safe" / "BATCH.md"
        under.write_text(under.read_text(encoding="utf-8").replace("plan: tpl\n", "plan: tpl\nphase: ph\n", 1),
                         encoding="utf-8")
        refuse("template-missing", lambda: section(root, ["tpl", "ph"], "Expected", EXPECTED))
        found = P.of(plans.check(root), "tpl")
        c.ok(any("`kind:`" in one for one in found) and any("`phase:`" in one for one in found), f"check says it {found}")
        kept = doc.read_bytes()
        mended, left = plans.repair(root)
        c.ok(not [one for one in P.of(mended, "tpl") if "kind" in one or "phase:" in one]
             and doc.read_bytes() == kept and front(under).get("phase") == "ph", f"mended {mended}")
        left = P.of(left, "tpl")
        gesture = plans.GESTURES["the form before the templates"]
        c.ok(len(left) == 2 and all(one.endswith(f" -- {gesture}") for one in left), f"left {left}")
        doc.write_text(written, encoding="utf-8")
        under.write_text(under.read_text(encoding="utf-8").replace("phase: ph\n", "", 1), encoding="utf-8")
        c.ok(clean(root, "tpl"), "check once the hand restored them")

    # --- a document of the form before: its sections read, served and kept ---------------------
    with case("the old document", "a plan, a phase and a batch carrying Survey, Target, Protocol, "
              "Arbitrations, Decisions and a Context under the plan: check clean, status reads them, the batch "
              "mounts whole and its ancestors from Expected with the older sections inside; its rework writes "
              "Choices before Items and keeps every older section; Target written refuses section-unknown") as c:
        section(root, ["vieux"], "Context", "A plan written before the form.")
        prepare(root, ["vieux", "ph"], "its phase")
        framed(root, ["vieux", "ph"])
        grow(root, ["vieux", "ph", "bt"], "its batch")
        framed(root, ["vieux", "ph", "bt"])
        todo(root, ["vieux", "ph", "bt"], "step", "one step")
        old = root / "plans" / "vieux"
        docs = {"plan": old / "PLAN.md", "phase": old / "1-ph" / "PHASE.md", "batch": old / "1-ph" / "1-bt" / "BATCH.md"}
        aged = {"plan": ("## Ground", "## Survey\n\nthe survey of before\n\n## Target\n\nthe target of before\n\n"
                                      "## Protocol\n\nthe protocol of before\n\n## Ground"),
                "phase": ("## Ground", "## Context\n\nthe brief of before\n\n## Target\n\nthe phase's target\n\n## Ground"),
                "batch": ("## Ground", "## Context\n\nthe batch's brief\n\n## Target\n\nthe batch's target\n\n## Ground")}
        for level, (where, older) in aged.items():
            text = docs[level].read_text(encoding="utf-8").replace("## Choices", "## Arbitrations\n\nthe arbitrations "
                                                                   "of before\n\n## Choices", 1)
            docs[level].write_text(text.replace(where, older, 1) + "## Decisions\n\n- 2026-01-01 : a word\n",
                                   encoding="utf-8")
        found = P.of(plans.check(root), "vieux")
        c.ok(found == [], f"check {found}")
        listed = json.loads(P.play(plans, ["status", "vieux", "--json"]))
        c.ok([one["address"] for one in listed] == ["vieux", "vieux/ph", "vieux/ph/bt"], f"status {listed}")
        chain = plans.mount_chain(root, ["vieux", "ph", "bt"])
        nodes = [one["body"] for one in chain if one["doc"].startswith("plans/")]
        c.ok(nodes == [["## Expected..## Items"], ["## Expected..## Items"], True], f"the mount {nodes}")
        ancestor = plans.read(docs["phase"])[1]
        run = ancestor[ancestor.index("## Expected"):ancestor.index("## Items")]
        c.ok("## Arbitrations" in run and "the arbitrations of before" in run, "an older section rides its run")
        refuse("section-unknown", lambda: section(root, ["vieux", "ph", "bt"], "Target", "rewritten"))
        before = plans.read(docs["batch"])[1]
        section(root, ["vieux", "ph", "bt"], "Choices", "the rework's choice")
        after = plans.read(docs["batch"])[1]
        order = [n for n, _ in plans.split_sections(after) if n]
        c.ok(order.index("Choices") < order.index("Items") and "the batch's target" in after
             and "the arbitrations of before" in after and "- 2026-01-01 : a word" in after, f"the rework {order}")
        c.ok([one for one in plans.split_sections(before) if one[0] != "Choices"]
             == [one for one in plans.split_sections(after) if one[0] != "Choices"], "every other section kept")
        c.ok(P.of(plans.check(root), "vieux") == [], "check after the rework")

    # --- the chain of templates: a plan as deep as its templates say ---------------------------
    place = root / "plans" / plans.TREE_TEMPLATES

    def template(name, sections, chain):
        lines = "".join(f"  {one}\n" for one in sections)
        place.mkdir(parents=True, exist_ok=True)
        (place / f"{name}.md").write_text(
            f"---\nname: {name}\ndescription: a level of the bench\n{chain}\nsections: |\n{lines}"
            f"statuses: |\n  doing  {sections[0]}\n  redo  {sections[0]}\n---\n\n# {name.upper()} `{{slug}}`\n",
            encoding="utf-8")

    with case("a plan of one level", "`chore`, a leaf: born by `--template`, its file CHORE.md, its items todos, "
              "closed by its Delivery once they are done; a node under it refuses path-unknown") as c:
        template("chore", ["Framing"], "leaf: yes")
        said = P.play(plans, ["section", "menage", "Framing", "--template", "chore", "-"], "Clean the room.")
        doc = root / "plans" / "menage" / "CHORE.md"
        c.ok("born" in said and doc.is_file() and front(doc)["template"] == "chore", f"born {said}")
        section(root, ["menage"], "Framing", "Clean the living room.")
        c.ok(front(doc)["status"] == "doing", "Framing frames it")
        section(root, ["menage"], "Items", "- vitres -- the windows\n- four -- the oven")
        refuse("path-unknown", lambda: plans.doc_of(root, "menage", "vitres"))
        refuse("item-missing", lambda: section(root, ["menage"], "Delivery", "both done"))
        plans.write_section(root, ["menage"], "Delivery", "no streak against the light", item="vitres")
        c.ok(front(doc)["status"] == "doing" and kids(doc)["vitres"] == "done", "one item delivered")
        plans.write_section(root, ["menage"], "Delivery", "racks soaked", item="four")
        c.ok(front(doc)["status"] == "done" and plans.next_move(root, "menage") is None, "the last closes it")
        c.ok("- vitres -- no streak" in plans.section_text(plans.read(doc)[1], "Delivery"), "the entry")
        _, said = section(root, ["menage"], "Framing", "The cellar too.")
        c.ok(front(doc)["status"] == "redo", f"the plan reopened {said}")
        section(root, ["menage"], "Items", "- plinthes -- the skirting", append=True)
        plans.write_section(root, ["menage"], "Delivery", "dusted", item="plinthes")
        c.ok(front(doc)["status"] == "done", "closed again")
        c.ok(clean(root, "menage"), "check")

    with case("a plan of two levels", "`project` -> `task`: an item prepared, born by the first section of the "
              "task's template in TASK.md, the parent's line following it, the cascade closing the project") as c:
        template("task", ["Framing"], "leaf: yes")
        template("project", ["Brief"], "next: task")
        plans.write_section(root, ["projet"], "Brief", "A project cut into tasks.", template="project")
        section(root, ["projet"], "Items", "- api -- the HTTP API")
        path, said = section(root, ["projet", "api"], "Framing", "GET /notes")
        c.ok(path == root / "plans" / "projet" / "1-api" / "TASK.md" and front(path)["template"] == "task",
             f"born {path}")
        c.ok(kids(root / "plans" / "projet" / "PROJECT.md")["api"] == "doing", "the parent's line")
        section(root, ["projet", "api"], "Items", "- route -- the route")
        refuse("item-is-node", lambda: plans.write_section(root, ["projet"], "Delivery", "x", item="api"))
        _, said = section(root, ["projet"], "Delivery", "a journal line")
        c.ok(P.moves(said) == {} and front(root / "plans" / "projet" / "PROJECT.md")["status"] == "doing",
             f"the branch's journal moves nothing {said}")
        _, written, moves = plans.write_section(root, ["projet", "api"], "Delivery", "the route answers", item="route")
        said = written + moves
        c.ok(P.moves(said).get("projet/api", P.Move("", (), "")).closes == ("projet",), f"the cascade {said}")
        c.ok(clean(root, "projet"), "check")

    with case("a plan of four levels", "`a` -> `b` -> `c` -> `d`: born, framed and closed by its leaf, the next "
              "move walking the chain to its vector plan:deep/x/y/z, which verify resolves; five names refuse "
              "path-unknown") as c:
        template("d", ["Dd"], "leaf: yes")
        template("c", ["Cc"], "next: d")
        template("b", ["Bb"], "next: c")
        template("a", ["Aa"], "next: b")
        plans.write_section(root, ["deep"], "Aa", "the root", template="a")
        chain = ["deep"]
        for name, first in (("x", "Bb"), ("y", "Cc"), ("z", "Dd")):
            section(root, chain, "Items", f"- {name} -- one level down")
            chain = chain + [name]
            section(root, chain, first, "framed")
        c.ok((root / "plans" / "deep" / "1-x" / "1-y" / "1-z" / "D.md").is_file(), "the deepest file")
        line = plans.next_move(root, "deep")
        c.ok(line and line.endswith("(plan:deep/x/y/z)"), f"the move and its vector {line}")
        plans.verify(root, "plan:deep/x/y/z")
        c.ok(json.loads(P.play(plans, ["status", "deep", "--json"]))[-1]["vector"] == "plan:deep/x/y/z",
             "the vector of status")
        section(root, chain, "Items", "- last -- the one step")
        refuse("path-unknown", lambda: plans.doc_of(root, "deep", "x", "y", "z", "last"))
        closed = plans.done(root, chain + ["last"])
        c.ok(closed == ["deep/x/y/z", "deep/x/y", "deep/x", "deep"], f"closed {closed}")
        c.ok(clean(root, "deep"), "check")

    with case("the hand closes what the work did not", "`done` on a node with a todo left open closes it, a "
              "dated Delivery line naming the todo; on a prepared item, its line closes, nothing is born; the "
              "closing rises") as c:
        plans.write_section(root, ["hand"], "Brief", "A project closed by hand.", template="project")
        section(root, ["hand"], "Items", "- left -- a task never framed\n- kept -- a task with a step")
        section(root, ["hand", "kept"], "Framing", "framed")
        section(root, ["hand", "kept"], "Items", "- step -- one step\n- other -- another")
        kept = root / "plans" / "hand" / "2-kept" / "TASK.md"
        plans.write_section(root, ["hand", "kept"], "Delivery", "landed", item="step")
        closed = plans.done(root, ["hand", "kept"])
        log = plans.section_text(plans.read(kept)[1], "Delivery")
        c.ok(front(kept)["status"] == "done" and "closed by hand -- open: other" in log, f"by hand {closed}")
        closed = plans.done(root, ["hand", "left"])
        c.ok(not (root / "plans" / "hand" / "1-left").exists() and closed == ["hand"], f"the prepared item {closed}")
        c.ok(front(root / "plans" / "hand" / "PROJECT.md")["status"] == "done" and clean(root, "hand"),
             f"check {P.of(plans.check(root), 'hand')}")
        refuse("done-invalid", lambda: plans.done(root, ["hand"]))

    with case("a chain that cannot serve refuses", "template-invalid for neither or both of `leaf` and `next`, "
              "template-unknown for a `next` no tree carries, node-twice for two node files in a plan's folder") as c:
        template("loose", ["Ll"], "description2: none")
        refuse("template-invalid", lambda: plans.write_section(root, ["loose1"], "Ll", "x", template="loose"))
        template("loose", ["Ll"], "leaf: yes\nnext: d")
        refuse("template-invalid", lambda: plans.write_section(root, ["loose2"], "Ll", "x", template="loose"))
        template("loose", ["Ll"], "next: ghost")
        refuse("template-unknown", lambda: plans.write_section(root, ["loose3"], "Ll", "x", template="loose"))
        c.ok(not any((root / "plans" / one).exists() for one in ("loose1", "loose2", "loose3")), "nothing born")
        twin = root / "plans" / "menage" / "TASK.md"
        twin.write_text((root / "plans" / "menage" / "CHORE.md").read_text(encoding="utf-8"), encoding="utf-8")
        refuse("node-twice", lambda: plans.doc_of(root, "menage"))
        twin.unlink()

    with case("the templates the tree sees", "`templates --json`: the tree's own first, then the product's, each "
              "with its name, its origin, its description, `leaf` or the chain it opens, its sections; a template "
              "that cannot serve with its refusal; the text says one line each; nothing written") as c:
        before = {one: one.read_bytes() for one in sorted((root / "plans").rglob("*")) if one.is_file()}
        listed = json.loads(P.play(plans, ["templates", "--json"]))
        names = [(one["name"], one["origin"]) for one in listed]
        own = sorted(one.stem for one in place.glob("*.md"))
        c.ok(names == [(one, "tree") for one in own] + [("batch", "product"), ("phase", "product"), ("plan", "product")],
             f"the order {names}")
        by = {(one["name"], one["origin"]): one for one in listed}
        product = by.get(("plan", "product"), {})
        c.ok(product.get("sections") == ["Context", "Ground", "Expected", "Choices", "Items", "Delivery"]
             and product.get("chain") == ["plan", "phase", "batch"] and product.get("leaf") is False
             and product.get("description"), f"the product's plan {product}")
        c.ok(by.get(("batch", "product"), {}).get("leaf") is True and by[("batch", "product")].get("chain") == ["batch"],
             "the product's batch")
        c.ok(by.get(("a", "tree"), {}).get("chain") == ["a", "b", "c", "d"]
             and by[("a", "tree")].get("description") == "a level of the bench", f"a tree's chain {by.get(('a', 'tree'))}")
        loose = by.get(("loose", "tree"), {})
        c.ok(loose.get("refusal", {}).get("code") == "template-unknown" and "sections" not in loose, f"the refusal {loose}")
        text = P.play(plans, ["templates"]).splitlines()
        c.ok(len(text) == len(listed) and text[0].split()[0] == own[0] and any("template-unknown" in one for one in text),
             f"the text {text}")
        refuse("argument-unexpected", lambda: P.play(plans, ["templates", "plan"]))
        c.ok({one: one.read_bytes() for one in sorted((root / "plans").rglob("*")) if one.is_file()} == before,
             "templates wrote")

    return 0
