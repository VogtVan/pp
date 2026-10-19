"""Scenario `composition-lint` -- what the build lint refuses in a composition, and what it
only warns:
- the topology: a package may only name what it requires -- each reference kind resolved to
  its owner, refused by name when the owner is outside the closure; an unknown target refuses
  `reference-unknown`, a serve token is judged on its closure alone; a package's proc HOOKs a
  socket its manifest declares, or refuses `socket-undeclared`; the instance is the top: its
  documents reference every pin and offer what their harness carries; nothing written under a
  refusal, the reference composition builds as before
- the names a package exposes (KPS31): a console verb wears the package's name or refuses
  `name-unprefixed`; a skill is `pp-<package>[-<name>]`; a vector family is
  `<package>[-<family>]:`, another package's family JOINED under its prefix, that package
  required; a payload token is `<package>-<token>`, another's provided or consumed under ITS
  prefix; a proc or a ref carried as a BASE by two packages refuses `name-ambiguous`, an
  overlay by the source name passes; nothing written under a refusal; the bus's record follows
  the families at upgrade (`migrate_families`); the install's gate judges a TARGET composition
  before anything is written
- the author's laws: a code declared twice by the instance's own documents, a law line out of
  form, an attach no proc hooks WARN for the author and the build passes, the same in a
  package's documents refuses; a bare `constraints:` key refuses `constraints-unsectioned`,
  author or not
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from conductor import compiling, instance, topology
from conductor.packaging import events

MANIFEST = "name: {name}\nversion: 0.0.1\ndescription: a witness of the composition\nrequires: [{requires}]\n{extra}"
PROC = "---\nname: {name}\nkind: proc\ndescription: a witness proc\n{front}proc: |\n{proc}---\n\nthe witness\n"
REF = "---\nname: {name}\nkind: doc\ndescription: a witness note\n---\n\na note\n"
SKILL = "---\nname: {name}\ndescription: a witness skill\n---\n\n{name}\n"
SCRIPT = "print('ok')\n"

DOUBLED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
           "constraints.behavior: |\n  Z9  the same code, twice\n---\n\nx\n")
MALFORMED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
             "constraints.behavior: |\n  Z7  a law in form\n  nocode\n---\n\nx\n")
ATTACHED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
            "attach: nobody.hooks.this\n---\n\nx\n")
UNSECTIONED = ("---\nname: {name}\nkind: doc\ndescription: >-\n  a holder\n"
               "constraints: |\n  Z6  the old regime\n---\n\nx\n")


def proc(name: str, proc_lines: str = "  INFER\n", front: str = "") -> str:
    return PROC.format(name=name, proc=proc_lines, front=front)


def _files(**files: str) -> dict[str, str]:
    """`procs__X` is `procs/X.md`, `skills__pp_x` the contract AND the script of `pp-x`."""
    out: dict[str, str] = {}
    for key, text in files.items():
        space, _, stem = key.partition("__")
        if space == "skills":
            skill = stem.replace("_", "-")
            out[f"skills/{skill}/SKILL.md"] = SKILL.format(name=skill)
            out[f"skills/{skill}/{skill}.py"] = SCRIPT
        else:
            out[f"{space}/{stem}.md"] = text
    return out


def _pin(made, name: str, manifest: str, files: dict[str, str]) -> None:
    """A package forged in the vendor space and pinned: its manifest, then its files by
    relative path -- the spaces of the previous forge removed first."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    for stale in ("procs", "overlays", "refs", "skills"):
        shutil.rmtree(root / stale, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(manifest, encoding="utf-8")
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


def _unpin(made, name: str) -> None:
    """The package unpinned AND gone, as `remove` leaves it."""
    pins = instance.read(made)
    pins["packages"].pop(name, None)
    instance.write(made, pins)
    shutil.rmtree(made / ".sys" / "vendor" / f"{name}@0.0.1", ignore_errors=True)


def topology_refusals(bench, made, before: bytes) -> None:
    """The references of a package, judged against its closure; the instance as the top."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    def lies(requires: str, extra: str = "", **files: str):
        files = {key.replace("__", "/") + ".md": text for key, text in files.items()}
        _pin(made, "witness", MANIFEST.format(name="witness", requires=requires, extra=extra), files)
        return lambda: compiling.build_tools(made)

    # --- every reference kind, owned by the kit, named by a package that requires nothing
    expect("dependency-undeclared", lies("", procs__W_CALL=proc("W_CALL", "  CALL TURN.md\n  INFER\n")))
    expect("dependency-undeclared", lies("", procs__W_ATTACH=proc("W_ATTACH", front="attach: boot.ready\n")))
    expect("dependency-undeclared", lies("", procs__W_TOOL=proc("W_TOOL", front="tools: |\n  TURN\n")))
    expect("dependency-undeclared", lies("", overlays__TURN=proc("TURN", front="tools: |\n  +BOOT\n")))
    expect("dependency-undeclared", lies("", procs__W_SERVE=proc("W_SERVE", front="serve: |\n  reference: BOOT.md\n")))
    expect("dependency-undeclared",
           lies("", extra="contributes:\n  cadences:\n    - {name: w, anchor: w_day, "
                          "record: w.jsonl, play: W_HOOK.md, at: boot.ready}\n",
                procs__W_HOOK=proc("W_HOOK")))

    # --- an unknown target refuses; a serve token is judged on its closure alone ----------
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
    shutil.rmtree(own)          # the borrowed home leaves: the reference composition is the kit's
    expect("contribution-malformed", lies("kit", procs__W_BARE=proc("W_BARE", front="provides: w\n")))
    expect("contribution-malformed", lies("kit", procs__W_ONLY=proc("W_ONLY", front="with: pp-witness\n")))
    expect("attach-and-mount",
           lies("kit", procs__W_BOTH=proc("W_BOTH", front="attach: boot.ready\nmount: boot.ready\n")))
    expect("socket-undeclared", lies("kit", procs__W_SOCK=proc("W_SOCK", "  HOOK witness.ready\n  INFER\n")))
    # --- an `exec:` plays the owner's own skill, on a document the engine enters ----------
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

    # --- the truth: the socket declared, the references owned, the token unresolved --------
    _pin(made, "witness", MANIFEST.format(
        name="witness", requires="kit",
        extra="contributes:\n  sockets: [witness.ready]\n"),
        {"procs/W_ALL.md": proc("W_ALL", "  HOOK witness.ready\n  CALL TURN.md\n  INFER\n",
                                front="tools: |\n  TURN\n  +harness-only\n"
                                      "output: table\nserve: |\n  reference: PP.md unknown-reading.md\n"),
         "overlays/TURN.md": proc("TURN", front="tools: |\n  +BOOT\n")})
    try:
        composed = topology.validate(made)
        held("an honest manifest passes", f"{len([c for c in composed if c['package'] == 'witness'])} "
             "contributions of the witness: every reference owned by the base, the socket "
             "declared, the harness offer and the unresolved serve token left to the run")
    except Exception as error:                                            # noqa: BLE001
        failures.append(f"  ✗ honest manifest              {error}")

    # --- the instance is the top: everything pinned, the harness's own offers -------------
    (made / "procs").mkdir(exist_ok=True)
    (made / "procs" / "TOP.md").write_text(
        proc("TOP", "  HOOK anything.goes\n  CALL TURN.md\n  INFER\n",
             front="tools: |\n  TURN\n  my-harness-skill\nattach: boot.ready\noutput: table\n"), encoding="utf-8")
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

    # --- the reference composition: the kit alone, nothing to declare, built as before ----
    _unpin(made, "witness")
    built = compiling.build_tools(made)
    if built.read_bytes() == before:
        held("the reference composition holds", "the kit judged whole, tools.md byte-identical")
    else:
        failures.append("  ✗ reference composition        tools.md moved")


def naming_refusals(bench, made, before: bytes) -> None:
    """The public names of a package: verbs, skills, families, tokens, bases."""
    held, expect, failures = bench.held, bench.expect, bench.failures

    def passes(label: str, detail: str) -> None:
        try:
            topology.validate(made)
            held(label, detail)
        except Exception as error:                                        # noqa: BLE001
            failures.append(f"  ✗ {label:<30} {error}")

    def witness(extra: str = "", **files: str):
        _pin(made, "witness", MANIFEST.format(name="witness", requires="kit", extra=extra),
             _files(skills__pp_witness="", **files))
        return lambda: compiling.build_tools(made)

    def friend(requires: str, extra: str = "", **files: str):
        _pin(made, "friend", MANIFEST.format(name="friend", requires=requires, extra=extra),
             _files(skills__pp_friend="", **files))
        return lambda: topology.validate(made)

    # --- a console verb wears the package's name -----------------------------------------
    verb = "contributes:\n  commands:\n    - {{verb: {verb}, skill: pp-witness, args: [hello]}}\n"
    expect("name-unprefixed", witness(verb.format(verb="hello")))
    witness(verb.format(verb="witness-hello"))
    passes("a prefixed verb passes", "`witness-hello`")
    witness(verb.format(verb="witness"))
    passes("the package's name alone counts", "`witness` as the verb")

    # --- a skill is pp-<package> ----------------------------------------------------------
    expect("name-unprefixed", witness(skills__pp_hello=""))
    witness(skills__pp_witness_more="")
    passes("pp-<package>-<name> passes", "`pp-witness-more` beside `pp-witness`")

    # --- a vector family wears the package's name, another's is joined under its prefix ---
    family = "contributes:\n  events:\n    vectors:\n      {family}: {{{worker}: {skill}}}\n"
    expect("name-unprefixed", witness(family.format(family="road", worker="verify", skill="pp-witness")))
    witness(family.format(family="witness-road", worker="verify", skill="pp-witness"))
    passes("a prefixed family passes", "`witness-road:` verified by pp-witness")
    witness(family.format(family="witness", worker="verify", skill="pp-witness"))
    passes("the family equal to the package", "`witness:`")
    witness(family.format(family="witness-road", worker="verify", skill="pp-witness"))
    expect("dependency-undeclared", friend("kit", family.format(family="witness-road", worker="guard", skill="pp-friend")))
    friend("kit, witness", family.format(family="witness-road", worker="guard", skill="pp-friend"))
    passes("a family joined under its owner's prefix", "`friend` guards `witness-road:` and requires witness")
    expect("name-unprefixed", friend("kit, witness", family.format(family="nobody-road", worker="verify", skill="pp-friend")))
    _unpin(made, "friend")

    # --- a payload token wears the package's name, another's is named under its prefix ----
    provider = proc("W_GIVE", front="provides: {token}\nwith: pp-witness serve\n")
    expect("name-unprefixed", witness(procs__W_GIVE=provider.format(token="stuff")))
    witness(procs__W_GIVE=provider.format(token="witness-stuff"))
    passes("a prefixed token passes", "`witness-stuff` provided by W_GIVE")
    taker = proc("F_TAKE", front="payloads: {token}\n")
    expect("dependency-undeclared", friend("kit", procs__F_TAKE=taker.format(token="witness-stuff")))
    friend("kit, witness", procs__F_TAKE=taker.format(token="witness-stuff"))
    passes("a token consumed under its owner's prefix", "`friend` consumes `witness-stuff` and requires witness")
    giver = proc("F_GIVE", front="provides: witness-stuff\nwith: pp-friend serve\n")
    friend("kit, witness", procs__F_GIVE=giver)
    passes("a token provided into another's", "`friend` provides `witness-stuff` with its own skill")
    expect("name-unprefixed", friend("kit, witness", procs__F_TAKE=taker.format(token="nobody-stuff")))
    _unpin(made, "friend")

    # --- a proc or a ref is ONE base across the packages -----------------------------------
    witness(procs__W_ONE=proc("W_ONE"), refs__NOTE=REF.format(name="NOTE"))
    expect("name-ambiguous", friend("kit, witness", procs__W_ONE=proc("W_ONE")))
    friend("kit, witness", overlays__W_ONE="---\nname: W_ONE\n---\n\nan amendment\n")
    passes("an overlay by the source name passes", "`friend/overlays/W_ONE.md` amends witness's W_ONE")
    expect("name-ambiguous", friend("kit, witness", refs__NOTE=REF.format(name="NOTE")))
    _unpin(made, "friend")

    # --- nothing written under a refusal ---------------------------------------------------
    if (made / ".sys" / "tools.md").read_bytes() == before:
        held("a refusal writes nothing", "tools.md byte-identical after every refused build")
    else:
        failures.append("  ✗ refusal wrote                tools.md changed under a refusal")

    # --- the bus's record follows the families at upgrade ----------------------------------
    witness(family.format(family="witness-road", worker="verify", skill="pp-witness"))
    record = made / instance.RECORDS / events.RECORD
    record.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record.write_text(json.dumps({
        "road:x": {"count": 2, "last_at": now},
        f"{events.STANDING}witness|sig|road:y": {"text": "held", "last_at": now},
        "zzz:q": {"count": 1, "last_at": now},
    }), encoding="utf-8")
    told = events.migrate_families(made)
    after = json.loads(record.read_text(encoding="utf-8"))
    moved = {"witness-road:x", f"{events.STANDING}witness|sig|witness-road:y"} <= set(after)
    if moved and "zzz:q" in after and "road:x" not in after and len(told) == 3 \
            and any("left as is" in line for line in told):
        held("the bus follows the families", f"{told[0]} · {told[1]} · the orphan said")
    else:
        failures.append(f"  ✗ the bus follows the families {told} {sorted(after)}")
    if events.migrate_families(made) == []:
        held("the migration replays silent", "nothing to do the second time")
    else:
        failures.append("  ✗ migration replay             said something twice")

    # --- the reference composition -- the kit alone -- builds as before -------------------
    _unpin(made, "witness")
    built = compiling.build_tools(made)
    if built.read_bytes() == before:
        held("the reference composition holds", "the kit judged whole, tools.md byte-identical")
    else:
        failures.append("  ✗ reference composition        tools.md moved")

    # --- the INSTALL's gate: a TARGET composition judged before anything is written --------
    # the four gates that MOVE a composition (install, add, upgrade, remove) judge it at
    # the source first, `roots` in hand: the names are judged there like every reference
    forged = bench.temp() / "forged" / "stray@0.0.1"
    (forged / "skills" / "pp-stray").mkdir(parents=True, exist_ok=True)
    (forged / "package.yaml").write_text(
        "name: stray\nversion: 0.0.1\ndescription: a package wearing a bare verb\n"
        "requires: [kit]\ncontributes:\n  commands:\n    - {verb: hello, skill: pp-stray}\n",
        encoding="utf-8")
    (forged / "skills" / "pp-stray" / "SKILL.md").write_text(SKILL.format(name="pp-stray"), encoding="utf-8")
    (forged / "skills" / "pp-stray" / "pp-stray.py").write_text(SCRIPT, encoding="utf-8")
    pinned = dict(instance.read(made)["packages"])
    target = [bench.source() / "bases" / "kit", forged]
    expect("name-unprefixed", lambda: topology.validate(
        made, target, template=bench.source() / "template" / "instance"))
    if (dict(instance.read(made)["packages"]) == pinned
            and (made / instance.SYS / "tools.md").read_bytes() == before):
        held("the install's gate judges the target", "a package wearing `hello` refuses at the "
             "roots+template form the fresh install plays -- the pins and the catalog untouched")
    else:
        failures.append("  ✗ install gate                 the refusal moved the instance")


def _package(env, name: str, text: str) -> Path:
    """The same document, written INSIDE the vendored kit -- a package's, by the only
    thing that makes one: a manifest above it."""
    vendor = next((env.made / instance.VENDOR).glob("kit@*"))
    path = vendor / "procs" / f"{name}.md"
    path.write_text(text.format(name=name), encoding="utf-8")
    return path


def _clear(env, *relpaths: str) -> None:
    for relpath in relpaths:
        (env.made / relpath).unlink(missing_ok=True)
    for stray in (env.made / instance.VENDOR).glob("kit@*/procs/Z*.md"):
        stray.unlink()


def author_laws(bench) -> None:
    """A law the AUTHOR wrote never blocks the build; the same defect in a package refuses.
    A house of its own: a member written, the build played through the console."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("author-lint")
    meta = env.made
    env.write_member()

    # --- the discriminant: who owns a document ---------------------------------------------
    vendored = next((meta / instance.VENDOR).glob("kit@*"))
    if compiling.authored(meta, "procs/MEMBER.md") and not compiling.authored(
            meta, str((vendored / "procs" / "TURN.md").relative_to(meta))):
        held("the discriminant judges", "procs/MEMBER.md is the author's, the vendored "
             "TURN.md is the base's")
    else:
        failures.append("  ✗ the discriminant judges       author/package told apart")

    # --- a double the AUTHOR holds: a warning, and the build passes -------------------------
    env.write("ONE.md", DOUBLED.format(name="ONE"))
    env.write("TWO.md", DOUBLED.format(name="TWO"))
    built = env.cli("-build")
    warned = [one for one in compiling.lint(meta) if one.startswith("constraint-doubled")]
    registry = compiling.render_registry(meta)   # derived on demand, no file
    written = any((meta / instance.SYS / name).is_file() for name in ("constraints.md", "_constraints.md"))
    if built.returncode == 0 and warned and "WARNING" in built.stdout and registry.count("`Z9`") == 1 and not written:
        held("the author's double warns", f"-build rc=0, `{warned[0][:52]}…`, Z9 once in "
             "the derived table -- and no registry file on disk")
    else:
        failures.append(f"  ✗ the author's double warns    rc={built.returncode} {warned}")
    _clear(env, "ONE.md", "TWO.md")

    # --- the same double between two PACKAGES: the refusal --------------------------------
    _package(env, "ZONE", DOUBLED)
    _package(env, "ZTWO", DOUBLED)
    expect("constraint-doubled", lambda: compiling.render_registry(meta))
    _clear(env)

    # --- a malformed law line: the author's document plays WITHOUT it ----------------------
    env.write("THREE.md", MALFORMED.format(name="THREE"))
    warned = [one for one in compiling.lint(meta) if one.startswith("constraint-malformed")]
    kept = compiling.declarations(meta)
    if warned and "`nocode`" in warned[0] and "Z7" in kept:
        held("the malformed line is dropped", "the warning names it, Z7 still declared")
    else:
        failures.append(f"  ✗ the malformed line is dropped {warned} {'Z7' in kept}")
    _clear(env, "THREE.md")

    # --- the same line in a package's document: the refusal --------------------------------
    _package(env, "ZTHREE", MALFORMED)
    expect("constraint-malformed", lambda: compiling.render_registry(meta))
    _clear(env)

    # --- an attach no proc hooks: warned for the author, refused for a package -------------
    env.write("FOUR.md", ATTACHED.format(name="FOUR"))
    warned = [one for one in compiling.lint(meta) if one.startswith("attach-unhooked")]
    passes = compiling.render_registry(meta)
    _clear(env, "FOUR.md")
    _package(env, "ZFOUR", ATTACHED)
    expect("attach-unhooked", lambda: compiling.render_registry(meta))
    _clear(env)
    if warned and passes:
        held("the author's attach warns", f"`{warned[0][:48]}…`, the registry renders")
    else:
        failures.append(f"  ✗ the author's attach warns    {warned}")

    # --- the migration gate is not a law defect: it refuses on both sides ------------------
    env.write("FIVE.md", UNSECTIONED.format(name="FIVE"))
    expect("constraints-unsectioned", lambda: compiling.render_registry(meta))
    _clear(env, "FIVE.md")


def scenario(bench) -> int:
    # topology and naming read one house: the reference composition, built -- each forges its
    # packages on it and leaves it as it found it (`the reference composition holds`)
    made = bench.env("composition").made
    before = compiling.build_tools(made).read_bytes()
    topology_refusals(bench, made, before)
    naming_refusals(bench, made, before)
    author_laws(bench)
    return 0
