"""packages/plan/skills/pp-plan -- the MOUNT of a plan's chain and the MATERIAL of its tree, on
real environments carrying the plan package: the chain grows by level, the node at work
whole and its ancestors by a selection of their sections, `--whole` handing every body
back; a chain mounted through the engine shows what the level needs and finds its methods
by name in the bundle; the node mounted replaces the other born nodes of its plan, so a
batch mounted after its sibling leaves the sibling's laws out of the view; the refusals of a chain that cannot be. The material: the verb
writes it on every born node, the birth copies it, the key is the model's, `serve` reminds
it, the mount serves the plan's tree from it, `check` sees a catalogue that moved."""
from __future__ import annotations

import json
import re
import shutil

from conductor import instance
from conductor.core import document
from tests.harness import load_script, support

P = support(__file__, "plan")
GROUND, TARGET, EXPECTED, TESTS = P.GROUND, P.TARGET, P.EXPECTED, P.TESTS

FLOOR = "---\nname: FLOOR\nkind: proc\ndescription: a floor\nproc: |\n  INFER\n---\n\nthe floor\n"


def _mounted(made) -> list[dict]:
    """-> the ledger lines the mounts of the instance wrote for its OWN plan documents."""
    return [line for log in sorted((made / ".sys" / "state").glob("session-*.jsonl"))
            for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
            if one.get("kind") == "block" for line in (one.get("served") or [])
            if line.get("origin") == "mount" and line.get("package") == "instance"]


