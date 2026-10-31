"""packages/plan/skills/pp-plan -- the CONSOLE of the plans keeper and the LAWS it writes, on
a real environment carrying the plan package: a writing verb waits for the plan's lock;
the gestures announce their moves (address, new status, the nodes closed) and push the
plan's next move on its signal, a closed plan clearing it; a malformed call refuses by
name, a flag never taken for an address and no argument a one-line usage; a plan
gone takes its next move with it; `section … --remove=<n>` takes an occurrence without reading stdin; `constrain`
poses, amends and retires a law by its code and `serve` writes a row the same by argv and
by stdin; a plan is born with the blueprint law under a code derived from its slug; the
verifier answers for the package's own families."""
from __future__ import annotations

import contextlib
import io
import shutil
import subprocess
import sys

from conductor import events

from tests.harness import support

P = support(__file__, "plan")
GROUND, TARGET, EXPECTED, TESTS = P.GROUND, P.TARGET, P.EXPECTED, P.TESTS


def scenario(bench) -> int:
    refuse = bench.expect_exit
    root = P.house(bench, "plan-console").made
    plans = P.script(root)
    plans.home = lambda: root
    fed = P.fed

    def case(label, detail=""):
        return P.case(bench, label, detail)

    def played(argv, stdin=""):
        return P.play(plans, argv, stdin)

    def clean(slug):
        return P.of(plans.check(root), slug) == []

    # --- the plan's CRITICAL SECTION: a writing verb waits while the lock is held ----
    played(["section", "locked", "Context"], stdin="Prose.")
    # the VENDORED script in a second PROCESS, the way another session would come
    call = [sys.executable, str(P.script_path(root)), "section", "locked", "Target"]
    with plans.regime().held(root / "plans" / "locked"):
        try:
            subprocess.run(call, input=TARGET, capture_output=True, text=True, timeout=2)
            waited = False          # it went through: no critical section
        except subprocess.TimeoutExpired:
            waited = True           # it BLOCKED on the lock, as a verb must
    freed = subprocess.run(call, input=TARGET, capture_output=True, text=True, timeout=20)
    through = P.answers(freed.stdout)[:1] == [("Target", ("replaced",), "locked", f"{root.name}/plans/locked/PLAN.md")]
    if waited and freed.returncode == 0 and through:
        bench.held("a writing verb waits for the plan's lock", "blocked while another session "
                   "holds it, through once released -- the read-modify-write span is closed")
    else:
        bench.failures.append(f"  ✗ plan lock                     waited={waited} "
                              f"rc={freed.returncode} said={freed.stdout.strip()[:60]}")

    # --- the gestures announce: the move, the push, the clear --------------------------------
    def pushed(said, slug):
        """-> the last push or clear of the plan `slug`: (verb, its next move parsed)."""
        found = [one for one in P.pushes(said) if one[1] == plans.SIGNAL and one[2] == f"plan:{slug}"]
        return (found[-1][0], P.move_of(found[-1][3])) if found else None

    with case("the gestures announce", "a birth says the path from the repo root; Expected says doing, "
              "Delivery says done and what it closed, deepest first; the push follows each move, the "
              "closed plan clears") as c:
        said = played(["section", "saga", "Context"], stdin="Prose.")
        c.ok(P.answers(said) == [("Context", ("born",), "saga", f"{root.name}/plans/saga/PLAN.md")], f"birth {said}")
        c.ok(pushed(said, "saga") == ("::push", ("plan", "phases", "plan:saga")), f"push {said}")
        played(["section", "saga", "Target", "-"], stdin=TARGET)
        played(["section", "saga", "Expected"], stdin=EXPECTED)
        said = played(["section", "saga", "Items"], stdin="- p1 -- Phase one\n")
        c.ok([one[:3] for one in P.answers(said)] == [("Items", ("replaced",), "saga")], f"Items {said}")
        c.ok(pushed(said, "saga") == ("::push", ("phase", "framing", "plan-phase:saga/p1")), f"push {said}")
        said = played(["section", "saga/p1", "Ground"], stdin=GROUND)
        c.ok(P.answers(said) == [("Ground", ("born", "replaced"), "saga/p1", f"{root.name}/plans/saga/1-p1/PHASE.md")],
             f"Ground {said}")
        played(["section", "saga/p1", "Target"], stdin=TARGET)
        said = played(["section", "saga/p1", "Expected"], stdin=EXPECTED)
        c.ok(P.moves(said).get("saga/p1", P.Move("", (), "")).status == "doing", f"Expected {said}")
        played(["section", "saga/p1", "Items"], stdin="- b -- the batch\n")
        for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED), ("Tests", TESTS)):
            played(["section", "saga/p1/b", name], stdin=prose)
        said = played(["section", "saga/p1/b", "Delivery"], stdin="landed")
        moved = P.moves(said).get("saga/p1/b", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == ("saga/p1", "saga"), f"Delivery {said}")
        c.ok(pushed(said, "saga") == ("::clear", None), f"clear {said}")
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
        c.ok(P.moves(said).get("chain/p/b/the-step") == P.Move("done", (), "") and "closes" not in said,
             f"done {said}")
        reason = ["waits", "a", "word"]
        said = played(["block", "chain/p/b", *reason])
        c.ok(P.moves(said).get("chain/p/b") == P.Move("blocked", (), " ".join(reason)), f"block {said}")
        said = played(["section", "chain/p/b", "Delivery"], stdin="landed")
        moved = P.moves(said).get("chain/p/b", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == ("chain/p", "chain"), f"Delivery {said}")
        c.ok(pushed(said, "chain") == ("::clear", None), f"clear {said}")

    # --- the arity: a malformed call refuses by name ----------------------------------------
    with case("a malformed call refuses by name", "argument-unexpected, argument-missing, verb-unknown -- one "
              "sentence with the verb's usage, never the docstring; a trailing `-` is the stdin marker; "
              "`set` and `reopen` are verbs no more") as c:
        out = refuse("argument-unexpected", lambda: played(["section", "saga", "Target", "extra"], stdin="x"))
        c.ok(plans.USAGE["section"] in out and "DETERMINISTIC" not in out, f"section {out}")
        out = refuse("argument-missing", lambda: played(["done"]))
        c.ok(plans.USAGE["done"] in out, f"done {out}")
        out = refuse("argument-missing", lambda: played(["rename", "saga/p1"]))
        c.ok(plans.USAGE["rename"] in out, f"rename {out}")
        out = refuse("verb-unknown", lambda: played(["frobnicate"]))
        c.ok("section, done, block, move" in out, f"verbs {out}")
        refuse("verb-unknown", lambda: played(["set", "saga", "done"]))
        refuse("verb-unknown", lambda: played(["reopen", "saga/p1"]))
        out = refuse("argument-unexpected", lambda: played(["section", "saga", "Target", "--frob"], stdin="x"))
        c.ok("--append" in out, f"flags {out}")
        for argv in (["done", "--help"], ["block", "--help", "why"], ["rename", "--help", "x"], ["constrain", "--help"],
                     ["serve", "--help", "x"], ["material", "--help"]):
            refuse("argument-unexpected", lambda argv=argv: played(argv))
        c.ok(not list((root / "plans").glob("--*")), f"a lock under a flag {sorted((root / 'plans').glob('--*'))}")
        told = io.StringIO()
        with contextlib.redirect_stderr(told):
            code = plans.main([])
        c.ok(code == 2 and 0 < len(told.getvalue()) < 300 and "section" in told.getvalue(),
             f"bare {code} {len(told.getvalue())}")

    with case("a plan gone takes its line with it", "the bus holds the next move of a plan whose folder was "
              "removed: `next-move` no longer serves it, `repair` clears it") as c:
        played(["section", "gone", "Context"], stdin="Prose.")
        events.stand(root, plans.SIGNAL, "plan:gone", "the plan has no phase yet (plan:gone)")
        c.ok(any("plan:gone" in one for one in played(["next-move"]).splitlines()), "served while it stands")
        shutil.rmtree(root / "plans" / "gone")
        c.ok(not any("plan:gone" in one for one in played(["next-move"]).splitlines()), "served once gone")
        said = played(["repair"])
        c.ok(pushed(said, "gone") == ("::clear", None), f"repair {said[-300:]}")

    # --- the console removes an occurrence by its flag --------------------------------------
    with case("the console removes by its flag", "section … --remove=1 plays without reading stdin, says the "
              "occurrence it took; a done batch, its phase and its plan keep their fronts; --remove with "
              "--append, a rank that is no positive integer refuse argument-unexpected") as c:
        docs = [root / "plans" / "saga" / "PLAN.md", root / "plans" / "saga" / "1-p1" / "PHASE.md",
                root / "plans" / "saga" / "1-p1" / "1-b" / "BATCH.md"]
        fronts = [plans.read(one)[0] for one in docs]
        c.ok([one["status"] for one in fronts] == ["done", "done", "done"], "the statuses before")
        btext = docs[2].read_text(encoding="utf-8")
        docs[2].write_text(btext + "## Le log\n\n(à la livraison)\n\n## Le log\n\nthe journal\n", encoding="utf-8")
        doubled = docs[2].read_bytes()
        for flags in (["--remove", "--append"], ["--remove=x"], ["--remove=0"]):
            refuse("argument-unexpected", lambda: played(["section", "saga/p1/b", "Le log"] + flags))
            c.ok(docs[2].read_bytes() == doubled, f"{flags}: bytes moved")
        unread, out = io.StringIO("## a prose the removal never reads"), io.StringIO()
        spot, sys.stdin = sys.stdin, unread
        try:
            with contextlib.redirect_stdout(out):
                plans.main(["section", "saga/p1/b", "Le log", "--remove=1"])
        finally:
            sys.stdin = spot
        said = out.getvalue()
        c.ok(unread.tell() == 0 and "pp-plan: Le log (1 of 2" in said, f"said {said}")
        c.ok(docs[2].read_text(encoding="utf-8") == btext + "## Le log\n\nthe journal\n", "the occurrence taken")
        c.ok([plans.read(one)[0] for one in docs] == fronts, "the fronts")

    # --- the framing writes its OWN sections, with no author's package anywhere -------
    mur = root / "plans" / "le-mur" / "PLAN.md"
    with case("the framing writes its own sections",
              "`constrain` and `serve` land on a plan document through the engine's writer, "
              "imported by the vendored bootstrap -- the composition carries no author's package, "
              "and the body is untouched") as c:
        wall = "The wall."
        plans.write_section(root, ["le-mur"], "Context", wall)
        law = "chaque pierre porte son mortier et le dit"
        with fed(law + "\n"):
            c.ok(plans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0, "constrain")
        c.ok(plans.main(["serve", "le-mur", "reference:", "README.md"]) == 0, "serve")
        c.ok(P.laws(mur).get("constraints.production", {}).get("KMU1") == law, f"laws {P.laws(mur)}")
        written = mur.read_text(encoding="utf-8")
        c.ok("serve: |\n  reference: README.md" in written, "the serve row")
        c.ok(P.title_line(plans, mur) == plans.title_of(plans.read(mur)[0])
             and plans.section_text(plans.read(mur)[1], "Context").strip() == wall, "the body")

    # --- a law amends and retires BY ITS CODE; a retired law disappears, nothing kept --------
    def production():
        """-> the KMU laws the wall poses in production -- its blueprint law aside."""
        return {code: text for code, text in P.laws(mur).get("constraints.production", {}).items()
                if code.startswith("KMU")}

    with case("a law amends and retires by its code; a retired law disappears",
              "a piped line opening on a posed code replaces that law in place, a bare line derives the "
              "next code; `--retire` takes the law out (the emptied block with it) and keeps NOTHING -- no "
              "`retired:` entry, so a retired number may be derived again; an unknown code refuses; the "
              "serve rows untouched") as c:
        amended, roof = "chaque pierre porte son mortier, et le dit", "la toiture suit"
        with fed(f"KMU1  {amended}\n{roof}\n"):
            c.ok(plans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0, "amend")
        c.ok(production() == {"KMU1": amended, "KMU2": roof}, f"amended {production()}")
        c.ok(mur.read_text(encoding="utf-8").count("KMU1") == 1, "KMU1 twice")
        with fed("KZZ9  nulle part\n"):
            refuse("code-unknown", lambda: plans.main(["constrain", "le-mur", "--section", "production"]))
        c.ok(plans.main(["constrain", "le-mur", "--retire", "KMU1"]) == 0, "retire KMU1")
        written = mur.read_text(encoding="utf-8")
        c.ok(production() == {"KMU2": roof} and "KMU1" not in written and "retired" not in written,
             f"retired {production()}")
        ground = "le sol tient"
        with fed(ground + "\n"):
            c.ok(plans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0, "pose")
        c.ok(production().get("KMU3") == ground, f"numbered past KMU2 {production()}")
        c.ok(plans.main(["constrain", "le-mur", "--retire", "KMU2"]) == 0
             and plans.main(["constrain", "le-mur", "--retire", "KMU3"]) == 0, "retire KMU2, KMU3")
        written = mur.read_text(encoding="utf-8")
        c.ok("KMU2" not in written and "KMU3" not in written and "retired" not in written, "retired again")
        night = "la nuit tombe"
        with fed(night + "\n"):
            c.ok(plans.main(["constrain", "le-mur", "KMU", "--section", "behavior"]) == 0, "behavior")
        c.ok(P.laws(mur).get("constraints.behavior") == {"KMU1": night}, "a retired number returns")
        c.ok(plans.main(["constrain", "le-mur", "--retire", "KMU1"]) == 0, "retire behavior")
        written = mur.read_text(encoding="utf-8")
        c.ok("constraints.behavior" not in written and "retired" not in written, "the emptied block")
        with fed("encore\n"):
            c.ok(plans.main(["constrain", "le-mur", "KMU", "--section", "production"]) == 0, "pose again")
        c.ok(production().get("KMU1") == "encore"
             and "serve: |\n  reference: README.md" in mur.read_text(encoding="utf-8"), "KMU1, the serve row")
        refuse("code-unknown", lambda: plans.main(["constrain", "le-mur", "--retire", "KMU9"]))
        refuse("argument-missing", lambda: plans.main(["constrain", "le-mur", "--retire"]))
        refuse("argument-unexpected", lambda: plans.main(["constrain", "le-mur", "KMU", "--retire", "KMU1"]))
        c.ok(clean("le-mur"), "check")

    # --- a plan is BORN with the blueprint law, under a code of its own ---------------
    codes = []
    with case("a plan is born with its blueprint law",
              "the template carries the rule and the script derives its code from the slug -- "
              "KLMD1 and KLT1: two plans of one instance never declare the same code") as c:
        plans.write_section(root, ["le-mur-du-jardin"], "Context", "The wall.")
        plans.write_section(root, ["la-toiture"], "Context", "The roof.")
        for slug in ("le-mur-du-jardin", "la-toiture"):
            posed = P.laws(root / "plans" / slug / "PLAN.md").get("constraints.production", {})
            codes += [code for code, text in posed.items() if text == plans.BLUEPRINT]
        c.ok(codes == ["KLMD1", "KLT1"], f"codes {codes}")

    # --- a row is written the same by argv and by stdin, blanks inside brackets kept -------
    with case("a row is written the same by argv and by stdin",
              "a piped token keeps the blanks inside its brackets: the same block by both ways, read "
              "back by the engine's reader in as many tokens; an open bracket refuses and leaves the "
              "bytes; the answer names the line range alone") as c:
        reading = sys.modules["conductor"].reading
        tagged = ["reference:", "W.md[## Beta..## Gamma]", "NOTE.md"]
        plans.write_section(root, ["le-toit"], "Context", "The roof.")
        toit = root / "plans" / "le-toit" / "PLAN.md"
        with fed(" ".join(tagged) + "\n"):
            c.ok(plans.main(["serve", "le-mur", "-"]) == 0, "by stdin")
        c.ok(plans.main(["serve", "le-toit", *tagged]) == 0, "by argv")
        block = "serve: |\n  " + " ".join(tagged) + "\n"
        c.ok(block in mur.read_text(encoding="utf-8") and block in toit.read_text(encoding="utf-8"), "the same block")
        c.ok(reading.serve_sections(reading.read(mur)) == ((tuple(tagged),),), "the engine's reading")
        before = mur.read_bytes()
        with fed("reference: W.md[## Beta NOTE.md\n"):
            refuse("serve-range-malformed", lambda: plans.main(["serve", "le-mur", "-"]))
        c.ok(mur.read_bytes() == before, "the bytes after a refusal")
        said = played(["serve", "le-toit", "-"], stdin="code: x.py[10-40] x.py[def a..def b]\n")
        c.ok(said.count("x.py[10-40]") == 1 and "x.py[def a" not in said, f"said {said}")
        c.ok(clean("le-mur") and clean("le-toit"), "check")

    # --- the verifier: plan's own families, an ADDRESS that resolves --------------------
    with case("the verifier answers for plan's own families",
              "plan:, plan-phase: and plan-lot: are ADDRESSES: a born plan, a born phase and a batch merely "
              "PREPARED in its parent's Items pass; an unknown address refuses with the resolver's "
              "reason, a depth that does not fit its family and a foreign family refuse by name -- "
              "read-only, the vector on stdin, no argument") as c:
        for name, prose in (("Context", "A plan to verify."), ("Target", "Its target."),
                            ("Expected", "What it frames."), ("Items", "- socle -- the base course\n")):
            plans.write_section(root, ["verif"], name, prose)
        for name, prose in (("Ground", "The ground of the base."), ("Target", "Its target."),
                            ("Expected", "What it frames."), ("Items", "- b1 -- the first batch\n")):
            plans.write_section(root, ["verif", "socle"], name, prose)
        for vector in ("plan:verif", "plan-phase:verif/socle", "plan-lot:verif/socle/b1"):
            with fed(vector + "\n"):
                c.ok(plans.main(["verify"]) == 0, vector)
        with fed("plan:nulle-part\n"):
            refuse("path-unknown", lambda: plans.main(["verify"]))
        with fed("plan-lot:verif/socle/nowhere\n"):
            refuse("path-unknown", lambda: plans.main(["verify"]))
        with fed("plan-phase:verif\n"):
            refuse("address-depth", lambda: plans.main(["verify"]))
        with fed("thread:piscine\n"):
            refuse("family-foreign", lambda: plans.main(["verify"]))
        refuse("argument-unexpected", lambda: plans.main(["verify", "verif"]))

    return 0
