"""Scenario `plan-package` -- the plan package on an instance that conducts, from its
absence to its removal, and what it holds of its own:
- without the package the socle is silent: no block, no offer, no sector
- a LATE add lands the keys and the offer and brings no steering: steering is OPTIONAL to
  plan, so the composition stands without it, NEXT_MOVE (mounted on steering's socket)
  sleeps and the build says so, the TURN overlay rides every turn, and `pp-plan next-move`
  reads the held next move on demand
- the reference (PLAN_CHEATSHEET.md) is not among what the boot or an exchange without a plan
  serves; the first mount of a plan brings it, a mount in a later exchange spares it; the PLANS
  space brings it at its opening
- the PLANS space opens without steering, pp-plan offered and nothing of steering
- steering added beside it, NEXT_MOVE rides NEXT's socket; the PLANS space, offered at TURN, opens
  on its board -- `status --engaged --json` served to an INFER in the form plan-board, no reading of
  steering --, then its WORK ends on a proof, and the close gives the root back
- the PLANS are the instance's data: an upgrade re-materializes the bundle and leaves the
  tree byte for byte, locks included, and a doctor repairs at constant pins
- remove takes the SURFACE away -- offer, contributor, bundle -- leaves the keys unowned,
  the plans untouched and the standing next moves at the record
- the package holds nothing that is not its own: prefixed keys, no seed, no optional
  neighbour named, the engine reached through its public face, and no artifact of its own
  in the kit or the engine but the frozen prose lines
"""
from __future__ import annotations

import re

import json

from conductor import compiling, events, install, instance, reading
from conductor.core import language
from tests.harness import SOURCE, body_of, cli, kept_document, load_script, na_proof, reaches

HOME = SOURCE / "packages" / "plan"
THESIS = "the wall of the garden, rebuilt stone by stone\n"
OPTIONAL = tuple(sorted(one.name for one in (SOURCE / "packages").iterdir()
                       if (one / "package.yaml").is_file() and one.name not in ("plan", "steering")))
# the engine's PROSE mentions of this package, frozen: docstrings that name it as an
# EXAMPLE and drive nothing. A new line anywhere reddens -- prose is counted, never
# rewritten from here (it belongs to the core's own documentary pass).
PROSE = {("engine/conductor/core/sections.py", "pp-plan"),
         ("engine/conductor/state/settings.py", "plan_implementation_care")}
NAMES = re.compile(r"pp-plan|plan-next-move|plan_implementation|NEXT_MOVE\.md|plans/<slug>")
SWEPT = ("engine", "bases/kit")           # the engine and the base the package stands on


def _offers(meta) -> set:
    """-> what TURN offers here: the composed tools, overlays applied."""
    document = reading.read(instance.resolve(meta, "TURN.md"))
    return {one.name for one in compiling.effective(meta, document)[1]}


def _tree(meta) -> dict:
    """-> every file under `plans/`, path -> bytes: the instance's OWN data, locks and all."""
    root = meta / "plans"
    return {str(one.relative_to(root)): one.read_bytes()
            for one in sorted(root.rglob("*")) if one.is_file()} if root.is_dir() else {}


def _contributors(meta, socket) -> list[str]:
    """-> the socket's contributors by BOTH entry verbs -- NEXT is called at `turn.end`,
    NEXT_MOVE is MOUNTED on NEXT's own socket `steering.next.begin`."""
    return list(instance.attached(meta, socket)) + list(instance.mounting(meta, socket))


def _vendored(meta) -> list[str]:
    return sorted(one.name.split("@")[0] for one in instance.vendored(meta))


def _standing(meta) -> list[str]:
    return sorted(key for key in events.counters(meta) if key.startswith("standing|plan|plan-next-move|"))


def _exchange(env) -> list[str]:
    """One exchange after the boot, the INFER proof answered n/a -> the blocks it served."""
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))
    blocks, pending, steps = [], env.conductor("t").submit(""), 0
    while pending is not None and steps < 8:
        steps += 1
        blocks.append(pending.document)
        if pending.judged:
            env.conductor("t").submit(na_proof(pending))
            break
        if pending.wait:
            break
        pending = env.conductor("t").submit("")
    return blocks