def scenario(bench) -> int:
    refuse = bench.expect_exit
    env = P.house(bench, "plan-mount", pin=True)
    root = env.made
    vendor = P.vendor(root)
    plans = P.script(root)

    def case(label, detail=""):
        return P.case(bench, label, detail)

    # --- the chain grows by level, plans/ untouched ------------------------------------------
    plans.write_section(root, ["job"], "Context", "A plan to mount.")
    plans.write_section(root, ["job"], "Target", TARGET)
    plans.write_section(root, ["job"], "Expected", EXPECTED)
    plans.write_section(root, ["job"], "Items", "- ph -- A phase\n- ph2 -- A prepared phase")
    plans.write_section(root, ["job", "ph"], "Ground", GROUND)
    plans.write_section(root, ["job", "ph"], "Target", TARGET)
    plans.write_section(root, ["job", "ph"], "Expected", EXPECTED)
    plans.write_section(root, ["job", "ph"], "Items", "- bt -- A batch\n- bt2 -- A prepared batch")
    plans.write_section(root, ["job", "ph", "bt"], "Ground", GROUND)
    six = []
    with case("the mount chain grows by level", "2 for a plan, 4 for a phase, 6 for a batch -- method nested, "
              "node stacked, both with their body; a PREPARED item, or one to come under a born parent, "
              "mounts its method ahead (3, 5); plans/ intact") as c:
        before = {p: p.read_bytes() for p in (root / "plans").rglob("*.md")}
        two = plans.mount_chain(root, ["job"])
        four = plans.mount_chain(root, ["job", "ph"])
        six = plans.mount_chain(root, ["job", "ph", "bt"])
        three = plans.mount_chain(root, ["job", "ph2"])
        five = plans.mount_chain(root, ["job", "ph", "bt2"])
        ahead = plans.mount_chain(root, ["job", "ph", "not-yet"])      # not even prepared
        after = {p: p.read_bytes() for p in (root / "plans").rglob("*.md")}
        c.ok([len(two), len(four), len(six), len(three), len(five), len(ahead)] == [2, 4, 6, 3, 5, 5], "the lengths")
        c.ok(two[0]["scope"] == "nested" and two[0]["body"] is True, "the method")
        c.ok(two[1]["scope"] == "stacked" and two[1]["body"] is True, "the node")
        c.ok([one["doc"] for one in six[0::2]] == ["PLAN.md", "PHASE.md", "BATCH.md"]
             and six[5]["doc"].startswith("plans/"), "the batch's chain")
        c.ok(three[2]["doc"].endswith("PHASE.md") and three[2]["scope"] == "nested", "the prepared phase")
        c.ok(five[4]["doc"].endswith("BATCH.md") and five[4]["scope"] == "nested", "the prepared batch")
        c.ok(all((root / one["doc"]).is_file() if one["doc"].startswith("plans/")
                 else (vendor / "procs" / one["doc"]).is_file() for one in six), "a document missing")
        c.ok(before == after, "plans/ moved")

    # --- the node at work mounts WHOLE, its ancestors by a selection of their sections -------
    def bodies(chain):
        return [one["body"] for one in chain if one["doc"].startswith("plans/")]

    with case("the node at work mounts whole, its ancestors by selection",
              "a plan, a phase, a batch, a prepared and a to-come batch: the last document whole, each "
              "ancestor from Target to Items; a section missing says nothing, an older heading stays "
              "with its section; `--whole` hands the former chain back") as c:
        plans.write_section(root, ["job"], "Arbitrations", "None.")
        plans.write_section(root, ["job", "ph"], "Arbitrations", "None.")
        plan_shown, phase_shown = ["## Target..## Arbitrations"], ["## Target..## Items"]
        c.ok(bodies(plans.mount_chain(root, ["job"])) == [True], "the plan")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph"])) == [plan_shown, True], "the phase")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph", "bt"])) == [plan_shown, phase_shown, True], "the batch")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph", "bt2"])) == [plan_shown, True], "prepared")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph", "not-yet"])) == [plan_shown, True], "to come")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph2"])) == [True], "a prepared phase")
        # a section the ancestor lacks says nothing: the couples follow what stands
        c.ok(plans.shown("phase", "# T\n\n## Context\nc\n## Target\nt\n## Items\n- a -- b\n") == ["## Target..## Items"],
             "a phase without Expected")
        c.ok(plans.shown("plan", "## Context\nc\n## Target\nt\n## Protocol\np\n## Expected\ne\n")
             == ["## Target..## Protocol", "## Expected.."], "a plan without Items")
        c.ok(plans.shown("plan", "## Context\nc\n") == [], "a plan without Target")
        # a heading that is no section of the kind stays with the section it details
        legacy = root / "plans" / "job" / "PLAN.md"
        legacy.write_text(legacy.read_text(encoding="utf-8").replace(
            "## Expected", "## An older heading\n\nkept with the target\n\n## Expected"), encoding="utf-8")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph"])) == [plan_shown, True], "an older heading")
        # --whole hands the former chain back, every body whole
        whole = plans.mount_chain(root, ["job", "ph", "bt"], whole=True)
        former = [{**one, "body": True} for one in six]
        c.ok(bodies(whole) == [True, True, True] and whole == former, "--whole")
        said = P.play(plans, ["mount", "job/ph/bt", "--whole"])
        c.ok(json.loads(said.splitlines()[0].removeprefix("::mount ")) == former, "the console's chain")
        refuse("argument-unexpected", lambda: plans.main(["mount", "job/ph/bt", "--all"]))

    with case("the mount refusals hold", "a child of a prepared item and an unborn plan refuse; "
              "a script with no procs/ beside it says it"):
        refuse("path-unknown", lambda: plans.mount_chain(root, ["job", "ph2", "x"]))
        refuse("path-unknown", lambda: plans.mount_chain(root, ["unborn"]))
        # a copy of the script with no procs/ beside it: the method it would name is nowhere
        lone = bench.temp() / "lone" / "skills" / "pp-plan"
        lone.mkdir(parents=True)
        shutil.copy(P.script_path(root), lone / "pp-plan.py")
        shutil.copy(vendor / "skills" / "_core.py", lone.parent / "_core.py")
        outside = load_script(lone / "pp-plan.py")
        refuse("method-missing", lambda: outside.mount_chain(root, ["job"]))

    # --- a chain MOUNTED through the engine: the batch whole, its ancestors by selection -----
    settings = root / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace(
        "proc_body_serve: always", "proc_body_serve: once"), encoding="utf-8")
    env.write("FLOOR.md", FLOOR)
    thesis, plan_target, phase_ground = ("the thesis nobody below needs again", "the plan's target",
                                         "the phase's ground, measured")
    batch_ground, phase_expected = "the batch's ground", "the phase's expected"
    for address, name, prose in ((["seen"], "Context", thesis),
                                 (["seen"], "Target", plan_target),
                                 (["seen"], "Expected", "the plan's expected"),
                                 (["seen"], "Items", "- ph -- a phase"),
                                 (["seen", "ph"], "Ground", phase_ground),
                                 (["seen", "ph"], "Target", "the phase's target"),
                                 (["seen", "ph"], "Expected", phase_expected),
                                 (["seen", "ph"], "Items", "- bt -- a batch"),
                                 (["seen", "ph", "bt"], "Ground", batch_ground)):
        plans.write_section(root, address, name, prose)
    own = plans.sections().constrain(root, root / "plans" / "seen" / "PLAN.md", "KJ", "production",
                                     ["the plan's own law"])

    def opened(key: str):
        runner = env.conductor(key)
        runner.forget()
        runner.start(root / "FLOOR.md")
        return lambda: env.conductor(key)

    by_selection, entire = opened("sel"), opened("all")
    chain = plans.mount_chain(root, ["seen", "ph", "bt"])
    said = by_selection().mount(chain)
    codes = sorted(one.code for one in by_selection()._mount_laws())
    light = sum(line.get("chars", 0) for line in _mounted(root) if line["state"] == "served")
    again = by_selection().mount([{**one, "constraints": False} for one in chain])
    spared = [line["subject"] for line in _mounted(root) if line["state"] == "spared"]
    entire().mount(plans.mount_chain(root, ["seen", "ph", "bt"], whole=True))
    heavy = sum(line.get("chars", 0) for line in _mounted(root) if line["state"] == "served") - light
    if (batch_ground in said and plan_target in said and phase_expected in said
            and thesis not in said and phase_ground not in said
            and "INFORMATION — PLAN[## Target.." in said and "INFORMATION — PHASE[## Target.." in said
            and codes == sorted(one.code for one in entire()._mount_laws()) and own and set(own) <= set(codes)
            and any(one.startswith("PLAN[## Target") for one in spared) and plan_target not in again
            and 0 < light < heavy):
        bench.held("a mounted chain shows what the level needs", f"the batch whole, the plan and the phase "
                   f"from their Target on, each part under its token and spared at a second mount; the same "
                   f"laws in force either way; {light} c by selection, {heavy} c whole")
    else:
        bench.failures.append(f"  ✗ mounted chain               codes={codes} spared={spared} "
                              f"light={light} heavy={heavy} {said[-300:]!r}")

    # --- by NAME: the chain names its methods, the engine finds them in the bundle --------
    by_name = "the batch's ground by name"
    for address, name, prose in ((["named"], "Context", "a plan mounted by name"),
                                 (["named"], "Target", "the plan's target"),
                                 (["named"], "Expected", "the plan's expected"),
                                 (["named"], "Items", "- ph -- a phase"),
                                 (["named", "ph"], "Ground", "the phase's ground by name"),
                                 (["named", "ph"], "Target", "the phase's target"),
                                 (["named", "ph"], "Expected", "the phase's expected"),
                                 (["named", "ph"], "Items", "- bt -- a batch"),
                                 (["named", "ph", "bt"], "Ground", by_name)):
        plans.write_section(root, address, name, prose)
    in_bundle = load_script(instance.bundle_of(root, "plan") / "skills" / "pp-plan" / "pp-plan.py")
    named_chain = in_bundle.mount_chain(root, ["named", "ph", "bt"])
    runner = env.conductor("pnamed")
    runner.forget()
    runner.start(root / "FLOOR.md")
    mounted = env.conductor("pnamed").mount(named_chain)
    methods = [one["doc"] for one in named_chain if not one["doc"].startswith("plans/")]
    if methods == ["PLAN.md", "PHASE.md", "BATCH.md"] and by_name in mounted and "▸ BATCH" in mounted:
        bench.held("a plan mounts its methods by name", "the chain names PLAN.md, PHASE.md, BATCH.md; "
                   "the engine finds the methods in the bundle")
    else:
        bench.failures.append(f"  ✗ plan methods by name        methods={methods} {mounted[-300:]!r}")

    # --- the node REPLACES the other born nodes of its plan: a sibling's laws leave the view ----
    for address, name, prose in ((["pair"], "Context", "a plan whose batches are mounted in turn"),
                                 (["pair"], "Target", "the plan's target"),
                                 (["pair"], "Expected", "the plan's expected"),
                                 (["pair"], "Items", "- p -- a phase\n- p2 -- another phase"),
                                 (["pair", "p"], "Ground", "the phase's ground"),
                                 (["pair", "p"], "Target", "the phase's target"),
                                 (["pair", "p"], "Expected", "the phase's expected"),
                                 (["pair", "p"], "Items", "- b1 -- a batch\n- b2 -- its sibling"),
                                 (["pair", "p", "b1"], "Ground", "the first batch"),
                                 (["pair", "p", "b2"], "Ground", "the sibling"),
                                 (["pair", "p2"], "Ground", "the other phase"),
                                 (["pair", "p2"], "Target", "the other phase's target"),
                                 (["pair", "p2"], "Expected", "the other phase's expected"),
                                 (["pair", "p2"], "Items", "- b -- its batch"),
                                 (["pair", "p2", "b"], "Ground", "the other phase's batch")):
        plans.write_section(root, address, name, prose)
    pair = root / "plans" / "pair"
    first = plans.sections().constrain(root, pair / "1-p" / "1-b1" / "BATCH.md", "KB", "production",
                                       ["the first batch's law"])
    sibling = plans.sections().constrain(root, pair / "1-p" / "2-b2" / "BATCH.md", "KS", "production",
                                         ["the sibling's law"])
    node = {one: str(path.relative_to(root)) for one, path in (
        ("p", pair / "1-p" / "PHASE.md"), ("b1", pair / "1-p" / "1-b1" / "BATCH.md"),
        ("b2", pair / "1-p" / "2-b2" / "BATCH.md"), ("p2", pair / "2-p2" / "PHASE.md"),
        ("b", pair / "2-p2" / "1-b" / "BATCH.md"))}
    with case("the node mounted replaces the other born nodes of its plan", "the last entry of a chain "
              "names every born node of the plan outside the chain; through the engine, b2 after b1 leaves "
              "b1 and its law out, p2/b after p/b2 leaves p and b2 out, the methods and the plan kept") as c:
        chain = plans.mount_chain(root, ["pair", "p", "b2"])
        c.ok(chain[-1].get("replaces") == [node["b1"], node["p2"], node["b"]]
             and all("replaces" not in one for one in chain[:-1]), f"the chain's replaces {chain[-1]}")
        runner = env.conductor("ppair")
        runner.forget()
        runner.start(root / "FLOOR.md")
        env.conductor("ppair").mount(plans.mount_chain(root, ["pair", "p", "b1"]))
        env.conductor("ppair").mount(chain)
        slot = [one["doc"] for one in env.conductor("ppair")._mounted()]
        laws = {one.code for one in env.conductor("ppair")._mount_laws()}
        c.ok(slot == ["PLAN.md", "plans/pair/PLAN.md", "PHASE.md", node["p"], "BATCH.md", node["b2"]],
             f"b2 after b1 {slot}")
        c.ok(set(sibling) <= laws and not set(first) & laws, f"the laws {sorted(laws)}")
        env.conductor("ppair").mount(plans.mount_chain(root, ["pair", "p2", "b"]))
        slot = [one["doc"] for one in env.conductor("ppair")._mounted()]
        c.ok(slot == ["PLAN.md", "plans/pair/PLAN.md", "PHASE.md", "BATCH.md", node["p2"], node["b"]],
             f"p2/b after p/b2 {slot}")

    # --- the MATERIAL of a plan: written on every born node, served from its tree ------------
    menv = P.house(bench, "plan-material")
    mroot = menv.made
    mplans = P.script(mroot)
    mplans.home = lambda: mroot
    tuned = (mroot / "SETTINGS.md").read_text(encoding="utf-8").replace(
        "max_harness_tool_output: 25000", "max_harness_tool_output: 200000")   # a mount read whole, uncut

    def declare(*names):
        """The operator's catalogue at SETTINGS: `material.<name>: alt` for each name given."""
        head, tail = tuned.split("\n---\n", 1)
        (mroot / "SETTINGS.md").write_text(
            head + "\n" + "".join(f"material.{one}: alt\n" for one in names) + "---\n" + tail, encoding="utf-8")

    def mplay(argv, stdin=""):
        out = P.play(mplans, argv, stdin)
        return out

    for relative, text in (("engine/x.py", "FROM = 'the repository'\n"), ("alt/engine/x.py", "FROM = 'alt'\n")):
        (menv.root / relative).parent.mkdir(parents=True, exist_ok=True)
        (menv.root / relative).write_text(text, encoding="utf-8")
    declare("core")
    for name, prose in (("Context", "A plan whose code lives in a worktree."), ("Target", TARGET),
                        ("Expected", EXPECTED), ("Items", "- ph -- A phase\n- ph2 -- A prepared phase")):
        mplans.write_section(mroot, ["job"], name, prose)
    for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED),
                        ("Items", "- bt -- A batch\n- bt2 -- A prepared batch")):
        mplans.write_section(mroot, ["job", "ph"], name, prose)
    for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED), ("Tests", TESTS)):
        mplans.write_section(mroot, ["job", "ph", "bt"], name, prose)
    job = mroot / "plans" / "job"
    mdocs = [job / "PLAN.md", job / "1-ph" / "PHASE.md", job / "1-ph" / "1-bt" / "BATCH.md"]
    bare = [one.read_bytes() for one in mdocs]                 # no material anywhere yet
    keyed = re.compile(r"^created: .*\nmaterial: (\S+)\n", re.M)

    def carried(docs=mdocs):
        return [(hit.group(1) if (hit := keyed.search(one.read_text(encoding="utf-8"))) else None)
                for one in docs]

    with case("(a) the verb writes the material everywhere", "`material job core`: `material: core` after "
              "`created` on the plan, its born phase and its born batch; the prepared batch has no document; "
              "the answer names the three") as c:
        said = P.material_said(mplay(["material", "job", "core"]))
        c.ok(carried() == ["core", "core", "core"], f"carried {carried()}")
        c.ok(said is not None and said[:3] == ("core", "job", 3)
             and any(one.endswith("1-ph/1-bt/BATCH.md") for one in said[3]), f"said {said}")
        c.ok(not (job / "1-ph" / "2-bt2").exists(), "the prepared batch born")

    born = [job / "1-ph" / "2-bt2" / "BATCH.md", job / "2-ph2" / "PHASE.md"]
    with case("(b) the birth copies the plan's material", "a batch and a phase born after the verb carry "
              "`material: core` after `created`") as c:
        mplans.write_section(mroot, ["job", "ph", "bt2"], "Ground", GROUND)
        mplans.write_section(mroot, ["job", "ph2"], "Ground", GROUND)
        c.ok(carried(born) == ["core", "core"], f"carried {carried(born)}")

    with case("(c) the slug by default, `-` takes the key out", "`material job` writes the slug once declared; "
              "`material job -` removes the key from the five documents -- the three written before the verb "
              "byte for byte as they were") as c:
        declare("core", "job")
        said = P.material_said(mplay(["material", "job"]))
        c.ok(carried() == ["job", "job", "job"] and said is not None and said[0] == "job", f"said {said}")
        said = P.material_said(mplay(["material", "job", "-"]))
        c.ok(carried() == [None, None, None] and said is not None and said[:3] == (None, "job", 5), f"said {said}")
        c.ok([one.read_bytes() for one in mdocs] == bare, "the bytes before the verb")
        c.ok(all("material" not in one.read_text(encoding="utf-8").split("\n---\n", 1)[0] for one in born),
             "the key on a born document")

    with case("(d) the refusal writes nothing, `repo` needs no declaration", "material-undeclared on a name "
              "the catalogue lacks (the line to write named) and on `work`; kind-mismatch on a phase address, "
              "path-unknown on an unborn plan, argument-unexpected -- every byte unchanged; `repo` passes") as c:
        declare("core")
        before = {one: one.read_bytes() for one in job.rglob("*.md")}
        out = refuse("material-undeclared", lambda: mplans.main(["material", "job", "nope"]))
        c.ok("material.nope: <path>" in out, f"the line to write {out}")
        refuse("material-undeclared", lambda: mplans.main(["material", "job", "work"]))
        refuse("kind-mismatch", lambda: mplans.main(["material", "job/ph", "core"]))
        refuse("path-unknown", lambda: mplans.main(["material", "ghost", "core"]))
        refuse("argument-unexpected", lambda: mplans.main(["material", "job", "core", "extra"]))
        c.ok({one: one.read_bytes() for one in job.rglob("*.md")} == before, "the bytes")
        said = P.material_said(mplay(["material", "job", "repo"]))
        c.ok(carried() == ["repo", "repo", "repo"] and said is not None and said[0] == "repo", f"said {said}")

    with case("(e) `material` is a key of the model", "read back by the script and by the engine's reader, "
              "emitted after `created`, the emit idempotent; check clean") as c:
        mplay(["material", "job", "core"])
        for one in mdocs + born:
            front, body = mplans.read(one)
            c.ok(front["material"] == "core" and mplans.emit(front, body) == one.read_text(encoding="utf-8"),
                 f"{one.name}: the script")
            c.ok(document.read(one).front["material"] == "core", f"{one.name}: the engine")
        c.ok(mplans.check(mroot) == [], "check")

    with case("(g) `serve` reminds the material", "an unmarked row on a node with a material: one line naming "
              "it and `@repo`; a marked row says nothing; by argv and by stdin, once per call") as c:
        said = mplay(["serve", "job/ph/bt", "engine/x.py"])
        c.ok("the rows read the material `core`" in said and "`@repo`" in said, f"said {said}")
        said = mplay(["serve", "job/ph2", "reference:", "@repo", "README.md"])
        c.ok("read the material" not in said, f"@repo said {said}")
        said = mplay(["serve", "job/ph2", "@core", "engine/x.py"])
        c.ok("read the material" not in said, f"@core said {said}")
        said = mplay(["serve", "job/ph2", "-"], stdin="engine/x.py\n@repo README.md\n")
        c.ok(said.count("read the material") == 1, f"stdin said {said}")

    def mounted_under_a_run():
        # a mount hosts documents in a RUN's view: one is opened at the console, the chain
        # mounted under its key -- a new run each time, one chain per turn
        opened = menv.cli("-new")
        key = re.search(r"run ([0-9a-f]{6})", opened.stdout).group(1)
        return menv.conductor(key).mount(mplans.mount_chain(mroot, ["job", "ph", "bt"]))

    with case("(f) the mount serves the plan's tree", "the batch's row `engine/x.py` is served from `alt`, "
              "titled `engine/x.py @core`; the key taken out, the same row serves the repository") as c:
        mounted = mounted_under_a_run()
        c.ok("engine/x.py @core" in mounted and "FROM = 'alt'" in mounted, mounted[-800:])
        c.ok("FROM = 'the repository'" not in mounted, mounted[-800:])
        mplay(["material", "job", "-"])
        again = mounted_under_a_run()
        c.ok("FROM = 'the repository'" in again and "@core" not in again, again[-800:])

    with case("(h) `check` sees a catalogue that moved", "the material gone from SETTINGS reddens the plan once "
              "(material-undeclared), repair says the gesture and touches nothing; declared again, check is clean") as c:
        mplay(["material", "job", "core"])
        declare()
        found = mplans.check(mroot)
        c.ok(len(found) == 1 and found[0].startswith("job: material `core`") and "material-undeclared" in found[0],
             f"findings {found}")
        mended, left = mplans.repair(mroot)
        c.ok(mended == [] and len(left) == 1 and "material <slug> -" in left[0], f"mended {mended} left {left}")
        declare("core")
        c.ok(mplans.check(mroot) == [], "check")

    return 0
