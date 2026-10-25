"""Scenario `manifest` -- the pattern `packaging/manifest`, played from its demonstration:
- the closure: a package pulls what it requires, level by level, at the source's versions; a name
  the source carries nowhere refuses `package-unknown`, two packages requiring each other
  `package-cycle`, a key no reader knows `manifest-key-unknown`
- `add` pins the closure in one transaction and the homes read in the requires topology,
  dependencies first; an add whose closure carries a contribution kind the engine does not know
  refuses `contribution-kind-unknown` and writes nothing
- `remove` refuses a package another still requires (`package-required-by`) and lets the packages
  go one by one; a prerequisite dropped by hand refuses the reading (`package-required`) and the
  sync pins it back
- a package names only what it requires: a CALL, an `attach:`, an offer, an overlay or a serve row
  reaching the base from a package that requires nothing refuses `dependency-undeclared`; the same
  documents in a package that requires the base pass
- `optional:`: a contributor mounted at the socket of an optional package sleeps while that
  package is absent (`mount-dormant`) and plays once it is there; a socket the present package
  opens nowhere refuses; a package neither required nor optional refuses `dependency-undeclared`
"""
from __future__ import annotations

import re
import shutil

from conductor import compiling, install, instance, topology
from tests.harness import PATTERNS, demonstrated, demos, manifests, support, vendor

DRAWER, PATTERN = "packaging", "manifest"
DEMOS = ("LOST_STAMP.md", "PASS.md", "REACH_ATTACH.md", "REACH_CALL.md", "REACH_SERVE.md",
         "REACH_TOOL.md", "STAMP.md")
OVERLAYS = ("TURN.md",)
MANIFESTS = ("client.yaml", "crown.yaml", "heir.yaml", "loner.yaml", "needy.yaml", "opener.yaml",
             "ring.yaml", "rung.yaml", "stem.yaml", "stranger.yaml", "typo.yaml", "widget.yaml")
REACHES = ("REACH_ATTACH", "REACH_CALL", "REACH_SERVE", "REACH_TOOL")
packaging = support(__file__, "source")


def _doc(name: str) -> str:
    return (demos(DRAWER, PATTERN) / name).read_text(encoding="utf-8")


def _overlay(name: str) -> str:
    return (PATTERNS / DRAWER / PATTERN / "overlays" / name).read_text(encoding="utf-8")


def _overlays() -> list[str]:
    return sorted(path.name for path in (PATTERNS / DRAWER / PATTERN / "overlays").glob("*.md"))


def _snapshot(made) -> tuple:
    return ((made / instance.MANIFEST).read_bytes(),
            tuple(sorted(p.name for p in (made / instance.VENDOR).iterdir())))


