"""Scenario `marble` -- the marble's mechanics that no author writes:
- one file per section: the marble compiles from `system/SYSTEM.md`, a `SYSTEM.COMMON.md` left
  beside it is not read
- the standing rules: `system.md` at install, byte-stable across builds, no replace artifact
  unasked; the standing-orders channel with and without `PP_MARBLE`
- the receipts: a stale receipt of the marble refuses `artifact-stale`; the doctor names the
  receipt and the card current, the card a harness receives being the engine's `refs/PP.md`
- the card: the marble carries it, closing the engine's section
- the system laws: the registry names each with its place; a `system/SYS.md` under a base refuses
  `sys-misplaced`, one that carries more than its laws `sys-shape`, a code held twice `law-twice`,
  nothing written
- card-drift is the engine's: an edited projection latches it at the boot though the base
  declares no check, and the verifier names the drifted card
What a package's `system/` and the instance's `SYSTEM_PROMPT.md` give -- the marble, its sections
and their order, the one name, a package switched off, the replace lock -- is the pattern
`packaging/system-fragment`'s; a base without `system/`, `packaging/base`'s.
"""
from __future__ import annotations

import os

import yaml

from conductor import Conductor, Refusal, compiling, discovery, install, persistence, render
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, kept_document, load_script, session_of, vendor

def _opened(env):
    env.conductor().forget()
    conductor = env.conductor()
    return conductor, conductor.start(conductor.boot("BOOT.md"))


def _engine_head() -> str:
    """-> the opening of the engine's standing orders, read at the source."""
    return body_of(kept_document(SOURCE / "engine", "SYSTEM"))[:60]


def standing(bench, env) -> None:
    """The standing rules compiled at install, byte-stable; the standing-orders channel."""
    held, failures = bench.held, bench.failures
    made = env.made
    system_art = made / ".sys" / "system.md"
    replaces = [made / ".sys" / "system.replace.md"]
    orders = _engine_head()
    first = system_art.read_bytes() if system_art.is_file() else b""
    compiling.build_system(made)
    compiled = first.decode("utf-8")
    if (system_art.is_file() and orders in compiled
            and system_art.read_bytes() == first
            and not (made / "SYSTEM_PROMPT.md").exists()
            and not any(one.exists() for one in replaces)):
        held("the marble compiles, append-only",
             "system.md at install, byte-stable across builds; SYSTEM_PROMPT.md never "
             "seeded, no replace artifact unasked")
    else:
        failures.append(f"  ✗ marble compile              {system_art.is_file()} {first[:60]!r}")

    marbled_engine = made / ".sys" / "engine" / "pp.py"
    marbled_member = discovery.instance_member(marbled_engine)

    def marbled_boot() -> str:
        one = Conductor(marbled_member, marbled_engine)
        block = one.start(one.boot("BOOT.md"))
        one.forget()
        return render(block) if block else ""

    served_boot = marbled_boot()
    os.environ["PP_MARBLE"] = "1"
    try:
        quiet_boot = marbled_boot()
    finally:
        del os.environ["PP_MARBLE"]
    if ("INFORMATION — standing orders" in served_boot
            and orders in served_boot
            and "INFORMATION — standing orders" not in quiet_boot and orders not in quiet_boot):
        held("the standing orders find their channel",
             "no PP_MARBLE: the boot serves them first; a wired marble declares itself "
             "and the boot stays quiet")
    else:
        failures.append(f"  ✗ standing orders channel     {('standing orders' in served_boot)}/"
                        f"{('INFORMATION — standing orders' in quiet_boot)}/{orders in quiet_boot}")


def cards(bench, env) -> None:
    """The card in the marble, after the engine's orders; no marble of another mode beside it."""
    held, failures = bench.held, bench.failures
    card = body_of(kept_document(SOURCE / "engine", "PP"))[:60]
    marble = (env.made / ".sys" / "system.md").read_text(encoding="utf-8")
    if (card in marble and marble.index(_engine_head()) < marble.index(card)
            and not (env.made / ".sys" / "system.common.md").exists()):
        held("the card", "system.md carries the card after the engine's orders; no other marble")
    else:
        failures.append(f"  ✗ the card                    in={card in marble} "
                        f"other={(env.made / '.sys' / 'system.common.md').exists()}")


