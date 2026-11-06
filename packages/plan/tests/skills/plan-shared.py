"""packages/plan/skills/pp-plan -- a plan SHARED by the runs opened under one root of
documents, on two real environments carrying the plan package, each run opened by the
console under the same root (`PP_DOCUMENTS` at `-new`) and the vendored script played
under `PP_RUN`: (a) `section <slug> Context --shared` births the plan under
`<root>/plans/`, its lock beside it, nothing in the instance; (b) `documents-none` with no
run and under a run opened with no root, nothing written; (c) `--shared` on another section
or a deeper address refuses; (d) `slug-taken` across the trees, both ways; (e) the instance
first: a plan of the same name in the instance hides the shared one; (f) the other instance
mounts the shared plan through the console; (g) the other instance frames, checks off and
delivers it -- the cascade closes it, `check` clean from both; (h) two processes write two
sections at once, both land; (i) `next-move` and `status --json` from the first instance say
the node the second advanced, `shared` on the nodes, the plan counted once; (j) `material
<slug> work` admitted, another undeclared name refused."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.harness import cli, support

P = support(__file__, "plan")
GROUND, TARGET, EXPECTED, TESTS = P.GROUND, P.TARGET, P.EXPECTED, P.TESTS
BODY = "shared-plan-body-7"           # one token: what the mount must show, never a sentence


def _frame_all(plans, tree: Path, slug: str) -> None:
    """A plan framed down to one todo: a phase and a batch born, the batch's todo prepared."""
    w = P.Writer(plans)
    w.section(tree, [slug], "Target", TARGET)
    w.section(tree, [slug], "Expected", EXPECTED)
    w.section(tree, [slug], "Items", "- ph -- the phase")
    w.section(tree, [slug, "ph"], "Ground", GROUND)
    w.section(tree, [slug, "ph"], "Target", TARGET)
    w.section(tree, [slug, "ph"], "Expected", EXPECTED)
    w.section(tree, [slug, "ph"], "Items", "- bt -- the batch")
    w.framed(tree, [slug, "ph", "bt"])
    w.section(tree, [slug, "ph", "bt"], "Items", "- t1 -- the todo")


