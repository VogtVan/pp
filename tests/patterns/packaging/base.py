"""Scenario `base` -- the pattern `packaging/base`, played from its demonstration:
- an install that names a base composes on it: `base:` at the manifest, the vendor carries it and not
  the stand-in, its precision compiles after the engine's orders, and a run boots on its BOOT under
  both conductions; an install that names none writes no `base:`
- a base is never removed (`package-base`)
- a base without `procs/TURN.md` refuses `base-incomplete` before anything is written; a base
  without `system/` installs, its marble the engine's section alone
- a base's names are bare: its sockets are their own address -- a document of the instance mounted
  at `boot.initialize` reaches the boot -- and its settings keys carry no prefix
"""
from __future__ import annotations

from conductor import Conductor, install, instance, render
from conductor.state import settings as tuning
from tests.harness import PATTERNS, body_of, principal, reaches, support

DRAWER, PATTERN = "packaging", "base"
HOME = PATTERNS / DRAWER / PATTERN
OWED = {"manifests": ["lantern.yaml", "stub.yaml", "wick.yaml"],
        "procs": ["BOOT.md", "TURN.md"],
        "systems": ["lantern.common.md", "lantern.conduct.md"],
        "fragments": ["lantern.md"]}
GREETING = """---
name: HELLO
kind: doc
description: a document of the instance mounted at the base's boot socket
mount: boot.initialize
---
Hello from the instance, at the lantern's boot.
"""
packaging = support(__file__, "source")


def _laid() -> dict:
    return {folder: sorted(path.name for path in (HOME / folder).glob("*")) for folder in OWED}


def _procs(*names: str) -> dict[str, str]:
    return {name: (HOME / "procs" / f"{name}.md").read_text(encoding="utf-8") for name in names}


def _source(bench):
    """-> a source carrying lantern (whole), stub (no TURN) and wick (no `system/`)."""
    bases = {"lantern": packaging.parts(PATTERN, "lantern") | {"procs": _procs("BOOT", "TURN")},
             "stub": packaging.parts(PATTERN, "stub") | {"procs": _procs("BOOT")},
             "wick": packaging.parts(PATTERN, "wick") | {"procs": _procs("BOOT", "TURN")}}
    return packaging.source(bench, {}, bases=bases)


def _booted(made, member):
    engine = made / ".sys" / "engine" / "pp.py"
    Conductor(member, engine).forget()
    conductor = Conductor(member, engine)
    block = conductor.start(conductor.boot("BOOT.md"))
    conductor.forget()
    return block


def composed(bench, root) -> None:
    """The named base composes, boots under both conductions, stays, and keeps its names bare."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    made, member = packaging.installed(bench, root, "lit", [], base="lantern")
    (made / "procs" / "HELLO.md").write_text(GREETING, encoding="utf-8")
    declared = instance.read(made)
    vendored = [one.name for one in instance.vendored(made)]
    marble = (made / ".sys" / "system.md").read_text(encoding="utf-8")
    common = (made / ".sys" / "system.common.md").read_text(encoding="utf-8")
    orders = body_of(made / ".sys" / "engine" / "system" / "SYSTEM.COMMON.md")[:60]
    precision = body_of(HOME / "systems" / "lantern.common.md")[:60]
    conduct = body_of(HOME / "systems" / "lantern.conduct.md")[:60]
    llm, led = _booted(made, member), principal(lambda: _booted(made, member))
    if (declared.get("base") == "lantern" and instance.base_of(made) == "lantern"
            and vendored and all(one.startswith("lantern@") for one in vendored)
            and orders in marble and precision in marble and conduct in marble
            and marble.index(orders) < marble.index(precision) < marble.index(conduct)
            and precision in common and conduct not in common
            and llm is not None and led is not None and "TURN" in llm.stack and "TURN" in led.stack):
        held("the named base composes", "`base: lantern` at the manifest, the vendor carries lantern "
             "alone, its COMMON after the engine's orders and its CONDUCT after its COMMON, in the "
             "model's marble alone; a run boots on its BOOT under both conductions")
    else:
        failures.append(f"  ✗ named base                   {declared.get('base')!r} {vendored} "
                        f"precision={precision in marble} llm={llm and llm.stack!r} led={led and led.stack!r}")

    expect("package-base", lambda: install.remove_package(member, "lantern"))

    fragments = [one for one in tuning.fragments(made) if one.name == "lantern"]
    if (instance.mounting(made, "boot.initialize") == ("HELLO.md",) and llm is not None
            and reaches(render(llm), body_of(made / "procs" / "HELLO.md"))
            and fragments and ("glow", "warm") in fragments[0].defaults):
        held("the base's names are bare", "`boot.initialize` is the base's socket address: the "
             "instance's document mounted there reaches the boot; the base's key `glow` carries no prefix")
    else:
        failures.append(f"  ✗ bare names                   {instance.mounting(made, 'boot.initialize')} "
                        f"{fragments and fragments[0].defaults}")


def plain(bench, root) -> None:
    """No base named, no key written."""
    held, failures = bench.held, bench.failures
    made, _ = packaging.installed(bench, root, "plain", [])
    if "base" not in instance.read(made) and instance.base_of(made) != "lantern":
        held("no base named, no key written", "the manifest of an install that names no base carries "
             "no `base:`, the stand-in answers")
    else:
        failures.append(f"  ✗ plain manifest               {instance.read(made)}")


def incomplete(bench, root) -> None:
    """A base without TURN refuses before anything is written; one without system/ installs."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    target = bench.temp() / "stub" / ".pp"
    expect("base-incomplete", lambda: install.install(root / "engine" / "pp.py", target, [], base="stub"))
    if not target.exists():
        held("nothing written on base-incomplete", "stub carries no procs/TURN.md: refused before the "
             "instance's directory exists")
    else:
        failures.append(f"  ✗ base-incomplete wrote        {sorted(p.name for p in target.iterdir())}")

    made, _ = packaging.installed(bench, root, "wick", [], base="wick")
    engine = made / ".sys" / "engine"
    marble = made / ".sys" / "system.md"
    text = marble.read_text(encoding="utf-8") if marble.is_file() else ""
    orders, card = body_of(engine / "system" / "SYSTEM.COMMON.md")[:60], body_of(engine / "refs" / "PP.CONDUCT.md")
    if orders in text and text.rstrip().endswith(card[-60:]):
        held("a base without system/ installs", "wick gives no fragment: its marble is the engine's "
             "orders closed by its cards, nothing after")
    else:
        failures.append(f"  ✗ silent base                  {marble.is_file()} {text[-80:]!r}")


def scenario(bench) -> int:
    failures = bench.failures
    laid = _laid()
    if laid != OWED:
        failures.append(f"  ✗ the demonstration           {laid!r} -- owed {OWED!r}")
        return 0
    root = _source(bench)
    composed(bench, root)
    plain(bench, root)
    incomplete(bench, root)
    return 0
