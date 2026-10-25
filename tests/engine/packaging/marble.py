"""Scenario `marble` -- the marble's mechanics that no author writes:
- the standing rules: `system.md` at install, byte-stable across builds, no replace artifact
  unasked; the standing-orders channel with and without `PP_MARBLE`
- the receipts: a stale receipt of the principal's marble refuses `artifact-stale`; the doctor
  names both receipts and the card current, the card a harness receives being the engine's card
  followed by its `SYSTEM.CONDUCT.md`
- card-drift is the engine's: an edited projection latches it at the boot though the base
  declares no check, and the verifier names the drifted card
What a package's `system/` and the instance's `SYSTEM_PROMPT.md` give -- the two marbles, their
sections and their order, the two names, the marble each run is served, a package switched off,
the replace lock -- is the pattern `packaging/system-fragment`'s; a base without `system/`,
`packaging/base`'s.
"""
from __future__ import annotations

import os

import yaml

from conductor import Conductor, compiling, discovery, install, persistence, render
from tests.harness import PRODUCT_ENGINE, SOURCE, body_of, kept_document, load_script, session_of

VARIABLE = "PP_CONDUCTED_BY_PRINCIPAL"
COMMON = "system.common.md"


def _opened(env, principal: bool):
    spot = os.environ.get(VARIABLE)
    if principal:
        os.environ[VARIABLE] = "true"
    else:
        os.environ.pop(VARIABLE, None)
    try:
        env.conductor().forget()
        conductor = env.conductor()
        return conductor, conductor.start(conductor.boot("BOOT.md"))
    finally:
        if spot is None:
            os.environ.pop(VARIABLE, None)
        else:
            os.environ[VARIABLE] = spot


def _engine_heads() -> tuple[str, str]:
    """-> the openings of the engine's two sections, read at the source."""
    return (body_of(kept_document(SOURCE / "engine", "SYSTEM.COMMON"))[:60],
            body_of(kept_document(SOURCE / "engine", "SYSTEM.CONDUCT"))[:60])


def standing(bench, env) -> None:
    """The standing rules compiled at install, byte-stable; the standing-orders channel."""
    held, failures = bench.held, bench.failures
    made = env.made
    system_art = made / ".sys" / "system.md"
    replaces = [made / ".sys" / "system.replace.md", made / ".sys" / "system.common.replace.md"]
    orders, conduct = _engine_heads()
    first = system_art.read_bytes() if system_art.is_file() else b""
    compiling.build_system(made)
    compiled = first.decode("utf-8")
    if (system_art.is_file() and orders in compiled and conduct in compiled
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
            and "standing orders" not in quiet_boot):
        held("the standing orders find their channel",
             "no PP_MARBLE: the boot serves them first; a wired marble declares itself "
             "and the boot stays quiet")
    else:
        failures.append(f"  ✗ standing orders channel     {('standing orders' in served_boot)}/"
                        f"{('standing orders' in quiet_boot)}")


def receipts(bench, env) -> None:
    """A stale receipt refuses; the doctor names the receipts and the card a harness receives."""
    held, expect, failures = bench.held, bench.expect, bench.failures
    conduct = body_of(kept_document(SOURCE / "engine", "SYSTEM.CONDUCT"))
    card_head = body_of(kept_document(SOURCE / "engine", "PP"))[:60]
    sys_dir = env.made / ".sys"

    # --- a stale receipt of the principal's marble refuses ----------------------------------------
    path = sys_dir / compiling.RECEIPTS
    kept = path.read_text(encoding="utf-8")
    held_receipts = yaml.safe_load(kept)
    held_receipts[COMMON]["inputs"] = "0" * 64
    path.write_text(yaml.safe_dump(held_receipts, sort_keys=True), encoding="utf-8")
    expect("artifact-stale", lambda: _opened(env, True))
    path.write_text(kept, encoding="utf-8")
    env.conductor().forget()

    # --- the doctor and the card a harness receives ---------------------------------------------
    ws = env.made.parent
    load_script(install.product_root(PRODUCT_ENGINE) / "adapters" / "claude" / "wire.py").wire(ws, env.made)
    card = (ws / ".claude" / "skills" / "pp" / "SKILL.md").read_text(encoding="utf-8")
    told = install.verify(env.member)
    booted, _ = _opened(env, False)
    latched = [one.get("signal") for one in persistence.signals_of(session_of(env.made))]
    booted.forget()
    if ("card-drift" not in latched and conduct[:60] in card and card_head in card
            and card.index(card_head) < card.index(conduct[:60])
            and any(one.startswith("receipt system.md: current") for one in told)
            and any(one.startswith(f"receipt {COMMON}: current") for one in told)
            and any(one.startswith("card .claude") and one.endswith("current") for one in told)):
        held("the doctor and the card", "the harness card is the card followed by the "
             "engine's SYSTEM.CONDUCT.md; the verifier names both receipts and the card current, "
             "and the boot latches no card-drift on it")
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
             "engine/refs/PP.md followed by engine/system/SYSTEM.CONDUCT.md; edited, the boot pushes "
             "`card-drift` from the engine though the base declares no check, and the verifier "
             "names the drifted card")
    else:
        failures.append(f"  ✗ engine card-drift           pristine={pristine} "
                        f"manifest-clean={'card-drift' not in manifest} {latched!r}")


def scenario(bench) -> int:
    plain = bench.env("marble")
    standing(bench, plain)
    receipts(bench, plain)
    drift(bench, plain)
    return 0
