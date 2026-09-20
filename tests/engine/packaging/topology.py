"""Scenario `topology` -- the lint of topology (plan pp-split, batch
le-lint-de-topologie):
- a package may only name what it requires: each reference kind resolved to its owner, refused by name when the owner is outside the closure
- an unknown target refuses `reference-unknown`; a serve token is judged on its closure alone
- a package's proc HOOKs a socket its manifest declares, or refuses `socket-undeclared`
- the instance is the top: its documents reference every pin and offer what their harness carries
- nothing written under a refusal; the reference composition builds as before
"""
from __future__ import annotations

from conductor import compiling, instance, topology

MANIFEST = "name: witness\nversion: 0.0.1\ndescription: a witness of the topology\nrequires: [{requires}]\n{extra}"
PROC = "---\nname: {name}\nkind: proc\ndescription: a witness proc\n{front}proc: |\n{proc}---\n\nthe witness\n"


def _pin(made, manifest: str, files: dict[str, str]) -> None:
    root = made / ".sys" / "vendor" / "witness@0.0.1"
    import shutil
    for stale in ("procs", "overlays", "skills", "refs"):
        shutil.rmtree(root / stale, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"]["witness"] = "0.0.1"
    instance.write(made, pins)


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("topo").made
    before = compiling.build_tools(made).read_bytes()   # the reference composition, built

    def lies(requires: str, extra: str = "", **files: str):
        files = {key.replace("__", "/") + ".md": text for key, text in files.items()}
        _pin(made, MANIFEST.format(requires=requires, extra=extra), files)
        return lambda: compiling.build_tools(made)

    def proc(name: str, proc_lines: str = "  INFER\n", front: str = "") -> str:
        return PROC.format(name=name, proc=proc_lines, front=front)

    # --- every reference kind, owned by the kit, named by a package that requires nothing
    expect("dependency-undeclared", lies("", procs__W_CALL=proc("W_CALL", "  CALL CAPABILITIES.md\n  INFER\n")))
    expect("dependency-undeclared", lies("", procs__W_ATTACH=proc("W_ATTACH", front="attach: boot.ready\n")))
    expect("dependency-undeclared", lies("", procs__W_TOOL=proc("W_TOOL", front="tools: |\n  CAPABILITIES\n")))
    expect("dependency-undeclared", lies("", overlays__TURN=proc("TURN", front="tools: |\n  +CAPABILITIES\n")))
    # the sink and guarded-key dependency flavors left with the kit's skills and keys --
    # their coverage returns with the packages that own sinks and keys (KPS21)
    # the format dependency flavor lost its subject: every mechanical form lives at the
    # engine since la-descente-du-kit -- its coverage returns when a package declares one
    # (steering's `next`, KPS21).
    expect("dependency-undeclared", lies("", procs__W_SERVE=proc("W_SERVE", front="serve: |\n  reference: PP.md\n")))
    expect("dependency-undeclared",
           lies("", extra="contributes:\n  cadences:\n    - {name: w, anchor: w_day, "
                          "record: w.jsonl, play: W_HOOK.md, at: boot.ready}\n",
                procs__W_HOOK=proc("W_HOOK")))

    # --- an unknown target refuses; a serve token is judged on its closure alone ----
    expect("reference-unknown", lies("kit", procs__W_LOST=proc("W_LOST", "  CALL NOWHERE.md\n  INFER\n")))
    expect("reference-unknown", lies("kit", procs__W_GHOST=proc("W_GHOST", front="tools: |\n  ghost-skill\n")))
    expect("reference-unknown", lies("kit", procs__W_FMT=proc("W_FMT", front="output: nonesuch\n")))
    expect("reference-unknown", lies("kit", procs__W_SNK=proc("W_SNK", front="sink: pp-nowhere\n")))
    expect("reference-unknown", lies("kit", overlays__NOBODY=proc("NOBODY")))
    expect("reference-unknown",
           lies("kit", procs__W_WITH=proc("W_WITH", front="provides: w\nwith: pp-nowhere\n")))
    # a skill the INSTANCE owns: it resolves, and it is not the witness's -- KPD14 bites
    own = made / "skills" / "pp-elsewhere"
    own.mkdir(parents=True, exist_ok=True)
    (own / "SKILL.md").write_text(
        "---\nname: pp-elsewhere\ndescription: a skill of another home\n---\n\nelsewhere\n",
        encoding="utf-8")
    expect("with-foreign", lies("kit", procs__W_BORROW=proc("W_BORROW", front="provides: w\nwith: pp-elsewhere\n")))
    import shutil
    shutil.rmtree(own)          # the borrowed home leaves: the reference composition is the kit's
    expect("contribution-malformed", lies("kit", procs__W_BARE=proc("W_BARE", front="provides: w\n")))
    expect("contribution-malformed", lies("kit", procs__W_ONLY=proc("W_ONLY", front="with: pp-witness\n")))
    expect("attach-and-mount",
           lies("kit", procs__W_BOTH=proc("W_BOTH", front="attach: boot.ready\nmount: boot.ready\n")))
    expect("socket-undeclared", lies("kit", procs__W_SOCK=proc("W_SOCK", "  HOOK witness.ready\n  INFER\n")))
    # --- an `exec:` plays the owner's own skill, on a document the engine enters -----
    expect("reference-unknown", lies("kit", procs__W_EXEC=proc("W_EXEC", front="exec: stamp\n")))
    skill = {"skills__pp-witness__SKILL": "---\nname: pp-witness\ndescription: the witness's skill\n---\n\npp-witness\n"}
    expect("reference-unknown",
           lies("kit", procs__W_TAG=proc("W_TAG", front="exec: stamp @NOPE.x\n"), **skill))
    expect("exec-unplayable",
           lies("kit", refs__W_REF="---\nname: W_REF\nkind: doc\nexec: stamp\n---\n\na ref\n", **skill))
    expect("exec-unplayable",
           lies("kit", procs__W_DATA="---\nname: W_DATA\nkind: doc\nexec: stamp\n---\n\nneither called nor mounted\n", **skill))
    if (made / ".sys" / "tools.md").read_bytes() == before:
        held("a refusal writes nothing", "tools.md byte-identical after every refused build")
    else:
        failures.append("  ✗ refusal wrote                tools.md changed under a refusal")

    # --- the truth: requires: [kit, plan], the socket declared, the token unresolved -
    _pin(made, MANIFEST.format(
        requires="kit",
        extra="contributes:\n  sockets: [witness.ready]\n"),
        {"procs/W_ALL.md": proc("W_ALL", "  HOOK witness.ready\n  CALL CAPABILITIES.md\n  INFER\n",
                                front="tools: |\n  CAPABILITIES\n  +harness-only\n"
                                      "output: table\nserve: |\n  reference: PP.md unknown-reading.md\n"),
         "overlays/TURN.md": proc("TURN", front="tools: |\n  +CAPABILITIES\n")})
    try:
        composed = topology.validate(made)
        held("an honest manifest passes", f"{len([c for c in composed if c['package'] == 'witness'])} "
             "contributions of the witness: every reference owned by kit or plan, the socket "
             "declared, the harness offer and the unresolved serve token left to the run")
    except Exception as error:                                            # noqa: BLE001
        failures.append(f"  ✗ honest manifest              {error}")

    # --- the instance is the top: everything pinned, the harness's own offers -------
    (made / "procs").mkdir(exist_ok=True)
    (made / "procs" / "TOP.md").write_text(
        proc("TOP", "  HOOK anything.goes\n  CALL CAPABILITIES.md\n  INFER\n",
             front="tools: |\n  CAPABILITIES\n  my-harness-skill\nattach: boot.ready\noutput: table\n"), encoding="utf-8")
    try:
        topology.validate(made)
        held("the instance references every pin", "a HOOK of its own, a CALL to the kit, "
             "a harness offer -- nothing refused")
    except Exception as error:                                            # noqa: BLE001
        failures.append(f"  ✗ instance top                 {error}")
    expect("reference-unknown", lambda: (
        (made / "procs" / "TOP.md").write_text(proc("TOP", "  CALL GONE.md\n  INFER\n"), encoding="utf-8"),
        topology.validate(made)))
    (made / "procs" / "TOP.md").unlink()

    # --- the reference composition: the kit alone, nothing to declare, built as before -
    pins = instance.read(made)
    del pins["packages"]["witness"]
    instance.write(made, pins)
    import shutil
    shutil.rmtree(made / ".sys" / "vendor" / "witness@0.0.1")   # unpinned AND gone, as `remove` leaves it
    built = compiling.build_tools(made)
    if built.read_bytes() == before:
        held("the reference composition holds", "the kit judged whole, tools.md byte-identical")
    else:
        failures.append("  ✗ reference composition        tools.md moved")
    return 0
