"""Scenario `marble-layers` -- 5 case(s) (batch le-marbre-et-la-carte-au-noyau, 2026-09-26; cut at
le-tri-de-l-execution-et-du-packaging, 2026-10-06: the comparison with the KIT's old marble lives at
`bases/kit/tests/engine/marble-layers.py`, the mechanism stays here on the stand-in):
- the sections (batch le-document-de-la-conduction, 2026-10-06): the engine's orders and
  its card, then the base's precision, then the other packages, in that order
- a base without its `system/SYSTEM.COMMON.md` refuses at the build: `base-silent`
- card-drift is the engine's: a modified projection pushes the signal though the base
  declares no check
- the projected card is the engine's `refs/PP.md` followed by its `SYSTEM.CONDUCT.md`
- another package's section compiles after the base's (the witness `sayer` on the sections)
- the harness keeps the product's document: a SYSTEM.COMMON.md under a dotted directory
  of the source (an instance, a projection) is not the body test's
"""
from __future__ import annotations

from conductor import Conductor, compiling, discovery, persistence
from conductor import install as install_module
from tests.harness import PRODUCT_ENGINE, SOURCE, kept_document, load_script, session_of


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("layers")
    made = env.made
    compiled = (made / ".sys" / "system.md").read_text(encoding="utf-8")

    # --- the sections, in order ----------------------------------------------------------
    engine_root = made / ".sys" / "engine"
    orders = (engine_root / "system" / "SYSTEM.COMMON.md").read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()[:60]
    card = (engine_root / "refs" / "PP.md").read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()[:60]
    kit_root = next((made / ".sys" / "vendor").glob("kit@*"))
    common = kit_root / "system" / "SYSTEM.COMMON.md"
    precision = common.read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()[:60]
    common_kept = common.read_bytes()
    common.write_bytes(common_kept + b"\nZebra orders hold.\n")
    compiling.build_system(made)
    layered = (made / ".sys" / "system.md").read_text(encoding="utf-8")
    common.write_bytes(common_kept)
    compiling.build_system(made)
    order = [layered.index(orders), layered.index(card), layered.index(precision),
             layered.index("Zebra orders hold.")]
    if order == sorted(order) and (made / ".sys" / "system.md").read_text(encoding="utf-8") == compiled:
        held("the marble compiles in sections", "the engine's orders and its card, then the "
             "base's precision -- and byte-identical once the base's text is restored")
    else:
        failures.append(f"  ✗ sections                    {order}")

    # --- a silent base refuses at the build ----------------------------------------------
    common.unlink()
    expect("base-silent", lambda: compiling.build_system(made))
    common.write_bytes(common_kept)
    compiling.build_system(made)
    held("a silent base refuses", "a base without its SYSTEM.COMMON.md says nothing of its "
         "principal: `base-silent`, nothing compiled")

    # --- card-drift is the engine's: pushed with no check declared by the base ------------
    ws = made.parent
    load_script(install_module.product_root(PRODUCT_ENGINE) / "adapters" / "claude" / "wire.py").wire(ws, made)
    projected = ws / ".claude" / "skills" / "pp" / "SKILL.md"
    pristine = projected.read_text(encoding="utf-8") == install_module.card(made)
    manifest = (kit_root / "package.yaml").read_text(encoding="utf-8")
    projected.write_text(projected.read_text(encoding="utf-8") + "\nOLD LAW\n", encoding="utf-8")
    member = discovery.instance_member(engine_root / "pp.py")
    conductor = Conductor(member, engine_root / "pp.py", "t")
    conductor.start(conductor.boot("BOOT.md"))
    latched = persistence.signals_of(session_of(made))
    conductor.forget()
    verified = install_module.verify(member)
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

    # --- another package's section stands after the base's -------------------------------
    with_sayer = bench.env("layers-sayer", packages=("sayer",)).made
    stacked = (with_sayer / ".sys" / "system.md").read_text(encoding="utf-8")
    sayer_root = next((with_sayer / ".sys" / "vendor").glob("sayer@*"))
    fragment = (sayer_root / "system" / "SYSTEM.COMMON.md").read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()[:60]
    if stacked.index(orders) < stacked.index(card) < stacked.index(precision) < stacked.index(fragment):
        held("the other packages come after the base", "the sayer's section compiles after the "
             "engine's orders and card and the base's precision")
    else:
        failures.append("  ✗ packages section            the sayer's section not after the base's")

    # --- the harness keeps the product's document, never a dotted directory's ----------
    # (on a copy of the engine's system/: the source tree is what other scenarios stage
    # meanwhile -- a decoy written there tears their copy)
    import shutil
    area = bench.temp() / "engine"
    shutil.copytree(SOURCE / "engine" / "system", area / "system")
    kept = kept_document(area, "SYSTEM.COMMON")
    decoy = area / ".decoy" / "system" / "SYSTEM.COMMON.md"
    decoy.parent.mkdir(parents=True, exist_ok=True)
    decoy.write_text("---\nname: SYSTEM.COMMON\nkind: doc\n---\nnot the product's\n", encoding="utf-8")
    same = kept_document(area, "SYSTEM.COMMON") == kept
    if same and kept == area / "system" / "SYSTEM.COMMON.md":
        held("the harness keeps the product's text", "a SYSTEM.COMMON.md under a dotted directory "
             "of the source changes nothing: `engine/system/SYSTEM.COMMON.md` stays the kept document")
    else:
        failures.append(f"  ✗ harness decoy               {kept}")
    return 0