def scenario(bench) -> int:
    refuse = bench.expect_exit
    a = P.house(bench, "shared-a", pin=True)
    b = P.house(bench, "shared-b", pin=True)
    shared = Path(tempfile.mkdtemp(prefix="shared-root-")).resolve()
    key_a, key_b = P.opened(a, shared), P.opened(b, shared)
    key_bare = P.opened(a)                       # a run of A opened with no root
    pa, pb = P.script(a.made), P.script(b.made)

    def case(label, detail=""):
        return P.case(bench, label, detail)

    # --- (a) the birth under the shared root -------------------------------------------------
    with case("(a) --shared births under the root", "R/plans/s/PLAN.md and its lock beside it; nothing "
              "under the instance's plans/; the push names plan:s") as c:
        with P.under(key_a):
            said = P.play(pa, ["section", "s", "Context", "--shared"], BODY + "\n")
        c.ok(key_a and key_b and key_bare, f"runs opened: {key_a!r} {key_b!r} {key_bare!r}")
        c.ok((shared / "plans" / "s" / "PLAN.md").is_file(), "the shared document")
        c.ok((shared / "plans" / "s.lock").is_file(), "the lock in the shared root")
        c.ok(not (a.made / "plans" / "s").exists(), "nothing in the instance")
        c.ok(any(one[0] == "::push" and one[2] == "plan:s" for one in P.pushes(said)), "the push")
        with P.under(key_a):
            c.ok(pa.tree_of(a.made, "s") == shared and pa.shared_root(a.made) == shared, "the tree resolved")

    # --- (b) no root, nothing written ---------------------------------------------------------
    with P.under(None):
        refuse("documents-none", lambda: pa.main(["section", "t", "Context", "--shared"]))
    with P.under(key_bare):
        refuse("documents-none", lambda: pa.main(["section", "t", "Context", "--shared"]))
    with case("(b) nothing written without a root", "no plans/t anywhere after the two refusals") as c:
        c.ok(not (a.made / "plans" / "t").exists() and not (shared / "plans" / "t").exists(), "no t")

    # --- (c) the flag on Context of a plan alone ---------------------------------------------
    with P.under(key_a):
        refuse("argument-unexpected", lambda: pa.main(["section", "s", "Target", "--shared"]))
        refuse("argument-unexpected", lambda: pa.main(["section", "s/ph", "Context", "--shared"]))

    # --- (d) slug-taken across the trees ----------------------------------------------------
    with P.under(key_b), P.fed("again\n"):
        refuse("slug-taken", lambda: pb.main(["section", "s", "Context", "--shared"]))
    with P.under(key_a):
        P.play(pa, ["section", "u", "Context"], "an instance plan\n")
        with P.fed("again\n"):
            refuse("slug-taken", lambda: pa.main(["section", "u", "Context", "--shared"]))
    with case("(d) the instance plan stays where it is", "u born in A's instance, not in the root") as c:
        c.ok((a.made / "plans" / "u" / "PLAN.md").is_file() and not (shared / "plans" / "u").exists(), "u")

    # --- (e) the instance first -----------------------------------------------------------------
    with case("(e) the instance's plan hides the shared one", "a copy of s in B's instance: tree_of "
              "answers the instance, status counts s once without `shared`") as c:
        shutil.copytree(shared / "plans" / "s", b.made / "plans" / "s")
        with P.under(key_b):
            c.ok(pb.tree_of(b.made, "s") == b.made, "the instance wins")
            listed = json.loads(P.play(pb, ["status", "--json"]))
        rows = [one for one in listed if one["address"] == "s"]
        c.ok(len(rows) == 1 and rows[0]["shared"] is False, f"rows={rows}")
        shutil.rmtree(b.made / "plans" / "s")

    # --- (f) the other instance mounts it through the console ---------------------------------
    with case("(f) the other run mounts the shared plan", "`-s pp-plan mount s` from B's run: the "
              "engine resolves plans/s/PLAN.md at the root of documents, the body served") as c:
        cli(b.engine, key_b, cwd=b.root)                 # past the boot's own step: the turn offers pp-plan
        shown = cli(b.engine, key_b, "-s", "pp-plan", "mount", "s", cwd=b.root)
        c.ok(shown.returncode == 0, f"rc={shown.returncode} {shown.stderr[-300:]!r} {shown.stdout[-400:]!r}")
        c.ok(BODY in shown.stdout, "the Context of the shared plan in the output")

    # --- (g) framed, checked off and delivered from the other instance -----------------------
    with case("(g) delivered from the other instance", "B frames s down to a todo, checks it off and "
              "writes the Delivery: batch, phase and plan close by the cascade; check clean from A and B") as c:
        with P.under(key_b):
            _frame_all(pb, shared, "s")
            P.play(pb, ["done", "s/ph/bt/t1"])
            moved = P.moves(P.play(pb, ["section", "s/ph/bt", "Delivery"], "landed\n"))
            clean_b = P.play(pb, ["check"])
        c.ok((shared / "plans" / "s" / "1-ph" / "1-bt" / "BATCH.md").is_file(), "the batch under the root")
        c.ok(moved.get("s/ph/bt") is not None and moved["s/ph/bt"].status == "done"
             and set(moved["s/ph/bt"].closes) == {"s/ph", "s"}, f"moves={moved}")
        with P.under(key_a):
            seen = P.play(pa, ["status", "s"])
            clean_a = P.play(pa, ["check"])
        c.ok("done" in seen.splitlines()[0] and "shared" in seen.splitlines()[0], f"status from A: {seen!r}")
        c.ok("clean" in clean_a and "clean" in clean_b, "check clean on both sides")

    # --- (h) two processes write at once -----------------------------------------------------
    with case("(h) two writers at once", "two processes of the script, one per run, write Protocol and "
              "Arbitrations of the same shared plan: both sections land, check clean") as c:
        with P.under(key_a):
            P.play(pa, ["section", "s2", "Context", "--shared"], "two writers\n")
            P.play(pa, ["section", "s2", "Target"], TARGET + "\n")
            P.play(pa, ["section", "s2", "Expected"], EXPECTED + "\n")
        import os
        clean_env = {one: value for one, value in os.environ.items() if one != "PP_RUN"}
        runs = [(a, key_a, "Protocol"), (b, key_b, "Arbitrations")]
        started = [subprocess.Popen([sys.executable, str(P.script_path(env.made)), "section", "s2", name],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, cwd=env.root, env={**clean_env, "PP_RUN": key})
                   for env, key, name in runs]
        # the lock is taken before the prose is read: each process is fed and waited for by its own
        # thread, so the one that holds the lock is never starved of its prose by the other
        import threading
        answers: list = [None, None]

        def feed(at: int) -> None:
            answers[at] = started[at].communicate(input=f"{runs[at][2]} written by {runs[at][1]}\n", timeout=60)

        feeders = [threading.Thread(target=feed, args=(at,)) for at in range(2)]
        for one in feeders:
            one.start()
        for one in feeders:
            one.join()
        codes = [one.returncode for one in started]
        body = (shared / "plans" / "s2" / "PLAN.md").read_text(encoding="utf-8")
        c.ok(codes == [0, 0], f"rc={codes} {[one[1][-200:] for one in answers]}")
        c.ok("## Protocol" in body and "## Arbitrations" in body, "both sections landed")
        with P.under(key_a):
            c.ok("clean" in P.play(pa, ["check"]), "check clean")

    # --- (i) the next move of a shared plan, read from its document ---------------------------
    with case("(i) next-move says what the other run did", "A births s3, B frames its phase: next-move "
              "from A names the batch to frame, status --json from A says shared and the same next; "
              "the plan counted once; born_plans covers both trees") as c:
        with P.under(key_a):
            P.play(pa, ["section", "s3", "Context", "--shared"], "the third\n")
        with P.under(key_b):
            w = P.Writer(pb)
            w.grow(shared, ["s3", "ph"], "the phase")        # s3 framed, ph prepared then born
            w.section(shared, ["s3", "ph"], "Target", TARGET)
            w.section(shared, ["s3", "ph"], "Expected", EXPECTED)
            w.section(shared, ["s3", "ph"], "Items", "- bt -- the batch")
        with P.under(key_a):
            lines = P.play(pa, ["next-move"]).splitlines()
            listed = json.loads(P.play(pa, ["status", "--json"]))
            born = pa.born_plans(a.made)
        said = [one for one in lines if one.endswith("(plan-lot:s3/ph/bt)")]
        rows = [one for one in listed if one["address"] == "s3"]
        c.ok(len(said) == 1 and P.move_of(said[0]) == ("batch", "framing", "plan-lot:s3/ph/bt"), f"lines={lines}")
        c.ok(len(rows) == 1 and rows[0]["shared"] is True and rows[0]["next"] == said[0], f"rows={rows}")
        c.ok({"s", "s2", "s3", "u"} <= born, f"born={born}")

    # --- (j) the launcher's material ---------------------------------------------------------
    with case("(j) material work", "`material s3 work` writes the key on the plan and its born phase; "
              "an undeclared name refuses") as c:
        with P.under(key_b):
            answered = P.material_said(P.play(pb, ["material", "s3", "work"]))
        fronts = [P.front(pb, shared / "plans" / "s3" / "PLAN.md"),
                  P.front(pb, shared / "plans" / "s3" / "1-ph" / "PHASE.md")]
        c.ok(answered is not None and answered[0] == "work" and answered[2] == 2, f"answered={answered}")
        c.ok(all(one.get("material") == "work" for one in fronts), "the key on both documents")
    with P.under(key_b):
        refuse("material-undeclared", lambda: pb.main(["material", "s3", "absent"]))
    return 0
