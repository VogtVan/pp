"""packages/plan/skills/pp-plan -- a plan SHARED by the runs opened under one root of
documents, on two real environments carrying the plan package, each run opened by the
console under the same root (`PP_DOCUMENTS` at `-new`) and the vendored script played
under `PP_RUN`: (a) `section <slug> Context --shared` births the plan under
`<root>/plans/`, its lock beside it, nothing in the instance; (b) `documents-none` with no
run and under a run opened with no root, nothing written; (c) `--shared` on another section
or a deeper address refuses; (d) `slug-taken` across the trees, both ways; (e) a plan of the
same name in the instance and under the root refuses `plan-twice` at every verb that resolves
its slug (`mount`, `section`, `status <slug>`, `done`, `move`, `block`, `rename`, `constrain`,
`serve`, `material`), the message naming both paths, nothing written; `status` without a slug,
`next-move` and `check` say the double as a `plan-twice` finding, neither tree's line served; (f) the other instance
mounts the shared plan through the console; (g) the other instance frames, checks off and
delivers it -- the cascade closes it, `check` clean from both; (h) two processes write two
sections at once, both land; (i) `next-move` and `status --json` from the first instance say
the node the second advanced, `shared` on the nodes, the plan counted once; (j) `material
<slug> work`, `repo` and any other name the plan does not declare refuse `material-undeclared`; (k) a tree the shared plan declares by a
RELATIVE path (`material s3 tree ../../src`, no `material.*` key at either SETTINGS) is read from the
plan's folder: a row mounted from both instances reads the same file, titled `@tree`, the same
rendering on both sides."""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.harness import cli, support

P = support(__file__, "plan")
GROUND, EXPECTED, TESTS, CHOICES = P.GROUND, P.EXPECTED, P.TESTS, P.CHOICES
BODY = "shared-plan-body-7"           # one token: what the mount must show, never a sentence


