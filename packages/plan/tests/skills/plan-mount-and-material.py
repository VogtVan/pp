"""packages/plan/skills/pp-plan -- the MOUNT of a plan's chain and the MATERIAL of its tree, on
real environments carrying the plan package: the chain grows by level, the node at work
whole and its ancestors by a selection of their sections, `--whole` handing every body
back; a chain mounted through the engine shows what the level needs and finds its methods
by name in the bundle; the node mounted replaces the other born nodes of its plan, so a
batch mounted after its sibling leaves the sibling's laws out of the view; the refusals of a chain that cannot be. The material: the verb
declares its tree in the plan's own `materials:` block -- `material <slug> <name> <path>`, the path kept
as given, read from the plan's folder when relative, no SETTINGS read -- and writes the name on every born
node, the birth copies it, the key is the model's, `serve` reminds it, the mount serves the plan's tree
from the plan's declaration, `check` sees a name its chain does not declare, `serve` refuses a whole row
whose file, read in the declared tree, passes the budget (serve-heavy); `check` judges every `materials:`
block once, named or not; a rewrite keeps the block's `#` lines; `material <slug> - <name>` withdraws one
declaration from the PLAN.md alone; a node that still carries `repo` or `work` is told the one gesture
that takes it out, `material <slug> -`."""
from __future__ import annotations

import json
import os
import re
import shutil

from conductor.core import messages
from conductor import Refusal, instance
from conductor.core import document, language
from tests.harness import load_script, support, titled, titles

