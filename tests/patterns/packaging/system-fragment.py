"""Scenario `system-fragment` -- the pattern `packaging/system-fragment`, played from its demonstration:
- a package's `system/SYSTEM.COMMON.md` and `SYSTEM.CONDUCT.md` compile into two marbles, one per
  mode, each with its receipt: every CONDUCT line in `system.md` alone; section by section, the
  engine (its card last), the base, then the packages in the requires topology
- the two names alone: an empty file and another name under `system/` leave both marbles byte
  for byte
- each run is served its mode's marble: a run its principal conducts `system.common.md`, at its
  opening and after `-compacted`; a run the LLM conducts `system.md`
- the instance's `SYSTEM_PROMPT.md`: without `override: true` it has no effect and the lint says
  so; granted, its body leads both replace marbles; revoked, they retract
- a package switched off leaves the marble and the catalog at the next boot, the receipts naming
  the switch; a second boot moves nothing
"""
from __future__ import annotations

from conductor import Conductor, compiling, install
from tests.harness import PATTERNS, body_of, pin_step, principal, support

DRAWER, PATTERN = "packaging", "system-fragment"
HOME = PATTERNS / DRAWER / PATTERN
OWED = {"manifests": ["crier.yaml", "herald.yaml", "hush.yaml"],
        "systems": ["crier.common.md", "herald.common.md", "herald.conduct.md", "hush.conduct.md",
                    "hush.notes.md"],
        "procs": ["HERALD.md"],
        "prompts": ["closed.md", "granted.md", "prose.md"]}
LLM, COMMON = "system.md", "system.common.md"
REPLACES = ("system.replace.md", "system.common.replace.md")
packaging = support(__file__, "source")


def _laid() -> dict:
    return {folder: sorted(path.name for path in (HOME / folder).glob("*")) for folder in OWED}


def _head(path) -> str:
    return body_of(path)[:60]


def _sentences(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if len(line.strip()) >= 20]


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
    """Two marbles, two receipts; the CONDUCT lines; the sections in order."""
    held, failures = bench.held, bench.failures
    sys_dir = made / ".sys"
    receipts, inputs = compiling.receipts(made), compiling.receipt_inputs(made)
    if not ((sys_dir / LLM).is_file() and (sys_dir / COMMON).is_file()
            and all((receipts.get(name) or {}).get("inputs") == inputs for name in (LLM, COMMON))):
        failures.append(f"  ✗ two marbles                  {sorted(receipts)}")
        return
    held("two marbles, two receipts", "system.md and system.common.md compiled at the install, "
         "each with its receipt on the same inputs")
    llm = (sys_dir / LLM).read_text(encoding="utf-8")
    common = (sys_dir / COMMON).read_text(encoding="utf-8")

    sections = [sys_dir / "engine" / "system"] + [root / "system" for root in
                                                  sorted((sys_dir / "vendor").glob("*@*"))]
    lines = [one for section in sections if (section / "SYSTEM.CONDUCT.md").is_file()
             for one in _sentences(body_of(section / "SYSTEM.CONDUCT.md"))]
    absent = [one for one in lines if one not in llm]
    leaked = [one for one in lines if one in common]
    if lines and not absent and not leaked:
        held("every CONDUCT line in system.md alone", f"{len(lines)} lines of the SYSTEM.CONDUCT.md "
             "files, the engine's and herald's: all in system.md, none in system.common.md")
    else:
        failures.append(f"  ✗ the CONDUCT lines            absent={absent[:2]!r} leaked={leaked[:2]!r}")

    engine = sys_dir / "engine"
    kit = next((sys_dir / "vendor").glob("kit@*"))
    e_common, e_conduct = _head(engine / "system" / "SYSTEM.COMMON.md"), _head(engine / "system" / "SYSTEM.CONDUCT.md")
    card, base = _head(engine / "refs" / "PP.md"), _head(kit / "system" / "SYSTEM.COMMON.md")
    h_common, h_conduct = _head(HOME / "systems" / "herald.common.md"), _head(HOME / "systems" / "herald.conduct.md")
    c_common = _head(HOME / "systems" / "crier.common.md")
    order = [llm.find(one) for one in (e_common, e_conduct, card, base, h_common, h_conduct, c_common)]
    order_common = [common.find(one) for one in (e_common, card, base, h_common, c_common)]
    if (-1 not in order and order == sorted(order) and -1 not in order_common
            and order_common == sorted(order_common)
            and e_conduct not in common and h_conduct not in common):
        held("the sections in order", "system.md: the engine's COMMON, CONDUCT and card, the base's "
             "COMMON, herald's COMMON and CONDUCT, then crier's, which requires herald; "
             "system.common.md the same without a CONDUCT")
    else:
        failures.append(f"  ✗ the order                    {order} / {order_common}")