def _cheatsheet(meta) -> list[tuple[str, str]]:
    """-> (state, document) of every ledger line the house's runs wrote for the plan's reference,
    in order: what served it, what spared it."""
    return [(line.get("state"), line.get("by")) for log in sorted((meta / ".sys" / "state").glob("session-*.jsonl"))
            for one in map(json.loads, filter(str.strip, log.read_text(encoding="utf-8").splitlines()))
            if one.get("kind") == "block" for line in (one.get("served") or [])
            if line.get("subject") == "PLAN_CHEATSHEET.md"]


def _space(env):
    """Opens PLANS on a fresh boot of run `t`, answers its welcome and its WORK, the proof n/a, then
    closes it -> (the boot's block, the welcome, the WORK, the proof, the block after the close)."""
    opener = env.conductor("t")
    before = opener.start(opener.boot("BOOT.md"))
    conductor = env.conductor("t")
    welcome = conductor.open("PLANS", route=conductor.route("PLANS"))
    work, steps = env.conductor("t").submit("the board, in tables"), 0
    while work is not None and work.document != "PLANS" and steps < 3:   # the welcome's frame closes first
        steps += 1
        work = env.conductor("t").submit("")
    proof = env.conductor("t").submit("the work of the space") if work is not None else None
    while proof is not None and proof.instruction.keyword != "PROVE" and not proof.wait and steps < 6:
        steps += 1
        proof = env.conductor("t").submit("")
    if proof is not None and proof.judged:
        env.conductor("t").submit(na_proof(proof))
    back = env.conductor("t").close()
    return before, welcome, work, proof, back


def _sources(home):
    return [one for one in sorted(home.rglob("*"))
            if one.is_file() and one.suffix in (".py", ".md", ".yaml")
            and "__pycache__" not in one.parts]


