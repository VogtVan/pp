"""packages/plan/skills/pp-plan -- the CONSOLE of the plans keeper and the LAWS it writes, on
a real environment carrying the plan package: a writing verb waits for the plan's lock, reads its stdin
BEFORE it takes the lock, refuses an absent plan or a missing prose before it, and never takes a lock file away --
a session that waited and a newcomer never hold the plan's lock together;
the gestures announce their moves (address, new status, the nodes closed) and push the
plan's next move on its signal, a closed plan clearing it; a malformed call refuses by
name, a flag never taken for an address and no argument a one-line usage; a section piped
with a byte-order mark ahead reads as without it; a plan
gone takes its next move with it, and `repair` counts that clearing among its repairs; `section … --remove=<n>` takes an occurrence without reading stdin; `constrain`
poses, amends and retires a law by its code and `serve` writes a row the same by argv and
by stdin; a plan is born with the blueprint law under a code derived from its slug; the
verifier answers for the package's own families."""
from __future__ import annotations

import contextlib
import io
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from conductor import events
from conductor.state import lock as engine_lock

from tests.harness import support

P = support(__file__, "plan")
GROUND, EXPECTED, TESTS, CHOICES = P.GROUND, P.EXPECTED, P.TESTS, P.CHOICES


PROC = Path("/proc/self/fd").is_dir()      # where the system shows a process's files and what it waits on


def holds(pid: int, path: Path) -> bool:
    """-> whether the process `pid` has `path` open, read at /proc."""
    try:
        return any(os.path.realpath(one) == str(path.resolve()) for one in Path(f"/proc/{pid}/fd").iterdir())
    except OSError:
        return False


def reading_stdin(pid: int) -> bool:
    """-> whether the process `pid` waits in a read of its stdin, a pipe: its syscall's first argument the fd 0 and
    its wait channel a pipe's, read at /proc."""
    try:
        fields = Path(f"/proc/{pid}/syscall").read_text(encoding="utf-8").split()
        waits = Path(f"/proc/{pid}/wchan").read_text(encoding="utf-8")
    except OSError:
        return False
    return len(fields) > 1 and fields[1] == "0x0" and "pipe" in waits


