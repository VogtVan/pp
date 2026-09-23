"""Scenario `steering-lifecycle` -- the package comes and goes on an instance that
conducts (plan pp-split, phase steering, batch le-cycle-de-vie-steering):
- a LATE add lands its keys, its offer and its attach on an instance already running
- the threads are the INSTANCE's data: an upgrade re-materializes the bundle and leaves
  the records byte for byte, and a doctor repairs at constant pins
- remove takes the SURFACE away -- offer, attach, bundle -- leaves the keys unowned and
  the records untouched, and the socket falls silent again
"""
from __future__ import annotations

from tests.harness import load_script
from conductor import compiling, install, instance, reading


def _offers(meta) -> set:
    """-> what TURN offers here: the composed tools, overlays applied."""
    document = reading.read(instance.resolve(meta, "TURN.md"))
    return {one.name for one in compiling.effective(meta, document)[1]}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("cycle")                 # the kit alone: no steering anywhere
    meta = env.made
    conductor = env.conductor("t")
    conductor.start(conductor.boot("BOOT.md"))   # the instance has conducted before the add
    before = (env.read("SETTINGS.md"), _offers(meta), instance.attached(meta, "turn.end"))

    # --- the late add lands the whole surface --------------------------------------------
    install.add_package(env.member, "steering")
    settings = env.read("SETTINGS.md")
    landed = ("steering_step_budget: 100" in settings and "steering_name_max: 60" in settings
              and "pp-steering" in _offers(meta) and "THREADS.md" in instance.attached(meta, "turn.end")
              and not list(instance.attached(meta, "turn.begin")) + list(instance.mounting(meta, "turn.begin")))
    was_bare = ("steering_" not in before[0] and "pp-steering" not in before[1]
                and "THREADS.md" not in before[2])
    if was_bare and landed:
        held("a late add lands the whole surface",
             "on an instance that already conducts: the two keys at the composed SETTINGS, the offer at TURN, THREADS among turn.end's contributors, nothing at turn.begin")
    else:
        failures.append(f"  ✗ late add                   bare={was_bare} landed={landed}")

    # --- the records are the instance's data: an upgrade leaves them alone ----------------
    threads = load_script(next(one for one in instance.vendored(meta)
                               if one.name.startswith("steering@")) / "skills" / "pp-steering" / "pp-steering.py")
    threads.open_thread(meta, "le-fil-du-cycle", "un-pas-avant-le-cycle | un pas ecrit avant le cycle\n")
    spool = meta / ".sys" / "records" / "threads.json"
    written = spool.read_bytes()
    pins_before = dict(instance.read(meta)["packages"])
    install.upgrade(env.member)
    kept = spool.read_bytes() == written
    install.doctor(env.member)
    steady = (dict(instance.read(meta)["packages"]) == pins_before
              and spool.read_bytes() == written and "pp-steering" in _offers(meta))
    if kept and steady:
        held("upgrade and doctor leave the records alone",
             "the bundle re-materializes and the repair runs at constant pins; threads.json stands byte for byte, the offer with it")
    else:
        failures.append(f"  ✗ upgrade and doctor         kept={kept} steady={steady}")

    # --- remove takes the surface, never the data -----------------------------------------
    install.remove_package(env.member, "steering")
    after = env.read("SETTINGS.md")
    gone = ("pp-steering" not in _offers(meta) and "THREADS.md" not in instance.attached(meta, "turn.end")
            and not [one for one in instance.vendored(meta) if one.name.startswith("steering@")])
    unowned = "# ---- unowned ----" in after and "steering_step_budget: 100" in after
    if gone and unowned and spool.read_bytes() == written:
        held("remove takes the surface, never the data",
             "offer, attach and bundle leave; the keys ride on as unowned and threads.json is untouched -- the instance's own")
    else:
        failures.append(f"  ✗ remove                     gone={gone} unowned={unowned} "
                        f"records={spool.read_bytes() == written}")

    # --- and the socket falls silent again --------------------------------------------------
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))
    blocks, pending, steps = [], env.conductor("t").submit(""), 0
    while pending is not None and steps < 6:
        steps += 1
        blocks.append(pending.document)
        if "FINAL" in (pending.next_call or ""):
            break
        pending = env.conductor("t").submit("")
    if "NEXT" not in blocks and "THREADS" not in blocks and "steering_" not in _offers(meta):
        held("the absent package costs nothing",
             "no block at the socket, no offer, no active path -- the whole matrix rides the witness of the phase's last batch")
    else:
        failures.append(f"  ✗ absence                    blocks={blocks}")
    return 0