def _surface(bench) -> None:
    """The package's life on one house: absent, added late without steering, steering
    beside it, upgraded, repaired, removed."""
    held, failures = bench.held, bench.failures

    env = bench.env("plancycle")             # the kit alone: no plan, no steering
    meta = env.made

    # --- the socle without the package is silent -----------------------------------------
    blocks = _exchange(env)                  # it has conducted before the add
    sectors = events.sectors(meta)
    before = (env.read("SETTINGS.md"), _offers(meta), _contributors(meta, "steering.next.begin"))
    if "NEXT_MOVE" not in blocks and "pp-plan" not in before[1] and "plan" not in sectors:
        held("the absent package costs nothing", "no block at the socket, no offer at TURN, "
             "no sector at the bus -- the absence is a diff, not an impression")
    else:
        failures.append(f"  ✗ absence                     blocks={blocks} sectors={sorted(sectors)}")

    # --- the late add: plan alone composes, steering optional -----------------------------
    install.add_package(env.member, "plan")
    settings = env.read("SETTINGS.md")
    alone = _vendored(meta)
    declared = instance.manifest_of(next(one for one in instance.vendored(meta)
                                         if one.name.startswith("plan@")))
    at_source = instance.manifest_of(HOME)
    requires, optional = declared.get("requires") or [], declared.get("optional") or []
    if ("steering" not in alone and {"kit", "plan"} <= set(alone) and requires == ["kit"]
            and optional == ["steering"]
            and (at_source.get("requires"), at_source.get("optional")) == (requires, optional)):
        held("plan composes without steering", f"vendored {alone}; plan requires {requires} "
             f"and declares steering optional -- pulled by nothing")
    else:
        failures.append(f"  ✗ composition                vendored={alone} "
                        f"requires={requires} optional={optional}")

    built = env.cli("-build")
    dormant = [one for one in (compiling.lint(meta) if built.returncode == 0 else [])
               if one.startswith("mount-dormant")]
    if built.returncode == 0 and len(dormant) == 1 and "NEXT_MOVE" in dormant[0] and "steering" in dormant[0]:
        held("the build passes, NEXT_MOVE sleeps", dormant[0])
    else:
        failures.append(f"  ✗ build                      rc={built.returncode} "
                        f"{built.stderr.strip()[-160:]!r} dormant={dormant}")

    base = instance.resolve(meta, "TURN.md")
    laws, tools = compiling.effective(meta, reading.read(base))
    text, _ = env.conductor("t")._composed(base)
    if built.returncode == 0:
        _exchange(env)                       # a boot and an exchange that work no plan
    unserved = _cheatsheet(meta)
    if ({"KT1", "KT2", "KT3", "KT4"} <= {one.code for one in laws}
            and "pp-plan" in [one.name for one in tools]
            and reaches(text, body_of(kept_document(HOME, "TURN")))
            and str(base).endswith("procs/TURN.md") and not unserved):
        held("the plan package overlays the TURN", "KT laws in force, pp-plan offered, "
             "the mode's body rides the served text -- the kit stays the base; the reference is not "
             "among what the boot or an exchange without a plan serves")
    else:
        failures.append(f"  ✗ plan TURN overlay           base={base} {[one.code for one in laws]} "
                        f"reference={unserved}")

    if built.returncode == 0:
        _exchange(env)
        born = cli(env.engine, "t", "-s", "pp-plan", "section", "le-mur", "Context", stdin=THESIS)
        read = cli(env.engine, "t", "-s", "pp-plan", "next-move")
        lines = [one for one in read.stdout.splitlines() if one.endswith("(plan:le-mur)")]
        if born.returncode == 0 and read.returncode == 0 and lines:
            held("pp-plan reads the next move on demand", lines[0])
        else:
            failures.append(f"  ✗ next move                  born={born.returncode} read={read.returncode} "
                            f"{read.stdout.strip()[-160:]!r} {read.stderr.strip()[-160:]!r}")
        keeper = load_script(next(one for one in instance.vendored(meta)
                                  if one.name.startswith("plan@")) / "skills" / "pp-plan" / "pp-plan.py")
        chain = keeper.mount_chain(meta, ["le-mur"])
        env.conductor("t").mount(chain)
        once = _cheatsheet(meta)
        env.conductor("t").submit("a message of a new exchange")
        env.conductor("t").mount(chain)
        twice = _cheatsheet(meta)
        if once == [("served", "PLAN")] and twice == [("served", "PLAN"), ("spared", "PLAN")]:
            held("a mount serves the reference once per run", "the PLAN method brings PLAN_CHEATSHEET.md at the "
                 "first mount; a second mount in a later exchange spares it -- the slot's proof holds across the run")
        else:
            failures.append(f"  ✗ reference at the mount      once={once} twice={twice}")

    # --- the PLANS space without steering: it opens, nothing of steering offered -------------
    if built.returncode == 0:
        _, welcome, work, _, _ = _space(env)
        offered = {one.name for one in work.tools} if work is not None else set()
        if (welcome is not None and welcome.document == "PLANS-BOARD" and work is not None
                and "pp-plan" in offered and "pp-steering" not in offered):
            held("the PLANS space opens without steering", "its welcome then its WORK, pp-plan offered, "
                 "nothing of steering")
        else:
            failures.append(f"  ✗ space without steering     welcome={getattr(welcome, 'document', None)} "
                            f"work={getattr(work, 'document', None)} offered={sorted(offered)}")

    # --- steering added beside it ---------------------------------------------------------
    install.add_package(env.member, "steering")
    attached = _contributors(meta, "steering.next.begin")
    passes = _contributors(meta, "turn.end")
    landed = ("plan_implementation_care: asked" in settings
              and "plan_implementation_control:" in settings
              and "pp-plan" in _offers(meta) and "NEXT_MOVE.md" in attached)
    closed = _vendored(meta)
    ordered = "NEXT.md" in passes and "NEXT_MOVE.md" not in passes
    # the kit's own SETTINGS names `plan_` in its PROSE (the prefix rule): the probe is the KEY
    was_bare = ("plan_implementation_care:" not in before[0] and "pp-plan" not in before[1]
                and "NEXT_MOVE.md" not in before[2])
    if was_bare and landed and "steering" not in alone and "steering" in closed and ordered:
        held("a late add lands the surface, steering beside it", "the two keys at the composed "
             "SETTINGS, the offer at TURN, no steering brought by plan; steering added, NEXT_MOVE "
             "rides NEXT's socket, NEXT at turn.end, the line read after the work")
    else:
        failures.append(f"  ✗ late add                    bare={was_bare} landed={landed} alone={alone} "
                        f"closed={closed} ordered={ordered} passes={passes}")

    # --- the PLANS space: its welcome once, the board from pp-plan alone, its WORK proven ------
    opened_before = len(_cheatsheet(meta))
    before, welcome, work, proof, back = _space(env)
    at_open = _cheatsheet(meta)[opened_before:]
    payloads = dict(welcome.payloads) if welcome is not None else {}
    board = json.loads(payloads.get("plan-board") or "[]")
    form = compiling.format_enumeration(meta).get("plan-board")
    offered = "PLANS" in _offers(meta)
    if (offered and welcome is not None and welcome.root == "PLANS" and welcome.document == "PLANS-BOARD"
            and welcome.output == "plan-board" and [one["address"] for one in board] == ["le-mur"]
            and not [token for token in payloads if token.startswith("steering")]
            and form is not None and form[0] == language.WORDS
            and work is not None and work.document == "PLANS" and proof is not None
            and proof.instruction.keyword == "PROVE" and proof.document == "PLANS"
            and back is not None and before is not None and back.root == before.root
            and [one[1] for one in at_open] == ["PLANS"]):
        held("the PLANS space opens on its board", "offered at TURN; opened, PLANS-BOARD serves `status --engaged "
             "--json` to an INFER in the form plan-board (words), no reading of steering, and the space brings the "
             "reference once; then the WORK, proven; closed, the root it was opened from is back")
    else:
        failures.append(f"  ✗ the PLANS space            offered={offered} root={getattr(welcome, 'root', None)} "
                        f"first={getattr(welcome, 'document', None)}/{getattr(welcome, 'output', None)} "
                        f"board={board} tokens={sorted(payloads)} form={form} work={getattr(work, 'document', None)} "
                        f"proof={getattr(proof, 'document', None)}/{getattr(getattr(proof, 'instruction', None), 'keyword', None)} "
                        f"back={getattr(back, 'root', None)} before={getattr(before, 'root', None)} reference={at_open}")

    # --- the plans are the instance's data: an upgrade leaves the tree alone -------------
    keeper.new(meta, "cycle", "The cycle plan.\n\nIts thesis, in prose.")
    (meta / "plans" / "cycle.lock").write_bytes(b"")      # the lock a verb leaves behind
    events.stand(meta, "plan-next-move", "plan:cycle", "the plan has no phase yet")
    written, pins_before = _tree(meta), dict(instance.read(meta)["packages"])
    install.upgrade(env.member)
    kept = _tree(meta) == written
    install.doctor(env.member)
    steady = (dict(instance.read(meta)["packages"]) == pins_before
              and _tree(meta) == written and "pp-plan" in _offers(meta))
    if kept and steady and "cycle.lock" in written:
        held("upgrade and doctor leave the plans alone", "the bundle re-materializes and the "
             "repair runs at constant pins; the tree under plans/ stands byte for byte, its "
             "lock file with it")
    else:
        failures.append(f"  ✗ upgrade and doctor          kept={kept} steady={steady}")

    # --- remove takes the surface, never the data ----------------------------------------
    standing_before = _standing(meta)
    install.remove_package(env.member, "plan")
    after = env.read("SETTINGS.md")
    gone = ("pp-plan" not in _offers(meta)
            and "NEXT_MOVE.md" not in _contributors(meta, "turn.end")
            and not [one for one in instance.vendored(meta) if one.name.startswith("plan@")])
    unowned = "# ---- unowned ----" in after and "plan_implementation_care: asked" in after
    # the held next moves STAY at the record (the instance's data) -- and leave the SERVE:
    # with the package gone its family has no verifier, and the service drops what it
    # cannot verify
    standing = _standing(meta)
    served = [one["signal"] for one in events.standing_entries(meta)]
    if (gone and unowned and _tree(meta) == written and standing == standing_before
            and "standing|plan|plan-next-move|plan:cycle" in standing and "plan-next-move" not in served):
        held("remove takes the surface, never the data", "offer, contributor and bundle "
             "leave; the keys ride on as unowned, the plans and their locks are untouched, "
             "and the held next move stays at the record -- the instance's own -- while the "
             "serve drops it: no package, no verifier, no line")
    else:
        failures.append(f"  ✗ remove                      gone={gone} unowned={unowned} "
                        f"tree={_tree(meta) == written} standing={standing} before={standing_before}")