def receipts(bench, env) -> None:
    """A stale receipt refuses; the doctor names the receipt and the card a harness receives."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    card_head = body_of(kept_document(SOURCE / "engine", "PP"))[:60]
    sys_dir = env.made / ".sys"

    # --- a stale receipt of the marble refuses -----------------------------------------------------
    path = sys_dir / compiling.RECEIPTS
    kept = path.read_text(encoding="utf-8")
    held_receipts = yaml.safe_load(kept)
    held_receipts[compiling.MARBLE]["inputs"] = "0" * 64
    path.write_text(yaml.safe_dump(held_receipts, sort_keys=True), encoding="utf-8")
    expect("artifact-stale", lambda: _opened(env))
    path.write_text(kept, encoding="utf-8")
    env.conductor().forget()

    # --- the doctor and the card a harness receives ---------------------------------------------
    ws = env.made.parent
    load_script(install.product_root(PRODUCT_ENGINE) / "adapters" / "claude" / "wire.py").wire(ws, env.made)
    card = (ws / ".claude" / "skills" / "pp" / "SKILL.md").read_text(encoding="utf-8")
    told = install.verify(env.member)
    booted, _ = _opened(env)
    latched = [one.get("signal") for one in persistence.signals_of(session_of(env.made))]
    booted.forget()
    if ("card-drift" not in latched and card_head in card and card == install.card(env.made)
            and any(one.startswith("receipt system.md: current") for one in told)
            and any(one.startswith("card .claude") and one.endswith("current") for one in told)):
        held("the doctor and the card", "the harness card is the engine's refs/PP.md; the verifier "
             "names the receipt and the card current, and the boot latches no card-drift on it")
    else:
        failures.append(f"  ✗ the doctor                  {told!r} latched={latched!r}")


def drift(bench, env) -> None:
    """card-drift is the engine's: pushed with no check declared by the base."""
    held, failures = bench.held, bench.failures
    made = env.made
    engine_root = made / ".sys" / "engine"
    kit_root = next((made / ".sys" / "vendor").glob("kit@*"))
    projected = made.parent / ".claude" / "skills" / "pp" / "SKILL.md"
    pristine = projected.read_text(encoding="utf-8") == install.card(made)
    manifest = (kit_root / "package.yaml").read_text(encoding="utf-8")
    projected.write_text(projected.read_text(encoding="utf-8") + "\nOLD LAW\n", encoding="utf-8")
    member = discovery.instance_member(engine_root / "pp.py")
    conductor = Conductor(member, engine_root / "pp.py", "t")
    conductor.start(conductor.boot("BOOT.md"))
    latched = persistence.signals_of(session_of(made))
    conductor.forget()
    verified = install.verify(member)
    if (pristine and "card-drift" not in manifest
            and any(one.get("signal") == "card-drift" and one.get("source") == "engine" for one in latched)
            and any("DRIFTED" in one for one in verified)):
        held("the card is the engine's, and so is its drift", "the projection is byte-identical to "
             "engine/refs/PP.md; edited, the boot pushes "
             "`card-drift` from the engine though the base declares no check, and the verifier "
             "names the drifted card")
    else:
        failures.append(f"  ✗ engine card-drift           pristine={pristine} "
                        f"manifest-clean={'card-drift' not in manifest} {latched!r}")


SOLE = "sole-system-marker"          # what a package's `system/SYSTEM.md` carries
LEFT = "left-common-marker"          # what a `system/SYSTEM.COMMON.md` left beside it carries


def single(bench) -> None:
    """A section's standing orders are ONE file, `system/SYSTEM.md`: the marble compiles from it,
    and a `SYSTEM.COMMON.md` left beside it is not read."""
    held, failures = bench.held, bench.failures
    env = bench.env("marble-single")
    vendor(env.made, "sole", "name: sole\nversion: 0.0.1\ndescription: a witness\nrequires: [kit]\n", {})
    system = env.made / ".sys" / "vendor" / "sole@0.0.1" / "system"
    system.mkdir(parents=True, exist_ok=True)
    (system / "SYSTEM.md").write_text(f"---\nname: SYSTEM\nkind: doc\n---\n\n{SOLE}\n", encoding="utf-8")
    (system / "SYSTEM.COMMON.md").write_text(f"---\nname: SYSTEM\nkind: doc\n---\n\n{LEFT}\n", encoding="utf-8")
    compiling.build_system(env.made)
    compiled = (env.made / ".sys" / "system.md").read_text(encoding="utf-8")
    if SOLE in compiled and LEFT not in compiled:
        held("one file per section", "the marble compiles from `system/SYSTEM.md`; a `SYSTEM.COMMON.md` "
             "left beside it is not read")
    else:
        failures.append(f"  ✗ one file per section        sole={SOLE in compiled} left={LEFT in compiled}")


