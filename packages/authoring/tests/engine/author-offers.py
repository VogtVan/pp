"""Scenario `author-offers` -- 3 case(s):
- with authoring, the boot offers the five doors and the turn offers pp-authoring and
  PP-DESIGN (the doors inherited): the overlays of the package, nothing of the kit
- the kit alone offers none of them: the absence, on the same two blocks
- the overlays compose with another overlay on the same document: the instance's own
  TURN overlay adds a tool of its own, and the turn offers it AND pp-authoring (plan's
  overlay joins this case when plan installs again -- its NEXT waits for steering)
"""
from __future__ import annotations

DOORS = ("PP-MEMBER", "PP-RULES", "PP-OFFERS", "PP-MIGRATE", "PP-DESIGN")


def _blocks(env):
    """-> (the boot block, the turn block) of a fresh run on `env`."""
    conductor = env.conductor()
    boot = conductor.start(conductor.boot("BOOT.md"))
    turn = env.conductor().submit("")
    return boot, turn


def _names(block) -> set[str]:
    return {one.name for one in block.tools} if block is not None else set()


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- with authoring: the surface of before, by the package's overlays ----------------
    with_boot, with_turn = _blocks(bench.env("offers-with", packages=("authoring",)))
    boot_names, turn_names = _names(with_boot), _names(with_turn)
    if (set(DOORS) <= boot_names and {"pp-authoring", "PP-DESIGN", "PP-MEMBER"} <= turn_names):
        held("authoring offers by its overlays", f"boot: {sorted(boot_names)}; turn: "
             f"{sorted(turn_names)}")
    else:
        failures.append(f"  ✗ offers with authoring      boot={sorted(boot_names)} turn={sorted(turn_names)}")

    # --- the kit alone: the absence ---------------------------------------------------------
    bare_boot, bare_turn = _blocks(bench.env("offers-without"))
    bare = _names(bare_boot) | _names(bare_turn)
    if not (bare & (set(DOORS) | {"pp-authoring"})):
        held("the kit alone offers no author tool", f"boot+turn: {sorted(bare) or 'nothing'}")
    else:
        failures.append(f"  ✗ offers without authoring   {sorted(bare)}")

    # --- two overlays on the same document compose --------------------------------------------
    layered = bench.env("offers-layered", packages=("authoring",))
    (layered.made / "procs").mkdir(exist_ok=True)
    (layered.made / "procs" / "TURN.md").write_text(
        "---\nname: TURN\ntools: |\n  +TAGGED\n---\n", encoding="utf-8")
    (layered.made / "TAGGED.md").write_text(
        "---\nname: TAGGED\ndescription: a tool of the instance\n---\nmatter\n",
        encoding="utf-8")
    _, both_turn = _blocks(layered)
    both = _names(both_turn)
    if {"TAGGED", "pp-authoring", "PP-DESIGN"} <= both:
        held("the overlays compose across spaces", "TURN offers TAGGED (the instance's overlay) "
             "and pp-authoring, PP-DESIGN (authoring's) at once -- plan's joins when it installs")
    else:
        failures.append(f"  ✗ offers compose             {sorted(both)}")
    return 0