def closure(bench, declared) -> None:
    """The closure, `add` and `remove`, the closed reading -- on an instance installed from a
    source carrying the demonstration's packages."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    root = packaging.source(bench, {name: {"manifest": declared[f"{name}.yaml"]}
                                    for name in ("crown", "stem", "ring", "rung", "widget", "needy", "typo")})
    made, member = packaging.installed(bench, root, "closed", [])
    kit = instance.pins(made)["kit"]
    pins = install.closure(root, ["kit", "crown"])
    if pins == {"kit": kit, "crown": "0.0.1", "stem": "0.0.2"} and list(pins)[:2] == ["kit", "crown"]:
        held("a package pulls what it requires", "crown requires stem requires kit: three pins, the "
             "requested first, then the pulled, at the source's versions")
    else:
        failures.append(f"  ✗ closure                      {pins}")
    expect("package-unknown", lambda: install.closure(root, ["kit", "nowhere"]))
    expect("package-cycle", lambda: install.closure(root, ["ring"]))
    expect("manifest-key-unknown", lambda: install.closure(root, ["kit", "typo"]))

    install.add_package(member, "crown")
    vendored = {p.name for p in (made / instance.VENDOR).iterdir()}
    homes = [one.name for one in instance.vendored(made)]
    if (instance.pins(made) == {"kit": kit, "crown": "0.0.1", "stem": "0.0.2"}
            and {"crown@0.0.1", "stem@0.0.2"} <= vendored):
        held("add pins the closure", "add crown pinned stem (required) and vendored both")
    else:
        failures.append(f"  ✗ add closure                  {instance.pins(made)} {vendored}")
    if homes == [f"kit@{kit}", "stem@0.0.2", "crown@0.0.1"]:
        held("the homes read in the requires topology", "kit, then stem, then crown")
    else:
        failures.append(f"  ✗ topology                     {homes}")

    before = _snapshot(made)
    expect("contribution-kind-unknown", lambda: install.add_package(member, "needy"))
    if _snapshot(made) == before:
        held("a refused add writes nothing", "needy pulls widget, whose `widgets:` no engine reads: "
             "the pins and the vendor byte for byte")
    else:
        failures.append("  ✗ add transaction              the refused add left a trace")

    expect("package-required-by", lambda: install.remove_package(member, "stem"))
    pinned = instance.read(made)
    dropped = pinned["packages"].pop("stem")
    instance.write(made, pinned)
    expect("package-required", lambda: instance.vendored(made))
    install.sync(member)
    if instance.pins(made).get("stem") == dropped and [one.name for one in instance.vendored(made)] == homes:
        held("the sync pins a dropped prerequisite back", "stem dropped by hand, the reading refused, "
             "the sync pinned it back with its bundle")
    else:
        failures.append(f"  ✗ repair closure               {instance.pins(made)}")
    install.remove_package(member, "crown")
    install.remove_package(member, "stem")
    if instance.pins(made) == {"kit": kit}:
        held("remove, one by one", "crown left, then stem once nothing required it")
    else:
        failures.append(f"  ✗ remove                       {instance.pins(made)}")


def references(bench, declared) -> None:
    """What a package names, judged against what it requires."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made = bench.env("reaching").made
    for name in REACHES:
        packaging.unpin(made, "loner")
        vendor(made, "loner", declared["loner.yaml"], {name: _doc(f"{name}.md")})
        expect("dependency-undeclared", lambda: compiling.build_tools(made))
    packaging.unpin(made, "loner")
    vendor(made, "loner", declared["loner.yaml"], {}, overlays={"TURN": _overlay("TURN.md")})
    expect("dependency-undeclared", lambda: compiling.build_tools(made))
    packaging.unpin(made, "loner")
    vendor(made, "heir", declared["heir.yaml"], {name: _doc(f"{name}.md") for name in REACHES},
           overlays={"TURN": _overlay("TURN.md")})
    try:
        topology.validate(made)
        compiling.build_tools(made)
        held("a package that requires the base names it", "heir CALLs TURN, attaches at "
             "boot.initialize, offers TURN, overlays TURN and serves BOOT: built")
    except Exception as error:                                            # noqa: BLE001
        failures.append(f"  ✗ heir                         {error}")


def optional(bench, declared) -> None:
    """A package the client MAY use: dormant while absent, played once there."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("optional")
    made = env.made
    vendor(made, "client", declared["client.yaml"], {"STAMP": _doc("STAMP.md")})
    compiling.build_tools(made)
    dormant = [one for one in compiling.lint(made) if one.startswith("mount-dormant")]
    if dormant and "STAMP" in dormant[0] and "opener" in dormant[0]:
        held("an optional package absent: dormant", dormant[0][:110])
    else:
        failures.append(f"  ✗ optional absent              {dormant}")
    vendor(made, "opener", declared["opener.yaml"], {"PASS": _doc("PASS.md")})
    compiling.build_tools(made)
    dormant = [one for one in compiling.lint(made) if "dormant" in one]
    if not dormant and "STAMP.md" in instance.mounting(made, "opener.pass.begin"):
        held("an optional package present: played", "STAMP mounted at opener.pass.begin, nothing dormant")
    else:
        failures.append(f"  ✗ optional present             {dormant}")
    shutil.rmtree(made / ".sys" / "vendor" / "client@0.0.1")
    vendor(made, "client", declared["client.yaml"], {"LOST_STAMP": _doc("LOST_STAMP.md")})
    built = env.cli("-build")
    if built.returncode == 2 and re.search(r"reference-unknown|attach-unhooked", built.stderr):
        held("a socket the present package opens nowhere: refused", "opener.nowhere.begin")
    else:
        failures.append(f"  ✗ unknown socket               rc={built.returncode} {built.stderr.strip()[-160:]!r}")
    packaging.unpin(made, "client")
    vendor(made, "stranger", declared["stranger.yaml"], {"STAMP": _doc("STAMP.md")})
    expect("dependency-undeclared", lambda: compiling.build_tools(made))


def scenario(bench) -> int:
    failures = bench.failures
    found, declared = demonstrated(DRAWER, PATTERN), manifests(DRAWER, PATTERN)
    overlaid = _overlays() if (PATTERNS / DRAWER / PATTERN / "overlays").is_dir() else []
    if found != sorted(DEMOS) or sorted(declared) != sorted(MANIFESTS) or overlaid != sorted(OVERLAYS):
        failures.append(f"  ✗ the demonstration           {found!r} {sorted(declared)!r} {overlaid!r} -- "
                        f"owed {sorted(DEMOS)!r} {sorted(MANIFESTS)!r} {sorted(OVERLAYS)!r}")
        return 0
    closure(bench, declared)
    references(bench, declared)
    optional(bench, declared)
    return 0
