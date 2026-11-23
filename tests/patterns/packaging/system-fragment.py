"""Scenario `system-fragment` -- the pattern `packaging/system-fragment`, played from its demonstration:
- a package's `system/SYSTEM.md` compiles into the one marble, with its receipt; section by section,
  the engine (its card last), the base, then the packages in the requires topology
- the one name alone: an empty `SYSTEM.md` and another name under `system/` leave the marble byte
  for byte
- every run is served the marble, at its opening and after `-compacted`
- the instance's `SYSTEM_PROMPT.md`: without `override: true` it has no effect and the lint says
  so; granted, its body leads the replace marble; revoked, it retracts
- a package switched off leaves the marble and the catalog at the next boot, the receipts naming
  the switch; a second boot moves nothing
"""
from __future__ import annotations

from conductor import Conductor, compiling, install
from tests.harness import PATTERNS, body_of, pin_step, support

DRAWER, PATTERN = "packaging", "system-fragment"
HOME = PATTERNS / DRAWER / PATTERN
OWED = {"manifests": ["crier.yaml", "herald.yaml", "hush.yaml"],
        "systems": ["crier.md", "herald.md", "hush.md", "hush.notes.md"],
        "procs": ["HERALD.md"],
        "prompts": ["closed.md", "granted.md", "prose.md"]}
MARBLE = "system.md"
REPLACE = "system.replace.md"
packaging = support(__file__, "source")


def _laid() -> dict:
    return {folder: sorted(path.name for path in (HOME / folder).glob("*")) for folder in OWED}


def _head(path) -> str:
    return body_of(path)[:60]


def _standing(block) -> str:
    return next((text for title, text in (block.payloads if block else ())
                 if title == "standing orders"), "")


def _house(bench):
    """-> `(made, member)`: crier installed, herald pulled with it, hush at the source."""
    herald = packaging.parts(PATTERN, "herald")
    herald["procs"] = {"HERALD": (HOME / "procs" / "HERALD.md").read_text(encoding="utf-8")}
    root = packaging.source(bench, {"herald": herald, "crier": packaging.parts(PATTERN, "crier"),
                                    "hush": packaging.parts(PATTERN, "hush")})
    return packaging.installed(bench, root, "said", ["crier"])


def marbles(bench, made) -> None:
    """One marble, its receipt; the sections in order."""
    held, failures = bench.held, bench.failures
    sys_dir = made / ".sys"
    receipts, inputs = compiling.receipts(made), compiling.receipt_inputs(made)
    if not ((sys_dir / MARBLE).is_file() and (receipts.get(MARBLE) or {}).get("inputs") == inputs
            and not (sys_dir / "system.common.md").exists()):
        failures.append(f"  ✗ one marble                   {sorted(receipts)}")
        return
    held("one marble, one receipt", "system.md compiled at the install with its receipt, no other marble")
    marble = (sys_dir / MARBLE).read_text(encoding="utf-8")

    engine = sys_dir / "engine"
    kit = next((sys_dir / "vendor").glob("kit@*"))
    orders, card = _head(engine / "system" / "SYSTEM.md"), _head(engine / "refs" / "PP.md")
    base, herald, crier = (_head(kit / "system" / "SYSTEM.md"), _head(HOME / "systems" / "herald.md"),
                           _head(HOME / "systems" / "crier.md"))
    order = [marble.find(one) for one in (orders, card, base, herald, crier)]
    if -1 not in order and order == sorted(order):
        held("the sections in order", "system.md: the engine's orders and its card, the base's, herald's, "
             "then crier's, which requires herald")
    else:
        failures.append(f"  ✗ the order                    {order}")


def names(bench, made, member) -> None:
    """The one name alone: hush's empty SYSTEM.md and its other file add nothing."""
    held, failures = bench.held, bench.failures
    sys_dir = made / ".sys"
    before = (sys_dir / MARBLE).read_bytes()
    install.add_package(member, "hush")
    after = (sys_dir / MARBLE).read_bytes()
    notes = _head(HOME / "systems" / "hush.notes.md")
    hushed = next((sys_dir / "vendor").glob("hush@*")) / "system"
    if (after == before and notes.encode("utf-8") not in after
            and sorted(path.name for path in hushed.iterdir()) == ["SYSTEM.NOTES.md", "SYSTEM.md"]):
        held("the one name alone", "hush added: an empty SYSTEM.md and a SYSTEM.NOTES.md "
             "leave the marble byte for byte")
    else:
        failures.append(f"  ✗ the names read               {after == before} "
                        f"{sorted(path.name for path in hushed.iterdir())}")


