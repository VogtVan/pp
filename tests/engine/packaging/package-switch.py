"""Scenario `package-switch` -- 12 case(s) (plan pp-split, batch l-interrupteur-de-package;
plan core, batch le-catalogue-de-ce-qui-joue):
- a package switched off at SETTINGS leaves the composition, and every package requiring it leaves with it, its cause said
- the switch acts at ONE point: documents, search paths, the catalog's entries and the contributions follow without a test of their own
- the whole composition still reads for what installs: the settings fragments and the unswitched read keep every pin
- the base never switches off; a value other than on/off refuses
- the run's own switches filter the same way, and an empty set plays every pin
- off is not gone: the switched package's pin, bundle and settings section stand byte for byte
- the key is SEEDED: one `package.<name>: on` per pin beyond the base, under its own group, none for the base
- the sync follows the pins and keeps the operator's value: remove drops the key, add seeds it again, off stays off
- a moved switch recompiles the marble and the catalog at the next boot, without a refusal; replayed, nothing moves
- the catalog and the run's offer compile from what PLAYS: a switched package leaves no entry, no format and no offered name -- not even a bare one under the harness section
- a name NOBODY owns stays the harness's: listed bare, offered name-only, whatever the switch says
- `on` again renders the catalog byte for byte; the registry keeps reading the WHOLE composition (a code doubled by a switched package still warns)
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from conductor import Conductor, compiling, contributions, discovery, install, instance, reading, settings
from tests.harness import PRODUCT_ENGINE

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.ready, turn.begin, turn.end]\n")
ALPHA = "name: alpha\nversion: 0.0.1\ndescription: needs the kit\nrequires: [kit]\n"
BETA = ("name: beta\nversion: 0.0.1\ndescription: needs alpha\nrequires: [alpha]\ncontributes:\n"
        "  sockets: [beta.ready]\n")
PROC = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n  INFER\n---\n\nSay one word.\n"
FRAGMENT = ("---\nname: SETTINGS\nkind: fragment\npackage: alpha\ndescription: alpha keys\n"
            "alpha_care: asked\ntypes: |\n  alpha_care  free\n---\n")


def _source(kit_version: str) -> Path:
    """A product checkout REDUCED to manifests: the kit whole, two witness packages --
    `alpha` (a proc and a settings fragment) and `beta` (a proc and a socket, requires alpha)."""
    root = Path(tempfile.mkdtemp()) / "product"
    for part in ("engine", "kit", "template"):
        shutil.copytree(PRODUCT_ENGINE.parent.parent / part, root / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (root / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
    for name, manifest in (("alpha", ALPHA), ("beta", BETA)):
        home = root / "packages" / name
        (home / "procs").mkdir(parents=True)
        (home / "package.yaml").write_text(manifest, encoding="utf-8")
        (home / "procs" / f"{name.upper()}.md").write_text(PROC.format(name=name.upper()), encoding="utf-8")
    # alpha declares a format and a law, and carries a skill; beta offers alpha's skill
    (root / "packages" / "alpha" / "procs" / "ALPHA.md").write_text(
        "---\nname: ALPHA\nkind: proc\ndescription: a witness\nformats: |\n"
        "  alpha-form  stdin  the alpha form\nconstraints.behavior: |\n  RGX  a thing\n"
        "proc: |\n  INFER\n---\n\nSay one word.\n", encoding="utf-8")
    (root / "packages" / "beta" / "procs" / "BETA.md").write_text(
        "---\nname: BETA\nkind: proc\ndescription: a witness\ntools: |\n  pp-alpha\n"
        "proc: |\n  INFER\n---\n\nSay one word.\n", encoding="utf-8")
    skill = root / "packages" / "alpha" / "skills" / "pp-alpha"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: pp-alpha\ndescription: the alpha skill\n---\n\n"
                                    "say what you were given.\n", encoding="utf-8")
    (root / "packages" / "alpha" / "settings").mkdir()
    (root / "packages" / "alpha" / "settings" / "SETTINGS.md").write_text(FRAGMENT, encoding="utf-8")
    (root / "packages" / "alpha" / "system").mkdir()
    (root / "packages" / "alpha" / "system" / "ALPHA-LAW.md").write_text(
        "---\nname: ALPHA-LAW\nkind: doc\ndescription: alpha's standing rule\n---\nAlpha law stands.\n",
        encoding="utf-8")
    return root


def _witness(bench, kit_version: str) -> Path:
    """-> a throwaway instance composing kit + alpha + beta from the witness source."""
    return install.install(_source(kit_version) / "engine" / "pp.py",
                           Path(tempfile.mkdtemp()) / ".pp", ["beta"])


def _names(roots) -> list[str]:
    return [root.name.split("@")[0] for root in roots]


def _switch(made: Path, lines: str) -> None:
    path = made / "SETTINGS.md"
    head, rest = path.read_text(encoding="utf-8").split("\n---", 1)
    path.write_text(head.rstrip("\n") + "\n" + lines + "\n---" + rest, encoding="utf-8")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    kit_version = instance.pins(bench.env("switch-kit").made)["kit"]
    made = _witness(bench, kit_version)
    whole_before = _names(instance.vendored(made))
    docs_before = {name for name, *_ in instance.documents(made)}
    entries_before = {str(entry[0]) for entry in compiling.entries(made)}
    kinds_before = {(one["package"], one["kind"]) for one in contributions.composed(made)}

    # --- a hard switch, and the dependents with it ------------------------------------
    _switch(made, "package.alpha: off")
    off = instance.switched_off(made)
    played = _names(instance.vendored(made))
    if whole_before == ["kit", "alpha", "beta"] and played == ["kit"] \
            and off == {"alpha": "alpha", "beta": "alpha"}:
        held("a switched package leaves with its dependents",
             "kit + alpha + beta; `package.alpha: off` -> kit alone plays, "
             "alpha off by itself, beta off (<- alpha)")
    else:
        failures.append(f"  ✗ hard switch                 before={whole_before} after={played} off={off}")

    # --- one point: every reader of the composition follows ----------------------------
    docs_after = {name for name, *_ in instance.documents(made)}
    paths_after = [str(p) for p in instance.search_paths(made)]
    entries_after = {str(entry[0]) for entry in compiling.entries(made)}
    kinds_after = {(one["package"], one["kind"]) for one in contributions.composed(made)}
    if ({"ALPHA.md", "BETA.md"} <= docs_before and not ({"ALPHA.md", "BETA.md"} & docs_after)
            and not any("alpha@" in p or "beta@" in p for p in paths_after)
            and {"ALPHA", "BETA"} <= (entries_before - entries_after)
            and ("beta", "sockets") in kinds_before and ("beta", "sockets") not in kinds_after):
        held("the switch acts at one point",
             "the documents (ALPHA.md, BETA.md), the search paths, the catalog's entries and "
             "beta's socket follow vendored() -- no reader tests a switch of its own")
    else:
        failures.append(f"  ✗ one point                   docs={sorted(docs_after)} paths={paths_after} "
                        f"entries={sorted(entries_before - entries_after)} kinds={sorted(kinds_after)}")

    # --- the whole composition for what installs ---------------------------------------
    whole = _names(instance.vendored(made, switched=False))
    fragments = [one.name for one in settings.fragments(made)]
    if whole == ["kit", "alpha", "beta"] and "alpha" in fragments:
        held("the whole composition still reads", "switched=False keeps every pin; alpha's "
             "settings fragment composes -- its keys stay in their section")
    else:
        failures.append(f"  ✗ whole read                  whole={whole} fragments={fragments}")

    # --- the base never switches; a bad value refuses ----------------------------------
    _switch(made, "package.kit: off")
    expect("settings-invalid", lambda: instance.vendored(made))
    _switch(made, "package.beta: maybe")
    expect("settings-invalid", lambda: instance.switched_off(made))

    # --- the run's own switches ---------------------------------------------------------
    made2 = _witness(bench, kit_version)
    try:
        instance.play_off(made2, {"alpha"})
        soft = _names(instance.vendored(made2)), instance.switched_off(made2)
        instance.play_off(made2, ())
        back = _names(instance.vendored(made2))
    finally:
        instance.play_off(made2, ())
    if soft == (["kit"], {"alpha": "alpha", "beta": "alpha"}) and back == ["kit", "alpha", "beta"]:
        held("the run's switches filter the same way", "play_off(meta, {alpha}) -> kit alone, "
             "beta off (<- alpha); play_off(meta, ()) -> every pin plays again -- one entry per "
             "instance, the conductor sets it from the run's slot")
    else:
        failures.append(f"  ✗ soft switch                 {soft} back={back}")

    # --- off is not gone ---------------------------------------------------------------
    def stamp(meta: Path):
        return (instance.pins(meta), sorted(p.name for p in (meta / instance.VENDOR).iterdir()),
                (meta / "SETTINGS.md").read_text(encoding="utf-8"))
    before = stamp(made2)
    _switch(made2, "package.beta: off")
    after = stamp(made2)
    if (before[0] == after[0] and before[1] == after[1]
            and after[2].replace("package.beta: off\n", "") == before[2]
            and instance.switched_off(made2) == {"beta": "beta"}
            and _names(instance.vendored(made2)) == ["kit", "alpha"]):
        held("off is not gone", "the pins, the vendored bundles and the settings sections stand "
             "byte for byte; beta alone leaves the play, alpha stays")
    else:
        failures.append(f"  ✗ off is not gone             pins={after[0]} off={instance.switched_off(made2)}")

    # --- the key is seeded, one per pin beyond the base, under its own group ---------
    made3 = _witness(bench, kit_version)
    seeded = (made3 / "SETTINGS.md").read_text(encoding="utf-8")
    front = seeded.split("\n---", 1)[0]
    if ("# ---- packages ----" in front and "package.alpha: on" in front and "package.beta: on" in front
            and "package.kit" not in front and settings.of(made3).switches == ()
            and front.index("# ---- packages ----") < front.index("# ---- alpha ----")):
        held("the key is seeded", "`package.alpha: on` and `package.beta: on` under `# ---- packages ----`, "
             "before the packages' own sections; none for the base; settings.of() reads none off")
    else:
        failures.append(f"  ✗ seeded                      {front!r} {settings.of(made3).switches}")

    # --- the sync follows the pins and keeps the operator's value -----------------------
    member3 = discovery.instance_member(made3 / ".sys" / "engine" / "pp.py")
    text = (made3 / "SETTINGS.md").read_text(encoding="utf-8").replace("package.alpha: on", "package.alpha: off")
    (made3 / "SETTINGS.md").write_text(text, encoding="utf-8")
    install.remove_package(member3, "beta")
    removed = (made3 / "SETTINGS.md").read_text(encoding="utf-8").split("\n---", 1)[0]
    install.add_package(member3, "beta")
    added = (made3 / "SETTINGS.md").read_text(encoding="utf-8").split("\n---", 1)[0]
    if ("package.beta" not in removed and "package.alpha: off" in removed
            and "package.beta: on" in added and "package.alpha: off" in added
            and settings.of(made3).switches == ("alpha",)):
        held("the sync follows the pins", "remove drops `package.beta`, add seeds it `on` again, "
             "the operator's `package.alpha: off` travels untouched; settings.of() says alpha")
    else:
        failures.append(f"  ✗ sync                        removed={removed!r} added={added!r}")

    # --- a moved switch recompiles at the next boot, without a refusal ----------------
    made4 = _witness(bench, kit_version)
    member4 = discovery.instance_member(made4 / ".sys" / "engine" / "pp.py")
    engine4 = made4 / ".sys" / "engine" / "pp.py"

    def boot() -> None:
        conductor = Conductor(member4, discovery.siblings_around(member4), engine4, "t")
        conductor.start(conductor.boot("BOOT.md"))
        conductor.forget()

    marble = made4 / ".sys" / "system.md"
    before_law = "Alpha law stands." in marble.read_text(encoding="utf-8")
    text = (made4 / "SETTINGS.md").read_text(encoding="utf-8").replace("package.alpha: on", "package.alpha: off")
    (made4 / "SETTINGS.md").write_text(text, encoding="utf-8")
    boot()
    after_law = "Alpha law stands." in marble.read_text(encoding="utf-8")
    receipt = compiling.receipts(made4)
    first = (marble.read_bytes(), (made4 / ".sys" / "tools.md").read_bytes(), receipt)
    boot()
    second = (marble.read_bytes(), (made4 / ".sys" / "tools.md").read_bytes(), compiling.receipts(made4))
    catalog_names = "ALPHA" in (made4 / ".sys" / "tools.md").read_text(encoding="utf-8")
    if (before_law and not after_law and receipt["system.md"]["switches"] == "alpha"
            and receipt["tools.md"]["switches"] == "alpha" and first == second and not catalog_names):
        held("a moved switch recompiles at the boot", "the marble held alpha's law, the boot after "
             "`package.alpha: off` recompiles it without it and the catalog without ALPHA, the receipts "
             "say `switches: alpha`; a second boot moves nothing")
    else:
        failures.append(f"  ✗ receipts                    law={before_law}/{after_law} "
                        f"receipt={receipt.get('system.md')} same={first == second} catalog={catalog_names}")

    # --- the catalog and the offer compile from what PLAYS ------------------------------
    made5 = _witness(bench, kit_version)
    own = made5 / "procs" / "OWN.md"       # the instance offers alpha's skill and a name
    own.parent.mkdir(exist_ok=True)        # nobody owns, and doubles alpha's law
    own.write_text("---\nname: OWN\nkind: proc\ndescription: the instance's own\ntools: |\n"
                   "  pp-alpha\n  nobody-home\nconstraints.behavior: |\n  RGX  a thing\n"
                   "proc: |\n  INFER\n---\n\nsay it.\n", encoding="utf-8")

    def offered() -> list[tuple[str, str, str]]:
        return [(one.name, one.description, one.contract.split("/skills/")[-1])
                for one in compiling.tools_of(reading.read(own), made5)]

    lit, lit_offer = compiling.render_tools(made5), offered()
    if ("`pp-alpha`** — the alpha skill" in lit and "`alpha-form`** (stdin)" in lit
            and "- `pp-alpha`\n" not in lit and "- `nobody-home`\n" in lit
            and "owned by nothing pp composes" in lit
            and lit_offer == [("pp-alpha", "the alpha skill", "pp-alpha/SKILL.md"),
                              ("nobody-home", "", "")]):
        held("a name nobody owns stays the harness's", "alpha on: `pp-alpha` described, `alpha-form` "
             "enumerated, `nobody-home` alone under the harness section -- said as unread; the "
             "offer carries alpha's contract and the bare name")
    else:
        failures.append(f"  ✗ catalog lit                 offer={lit_offer} "
                        f"ghost={'- `pp-alpha`' in lit} said={'owned by nothing' in lit}")

    _switch(made5, "package.alpha: off")
    dark, dark_offer, dark_lint = compiling.render_tools(made5), offered(), compiling.lint(made5)
    if ("pp-alpha" not in dark and "alpha-form" not in dark and "- `nobody-home`\n" in dark
            and dark_offer == [("nobody-home", "", "")]
            and any(one.startswith("constraint-doubled: `RGX`") for one in dark_lint)):
        held("a switched package leaves no entry, format or name",
             "alpha off: no `pp-alpha` line, bare or described, no `alpha-form`; the offer drops "
             "it and keeps `nobody-home`; the registry still sees alpha's doubled RGX")
    else:
        failures.append(f"  ✗ catalog dark                offer={dark_offer} "
                        f"ghost={'pp-alpha' in dark} format={'alpha-form' in dark} "
                        f"doubled={[one for one in dark_lint if 'RGX' in one]}")

    text = (made5 / "SETTINGS.md").read_text(encoding="utf-8")
    (made5 / "SETTINGS.md").write_text(text.replace("package.alpha: off", "package.alpha: on"),
                                       encoding="utf-8")
    if compiling.render_tools(made5) == lit and offered() == lit_offer:
        held("on again renders byte for byte", "the catalog and the offer return as they were")
    else:
        failures.append("  ✗ catalog relit               the catalog or the offer moved after `on`")
    return 0
