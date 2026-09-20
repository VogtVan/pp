"""Scenario `naming` -- the names a package exposes (plan pp-split, batch
le-lint-des-noms-publics, the naming law KPS31):
- a console verb wears the package's name (`<package>-<verb>`, or the name alone) or refuses `name-unprefixed`
- a skill is `pp-<package>` (or `pp-<package>-<name>`) or refuses
- a vector family is `<package>-<family>:` (or `<package>:`) or refuses; another package's family is JOINED under its prefix, and that package must be required
- a payload token is `<package>-<token>` or refuses; another package's token is provided into or consumed from under ITS prefix, that package required
- a proc or a ref carried as a BASE by two packages refuses `name-ambiguous`; an overlay by the source name passes
- nothing written under a refusal; the reference composition -- the kit alone -- builds as before
- the bus's record follows the families at upgrade: `migrate_families` rewrites a latched vector to the one registered family wearing its old name as tail, standing keys included, says it, replays silent, leaves the ambiguous and the orphan
- the INSTALL's own gate judges a TARGET composition before anything is written: a package that wears a bare verb refuses there too, pins and catalog untouched
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone

from conductor import compiling, instance, topology
from conductor.packaging import events
from tests.harness import SOURCE

MANIFEST = "name: {name}\nversion: 0.0.1\ndescription: a witness of the names\nrequires: [{requires}]\n{extra}"
PROC = "---\nname: {name}\nkind: proc\ndescription: a witness proc\n{front}proc: |\n  INFER\n---\n\nthe witness\n"
REF = "---\nname: {name}\nkind: doc\ndescription: a witness note\n---\n\na note\n"
SKILL = "---\nname: {name}\ndescription: a witness skill\n---\n\n{name}\n"
SCRIPT = "print('ok')\n"


def _pin(made, name: str, requires: str, extra: str = "", **files: str) -> None:
    """A package forged in the vendor space and pinned: its manifest, then its files
    (`procs__X` is `procs/X.md`, `skills__pp_x` a contract AND its script)."""
    root = made / ".sys" / "vendor" / f"{name}@0.0.1"
    for stale in ("procs", "overlays", "refs", "skills"):
        shutil.rmtree(root / stale, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)
    (root / "package.yaml").write_text(MANIFEST.format(name=name, requires=requires, extra=extra), encoding="utf-8")
    for key, text in files.items():
        space, _, stem = key.partition("__")
        if space == "skills":
            skill = stem.replace("_", "-")
            (root / "skills" / skill).mkdir(parents=True, exist_ok=True)
            (root / "skills" / skill / "SKILL.md").write_text(SKILL.format(name=skill), encoding="utf-8")
            (root / "skills" / skill / f"{skill}.py").write_text(SCRIPT, encoding="utf-8")
            continue
        path = root / space / f"{stem}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    pins = instance.read(made)
    pins["packages"][name] = "0.0.1"
    instance.write(made, pins)


def _unpin(made, name: str) -> None:
    pins = instance.read(made)
    pins["packages"].pop(name, None)
    instance.write(made, pins)
    shutil.rmtree(made / ".sys" / "vendor" / f"{name}@0.0.1", ignore_errors=True)


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("naming").made
    before = compiling.build_tools(made).read_bytes()   # the reference composition, built

    def passes(label: str, detail: str) -> None:
        try:
            topology.validate(made)
            held(label, detail)
        except Exception as error:                                        # noqa: BLE001
            failures.append(f"  ✗ {label:<30} {error}")

    def witness(extra: str = "", **files: str):
        _pin(made, "witness", "kit", extra, skills__pp_witness="", **files)
        return lambda: compiling.build_tools(made)

    def friend(requires: str, extra: str = "", **files: str):
        _pin(made, "friend", requires, extra, skills__pp_friend="", **files)
        return lambda: topology.validate(made)

    # --- a console verb wears the package's name -------------------------------------
    verb = "contributes:\n  commands:\n    - {{verb: {verb}, skill: pp-witness, args: [hello]}}\n"
    expect("name-unprefixed", witness(verb.format(verb="hello")))
    witness(verb.format(verb="witness-hello"))
    passes("a prefixed verb passes", "`witness-hello`")
    witness(verb.format(verb="witness"))
    passes("the package's name alone counts", "`witness` as the verb")

    # --- a skill is pp-<package> ------------------------------------------------------
    expect("name-unprefixed", witness(skills__pp_hello=""))
    witness(skills__pp_witness_more="")
    passes("pp-<package>-<name> passes", "`pp-witness-more` beside `pp-witness`")

    # --- a vector family wears the package's name, another's is joined under its prefix
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

    # --- a payload token wears the package's name, another's is named under its prefix
    provider = PROC.format(name="W_GIVE", front="provides: {token}\nwith: pp-witness serve\n")
    expect("name-unprefixed", witness(procs__W_GIVE=provider.format(token="stuff")))
    witness(procs__W_GIVE=provider.format(token="witness-stuff"))
    passes("a prefixed token passes", "`witness-stuff` provided by W_GIVE")
    taker = PROC.format(name="F_TAKE", front="payloads: {token}\n")
    expect("dependency-undeclared", friend("kit", procs__F_TAKE=taker.format(token="witness-stuff")))
    friend("kit, witness", procs__F_TAKE=taker.format(token="witness-stuff"))
    passes("a token consumed under its owner's prefix", "`friend` consumes `witness-stuff` and requires witness")
    giver = PROC.format(name="F_GIVE", front="provides: witness-stuff\nwith: pp-friend serve\n")
    friend("kit, witness", procs__F_GIVE=giver)
    passes("a token provided into another's", "`friend` provides `witness-stuff` with its own skill")
    expect("name-unprefixed", friend("kit, witness", procs__F_TAKE=taker.format(token="nobody-stuff")))
    _unpin(made, "friend")

    # --- a proc or a ref is ONE base across the packages ------------------------------
    witness(procs__W_ONE=PROC.format(name="W_ONE", front=""), refs__NOTE=REF.format(name="NOTE"))
    expect("name-ambiguous", friend("kit, witness", procs__W_ONE=PROC.format(name="W_ONE", front="")))
    friend("kit, witness", overlays__W_ONE="---\nname: W_ONE\n---\n\nan amendment\n")
    passes("an overlay by the source name passes", "`friend/overlays/W_ONE.md` amends witness's W_ONE")
    expect("name-ambiguous", friend("kit, witness", refs__NOTE=REF.format(name="NOTE")))
    _unpin(made, "friend")

    # --- nothing written under a refusal ---------------------------------------------
    if (made / ".sys" / "tools.md").read_bytes() == before:
        held("a refusal writes nothing", "tools.md byte-identical after every refused build")
    else:
        failures.append("  ✗ refusal wrote                tools.md changed under a refusal")

    # --- the bus's record follows the families at upgrade ------------------------------
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

    # --- the reference composition -- the kit alone -- builds as before ---------------
    _unpin(made, "witness")
    built = compiling.build_tools(made)
    if built.read_bytes() == before:
        held("the reference composition holds", "the kit judged whole, tools.md byte-identical")
    else:
        failures.append("  ✗ reference composition        tools.md moved")

    # --- the INSTALL's gate: a TARGET composition judged before anything is written ----
    # the four gates that MOVE a composition (install, add, upgrade, remove) judge it at
    # the source first, `roots` in hand: the names are judged there like every reference
    forged = bench.temp() / "forged" / "stray@0.0.1"
    (forged / "skills" / "pp-stray").mkdir(parents=True, exist_ok=True)
    (forged / "package.yaml").write_text(
        "name: stray\nversion: 0.0.1\ndescription: a package wearing a bare verb\n"
        "requires: [kit]\ncontributes:\n  commands:\n    - {verb: hello, skill: pp-stray}\n",
        encoding="utf-8")
    (forged / "skills" / "pp-stray" / "SKILL.md").write_text(
        "---\nname: pp-stray\ndescription: a witness skill\n---\n\npp-stray\n", encoding="utf-8")
    (forged / "skills" / "pp-stray" / "pp-stray.py").write_text(SCRIPT, encoding="utf-8")
    pinned = dict(instance.read(made)["packages"])
    target = [SOURCE / "kit", forged]
    expect("name-unprefixed", lambda: topology.validate(
        made, target, template=SOURCE / "template" / "instance"))
    if (dict(instance.read(made)["packages"]) == pinned
            and (made / instance.SYS / "tools.md").read_bytes() == before):
        held("the install's gate judges the target", "a package wearing `hello` refuses at the "
             "roots+template form the fresh install plays -- the pins and the catalog untouched")
    else:
        failures.append("  ✗ install gate                 the refusal moved the instance")
    return 0
