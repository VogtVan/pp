"""Scenario `composition-lint` -- what the build lint refuses in a composition, and what it
only warns:
- the topology: an unknown target refuses `reference-unknown`, a serve token is judged on its
  closure alone; `boot.ready` resolves nowhere; the words the language dropped refuse by name: a
  proc writing the dropped keyword (`final-gone`), a document declaring the session cycle
  (`cycle-gone`); the instance is the top: its documents reference every pin and offer what their
  harness carries; nothing written under a refusal, the reference composition builds as before
  (what a package may name, its sockets and its `optional:` are the patterns
  `packaging/manifest` and `packaging/sockets`; `attach-and-mount`, `socket-reserved` are
  `composition/mount`'s and `composition/initialize`'s)
- the names a package exposes (KPS31): a skill is `pp-<package>[-<name>]`; a vector family is
  `<package>[-<family>]:`, another package's family JOINED under its prefix, that package
  required; a payload token is `<package>-<token>`, another's provided or consumed under ITS
  prefix; a proc or a ref carried as a BASE by two packages refuses `name-ambiguous`, an
  overlay by the source name passes; nothing written under a refusal; the bus's record follows
  the families at upgrade (`migrate_families`); the install's gate judges a TARGET composition
  before anything is written; a console verb's name is the pattern `automation/commands`'s
- the author's documents: the discriminant tells them from a package's; the engine's copy is
  never swept, nor the operator's working folders (a plan's matter): a `tools:` there declares nothing (the author's law defects are the pattern `rules/laws`'s, an attach no proc hooks
  `composition/hook`'s and `packaging/sockets`')
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from conductor import compiling, instance, topology
from conductor.core import language
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
    # --- the old boot socket is gone --------------------------------------------------------
    expect("reference-unknown", lies("kit", procs__W_OLD=proc("W_OLD", front="attach: boot.ready\n")))
    # --- the words the language dropped: refused by name, nothing written ---------------------
    dropped = next(iter(language.RETIRED))                  # the word itself never written here
    expect("final-gone", lies("kit", procs__W_FIN=proc("W_FIN", f"  INFER\n  {dropped}\n")))
    expect("cycle-gone", lies("kit", procs__W_CYC=proc("W_CYC", front=f"cycle: {str(True).lower()}\n")))
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
             front="tools: |\n  TURN\n  my-harness-skill\nattach: boot.initialize\noutput: table\n"), encoding="utf-8")
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
    """The public names of a package: skills, families, tokens, bases."""
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


def _clear(env, *relpaths: str) -> None:
    for relpath in relpaths:
        (env.made / relpath).unlink(missing_ok=True)
    for stray in (env.made / instance.VENDOR).glob("kit@*/procs/Z*.md"):
        stray.unlink()


def author_laws(bench) -> None:
    """A law the AUTHOR wrote never blocks the build; the same defect in a package refuses.
    A house of its own: a member written, the build played through the console."""
    held, failures = bench.held, bench.failures
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

    # --- the engine's copy is the machine's, never a document of the composition ----------
    demos = meta / instance.SYS / "engine" / "patterns" / "demo"
    demos.mkdir(parents=True, exist_ok=True)
    (demos / "GATE.md").write_text(DOUBLED.format(name="GATE").replace("Z9", "Z5"), encoding="utf-8")
    (demos / "BROKEN.md").write_text("---\nname: BROKEN\nkind: proc\nproc: [\n---\n\nx\n", encoding="utf-8")
    env.write("SIX.md", DOUBLED.format(name="SIX").replace("Z9", "Z5"))
    try:
        compiling.build_tools(meta)
        warned = [one for one in compiling.lint(meta) if "Z5" in one or "BROKEN" in one]
        holders = [holder for holder, _, _ in compiling.declarations(meta).get("Z5", [])]
        swept = None
    except Exception as error:                                            # noqa: BLE001
        warned, holders, swept = [], [], error
    shutil.rmtree(demos)
    _clear(env, "SIX.md")
    if swept is None and not warned and holders and all("SIX" in one for one in holders):
        held("the engine's copy is never swept", "a demonstration proc under .sys/engine/ with the "
             "author's own code Z5, and one whose front matter breaks: the build passes, Z5 is the "
             "author's alone, nothing warned")
    else:
        failures.append(f"  ✗ engine copy swept            error={swept!r} warned={warned} holders={holders}")

    # --- the operator's working folders are not the composition ----------------------------
    env.write("plans/x/overlays/TURN.md", "---\nname: TURN\ntools: |\n  +GHOST\n---\n\na copy\n")
    env.write("plans/x/NODE.md", DOUBLED.format(name="NODE").replace("Z9", "Z4"))
    env.write("FOUR.md", DOUBLED.format(name="FOUR").replace("Z9", "Z4"))
    try:
        catalog = compiling.build_tools(meta).read_text(encoding="utf-8")
        four = [holder for holder, _, _ in compiling.declarations(meta).get("Z4", [])]
        error = None
    except Exception as wrong:                                            # noqa: BLE001
        catalog, four, error = "", [], wrong
    shutil.rmtree(meta / "plans")
    _clear(env, "FOUR.md")
    if error is None and "GHOST" not in catalog and four and all("FOUR" in one for one in four):
        held("a working folder is never swept", "a copy under plans/ offering `+GHOST` and a node "
             "declaring the author's Z4: the catalog names no GHOST, Z4 is the author's alone")
    else:
        failures.append(f"  ✗ working folder swept         error={error!r} ghost={'GHOST' in catalog} holders={four}")


def scenario(bench) -> int:
    # topology and naming read one house: the reference composition, built -- each forges its
    # packages on it and leaves it as it found it (`the reference composition holds`)
    made = bench.env("composition").made
    before = compiling.build_tools(made).read_bytes()
    topology_refusals(bench, made, before)
    naming_refusals(bench, made, before)
    author_laws(bench)
    return 0