def served(bench, made, member) -> None:
    """Every run the marble, at the opening and after -compacted."""
    held, failures = bench.held, bench.failures
    engine = made / ".sys" / "engine" / "pp.py"
    pin_step(made)                  # the bench rule: the boot's own block carries the orders
    Conductor(member, engine).forget()
    run = Conductor(member, engine)
    block = run.start(run.boot("BOOT.md"))
    compacted = Conductor(member, engine, run.run_id).compacted()
    marble = (made / ".sys" / MARBLE).read_text(encoding="utf-8").strip()
    if _standing(block) == marble and _standing(compacted) == marble:
        held("every run the marble", "a run is served system.md, at its opening and after -compacted")
    else:
        failures.append(f"  ✗ the served marble            opening={_standing(block)[:40]!r} "
                        f"compacted={_standing(compacted)[:40]!r} stack={block and block.stack!r}")
    Conductor(member, engine).forget()


def prompt(bench, made) -> None:
    """The instance's SYSTEM_PROMPT.md and its lock."""
    held, failures = bench.held, bench.failures
    sys_dir = made / ".sys"
    replaces = [sys_dir / REPLACE]
    standing = made / "SYSTEM_PROMPT.md"
    own, orders = _head(HOME / "prompts" / "granted.md"), _head(sys_dir / "engine" / "system" / "SYSTEM.md")

    def lay(name: str) -> bool:
        """-> whether the lint says the lock: the demonstration laid as the instance's file."""
        standing.write_text((HOME / "prompts" / name).read_text(encoding="utf-8"), encoding="utf-8")
        compiling.build_system(made)
        return any("override: true" in one for one in compiling.lint(made))

    warned_prose = lay("prose.md") and not any(one.exists() for one in replaces)
    warned_closed = lay("closed.md") and not any(one.exists() for one in replaces)
    quiet = not lay("granted.md")
    texts = [one.read_text(encoding="utf-8") if one.is_file() else "" for one in replaces]
    granted = quiet and all(text.startswith(own) and orders in text and text.index(own) < text.index(orders)
                            for text in texts)
    lay("closed.md")
    retracted = not any(one.exists() for one in replaces)
    standing.unlink()
    compiling.build_system(made)
    if warned_prose and warned_closed and granted and retracted:
        held("the replace lock holds", "prose or `override: false`: no effect, said by the lint; "
             "granted, its body leads the replace marble; revoked, it retracts")
    else:
        failures.append(f"  ✗ replace lock                 {warned_prose}/{warned_closed}/{granted}/{retracted}")


def switched(bench, made, member) -> None:
    """A package switched off leaves the marble and the catalog at the next boot."""
    held, failures = bench.held, bench.failures
    engine = made / ".sys" / "engine" / "pp.py"
    marble, tools = made / ".sys" / MARBLE, made / ".sys" / "tools.md"
    law = _head(HOME / "systems" / "herald.md")

    def boot() -> None:
        conductor = Conductor(member, engine, "t")
        conductor.start(conductor.boot("BOOT.md"))
        conductor.forget()

    before = law in marble.read_text(encoding="utf-8")
    settings = made / "SETTINGS.md"
    settings.write_text(settings.read_text(encoding="utf-8").replace("package.herald: on", "package.herald: off"),
                        encoding="utf-8")
    boot()
    receipt = compiling.receipts(made)
    first = (marble.read_bytes(), tools.read_bytes(), receipt)
    boot()
    second = (marble.read_bytes(), tools.read_bytes(), compiling.receipts(made))
    if (before and law not in marble.read_text(encoding="utf-8")
            and "HERALD" not in tools.read_text(encoding="utf-8")
            and receipt[MARBLE]["switches"] == "herald"
            and all(receipt[name]["switches"] == "herald" for name in compiling.CATALOGS)
            and first == second):
        held("a package switched off leaves the marble", "the marble held herald's section; the boot "
             "after `package.herald: off` recompiles it without it and the catalog without HERALD, the "
             "receipts say `switches: herald`; a second boot moves nothing")
    else:
        failures.append(f"  ✗ switched off                 law={before} receipt={receipt.get(MARBLE)} "
                        f"same={first == second}")


def scenario(bench) -> int:
    failures = bench.failures
    laid = _laid()
    if laid != OWED:
        failures.append(f"  ✗ the demonstration           {laid!r} -- owed {OWED!r}")
        return 0
    made, member = _house(bench)
    marbles(bench, made)
    names(bench, made, member)
    served(bench, made, member)
    prompt(bench, made)
    switched(bench, made, member)
    return 0
