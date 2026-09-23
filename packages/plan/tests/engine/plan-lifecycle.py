"""Scenario `plan-lifecycle` -- the package comes and goes on an instance that conducts
(plan pp-split, phase plan, batch le-cycle-de-vie-plan):
- a LATE add lands its keys, its offer, its contributor and the closure that brings steering
- the PLANS are the instance's data: an upgrade re-materializes the bundle and leaves the
  tree byte for byte, locks included, and a doctor repairs at constant pins
- remove takes the SURFACE away -- offer, contributor, bundle -- leaves the keys unowned,
  the plans untouched and the standing next move at the record
- and without the package the socle is silent again: no block, no offer, no sector
"""
from __future__ import annotations

from tests.harness import load_script
from conductor import compiling, events, install, instance, reading


def _offers(meta) -> set:
    """-> what TURN offers here: the composed tools, overlays applied."""
    document = reading.read(instance.resolve(meta, "TURN.md"))
    return {one.name for one in compiling.effective(meta, document)[1]}


def _tree(meta) -> dict:
    """-> every file under `plans/`, path -> bytes: the instance's OWN data, locks and all."""
    root = meta / "plans"
    return {str(one.relative_to(root)): one.read_bytes()
            for one in sorted(root.rglob("*")) if one.is_file()} if root.is_dir() else {}


def _contributors(meta, socket) -> list[str]:
    """-> the socket's contributors by BOTH entry verbs -- NEXT_MOVE is MOUNTED at
    `turn.end` since le-mount-au-socket, THREADS is called there."""
    return list(instance.attached(meta, socket)) + list(instance.mounting(meta, socket))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("plancycle")             # the kit alone: no plan, no steering
    meta = env.made
    conductor = env.conductor("t")
    conductor.start(conductor.boot("BOOT.md"))   # it has conducted before the add
    before = (env.read("SETTINGS.md"), _offers(meta), _contributors(meta, "turn.end"))

    # --- the late add lands the surface, and the closure brings what it requires ---------
    install.add_package(env.member, "plan")
    settings = env.read("SETTINGS.md")
    attached = _contributors(meta, "turn.end")
    # the RAW scan gives the derived order; the socket plays `ordering`, preferences applied
    played = instance.ordering(meta, "turn.end", list(attached))
    landed = ("plan_implementation_care: asked" in settings
              and "plan_implementation_control:" in settings
              and "pp-plan" in _offers(meta) and "NEXT_MOVE.md" in attached)
    closed = [one.name.split("@")[0] for one in instance.vendored(meta)]
    ordered = (played.index("NEXT_MOVE.md") < played.index("THREADS.md")
               if "THREADS.md" in played else False)
    # the kit's own SETTINGS names `plan_` in its PROSE (the prefix rule): the probe is the KEY
    was_bare = ("plan_implementation_care:" not in before[0] and "pp-plan" not in before[1]
                and "NEXT_MOVE.md" not in before[2])
    if was_bare and landed and "steering" in closed and ordered:
        held("a late add lands the surface and its closure", "the two keys at the composed "
             "SETTINGS, the offer at TURN, NEXT_MOVE among turn.end's contributors -- and "
             "steering comes with it, and NEXT_MOVE plays before its NEXT as the preference asks")
    else:
        failures.append(f"  ✗ late add                    bare={was_bare} landed={landed} "
                        f"closed={closed} ordered={ordered} played={played}")

    # --- the plans are the instance's data: an upgrade leaves the tree alone -------------
    keeper = load_script(next(one for one in instance.vendored(meta)
                              if one.name.startswith("plan@")) / "skills" / "pp-plan" / "pp-plan.py")
    keeper.new(meta, "cycle", "The cycle plan.\n\nIts thesis, in prose.")
    (meta / "plans" / "cycle.lock").write_bytes(b"")      # the lock a verb leaves behind
    events.stand(meta, "plan-next-move", "plan:cycle", "the plan has no phase yet")
    written, pins_before = _tree(meta), dict(instance.read(meta)["packages"])
    install.upgrade(env.member)
    kept = _tree(meta) == written
    install.doctor(env.member)
    steady = (dict(instance.read(meta)["packages"]) == pins_before
              and _tree(meta) == written and "pp-plan" in _offers(meta))
    if kept and steady and "cycle.lock" in written:
        held("upgrade and doctor leave the plans alone", "the bundle re-materializes and the "
             "repair runs at constant pins; the tree under plans/ stands byte for byte, its "
             "lock file with it")
    else:
        failures.append(f"  ✗ upgrade and doctor          kept={kept} steady={steady}")

    # --- remove takes the surface, never the data ----------------------------------------
    install.remove_package(env.member, "plan")
    after = env.read("SETTINGS.md")
    gone = ("pp-plan" not in _offers(meta)
            and "NEXT_MOVE.md" not in _contributors(meta, "turn.end")
            and not [one for one in instance.vendored(meta) if one.name.startswith("plan@")])
    unowned = "# ---- unowned ----" in after and "plan_implementation_care: asked" in after
    # the held next move STAYS at the record (the instance's data) -- and leaves the SERVE:
    # with the package gone its family has no verifier, and the service drops what it
    # cannot verify (the bus's rule since le-bus-lit-le-registre)
    standing = [key for key in events.counters(meta) if key.startswith("standing|plan|plan-next-move|")]
    served = [one["signal"] for one in events.standing_entries(meta)]
    if (gone and unowned and _tree(meta) == written and standing == ["standing|plan|plan-next-move|plan:cycle"]
            and "plan-next-move" not in served):
        held("remove takes the surface, never the data", "offer, contributor and bundle "
             "leave; the keys ride on as unowned, the plans and their locks are untouched, "
             "and the held next move stays at the record -- the instance's own -- while the "
             "serve drops it: no package, no verifier, no line")
    else:
        failures.append(f"  ✗ remove                      gone={gone} unowned={unowned} "
                        f"tree={_tree(meta) == written} standing={standing}")

    # --- and the socle is silent again -----------------------------------------------------
    bare = bench.env("planbare")
    opener = bare.conductor("t")
    opener.start(opener.boot("BOOT.md"))
    blocks, pending, steps = [], bare.conductor("t").submit(""), 0
    while pending is not None and steps < 6:
        steps += 1
        blocks.append(pending.document)
        if "FINAL" in (pending.next_call or ""):
            break
        pending = bare.conductor("t").submit("")
    sectors = events.sectors(bare.made)
    if "NEXT_MOVE" not in blocks and "pp-plan" not in _offers(bare.made) and "plan" not in sectors:
        held("the absent package costs nothing", "no block at the socket, no offer at TURN, "
             "no sector at the bus -- the absence is a diff, not an impression")
    else:
        failures.append(f"  ✗ absence                     blocks={blocks} "
                        f"sectors={sorted(sectors)}")
    return 0