def names(bench, made, member) -> None:
    """The two names alone: hush's empty CONDUCT and its other file add nothing."""
    held, failures = bench.held, bench.failures
    sys_dir = made / ".sys"
    before = {name: (sys_dir / name).read_bytes() for name in (LLM, COMMON)}
    install.add_package(member, "hush")
    after = {name: (sys_dir / name).read_bytes() for name in (LLM, COMMON)}
    notes = _head(HOME / "systems" / "hush.notes.md")
    hushed = next((sys_dir / "vendor").glob("hush@*")) / "system"
    if (after == before and notes.encode("utf-8") not in after[LLM]
            and sorted(path.name for path in hushed.iterdir()) == ["SYSTEM.CONDUCT.md", "SYSTEM.NOTES.md"]):
        held("the two names alone", "hush added: an empty SYSTEM.CONDUCT.md and a SYSTEM.NOTES.md "
             "leave both marbles byte for byte")
    else:
        failures.append(f"  ✗ the names read               {[after[n] == before[n] for n in before]}")


def served(bench, made, member) -> None:
    """Each run its mode's marble, at the opening and after -compacted."""
    held, failures = bench.held, bench.failures
    engine = made / ".sys" / "engine" / "pp.py"
    pin_step(made)                  # the bench rule: the boot's own block carries the orders

    def opened():
        Conductor(member, engine).forget()
        conductor = Conductor(member, engine)
        return conductor, conductor.start(conductor.boot("BOOT.md"))

    led, led_block = principal(opened)
    led_compacted = Conductor(member, engine, led.run_id).compacted()
    plain, plain_block = opened()
    llm = (made / ".sys" / LLM).read_text(encoding="utf-8").strip()
    common = (made / ".sys" / COMMON).read_text(encoding="utf-8").strip()
    if (_standing(led_block) == common and _standing(led_compacted) == common
            and _standing(plain_block) == llm):
        held("each run its mode's marble", "a run its principal conducts is served system.common.md, "
             "at its opening and after -compacted; a run the LLM conducts system.md")
    else:
        failures.append(f"  ✗ the served marble            principal={_standing(led_block)[:40]!r} "
                        f"llm={_standing(plain_block)[:40]!r} compacted={_standing(led_compacted)[:40]!r} "
                        f"stack={plain_block and plain_block.stack!r}")
    Conductor(member, engine).forget()


def prompt(bench, made) -> None:
    """The instance's SYSTEM_PROMPT.md and its lock."""
    held, failures = bench.held, bench.failures
    sys_dir = made / ".sys"
    replaces = [sys_dir / name for name in REPLACES]
    standing = made / "SYSTEM_PROMPT.md"
    own, orders = _head(HOME / "prompts" / "granted.md"), _head(sys_dir / "engine" / "system" / "SYSTEM.COMMON.md")
    conduct = _head(sys_dir / "engine" / "system" / "SYSTEM.CONDUCT.md")

    def lay(name: str) -> bool:
        """-> whether the lint says the lock: the demonstration laid as the instance's file."""
        standing.write_text((HOME / "prompts" / name).read_text(encoding="utf-8"), encoding="utf-8")
        compiling.build_system(made)
        return any("override: true" in one for one in compiling.lint(made))

    warned_prose = lay("prose.md") and not any(one.exists() for one in replaces)
    warned_closed = lay("closed.md") and not any(one.exists() for one in replaces)
    quiet = not lay("granted.md")
    texts = [one.read_text(encoding="utf-8") if one.is_file() else "" for one in replaces]
    granted = (quiet and all(text.startswith(own) and orders in text and text.index(own) < text.index(orders)
                             for text in texts)
               and conduct in texts[0] and conduct not in texts[1])
    lay("closed.md")
    retracted = not any(one.exists() for one in replaces)
    standing.unlink()
    compiling.build_system(made)
    if warned_prose and warned_closed and granted and retracted:
        held("the replace lock holds", "prose or `override: false`: no effect, said by the lint; "
             "granted, its body leads both replace marbles; revoked, they retract")
    else:
        failures.append(f"  ✗ replace lock                 {warned_prose}/{warned_closed}/{granted}/{retracted}")


def switched(bench, made, member) -> None:
    """A package switched off leaves the marble and the catalog at the next boot."""
    held, failures = bench.held, bench.failures
    engine = made / ".sys" / "engine" / "pp.py"
    marble, tools = made / ".sys" / LLM, made / ".sys" / "tools.md"
    law = _head(HOME / "systems" / "herald.common.md")

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
            and receipt[LLM]["switches"] == "herald"
            and all(receipt[name]["switches"] == "herald" for name in compiling.CATALOGS)
            and first == second):
        held("a package switched off leaves the marble", "the marble held herald's section; the boot "
             "after `package.herald: off` recompiles it without it and the catalog without HERALD, the "
             "receipts say `switches: herald`; a second boot moves nothing")
    else:
        failures.append(f"  ✗ switched off                 law={before} receipt={receipt.get(LLM)} "
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