def system_build(bench) -> None:
    """The build judges the system laws before it writes: a `system/SYS.md` under a base refuses
    `sys-misplaced`, a SYS.md that carries more than its laws `sys-shape`, a code a system law holds
    twice `law-twice` and named once when one SYS.md doubles it, a law of a SYS.md out of the
    `SYS<n>` prefix `sys-shape`, a `SYS<n>` a document of the catalog declares `sys-misplaced` --,
    nothing written; held,
    the registry names each system law with its place."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("marble-sys")
    made = env.made
    compiled = sorted(path for path in (made / ".sys").glob("*") if path.is_file())

    def stood() -> dict:
        return {path.name: path.read_bytes() for path in compiled}

    engine = compiling.system_laws(made)
    before = stood()
    env.write_system(behavior="SYS9  the instance's law holds.")
    registry = compiling.render_registry(made)
    rows = {code: next((line for line in registry.splitlines() if line.startswith(f"| `{code}` |")), "")
            for code in [one.code for one in engine] + ["SYS9"]}
    if (engine and all(f"`{compiling.ENGINE_SYS}`" in rows[one.code] for one in engine)
            and f"`{compiling.INSTANCE_SYS}`" in rows["SYS9"]):
        held("the registry names each system law with its place", f"{' '.join(one.code for one in engine)} "
             f"held by `{compiling.ENGINE_SYS}`, SYS9 by `{compiling.INSTANCE_SYS}`")
    else:
        failures.append(f"  ✗ the system registry         {rows}")

    def build() -> None:
        compiling.render_registry(made)
        compiling.build_tools(made)
        compiling.build_system(made)

    for extra, body in (("tools: |\n  DOORN\n", ""), ("", "a body\n"), ("kind: doc\n", "")):
        path = env.write_system(behavior="SYS9  the instance's law holds.", extra=extra)
        if body:
            path.write_text(path.read_text(encoding="utf-8") + body, encoding="utf-8")
        if extra.startswith("kind"):
            path.write_text(path.read_text(encoding="utf-8").replace("kind: sys\n", "", 1), encoding="utf-8")
        expect("sys-shape", build)
    env.write_system(behavior="Q1  a law without the system's prefix.")
    expect("sys-shape", build)
    env.write_system(behavior=f"{engine[0].code}  the instance's own law.")
    expect("law-twice", build)
    env.write_system(behavior="SYS9  the instance's law holds.\nSYS9  the same code again.")
    try:
        build()
        doubled = ""
    except Refusal as refusal:
        doubled = str(refusal) if refusal.code == "law-twice" else f"{refusal.code}: {refusal}"
    if doubled.count(f"`{compiling.INSTANCE_SYS}`") == 1:
        held("a code doubled in one SYS.md names its place once", doubled)
    else:
        failures.append(f"  ✗ the doubled code's place     {doubled!r}")
    env.write_system(behavior="SYS9  the instance's law holds.")
    for code in ("SYS9", "SYS5"):           # held by the SYS.md, or by no SYS.md at all
        env.write("procs/TWIN.md", f"---\nname: TWIN\nkind: proc\nconstraints.behavior: |\n  {code}  a twin.\n"
                                   "proc: |\n  INFER\n---\ntwin\n")
        expect("sys-misplaced", build)
    (made / "procs" / "TWIN.md").unlink()
    (made / "system" / "SYS.md").unlink()
    placed = next((made / ".sys" / "vendor").glob("kit@*")) / "system" / "SYS.md"
    placed.parent.mkdir(parents=True, exist_ok=True)
    placed.write_text("---\nname: SYS\nkind: sys\nconstraints.behavior: |\n  SYS9  a base's law.\n---\n",
                      encoding="utf-8")
    expect("sys-misplaced", build)
    placed.unlink()
    if stood() == before:
        held("a refused build writes nothing", f"{', '.join(sorted(before))} unchanged after the nine refusals")
    else:
        failures.append(f"  ✗ the refused build wrote     "
                        f"{[name for name, text in stood().items() if before.get(name) != text]}")


def scenario(bench) -> int:
    system_build(bench)
    single(bench)
    plain = bench.env("marble")
    standing(bench, plain)
    cards(bench, plain)
    receipts(bench, plain)
    drift(bench, plain)
    return 0