def _purity(bench) -> None:
    """What the package holds is its own -- read at the source, no house."""
    held, failures = bench.held, bench.failures

    # --- the keys wear the prefix, and nothing is sown ------------------------------------
    fragment = (HOME / "settings" / "SETTINGS.md").read_text(encoding="utf-8")
    front = fragment.split("---")[1] if fragment.startswith("---") else ""
    model = ("name", "kind", "package", "description", "types")
    keys = [line.split(":")[0] for line in front.splitlines()
            if re.match(r"^[a-z_]+:", line) and line.split(":")[0] not in model]
    sown = (HOME / "seed").exists()
    if keys and all(one.startswith("plan_") for one in keys) and not sown:
        held("the keys wear the prefix and nothing is sown",
             f"{', '.join(keys)} -- and no seed/ directory: the mode plants nothing in an instance")
    else:
        failures.append(f"  ✗ prefix and seeds            keys={keys} sown={sown}")

    # --- what it names, it requires --------------------------------------------------------
    named = {}
    for path in _sources(HOME):
        if "tests" in path.relative_to(HOME).parts:
            continue                     # a bench composes what it needs to prove
        text = path.read_text(encoding="utf-8")
        for neighbour in OPTIONAL:
            # a package is NAMED the way the house names one: backticked in prose, or as a
            # path or a skill in code -- `doc` the package, never `doc` the local variable
            if re.search(rf"`{neighbour}`|packages/{neighbour}\b|\bpp-{neighbour}\b", text):
                named.setdefault(neighbour, []).append(str(path.relative_to(HOME)))
    if not named:
        held("what it names, it requires", "no optional neighbour appears in the package's "
             "own files -- only steering, which its manifest declares")
    else:
        failures.append(f"  ✗ optional neighbours         {named}")

    # --- what it takes from the engine goes through the face -------------------------------
    from conductor import __all__ as face
    keeper = (HOME / "skills" / "pp-plan" / "pp-plan.py").read_text(encoding="utf-8")
    taken = set(re.findall(r"core\(__file__\)\.(\w+)", keeper))
    direct = re.findall(r"^\s*(?:from|import)\s+conductor", keeper, re.MULTILINE)
    if taken and taken <= set(face) and not direct:
        held("what it takes from the engine stands on the face",
             f"{', '.join(sorted(taken))} -- reached by the vendored bootstrap, and every one "
             "of them is a name the public face exports")
    else:
        failures.append(f"  ✗ engine surface              taken={sorted(taken)} direct={direct}")

    # --- no artifact of its own in the kit or the engine; the prose is frozen ---------------
    strays, prose, read = [], set(), 0
    for area in SWEPT:
        for path in _sources(SOURCE / area):
            read += 1
            for line in path.read_text(encoding="utf-8").splitlines():
                if NAMES.search(line):
                    spot = str(path.relative_to(SOURCE))
                    known = [one for one in PROSE if one[0] == spot and one[1] in line]
                    (prose.add((spot, known[0][1])) if known else strays.append(f"{spot}: {line.strip()[:60]}"))
    swept = {area: len(_sources(SOURCE / area)) for area in SWEPT}
    if all(swept.values()) and not strays and prose == PROSE:
        held("no artifact of its own outside the package",
             f"{read} files read ({swept}); the kit and the engine name it in {len(PROSE)} PROSE "
             "lines and nowhere else -- frozen here, so a new mention reddens by name")
    else:
        failures.append(f"  ✗ kit and engine              swept={swept} strays={strays} prose={sorted(prose)}")


def scenario(bench) -> int:
    _surface(bench)
    _purity(bench)
    return 0