def _frame_all(plans, tree: Path, slug: str) -> None:
    """A plan framed down to one todo: a phase and a batch born, the batch's todo prepared."""
    w = P.Writer(plans)
    w.section(tree, [slug], "Expected", EXPECTED)
    w.section(tree, [slug], "Choices", CHOICES)
    w.section(tree, [slug], "Items", "- ph -- the phase")
    w.section(tree, [slug, "ph"], "Ground", GROUND)
    w.section(tree, [slug, "ph"], "Expected", EXPECTED)
    w.section(tree, [slug, "ph"], "Choices", CHOICES)
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
        refuse("argument-unexpected", lambda: pa.main(["section", "s", "Expected", "--shared"]))
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

    # --- (e) a plan in both trees: refused by name, nothing written ----------------------------
    shutil.copytree(shared / "plans" / "s", b.made / "plans" / "s")
    copy, root_doc = b.made / "plans" / "s" / "PLAN.md", shared / "plans" / "s" / "PLAN.md"

    def printed() -> dict:
        return {str(one): one.read_bytes() for tree in (b.made / "plans", shared / "plans")
                for one in sorted(tree.rglob("*")) if one.is_file()}

    before = printed()
    said: list[str] = []
    with P.under(key_b):
        said.append(refuse("plan-twice", lambda: pb.main(["mount", "s"])))
        with P.fed("twice\n"):
            said.append(refuse("plan-twice", lambda: pb.main(["section", "s", "Ground"])))
        said.append(refuse("plan-twice", lambda: pb.main(["status", "s"])))
        said.append(refuse("plan-twice", lambda: pb.main(["done", "s"])))
        for argv, fed in ((["move", "s/ph", "s", "1"], ""), (["block", "s", "a", "reason"], ""),
                          (["rename", "s", "s9"], ""), (["constrain", "s", "--section", "production"], "a law\n"),
                          (["serve", "s", "README.md"], ""), (["material", "s", "tree"], "")):
            with P.fed(fed):
                said.append(refuse("plan-twice", lambda: pb.main(argv)))
        heard = io.StringIO()
        with contextlib.redirect_stderr(heard):
            checked_rc = pb.main(["check"])            # check says its findings and returns 2, no raise
        checked = heard.getvalue()
    with case("(e) a plan in both trees is refused", "mount, section, status s, done, move, block, rename, "
              "constrain, serve, material refuse plan-twice naming both paths, nothing written; status says "
              "the double, check reddens with plan-twice") as c:
        c.ok(len(said) == 10, f"{len(said)} refusals said")
        c.ok(all(str(copy.parent) in one and str(root_doc.parent) in one for one in said), f"said={said}")
        c.ok(printed() == before, "nothing written in either tree")
        c.ok(checked_rc == 2 and "s: plan-twice" in checked and str(copy.parent) in checked
             and str(root_doc.parent) in checked, f"check rc={checked_rc} {checked!r}")
        with P.under(key_b):
            listed = json.loads(P.play(pb, ["status", "--json"]))
            text = P.play(pb, ["status"])
        rows = [one for one in listed if one["address"] == "s"]
        c.ok(len(rows) == 1 and rows[0]["status"] == "plan-twice"
             and rows[0].get("twice") == [str(copy.parent), str(root_doc.parent)], f"rows={rows}")
        lines = [one for one in text.splitlines() if one.startswith("s ")]
        c.ok(len(lines) == 1 and "plan-twice" in lines[0], f"text={text!r}")
    with case("(e) next-move says the double", "next-move from B: one plan-twice line naming both "
              "directories, no next move of either s served") as c:
        with P.under(key_b):
            moves = P.play(pb, ["next-move"]).splitlines()
        doubled = [one for one in moves if "plan-twice" in one]
        c.ok(len(doubled) == 1 and str(copy.parent) in doubled[0] and str(root_doc.parent) in doubled[0]
             and not any(one.endswith("(plan:s)") for one in moves), f"moves={moves}")
    shutil.rmtree(b.made / "plans" / "s")

    # --- (f) the other instance mounts it through the console ---------------------------------
    with case("(f) the other run mounts the shared plan", "`-s pp-plan mount s` from B's run: the "
              "engine resolves plans/s/PLAN.md at the root of documents, the body served") as c:
        P.stepped_on(b, key_b)                          # past the boot's own step: the turn offers pp-plan
        shown = cli(b.engine, key_b, "-s", "pp-plan", "mount", "s", cwd=b.root)
        c.ok(shown.returncode == 0, f"rc={shown.returncode} {shown.stderr[-300:]!r} {shown.stdout[-400:]!r}")
        c.ok(BODY in shown.stdout, "the Context of the shared plan in the output")

    # --- (g) framed, checked off and delivered from the other instance -----------------------
    with case("(g) delivered from the other instance", "B frames s down to a todo and delivers it by "
              "its Delivery entry: batch, phase and plan close by the cascade; check clean from A and B") as c:
        with P.under(key_b):
            _frame_all(pb, shared, "s")
            moved = P.moves(P.play(pb, ["section", "s/ph/bt", "Delivery", "--item", "t1"], "landed\n"))
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
    with case("(h) two writers at once", "two processes of the script, one per run, write Ground and "
              "Choices of the same shared plan: both sections land, check clean") as c:
        with P.under(key_a):
            P.play(pa, ["section", "s2", "Context", "--shared"], "two writers\n")
            P.play(pa, ["section", "s2", "Expected"], EXPECTED + "\n")
        import os
        clean_env = {one: value for one, value in os.environ.items() if one != "PP_RUN"}
        runs = [(a, key_a, "Ground"), (b, key_b, "Choices")]
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
        c.ok("## Ground" in body and "## Choices" in body, "both sections landed")
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
            w.section(shared, ["s3", "ph"], "Expected", EXPECTED)
            w.section(shared, ["s3", "ph"], "Choices", CHOICES)
            w.section(shared, ["s3", "ph"], "Items", "- bt -- the batch")
        with P.under(key_a):
            lines = P.play(pa, ["next-move"]).splitlines()
            listed = json.loads(P.play(pa, ["status", "--json"]))
            born = pa.born_plans(a.made)
        said = [one for one in lines if one.endswith("(plan:s3/ph/bt)")]
        rows = [one for one in listed if one["address"] == "s3"]
        c.ok(len(said) == 1 and P.move_of(said[0]) == ("batch", "framing", "plan:s3/ph/bt"), f"lines={lines}")
        c.ok(len(rows) == 1 and rows[0]["shared"] is True and rows[0]["next"] == said[0], f"rows={rows}")
        c.ok({"s", "s2", "s3", "u"} <= born, f"born={born}")

    # --- (j) a shared plan names a tree it declares, never `work` nor `repo` -------------------
    with case("(j) a name the plan does not declare refuses", "`material s3 work`, `material s3 repo` and an "
              "absent name refuse material-undeclared: no tree is called so; no key written") as c:
        fronts = lambda: [P.front(pb, shared / "plans" / "s3" / "PLAN.md"),             # noqa: E731
                          P.front(pb, shared / "plans" / "s3" / "1-ph" / "PHASE.md")]
        with P.under(key_b):
            for name in ("work", "repo", "absent"):
                refuse("material-undeclared", lambda: pb.main(["material", "s3", name]))
        c.ok(all("material" not in one for one in fronts()), "no key on either document")

    # --- (k) a tree the shared plan declares, read alike from both instances ------------------
    with case("(k) the shared plan's tree, read alike", "A declares `material s3 tree ../../src` and serves "
              "`lib/x.py` on s3/ph; no SETTINGS names a material; the console mounts s3/ph from A's run and "
              "from B's: the row read from <root>/src under `lib/x.py @tree`, the same lines on both") as c:
        (shared / "src" / "lib").mkdir(parents=True)
        (shared / "src" / "lib" / "x.py").write_text("TREE = 'shared-tree-token-9'\n", encoding="utf-8")
        with P.under(key_a):
            said = P.material_said(P.play(pa, ["material", "s3", "tree", "../../src"]))
            P.play(pa, ["serve", "s3/ph", "lib/x.py"])
        c.ok(said is not None and said[0] == "tree", f"said={said}")
        c.ok(not any("material." in (env.made / "SETTINGS.md").read_text(encoding="utf-8") for env in (a, b)),
             "a material key at a SETTINGS")
        fresh = [(env, P.opened(env, shared)) for env in (a, b)]     # one new run each: a view with no mount yet
        for env, key in fresh:
            P.stepped_on(env, key)                       # past the boot's own step: the turn offers pp-plan
        shown = [cli(env.engine, key, "-s", "pp-plan", "mount", "s3/ph", cwd=env.root) for env, key in fresh]
        rendered = [[line for line in one.stdout.splitlines() if "lib/x.py" in line or "shared-tree-token-9" in line]
                    for one in shown]
        c.ok(all(one.returncode == 0 for one in shown), f"rc={[one.returncode for one in shown]} "
             f"{[one.stderr[-200:] for one in shown]}")
        c.ok(all(any("lib/x.py @tree" in line for line in one) and any("shared-tree-token-9" in line for line in one)
                 for one in rendered), f"rendered={rendered} {shown[0].stdout[-600:]!r}")
        c.ok(rendered[0] == rendered[1], f"A={rendered[0]} B={rendered[1]}")
    return 0