def until(predicate, timeout: float = 20.0) -> bool:
    """Polls `predicate` until it holds; False past the bound."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return bool(predicate())


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
    call = [sys.executable, str(P.script_path(root)), "section", "locked", "Ground"]
    with plans.regime().held(root / "plans" / "locked"):
        try:
            subprocess.run(call, input=GROUND, capture_output=True, text=True, timeout=2)
            waited = False          # it went through: no critical section
        except subprocess.TimeoutExpired:
            waited = True           # it BLOCKED on the lock, as a verb must
    freed = subprocess.run(call, input=GROUND, capture_output=True, text=True, timeout=20)
    through = P.answers(freed.stdout)[:1] == [("Ground", ("inserted",), "locked", f"{root.name}/plans/locked/PLAN.md")]
    if waited and freed.returncode == 0 and through:
        bench.held("a writing verb waits for the plan's lock", "blocked while another session "
                   "holds it, through once released -- the read-modify-write span is closed")
    else:
        bench.failures.append(f"  ✗ plan lock                     waited={waited} "
                              f"rc={freed.returncode} said={freed.stdout.strip()[:60]}")

    # --- stdin is read BEFORE the lock: a verb that waits for its prose holds nobody up -------
    # the first call is started with its stdin still open: read at /proc, it waits in the read of its stdin with no
    # file open on the plan's lock; then a second call fed at once on the same plan must go through while the first
    # still waits for its prose. Without /proc the case is not played: nothing shows where the first call waits
    lockfile = root / "plans" / "locked.lock"
    if PROC:
        first = subprocess.Popen([sys.executable, str(P.script_path(root)), "section", "locked", "Expected"],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        blocked = until(lambda: first.poll() is not None or reading_stdin(first.pid))
        waiting = first.poll() is None and reading_stdin(first.pid) and not holds(first.pid, lockfile)
        try:
            second = subprocess.run(call, input=GROUND, capture_output=True, text=True, timeout=20)
            passed = second.returncode == 0
        except subprocess.TimeoutExpired:
            passed = False      # it waited on the lock the first call holds while it reads its stdin
        out, _ = first.communicate(input="the decision of the day\n", timeout=20)
        if (blocked and waiting and passed and first.returncode == 0 and P.answers(out)[:1]
                and P.answers(out)[0][0] == "Expected"):
            bench.held("stdin is read before the lock", "the first call seen at /proc waiting on its stdin with no "
                       "file on the plan's lock: a second call on the same plan went through, then the first wrote "
                       "once fed")
        else:
            bench.failures.append(f"  ✗ stdin before the lock         blocked={blocked} waiting={waiting} passed={passed} "
                                  f"rc={first.returncode} said={out.strip()[:60]!r}")
    else:
        print("  · stdin is read before the lock NOT PLAYED -- no /proc here to see where the first call waits")

    # --- no lock is left for a plan that is not there ---------------------------------------
    with case("no lock is left for a plan that is not there", "a writing verb refused on a plan absent from "
              "every tree -- a node under it, a law, a move, a rename, a material, a removal, a birth with no "
              "prose -- refuses and leaves no `plans/<slug>.lock`; a removal says path-unknown, never "
              "the refusal of a birth") as c:
        for argv, stdin, owed in ((["done", "nowhere/p/b/step"], "", "path-unknown"),
                                  (["section", "nowhere/p", "Ground"], GROUND, "path-unknown"),
                                  (["block", "nowhere", "why"], "", "path-unknown"),
                                  (["constrain", "nowhere", "--section", "production"], "a law\n", "path-unknown"),
                                  (["section", "nowhere", "Context"], "", "prose-missing"),
                                  (["move", "nowhere/p", "saga", "1"], "", "path-unknown"),
                                  (["rename", "nowhere/p", "q"], "", "path-unknown"),
                                  (["material", "nowhere", "core", "../src"], "", "path-unknown"),
                                  (["section", "nowhere", "Ground", "--remove=1"], "", "path-unknown")):
            told = io.StringIO()
            code = 0
            with contextlib.redirect_stderr(told):
                try:
                    played(argv, stdin=stdin)
                except SystemExit as stop:
                    code = stop.code
            said = told.getvalue()
            c.ok(code not in (0, None) and said.startswith(f"pp-plan: {owed} --"), f"{argv}: rc {code} {said.strip()[:80]!r}")
            c.ok(not (root / "plans" / "nowhere").exists() and not (root / "plans" / "nowhere.lock").exists(),
                 f"{argv}: {sorted(one.name for one in (root / 'plans').glob('nowhere*'))}")

    # --- the lock file is never taken away: a waiter and a newcomer never hold it together ---
    # the critical section held here on a plan not born, a birth of it waiting on the lock in a second process -- its
    # prose read, its lock file seen open at /proc --; the section left, a newcomer tries the lock at once and keeps it
    # while the birth may finish: the birth must never go through under the newcomer's hold. The waiter not seen on
    # the lock within its bound is a red; without /proc the case is not played
    lockfile = root / "plans" / "duel.lock"
    birth = [sys.executable, str(P.script_path(root)), "section", "duel", "Context"]
    if PROC:
        with plans.guarded(root, "duel"):
            waiter = subprocess.Popen(birth, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, text=True)
            waiter.stdin.write("The duel.\n")
            waiter.stdin.close()
            seen = until(lambda: waiter.poll() is not None or holds(waiter.pid, lockfile)) and waiter.poll() is None
        lease = engine_lock.try_(lockfile)
        together = False
        if lease is not None:
            try:
                waiter.wait(timeout=2)
                together = True                # the birth went through while the newcomer held the lock
            except subprocess.TimeoutExpired:
                pass
            finally:
                engine_lock.release(lease)
        waiter.wait(timeout=20)
        if seen and not together and waiter.returncode == 0 and (root / "plans" / "duel" / "PLAN.md").is_file():
            bench.held("a waiter and a newcomer never hold the lock together", "the waiter seen at /proc on the "
                       "lock of a plan not born; the section left, a newcomer's lease and the waiting birth never "
                       "overlap; the birth went through after")
        else:
            bench.failures.append(f"  ✗ the lock held twice           seen={seen} together={together} rc={waiter.returncode}")
    else:
        print("  · a waiter and a newcomer never hold the lock together NOT PLAYED -- no /proc here to see the "
              "waiter on the lock")

    # --- the gestures announce: the move, the push, the clear --------------------------------
    def pushed(said, slug):
        """-> the last push or clear of the plan `slug`: (verb, its next move parsed)."""
        found = [one for one in P.pushes(said) if one[1] == plans.SIGNAL and one[2] == f"plan:{slug}"]
        return (found[-1][0], P.move_of(found[-1][3])) if found else None

    with case("the gestures announce", "a birth says the path from the repo root; Choices says doing, "
              "Delivery says done and what it closed, deepest first; the push follows each move, the "
              "closed plan clears") as c:
        said = played(["section", "saga", "Context"], stdin="Prose.")
        c.ok(P.answers(said) == [("Context", ("born",), "saga", f"{root.name}/plans/saga/PLAN.md")], f"birth {said}")
        c.ok(pushed(said, "saga") == ("::push", ("plan", "phases", "plan:saga")), f"push {said}")
        played(["section", "saga", "Expected", "-"], stdin=EXPECTED)
        played(["section", "saga", "Choices"], stdin=CHOICES)
        said = played(["section", "saga", "Items"], stdin="\ufeff- p1 -- Phase one\n")   # PowerShell's BOM ahead
        c.ok([one[:3] for one in P.answers(said)] == [("Items", ("inserted",), "saga")], f"Items {said}")
        c.ok(pushed(said, "saga") == ("::push", ("phase", "framing", "plan:saga/p1")), f"push {said}")
        said = played(["section", "saga/p1", "Ground"], stdin=GROUND)
        c.ok(P.answers(said) == [("Ground", ("born", "inserted"), "saga/p1", f"{root.name}/plans/saga/1-p1/PHASE.md")],
             f"Ground {said}")
        played(["section", "saga/p1", "Expected"], stdin=EXPECTED)
        said = played(["section", "saga/p1", "Choices"], stdin=CHOICES)
        c.ok(P.moves(said).get("saga/p1", P.Move("", (), "")).status == "doing", f"Choices {said}")
        played(["section", "saga/p1", "Items"], stdin="- b -- the batch\n")
        for name, prose in (("Ground", GROUND), ("Expected", EXPECTED), ("Tests", TESTS), ("Choices", CHOICES)):
            played(["section", "saga/p1/b", name], stdin=prose)
        played(["section", "saga/p1/b", "Items"], stdin="- the-step -- the step\n")
        said = played(["section", "saga/p1/b", "Delivery", "--item", "the-step"], stdin="landed")
        moved = P.moves(said).get("saga/p1/b", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == ("saga/p1", "saga"), f"Delivery {said}")
        c.ok(pushed(said, "saga") == ("::clear", None), f"clear {said}")
        played(["section", "chain", "Context"], stdin="Prose.")
        played(["section", "chain", "Expected"], stdin=EXPECTED)
        played(["section", "chain", "Choices"], stdin=CHOICES)
        played(["section", "chain", "Items"], stdin="- p -- P.\n")
        for name, prose in (("Ground", GROUND), ("Expected", EXPECTED), ("Choices", CHOICES)):
            played(["section", "chain/p", name], stdin=prose)
        played(["section", "chain/p", "Items"], stdin="- b -- B.\n")
        for name, prose in (("Ground", GROUND), ("Expected", EXPECTED), ("Tests", TESTS), ("Choices", CHOICES)):
            played(["section", "chain/p/b", name], stdin=prose)
        played(["section", "chain/p/b", "Items"], stdin="- the-step -- the step\n- last-step -- the last\n")
        said = played(["done", "chain/p/b/the-step"])
        c.ok(P.moves(said).get("chain/p/b/the-step") == P.Move("done", (), "") and "closes" not in said,
             f"done {said}")
        reason = ["waits", "a", "word"]
        said = played(["block", "chain/p/b", *reason])
        c.ok(P.moves(said).get("chain/p/b") == P.Move("blocked", (), " ".join(reason)), f"block {said}")
        said = played(["section", "chain/p/b", "Delivery", "--item", "last-step"], stdin="landed")
        moved = P.moves(said).get("chain/p/b", P.Move("", (), ""))
        c.ok(moved.status == "done" and moved.closes == ("chain/p", "chain"), f"Delivery {said}")
        c.ok(pushed(said, "chain") == ("::clear", None), f"clear {said}")

    # --- the arity: a malformed call refuses by name ----------------------------------------
    with case("a malformed call refuses by name", "argument-unexpected, argument-missing, verb-unknown -- one "
              "sentence with the verb's usage, never the docstring; a trailing `-` is the stdin marker; "
              "`set` and `reopen` are verbs no more") as c:
        out = refuse("argument-unexpected", lambda: played(["section", "saga", "Expected", "extra"], stdin="x"))
        c.ok(plans.USAGE["section"] in out and "DETERMINISTIC" not in out, f"section {out}")
        out = refuse("argument-missing", lambda: played(["done"]))
        c.ok(plans.USAGE["done"] in out, f"done {out}")
        out = refuse("argument-missing", lambda: played(["rename", "saga/p1"]))
        c.ok(plans.USAGE["rename"] in out, f"rename {out}")
        out = refuse("verb-unknown", lambda: played(["frobnicate"]))
        c.ok("section, done, block, move" in out, f"verbs {out}")
        refuse("verb-unknown", lambda: played(["set", "saga", "done"]))
        refuse("verb-unknown", lambda: played(["reopen", "saga/p1"]))
        out = refuse("argument-unexpected", lambda: played(["section", "saga", "Expected", "--frob"], stdin="x"))
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
              "removed: `next-move` no longer serves it, `repair` clears it and counts it among its repairs") as c:
        played(["section", "gone", "Context"], stdin="Prose.")
        events.stand(root, plans.SIGNAL, "plan:gone", "the plan has no phase yet (plan:gone)")
        c.ok(any("plan:gone" in one for one in played(["next-move"]).splitlines()), "served while it stands")
        shutil.rmtree(root / "plans" / "gone")
        c.ok(not any("plan:gone" in one for one in played(["next-move"]).splitlines()), "served once gone")
        mended = plans.repair(root)[0]
        c.ok(any("`gone`" in one for one in mended), f"the clearing among the repairs {mended}")
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
        c.ok(P.title_line(plans, mur) == plans.title_of(root, plans.read(mur)[0])
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
    with case("the blueprint law rides with the plan's template",
              "a plan born carries no law of its own; its mount carries the template `plan`, whose front "
              "poses the blueprint law -- one code for every plan") as c:
        plans.write_section(root, ["le-mur-du-jardin"], "Context", "The wall.")
        plans.write_section(root, ["la-toiture"], "Context", "The roof.")
        posed = [P.laws(root / "plans" / slug / "PLAN.md").get("constraints.production", {})
                 for slug in ("le-mur-du-jardin", "la-toiture")]
        c.ok(posed == [{}, {}], f"laws in the plans {posed}")
        chain = [one["doc"] for one in plans.mount_chain(root, ["la-toiture"])]
        template = P.laws(plans.level(root, "plan").path).get("constraints.production", {})
        c.ok("plan:templates/plan.md" in chain and list(template) == ["TPL1"], f"chain {chain} template {template}")

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
    with case("the verifier answers for plan's one family",
              "plan:<address> at every depth is an ADDRESS: a born plan, a born phase and a batch merely "
              "PREPARED in its parent's Items pass; an unknown address refuses with the resolver's "
              "reason, an empty name refuses address-malformed, plan-phase:, plan-lot: and any other "
              "family refuse family-foreign -- read-only, the vector on stdin, no argument") as c:
        for name, prose in (("Context", "A plan to verify."), ("Expected", "What it frames."),
                            ("Choices", "Its choices."), ("Items", "- socle -- the base course\n")):
            plans.write_section(root, ["verif"], name, prose)
        for name, prose in (("Ground", "The ground of the base."), ("Expected", "What it frames."),
                            ("Choices", "Its choices."), ("Items", "- b1 -- the first batch\n")):
            plans.write_section(root, ["verif", "socle"], name, prose)
        for vector in ("plan:verif", "plan:verif/socle", "plan:verif/socle/b1"):
            with fed(vector + "\n"):
                c.ok(plans.main(["verify"]) == 0, vector)
        with fed("plan:nulle-part\n"):
            refuse("path-unknown", lambda: plans.main(["verify"]))
        with fed("plan:verif/socle/nowhere\n"):
            refuse("path-unknown", lambda: plans.main(["verify"]))
        for vector in ("plan:", "plan:verif//b1"):
            with fed(vector + "\n"):
                refuse("address-malformed", lambda: plans.main(["verify"]))
        for vector in ("plan-phase:verif/socle", "plan-lot:verif/socle/b1", "thread:piscine"):
            with fed(vector + "\n"):
                refuse("family-foreign", lambda: plans.main(["verify"]))
        refuse("argument-unexpected", lambda: plans.main(["verify", "verif"]))

    return 0
