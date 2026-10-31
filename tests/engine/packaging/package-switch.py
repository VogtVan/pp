"""Scenario `package-switch` -- 4 case(s) (plan pp-split, batch l-interrupteur-de-package;
plan core, batch le-catalogue-de-ce-qui-joue):
- the switch acts at ONE point: documents, search paths, the catalog's entries and the contributions follow without a test of their own
- the whole composition still reads for what installs: the settings fragments and the unswitched read keep every pin
- the run's own switches filter the same way, and an empty set plays every pin
- a name NOBODY owns stays the harness's: listed bare, offered name-only, whatever the switch says; the registry keeps reading the WHOLE composition (a code doubled by a switched package still warns)
What the operator writes and gets of a switch -- the dependents leaving, off is not gone, the seeded
key, the sync, the catalog without the package and back, `-disable` / `-enable` -- is the pattern
`packaging/package-switch`'s; a moved switch recompiling the marble and the catalog at the next
boot, `packaging/system-fragment`'s.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from conductor import compiling, contributions, install, instance, reading, settings

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.initialize, turn.begin, turn.end]\n")
ALPHA = "name: alpha\nversion: 0.0.1\ndescription: needs the kit\nrequires: [kit]\n"
BETA = ("name: beta\nversion: 0.0.1\ndescription: needs alpha\nrequires: [alpha]\ncontributes:\n"
        "  sockets: [beta.ready]\n")
PROC = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n  INFER\n---\n\nSay one word.\n"
FRAGMENT = ("---\nname: SETTINGS\nkind: fragment\npackage: alpha\ndescription: alpha keys\n"
            "alpha_care: asked\ntypes: |\n  alpha_care  free\n---\n")


def _source(product: Path, kit_version: str) -> Path:
    """The bench's source REDUCED to manifests: the base whole (the stand-in), two witness
    packages -- `alpha` (a proc and a settings fragment) and `beta` (a proc and a socket,
    requires alpha)."""
    root = Path(tempfile.mkdtemp()) / "product"
    for part in ("engine", "bases", "template"):
        shutil.copytree(product / part, root / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    (root / "bases" / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
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
    return root


def _witness(bench, kit_version: str) -> Path:
    """-> a throwaway instance composing kit + alpha + beta from the witness source."""
    return install.install(_source(bench.source(), kit_version) / "engine" / "pp.py",
                           Path(tempfile.mkdtemp()) / ".pp", ["beta"])


def _names(roots) -> list[str]:
    return [root.name.split("@")[0] for root in roots]


def _switch(made: Path, lines: str) -> None:
    path = made / "SETTINGS.md"
    head, rest = path.read_text(encoding="utf-8").split("\n---", 1)
    path.write_text(head.rstrip("\n") + "\n" + lines + "\n---" + rest, encoding="utf-8")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    kit_version = instance.pins(bench.env("switch-kit").made)["kit"]
    made = _witness(bench, kit_version)
    docs_before = {name for name, *_ in instance.documents(made)}
    entries_before = {str(entry[0]) for entry in compiling.entries(made)}
    kinds_before = {(one["package"], one["kind"]) for one in contributions.composed(made)}

    _switch(made, "package.alpha: off")

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
    if ("- `nobody-home`\n" in lit and "owned by nothing pp composes" in lit
            and lit_offer == [("pp-alpha", "the alpha skill", "pp-alpha/SKILL.md"),
                              ("nobody-home", "", "")]):
        held("a name nobody owns stays the harness's", "alpha on: `nobody-home` alone under the "
             "harness section -- said as unread; the offer carries alpha's contract and the bare name")
    else:
        failures.append(f"  ✗ catalog lit                 offer={lit_offer} "
                        f"said={'owned by nothing' in lit}")

    _switch(made5, "package.alpha: off")
    dark, dark_offer, dark_lint = compiling.render_tools(made5), offered(), compiling.lint(made5)
    if ("- `nobody-home`\n" in dark and dark_offer == [("nobody-home", "", "")]
            and any(one.startswith("constraint-doubled: `RGX`") for one in dark_lint)):
        held("the bare name survives the switch", "alpha off: the offer keeps `nobody-home` alone; "
             "the registry still sees alpha's doubled RGX")
    else:
        failures.append(f"  ✗ catalog dark                offer={dark_offer} "
                        f"doubled={[one for one in dark_lint if 'RGX' in one]}")
    return 0