P = support(__file__, "plan")
GROUND, EXPECTED, TESTS, CHOICES = P.GROUND, P.EXPECTED, P.TESTS, P.CHOICES

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
    plans.write_section(root, ["job"], "Choices", CHOICES)
    plans.write_section(root, ["job"], "Expected", EXPECTED)
    plans.write_section(root, ["job"], "Items", "- ph -- A phase\n- ph2 -- A prepared phase")
    plans.write_section(root, ["job", "ph"], "Ground", GROUND)
    plans.write_section(root, ["job", "ph"], "Choices", CHOICES)
    plans.write_section(root, ["job", "ph"], "Expected", EXPECTED)
    plans.write_section(root, ["job", "ph"], "Items", "- bt -- A batch\n- bt2 -- A prepared batch")
    plans.write_section(root, ["job", "ph", "bt"], "Ground", GROUND)
    six = []
    with case("the mount chain grows by level", "the one method, then per level its template and its node, then "
              "the reading of the templates: 4 for a plan, 6 for a phase, 8 for a batch; the template's body at the "
              "node at work alone; a PREPARED item, or one to come under a born parent, mounts its template ahead "
              "(5, 7); plans/ intact") as c:
        before = {p: p.read_bytes() for p in (root / "plans").rglob("*.md")}
        three = plans.mount_chain(root, ["job"])
        five = plans.mount_chain(root, ["job", "ph"])
        seven = plans.mount_chain(root, ["job", "ph", "bt"])
        four = plans.mount_chain(root, ["job", "ph2"])
        six = plans.mount_chain(root, ["job", "ph", "bt2"])
        ahead = plans.mount_chain(root, ["job", "ph", "not-yet"])      # not even prepared
        after = {p: p.read_bytes() for p in (root / "plans").rglob("*.md")}
        c.ok([len(three), len(five), len(seven), len(four), len(six), len(ahead)] == [4, 6, 8, 5, 7, 7], "the lengths")
        c.ok(all(chain[-1] == {"doc": "PLANS-TEMPLATES.md", "body": True}
                 and [one["doc"] for one in chain].count("PLANS-TEMPLATES.md") == 1
                 for chain in (three, five, seven, four, six, ahead)), "the reading of the templates, last")
        c.ok(three[0] == {"doc": "PLAN.md", "body": True}, "the method")
        c.ok(three[1] == {"doc": "plan:templates/plan.md", "body": True} and three[2]["doc"].startswith("plans/")
             and three[2]["body"] is True, "the template and the node")
        c.ok(all(set(one) <= {"doc", "body", "replaces"}
                 for chain in (three, five, seven, four, six, ahead) for one in chain),
             "an entry names more than its document, its body and what it replaces")
        c.ok([one["doc"] for one in seven[1:7:2]] == ["plan:templates/plan.md", "plan:templates/phase.md",
                                                     "plan:templates/batch.md"]
             and [one["body"] for one in seven[1:7:2]] == [False, False, True], "the batch's chain")
        c.ok((four[3]["doc"], four[3]["body"]) == ("plan:templates/phase.md", True), "the prepared phase")
        c.ok((six[5]["doc"], six[5]["body"]) == ("plan:templates/batch.md", True), "the prepared batch")
        c.ok(all((root / one["doc"]).is_file() if one["doc"].startswith("plans/")
                 else (vendor / "templates" / one["doc"].split(":", 1)[1].split("/", 1)[1]).is_file()
                 if ":" in one["doc"] else (vendor / "procs" / one["doc"]).is_file() for one in seven),
             "a document missing")
        c.ok(before == after, "plans/ moved")

    # --- the node at work mounts WHOLE, its ancestors by a selection of their sections -------
    def bodies(chain):
        return [one["body"] for one in chain if one["doc"].startswith("plans/")]

    with case("the node at work mounts whole, its ancestors by selection",
              "a plan, a phase, a batch, a prepared and a to-come batch: the last document whole, each "
              "ancestor from Expected to Items; a section missing says nothing, an older heading stays "
              "with its section; `--whole` hands the former chain back") as c:
        plans.write_section(root, ["job"], "Ground", "The plan's ground.")
        plan_shown, phase_shown = ["## Expected..## Items"], ["## Expected..## Items"]
        c.ok(bodies(plans.mount_chain(root, ["job"])) == [True], "the plan")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph"])) == [plan_shown, True], "the phase")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph", "bt"])) == [plan_shown, phase_shown, True], "the batch")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph", "bt2"])) == [plan_shown, True], "prepared")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph", "not-yet"])) == [plan_shown, True], "to come")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph2"])) == [True], "a prepared phase")
        # a section the ancestor lacks says nothing: the couples follow what stands
        c.ok(plans.shown(plans.level(root, "phase"), "# T\n\n## Ground\ng\n## Choices\nc\n## Items\n- a -- b\n") == ["## Choices..## Items"],
             "a phase without Expected")
        c.ok(plans.shown(plans.level(root, "plan"), "## Context\nc\n## Expected\ne\n## Ground\ng\n## Choices\nc\n")
             == ["## Expected..## Ground", "## Choices.."], "a plan without Items, two runs")
        c.ok(plans.shown(plans.level(root, "plan"), "## Context\nc\n") == [], "a plan without Expected")
        # a heading that is no section of the kind stays with the section it details
        legacy = root / "plans" / "job" / "PLAN.md"
        legacy.write_text(legacy.read_text(encoding="utf-8").replace(
            "## Choices", "## An older heading\n\nkept with the expected\n\n## Choices"), encoding="utf-8")
        c.ok(bodies(plans.mount_chain(root, ["job", "ph"])) == [plan_shown, True], "an older heading")
        # --whole hands the former chain back, every body whole
        whole = plans.mount_chain(root, ["job", "ph", "bt"], whole=True)
        former = [{**one, "body": True} for one in seven]
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
                                 (["seen"], "Choices", plan_target),
                                 (["seen"], "Expected", "the plan's expected"),
                                 (["seen"], "Items", "- ph -- a phase"),
                                 (["seen", "ph"], "Ground", phase_ground),
                                 (["seen", "ph"], "Choices", "the phase's target"),
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
            and "INFORMATION — PLAN[## Expected.." in said and "INFORMATION — PHASE[## Expected.." in said
            and codes == sorted(one.code for one in entire()._mount_laws()) and own and set(own) <= set(codes)
            and any(one.startswith("PLAN[## Expected") for one in spared) and plan_target not in again
            and 0 < light < heavy):
        bench.held("a mounted chain shows what the level needs", f"the batch whole, the plan and the phase "
                   f"from their Expected on, each part under its token and spared at a second mount; the same "
                   f"laws in force either way; {light} c by selection, {heavy} c whole")
    else:
        bench.failures.append(f"  ✗ mounted chain               codes={codes} spared={spared} "
                              f"light={light} heavy={heavy} {said[-300:]!r}")

    # --- by NAME: the chain names its methods, the engine finds them in the bundle --------
    by_name = "the batch's ground by name"
    for address, name, prose in ((["named"], "Context", "a plan mounted by name"),
                                 (["named"], "Choices", "the plan's target"),
                                 (["named"], "Expected", "the plan's expected"),
                                 (["named"], "Items", "- ph -- a phase"),
                                 (["named", "ph"], "Ground", "the phase's ground by name"),
                                 (["named", "ph"], "Choices", "the phase's target"),
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
    shown = titles(mounted)
    mark = f"{messages.MARK} "
    headings = [one for one in shown if one.startswith(mark) and "{" in one     # a segment's heading points at a step
                and not language.section_of(one.removeprefix(mark))[0]]
    try:
        routed = env.conductor("pnamed").route("pp-plan")
    except Refusal as refusal:
        routed = refusal.code
    readings = [one for one in shown if one.startswith(titled(language.INFORMATION, ""))]
    if (methods == ["PLAN.md", "plan:templates/plan.md", "plan:templates/phase.md", "plan:templates/batch.md",
                    "PLANS-TEMPLATES.md"]
            and by_name in mounted and titled(language.INFORMATION, "PLAN") in shown
            and titled(language.INFORMATION, "plan-templates") in shown and '"chain": ["plan", "phase", "batch"]' in mounted
            and readings[:1] == [titled(language.INFORMATION, "PLAN")]
            and readings[-1:] == [titled(language.INFORMATION, "plan-templates")]
            and any("batch" in one for one in readings) and not any("phase" in one for one in readings)
            and len(headings) == 1 and titled(language.INSTRUCTION) in shown
            and isinstance(routed, dict) and "pp-plan" in routed.get("tools", [])):
        bench.held("a plan mounts its method by name and its templates from the bundle, in the segment of the step that stands",
                   "the chain names PLAN.md then plan:templates/<level>.md, PLANS-TEMPLATES.md last; the engine "
                   "finds them in the bundle, "
                   "the PLAN method read first, the reading plan-templates last, "
                   f"PLAN and the batch's template readings under `{headings[0]}`, the phase's template its laws "
                   "alone; `pp-plan`, which PLAN offers, routes without an address")
    else:
        bench.failures.append(f"  ✗ plan methods by name        methods={methods} readings={readings} headings={headings} "
                              f"routed={routed if isinstance(routed, str) else bool(routed)} {mounted[-300:]!r}")

    # --- PLAN played with no node mounted, the birth's own moment: the templates on screen -----------
    runner = env.conductor("pbare")
    runner.forget()
    runner.start(root / "FLOOR.md")
    bare = env.conductor("pbare").play("PLAN")
    subjects = [subject for subject, _ in bare.payloads] if bare is not None else []
    listed = dict(bare.payloads).get("plan-templates", "") if bare is not None else ""
    if (bare is not None and bare.document == "PLAN" and subjects[-1:] == ["PLAN"]
            and "plan-templates" in subjects and '"chain": ["plan", "phase", "batch"]' in listed):
        bench.held("PLAN played bare serves the templates", f"no node mounted, PLAN opened as a door: its block "
                   f"stands on PLAN's own step and carries {subjects} -- the reading plan-templates before the "
                   "method, the method last, closest to its step")
    else:
        bench.failures.append(f"  ✗ PLAN played bare             document={getattr(bare, 'document', None)} "
                              f"subjects={subjects}")

    # --- the node REPLACES the other born nodes of its plan: a sibling's laws leave the view ----
    for address, name, prose in ((["pair"], "Context", "a plan whose batches are mounted in turn"),
                                 (["pair"], "Choices", "the plan's target"),
                                 (["pair"], "Expected", "the plan's expected"),
                                 (["pair"], "Items", "- p -- a phase\n- p2 -- another phase"),
                                 (["pair", "p"], "Ground", "the phase's ground"),
                                 (["pair", "p"], "Choices", "the phase's target"),
                                 (["pair", "p"], "Expected", "the phase's expected"),
                                 (["pair", "p"], "Items", "- b1 -- a batch\n- b2 -- its sibling"),
                                 (["pair", "p", "b1"], "Ground", "the first batch"),
                                 (["pair", "p", "b2"], "Ground", "the sibling"),
                                 (["pair", "p2"], "Ground", "the other phase"),
                                 (["pair", "p2"], "Choices", "the other phase's target"),
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
    with case("the node mounted replaces the other born nodes of its plan", "the node's entry of a chain "
              "names every born node of the plan outside the chain; through the engine, b2 after b1 leaves "
              "b1 and its law out, p2/b after p/b2 leaves p and b2 out, the methods and the plan kept") as c:
        chain = plans.mount_chain(root, ["pair", "p", "b2"])
        c.ok(chain[-2].get("replaces") == [node["b1"], node["p2"], node["b"]]
             and all("replaces" not in one for one in chain[:-2] + chain[-1:]), f"the chain's replaces {chain[-2]}")
        runner = env.conductor("ppair")
        runner.forget()
        runner.start(root / "FLOOR.md")
        env.conductor("ppair").mount(plans.mount_chain(root, ["pair", "p", "b1"]))
        env.conductor("ppair").mount(chain)
        slot = [one["doc"] for one in env.conductor("ppair")._mounted() if one["doc"] != "PLANS-TEMPLATES.md"]
        laws = {one.code for one in env.conductor("ppair")._mount_laws()}
        c.ok(slot == ["PLAN.md", "plan:templates/plan.md", "plans/pair/PLAN.md", "plan:templates/phase.md", node["p"],
                     "plan:templates/batch.md", node["b2"]],
             f"b2 after b1 {slot}")
        c.ok(set(sibling) <= laws and not set(first) & laws, f"the laws {sorted(laws)}")
        env.conductor("ppair").mount(plans.mount_chain(root, ["pair", "p2", "b"]))
        slot = [one["doc"] for one in env.conductor("ppair")._mounted() if one["doc"] != "PLANS-TEMPLATES.md"]
        c.ok(slot == ["PLAN.md", "plan:templates/plan.md", "plans/pair/PLAN.md", "plan:templates/phase.md",
                     "plan:templates/batch.md", node["p2"], node["b"]],
             f"p2/b after p/b2 {slot}")

    with case("a tree's templates mount with their laws, at one and two levels", "`chore` (a leaf): PLAN, its "
              "template with its body, the plan whole, CH1 in force; `project` -> `task`: PLAN, the project's "
              "template for its law alone, the project by its `shown:`, the task's template with its body, the "
              "task whole, PJ1 and TK1 in force; the product's chain puts PH and BA laws in force") as c:
        place = root / "plans" / plans.TREE_TEMPLATES
        place.mkdir(parents=True, exist_ok=True)
        for name, chain, first, law in (("chore", "leaf: yes", "Framing", "CH1  an item is checked on sight."),
                                        ("task", "leaf: yes", "Framing", "TK1  a step is delivered with its command."),
                                        ("project", "next: task\nshown: |\n  Brief", "Brief",
                                         "PJ1  a task is cut so that one session delivers it.")):
            (place / f"{name}.md").write_text(
                f"---\nname: {name}\ndescription: a level of the bench\n{chain}\nsections: |\n  {first}\n"
                f"statuses: |\n  doing  {first}\n  redo  {first}\nconstraints.behavior: |\n  {law}\n---\n\n"
                f"# {name.upper()} `{{slug}}`\n\nthe method of the {name} level\n", encoding="utf-8")
        plans.write_section(root, ["menage"], "Framing", "Clean the room.", template="chore")
        plans.write_section(root, ["projet"], "Brief", "A notes API.", template="project")
        plans.write_section(root, ["projet"], "Items", "- api -- the HTTP API")
        plans.write_section(root, ["projet", "api"], "Framing", "GET /notes")

        def mounted(key, chain):
            runner = env.conductor(key)
            runner.forget()
            runner.start(root / "FLOOR.md")
            env.conductor(key).mount(chain)
            return ([(one["doc"], one.get("body")) for one in env.conductor(key)._mounted()
                     if one["doc"] != "PLANS-TEMPLATES.md"],
                    {one.code for one in env.conductor(key)._mount_laws()})

        slot, laws = mounted("pchore", plans.mount_chain(root, ["menage"]))
        c.ok(slot == [("PLAN.md", True), ("plans/_templates/chore.md", True), ("plans/menage/CHORE.md", True)],
             f"one level {slot}")
        c.ok("CH1" in laws, f"the chore's law {sorted(laws)}")
        slot, laws = mounted("pproj", plans.mount_chain(root, ["projet", "api"]))
        c.ok([doc for doc, _ in slot] == ["PLAN.md", "plans/_templates/project.md", "plans/projet/PROJECT.md",
                                          "plans/_templates/task.md", "plans/projet/1-api/TASK.md"]
             and slot[1][1] is False and slot[2][1] == ["## Brief..## Items"] and slot[3][1] is True, f"two levels {slot}")
        c.ok({"PJ1", "TK1"} <= laws, f"the levels' laws {sorted(laws)}")
        chore = place / "chore.md"
        chore.write_text(chore.read_text(encoding="utf-8").replace("sections: |\n  Framing\n",
                                                                   "sections: |\n  Framing\n  Items\n  Delivery  unserved\n"),
                         encoding="utf-8")
        plans.write_section(root, ["menage"], "Items", "- vitres -- the windows\n- four -- the oven")
        plans.write_section(root, ["menage"], "Delivery", "the delivered windows, kept off the mount", item="vitres")
        chain = plans.mount_chain(root, ["menage"])
        c.ok(chain[-2]["body"] == ["..## Delivery"], f"the served sections {chain[-2]}")
        runner = env.conductor("pserved")
        runner.forget()
        runner.start(root / "FLOOR.md")
        text = env.conductor("pserved").mount(chain)
        c.ok("Clean the room." in text and "`menage`" in text and "kept off the mount" not in text,
             "the title and Framing served, the Delivery not")
        chore.write_text(chore.read_text(encoding="utf-8").replace("Delivery  unserved", "Delivery  hidden"),
                         encoding="utf-8")
        refuse("template-invalid", lambda: plans.mount_chain(root, ["menage"]))
        chore.write_text(chore.read_text(encoding="utf-8").replace("  Items\n  Delivery  hidden\n", ""), encoding="utf-8")
        _, laws = mounted("pprod", plans.mount_chain(root, ["named", "ph", "bt"]))
        c.ok(any(code.startswith("PH") for code in laws) and any(code.startswith("BA") for code in laws)
             and "TPL1" in laws, f"the product's laws {sorted(laws)}")

    # --- the MATERIAL of a plan: written on every born node, served from its tree ------------
    menv = P.house(bench, "plan-material")
    mroot = menv.made
    mplans = P.script(mroot)
    mplans.home = lambda: mroot
    tuned = (mroot / "SETTINGS.md").read_text(encoding="utf-8").replace(
        "max_harness_tool_output: 25000", "max_harness_tool_output: 200000")   # a mount read whole, uncut
    (mroot / "SETTINGS.md").write_text(tuned, encoding="utf-8")              # no material.* key, ever

    def mplay(argv, stdin=""):
        out = P.play(mplans, argv, stdin)
        return out

    for relative, text in (("engine/x.py", "FROM = 'the repository'\n"), ("alt/engine/x.py", "FROM = 'alt'\n")):
        (menv.root / relative).parent.mkdir(parents=True, exist_ok=True)
        (menv.root / relative).write_text(text, encoding="utf-8")
    for name, prose in (("Context", "A plan whose code lives in a worktree."), ("Choices", CHOICES),
                        ("Expected", EXPECTED), ("Items", "- ph -- A phase\n- ph2 -- A prepared phase")):
        mplans.write_section(mroot, ["job"], name, prose)
    for name, prose in (("Ground", GROUND), ("Choices", CHOICES), ("Expected", EXPECTED),
                        ("Items", "- bt -- A batch\n- bt2 -- A prepared batch")):
        mplans.write_section(mroot, ["job", "ph"], name, prose)
    for name, prose in (("Ground", GROUND), ("Choices", CHOICES), ("Expected", EXPECTED), ("Tests", TESTS)):
        mplans.write_section(mroot, ["job", "ph", "bt"], name, prose)
    job = mroot / "plans" / "job"
    mdocs = [job / "PLAN.md", job / "1-ph" / "PHASE.md", job / "1-ph" / "1-bt" / "BATCH.md"]
    bare = [one.read_bytes() for one in mdocs]                 # no material anywhere yet
    keyed = re.compile(r"^created: .*\nmaterial: (\S+)\n", re.M)
    alt = os.path.relpath(menv.root / "alt", job)              # relative: read from the plan's folder

    def declared() -> str:
        """-> the plan's `materials:` block as the engine's reader reads it."""
        return str(document.read(job / "PLAN.md").front.get("materials") or "")

    def carried(docs=mdocs):
        return [(hit.group(1) if (hit := keyed.search(one.read_text(encoding="utf-8"))) else None)
                for one in docs]

    with case("(a) the verb declares the tree and writes the material everywhere", "`material job core <rel>`: "
              "`core: <rel>` in the plan's `materials:` block, the path as given; `material: core` after "
              "`created` on the plan, its born phase and its born batch; the prepared batch has no document; "
              "the answer names the three") as c:
        said = P.material_said(mplay(["material", "job", "core", alt]))
        c.ok(declared().splitlines() == [f"core: {alt}"], f"declared {declared()!r}")
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

    with case("(c) a declared name chosen, the slug by default, `-` takes the key out", "`material job job <path>` "
              "declares a second tree beside the first; `material job core` without a path chooses the declared "
              "core; `material job` writes the slug, declared; a path again for a declared name rewrites its line; "
              "`material job -` removes the key from the five documents, the declaration kept -- the phase and "
              "the batch written before the verb byte for byte as they were") as c:
        said = P.material_said(mplay(["material", "job", "job", "/elsewhere"]))
        c.ok(declared().splitlines() == [f"core: {alt}", "job: /elsewhere"], f"declared {declared()!r}")
        said = P.material_said(mplay(["material", "job", "core"]))
        c.ok(carried() == ["core", "core", "core"] and said is not None and said[0] == "core", f"said {said}")
        said = P.material_said(mplay(["material", "job"]))
        c.ok(carried() == ["job", "job", "job"] and said is not None and said[0] == "job", f"said {said}")
        mplay(["material", "job", "job", "/moved"])
        c.ok(declared().splitlines() == [f"core: {alt}", "job: /moved"], f"rewritten {declared()!r}")
        said = P.material_said(mplay(["material", "job", "-"]))
        c.ok(carried() == [None, None, None] and said is not None and said[:3] == (None, "job", 5), f"said {said}")
        c.ok(declared().splitlines() == [f"core: {alt}", "job: /moved"], "the declaration kept")
        c.ok([one.read_bytes() for one in mdocs[1:]] == bare[1:], "the bytes before the verb")
        c.ok(all("material" not in one.read_text(encoding="utf-8").split("\n---\n", 1)[0] for one in born),
             "the key on a born document")

    with case("(d) the refusal writes nothing, `repo` and `work` name no tree", "material-undeclared "
              "on a name the plan does not declare (the call that declares it named), `repo` and `work` among "
              "them; material-invalid on a path for `work` or a name with a colon; kind-mismatch on a phase "
              "address, path-unknown on an unborn plan, argument-unexpected -- every byte unchanged") as c:
        before = {one: one.read_bytes() for one in job.rglob("*.md")}
        out = refuse("material-undeclared", lambda: mplans.main(["material", "job", "nope"]))
        c.ok("material job nope <path>" in out, f"the call to play {out}")
        refuse("material-invalid", lambda: mplans.main(["material", "job", "work", "/somewhere"]))
        refuse("material-invalid", lambda: mplans.main(["material", "job", "a:b", "/somewhere"]))
        refuse("kind-mismatch", lambda: mplans.main(["material", "job/ph", "core"]))
        refuse("path-unknown", lambda: mplans.main(["material", "ghost", "core"]))
        refuse("argument-unexpected", lambda: mplans.main(["material", "job", "core", alt, "extra"]))
        refuse("material-undeclared", lambda: mplans.main(["material", "job", "repo"]))
        refuse("material-undeclared", lambda: mplans.main(["material", "job", "work"]))
        c.ok({one: one.read_bytes() for one in job.rglob("*.md")} == before, "the bytes")

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
              "it; a marked row says nothing; by argv and by stdin, once per call; a row marked `@repo` or "
              "`@work` refuses material-invalid, nothing written") as c:
        def reminded(said: str) -> list[list[str]]:
            """-> the backticked fields of each line `serve` says after its answer: a reminder's
            first field is the material it names."""
            return [re.findall(r"`([^`]+)`", line) for line in said.splitlines()[1:] if line.strip()]
        said = mplay(["serve", "job/ph/bt", "engine/x.py"])
        c.ok([one[:1] for one in reminded(said)] == [["core"]]
             and not any(field in ("@repo", "@work") for one in reminded(said) for field in one), f"said {said}")
        said = mplay(["serve", "job/ph2", "@core", "engine/x.py"])
        c.ok(reminded(said) == [], f"@core said {said}")
        said = mplay(["serve", "job/ph2", "-"], stdin="engine/x.py\n@core README.md\n")
        c.ok([one[:1] for one in reminded(said)] == [["core"]], f"stdin said {said}")
        before = {one: one.read_bytes() for one in job.rglob("*.md")}
        refuse("material-invalid", lambda: mplans.main(["serve", "job/ph2", "reference:", "@repo", "README.md"]))
        refuse("material-invalid", lambda: mplans.main(["serve", "job/ph2", "engine/x.py", "@work"]))
        c.ok({one: one.read_bytes() for one in job.rglob("*.md")} == before, "the bytes after the refusals")

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

    with case("(h) `check` sees a name its chain does not declare", "the declaration gone from PLAN.md by a hand "
              "reddens the plan once (material-undeclared), repair says the gesture and touches nothing; declared "
              "again by the verb, check is clean") as c:
        mplay(["material", "job", "core"])
        plan_doc = job / "PLAN.md"
        kept = plan_doc.read_text(encoding="utf-8")
        plan_doc.write_text(re.sub(r"^materials: \|\n(?:  .*\n)+", "", kept, count=1, flags=re.M), encoding="utf-8")
        found = mplans.check(mroot)
        c.ok(len(found) == 1 and found[0].startswith("job: material `core`") and "material-undeclared" in found[0],
             f"findings {found}")
        mended, left = mplans.repair(mroot)
        c.ok(mended == [] and len(left) == 1 and "material <slug> -" in left[0], f"mended {mended} left {left}")
        mplay(["material", "job", "core", alt])
        c.ok(mplans.check(mroot) == [], "check")

    with case("(i) `serve` weighs a whole row", "a row without a range whose file, read in the material, passes "
              "the budget refuses serve-heavy, by argv and by stdin, its size and a range said, every byte "
              "unchanged; the same row with a range, a light row, a file the material lacks are written") as c:
        heavy = menv.root / "alt" / "engine" / "heavy.py"
        heavy.write_text("# a heavy module\n" + "x = 1\n" * 7000, encoding="utf-8")   # 42 017 characters
        rows = lambda: mplans.read(mdocs[2])[0].get("serve", "")          # noqa: E731
        before = {one: one.read_bytes() for one in job.rglob("*.md")}
        out = refuse("serve-heavy", lambda: mplans.main(["serve", "job/ph/bt", "engine/heavy.py"]))
        c.ok("42017" in out and "engine/heavy.py[" in out, f"the size and the remedy {out}")
        with P.fed("engine/x.py\nengine/heavy.py\n"):
            refuse("serve-heavy", lambda: mplans.main(["serve", "job/ph/bt", "-"]))
        c.ok({one: one.read_bytes() for one in job.rglob("*.md")} == before, "the bytes after the refusals")
        mplay(["serve", "job/ph/bt", "engine/heavy.py[# a heavy..x = 1]"])
        mplay(["serve", "job/ph/bt", "engine/heavy.py[1-40]"])
        mplay(["serve", "job/ph/bt", "engine/x.py"])
        mplay(["serve", "job/ph/bt", "@job", "engine/heavy.py"])             # the tree `job` lacks it
        mplay(["serve", "job/ph/bt", "engine/ghost.py"])
        written = rows()
        c.ok(all(one in written for one in ("engine/heavy.py[# a heavy..x = 1]", "engine/heavy.py[1-40]",
                                            "engine/x.py", "@job engine/heavy.py", "engine/ghost.py")),
             f"the rows written {written!r}")


    with case("(j) `check` judges every `materials:` block once", "a plan whose block a hand wrote badly and whose "
              "nodes name no material: check reddens once, material-invalid, naming the plan") as c:
        mplans.write_section(mroot, ["loose"], "Context", "A plan with a block written by a hand.")
        loose = mroot / "plans" / "loose" / "PLAN.md"
        text = loose.read_text(encoding="utf-8")
        loose.write_text(re.sub(r"^(created: .*\n)", lambda hit: hit.group(1) + "materials: |\n  nopath\n",
                                text, count=1, flags=re.M), encoding="utf-8")
        found = mplans.check(mroot)
        c.ok(len(found) == 1 and found[0].startswith("loose:") and "material-invalid" in found[0], f"findings {found}")
        shutil.rmtree(loose.parent)

    plan_doc = job / "PLAN.md"
    with case("(k) a rewrite keeps the block's `#` lines", "a comment a hand wrote in the block stays as written, "
              "in its place, when the verb declares another tree") as c:
        plan_doc.write_text(plan_doc.read_text(encoding="utf-8").replace(
            "materials: |\n", "materials: |\n  # the worktree of the branch\n", 1), encoding="utf-8")
        mplay(["material", "job", "extra", "/x"])
        mplay(["material", "job", "core"])             # declaring chose extra: the nodes go back to core
        c.ok(declared().splitlines() == ["# the worktree of the branch", f"core: {alt}", "extra: /x"],
             f"declared {declared()!r}")

    with case("(l) `material <slug> - <name>` withdraws one declaration", "the line `extra` leaves the PLAN.md's "
              "block, the comment and the other lines kept, no other document touched; an absent name refuses "
              "material-undeclared, nothing written; `core` withdrawn while the nodes carry it: check says "
              "material-undeclared for job; declared again, check is clean") as c:
        others = {one: one.read_bytes() for one in job.rglob("*.md") if one != plan_doc}
        said = mplay(["material", "job", "-", "extra"])
        c.ok(declared().splitlines() == ["# the worktree of the branch", f"core: {alt}"],
             f"declared {declared()!r} said {said!r}")
        c.ok({one: one.read_bytes() for one in job.rglob("*.md") if one != plan_doc} == others, "another document")
        c.ok(carried() == ["core", "core", "core"], f"carried {carried()}")
        before = {one: one.read_bytes() for one in job.rglob("*.md")}
        refuse("material-undeclared", lambda: mplans.main(["material", "job", "-", "absent"]))
        c.ok({one: one.read_bytes() for one in job.rglob("*.md")} == before, "the bytes after the refusal")
        mplay(["material", "job", "-", "core"])
        found = mplans.check(mroot)
        c.ok(len(found) == 1 and found[0].startswith("job: material `core`") and "material-undeclared" in found[0],
             f"findings {found}")
        mplay(["material", "job", "core", alt])
        c.ok(mplans.check(mroot) == [], f"check {mplans.check(mroot)}")

    def gestures(text: str) -> list[str]:
        """-> the `material ...` gestures a finding or an advice names, in their order."""
        return re.findall(r"`(material [^`]*)`", text)

    with case("(m) a retired name carried by a node", "a plan born before `repo` and `work` were retired, its "
              "nodes carrying `material: work`: check says it once, material-undeclared, and names one gesture, "
              "`material job -`; repair advises that gesture alone; played, check is clean") as c:
        for one in mdocs:
            one.write_text(re.sub(r"^material: core$", "material: work", one.read_text(encoding="utf-8"),
                                  flags=re.M), encoding="utf-8")
        found = mplans.check(mroot)
        codes = [hit.group(1) if (hit := re.search(r"\((material-[a-z-]+)\)$", one)) else None for one in found]
        c.ok(codes == ["material-undeclared"] and found[0].startswith("job:")
             and gestures(found[0]) == ["material job -"], f"findings {found}")
        mended, left = mplans.repair(mroot)
        advice = left[0].rsplit(" -- ", 1)[-1] if left else ""
        c.ok(mended == [] and len(left) == 1 and gestures(advice) == ["material <slug> -"],
             f"mended {mended} left {left}")
        mplay(["material", "job", "-"])
        c.ok(mplans.check(mroot) == [], f"check {mplans.check(mroot)}")
        mplay(["material", "job", "core"])

    return 0
