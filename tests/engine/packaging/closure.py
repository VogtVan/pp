"""Scenario `closure` -- the pins CLOSED over requires (plan pp-split, batch
la-resolution-des-dependances):
- closure pulls the prerequisites at the source's versions; unknown and cycle refuse
- add pins the closure as ONE transaction; a refused add leaves the instance as it was
- vendored refuses a pin whose prerequisite is not pinned
- remove is the inverse: refused while required, the records stay, the keys ride unowned
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from conductor import discovery, install, instance
from tests.harness import PRODUCT_ENGINE

KIT = ("name: kit\nversion: {v}\ndescription: the base\nrequires: []\ncontributes:\n"
       "  sockets: [boot.ready, turn.begin, turn.end]\n")
X = "name: x\nversion: 0.0.1\ndescription: needs y\nrequires: [y]\n"
Y = "name: y\nversion: 0.0.2\ndescription: needs the kit\nrequires: [kit]\n"
Y_BAD = "name: y\nversion: 0.0.2\ndescription: a broken contract\nrequires: [kit]\ncontributes:\n  widgets: []\n"
LOOP_A = "name: a\nversion: 0.0.1\ndescription: loops\nrequires: [b]\n"
LOOP_B = "name: b\nversion: 0.0.1\ndescription: loops\nrequires: [a]\n"


def _source(kit_version: str, **packages: str) -> Path:
    """A product checkout REDUCED to manifests: the kit at the root, the rest under packages/."""
    root = Path(tempfile.mkdtemp()) / "product"
    shutil.copytree(PRODUCT_ENGINE.parent, root / "engine",     # a repair copies the engine
                    ignore=shutil.ignore_patterns("__pycache__"))   # too: the source carries one
    shutil.copytree(PRODUCT_ENGINE.parent.parent / "kit", root / "kit",   # the kit whole: the
                    ignore=shutil.ignore_patterns("__pycache__"))      # instance's documents
    shutil.copytree(PRODUCT_ENGINE.parent.parent / "template", root / "template",
                    ignore=shutil.ignore_patterns("__pycache__"))   # MEMBER seeds from it
    (root / "kit" / "package.yaml").write_text(KIT.format(v=kit_version), encoding="utf-8")
    # CALL its procs, and the topology lint judges the target composition whole --
    # a kit reduced to its manifest would make every CALL of the instance unknown
    for name, text in packages.items():
        (root / "packages" / name).mkdir(parents=True)
        (root / "packages" / name / "package.yaml").write_text(text, encoding="utf-8")
    return root


def _snapshot(meta: Path) -> tuple[bytes, tuple[str, ...]]:
    return ((meta / instance.MANIFEST).read_bytes(),
            tuple(sorted(p.name for p in (meta / instance.VENDOR).iterdir())))


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("closed")
    meta, member = env.made, env.member
    kit_version = instance.pins(meta)["kit"]

    # --- the closure: two levels pulled, the requested first, the source's versions ----
    source = _source(kit_version, x=X, y=Y)
    pins = install.closure(source, ["kit", "x"])
    if pins == {"kit": kit_version, "x": "0.0.1", "y": "0.0.2"} and list(pins)[:2] == ["kit", "x"]:
        held("closure pulls the prerequisites", "x requires y requires kit: three pins, the "
             "requested first, then the pulled, at the source's versions")
    else:
        failures.append(f"  ✗ closure                      {pins}")
    expect("package-unknown", lambda: install.closure(source, ["kit", "nowhere"]))
    expect("package-cycle", lambda: install.closure(_source(kit_version, a=LOOP_A, b=LOOP_B), ["a"]))

    # --- add as a transaction: the prerequisite rides in, said ---------------------------
    declared = instance.read(meta)
    declared["source"] = str(source)
    instance.write(meta, declared)
    made = install.add_package(member, "x")
    after = instance.pins(meta)
    vendor = {p.name for p in (meta / instance.VENDOR).iterdir()}
    if (after == {"kit": kit_version, "x": "0.0.1", "y": "0.0.2"} and made.is_dir()
            and {"x@0.0.1", "y@0.0.2"} <= vendor):
        held("add pins the closure", "add x pinned y (required) and materialized both")
    else:
        failures.append(f"  ✗ add closure                  {after} {vendor}")
    roots = [one.name for one in instance.vendored(meta)]
    if roots == [f"kit@{kit_version}", "y@0.0.2", "x@0.0.1"]:
        held("the requires topology holds", "kit, then y, then x")
    else:
        failures.append(f"  ✗ topology                     {roots}")

    # --- a refused add leaves the instance byte for byte ---------------------------------
    before = _snapshot(meta)
    broken = _source(kit_version, x=X, y=Y_BAD, z="name: z\nversion: 0.0.1\ndescription: needs w\nrequires: [w]\n",
                     w="name: w\nversion: 0.0.1\ndescription: a bad contract\nrequires: [kit]\ncontributes:\n  widgets: []\n")
    declared = instance.read(meta)
    declared["source"] = str(broken)
    instance.write(meta, declared)
    before = _snapshot(meta)
    expect("contribution-kind-unknown", lambda: install.add_package(member, "z"))
    if _snapshot(meta) == before:
        held("a refused add writes nothing", "instance.yaml and the vendor byte-identical "
             "after the refused transaction")
    else:
        failures.append("  ✗ add transaction              the refused add left a trace")

    # --- the closed reading: a pin whose prerequisite is gone refuses by name ------------
    declared = instance.read(meta)
    declared["source"] = str(source)
    instance.write(meta, declared)
    expect("package-required-by", lambda: install.remove_package(member, "y"))
    expect("package-base", lambda: install.remove_package(member, "kit"))
    expect("package-unpinned", lambda: install.remove_package(member, "nowhere"))
    # the hand edit that drops a prerequisite: the reading refuses, doctor repairs
    declared = instance.read(meta)
    dropped = declared["packages"].pop("y")
    instance.write(meta, declared)
    expect("package-required", lambda: instance.vendored(meta))
    told = install.sync(member)
    if instance.pins(meta).get("y") == dropped and [one.name for one in instance.vendored(meta)] == roots:
        held("a repair closes the pins", "sync pinned y back with its bundle")
    else:
        failures.append(f"  ✗ repair closure               {instance.pins(meta)}")

    # --- remove: the inverse, one by one, the records stay ------------------------------
    records = meta / instance.RECORDS
    records.mkdir(parents=True, exist_ok=True)
    (records / "x.jsonl").write_text('{"kept": true}\n', encoding="utf-8")
    told = install.remove_package(member, "x")
    vendor = {p.name for p in (meta / instance.VENDOR).iterdir()}
    if ("x" not in instance.pins(meta) and "x@0.0.1" not in vendor
            and (records / "x.jsonl").is_file() and any("removed" in line for line in told)):
        held("remove lets one package go", "unpinned, its bundle gone, its record kept")
    else:
        failures.append(f"  ✗ remove                       {instance.pins(meta)} {vendor} {told}")
    told = install.remove_package(member, "y")
    if instance.pins(meta) == {"kit": kit_version}:
        held("remove, one by one", "y left once nothing required it")
    else:
        failures.append(f"  ✗ remove y                     {instance.pins(meta)}")

    # --- the settings of a removed package ride as unowned, a later add finds them ------
    FRAG = "name: frag\nversion: 0.0.1\ndescription: carries keys\nrequires: [kit]\n"
    frag_root = _source("0.0.9", frag=FRAG)
    (frag_root / "packages" / "frag" / "settings").mkdir()
    (frag_root / "packages" / "frag" / "settings" / "SETTINGS.md").write_text(
        "---\nname: SETTINGS\nkind: fragment\npackage: frag\ndescription: frag keys\n"
        "frag_care: asked\ntypes: |\n  frag_care  free\n---\n", encoding="utf-8")
    frag_meta = install.install(frag_root / "engine" / "pp.py",
                                Path(tempfile.mkdtemp()) / ".pp", ["frag"])
    frag_member = discovery.instance_member(frag_meta / ".sys" / "engine" / "pp.py")
    frag_settings = frag_meta / "SETTINGS.md"
    text = frag_settings.read_text(encoding="utf-8").replace("frag_care: asked", "frag_care: total")
    frag_settings.write_text(text, encoding="utf-8")
    install.remove_package(frag_member, "frag")
    after_remove = frag_settings.read_text(encoding="utf-8")
    install.add_package(frag_member, "frag")
    after_add = frag_settings.read_text(encoding="utf-8")
    if ("# ---- unowned ----" in after_remove and "frag_care: total" in after_remove
            and "# ---- unowned ----" not in after_add and "frag_care: total" in after_add):
        held("the keys remain as unowned", "frag's key survives its removal under unowned, "
             "the operator's value intact; add brings it home")
    else:
        failures.append(f"  ✗ unowned keys                 {'unowned' in after_remove} {'total' in after_add}")
    return 0
