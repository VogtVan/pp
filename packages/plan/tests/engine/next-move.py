"""Scenario `next-move` -- a plan's next move reaches the steering surface (plan pp-split,
phase plan, batch les-frontieres-de-pilotage):
- a mutating gesture of `pp-plan` publishes ONE held entry on the generic bus
- a second gesture REPLACES it: one line per plan, never a pile
- the package's own consumer carries that line into the turn BEFORE the surface --
  `order: turn.end before steering`, declared at the contributor, not suffered
- closing the plan clears the entry, and the next exchange carries nothing
- the line ends with the VECTOR of the node it names (batch la-cle-au-next-move): the key
  of the thread's step, at the three levels

The composition is `("plan",)`: steering arrives by the requires closure, and no
improvement package exists anywhere -- KSL4 is what this scenario keeps honest.
The line's PROSE is never judged (KFP4): it arrives, it is replaced, it goes.
"""
from __future__ import annotations

from conductor import events, instance, render
from tests.harness import cli, na_proof

THESIS = "the wall of the garden, rebuilt stone by stone\n"


def _exchange(env) -> list:
    """One exchange after the boot; -> its blocks, from the work to the closing."""
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))
    blocks, pending, steps = [], env.conductor("t").submit(""), 0
    while pending is not None and steps < 8:
        steps += 1
        blocks.append(pending)
        if "INFER proof" in render(pending):
            env.conductor("t").submit(na_proof(pending))
            break
        if "FINAL" in (pending.next_call or ""):
            break
        pending = env.conductor("t").submit("")
    return blocks


def _lines(env) -> list[str]:
    """-> the rendered blocks of one exchange -- the consumer has no step of its own, so
    its payload rides the block that follows it."""
    return [render(one) for one in _exchange(env) if one is not None]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("next-move", packages=("plan",))
    made = env.made
    engine = made / ".sys" / "engine" / "pp.py"
    key = "t"
    _exchange(env)              # past the boot: the turn's blocks offer `pp-plan`

    # --- publication: a mutating gesture holds ONE entry ---------------------------------
    born = cli(engine, key, "-s", "pp-plan", "section", "le-mur", "Context", stdin=THESIS)
    standing = events.standing_entries(made)
    published = (born.returncode == 0 and "::push" not in born.stdout
                 and len(standing) == 1 and standing[0]["vector"] == "plan:le-mur"
                 and standing[0]["text"])
    if published:
        held("a mutating gesture publishes its next move",
             "`pp-plan section … Context` prints its `::push`, the conductor harvests it, and the bus holds "
             "ONE entry for `plan:le-mur` -- no improvement package in the composition")
    else:
        failures.append(f"  ✗ publication                rc={born.returncode} standing={standing}")

    # --- replacement: the newest wins, the pile never grows -------------------------------
    was = standing[0]["text"] if standing else ""
    cli(engine, key, "-s", "pp-plan", "section", "le-mur", "Target", stdin="a wall that stands\n")
    cli(engine, key, "-s", "pp-plan", "section", "le-mur", "Expected", stdin="the wall stands -- seen\n")
    cli(engine, key, "-s", "pp-plan", "section", "le-mur", "Items", stdin="- les-fondations -- dig first\n")
    after = events.standing_entries(made)
    replaced = len(after) == 1 and after[0]["vector"] == "plan:le-mur" and after[0]["text"] != was
    if replaced:
        held("the newest next move replaces the previous",
             "a second gesture leaves ONE entry for the plan, its text moved on -- a delivery "
             "cleans its own push by pushing the next")
    else:
        failures.append(f"  ✗ replacement                was={was!r} after={after}")

    # --- arrival: the line reaches the turn BEFORE the surface ----------------------------
    # the socket's contributors come by BOTH entry verbs since le-mount-au-socket:
    # NEXT_MOVE is MOUNTED there, THREADS is called -- one list, one ordering
    derived = list(instance.attached(made, "turn.end")) + list(instance.mounting(made, "turn.end"))
    order = instance.ordering(made, "turn.end", list(derived))
    carried = _lines(env)
    wanted = after[0]["text"] if after else "@"
    seat = next((one for one in carried if wanted in one), "")
    arrived = bool(seat)
    # the consumer carries no step of its own: its payload and its brief ride the block
    # that follows -- the surface's -- so precedence is read at the socket AND on the page
    ahead = (order.index("NEXT_MOVE.md") < order.index("THREADS.md")
             and 0 <= seat.find("INFORMATION — plan-next-move") < seat.find("NEXT INSTRUCTION CONTEXT"))
    if arrived and ahead:
        held("the next move arrives before the surface that carries it",
             f"the package's own consumer opens at `turn.end`; the requires topology derives "
             f"{derived} and the socket expands {order} -- `order: turn.end before steering`, "
             "DECLARED at the contributor, is what puts the line ahead of the surface")
    else:
        failures.append(f"  ✗ arrival                    derived={derived} order={order} "
                        f"arrived={arrived} ahead={ahead}")

    # --- the closing clears it, and it does not come back ---------------------------------
    # the prepared phase is born by its first section and framed, its batch prepared, born,
    # framed and DELIVERED: the Delivery closes the batch, the phase and the plan -- the
    # script's cascade, no word
    cli(engine, key, "-s", "pp-plan", "section", "le-mur/les-fondations", "Ground", stdin="the soil\n")
    cli(engine, key, "-s", "pp-plan", "section", "le-mur/les-fondations", "Target", stdin="a base\n")
    cli(engine, key, "-s", "pp-plan", "section", "le-mur/les-fondations", "Expected", stdin="the base holds\n")
    cli(engine, key, "-s", "pp-plan", "section", "le-mur/les-fondations", "Items", stdin="- socle -- the base\n")
    for name, prose in (("Ground", "the soil"), ("Target", "a base"), ("Expected", "it holds"), ("Tests", "the load")):
        cli(engine, key, "-s", "pp-plan", "section", "le-mur/les-fondations/socle", name, stdin=prose + "\n")

    # --- the line ends with the VECTOR of the node it names -- the thread step's key ------
    # (batch la-cle-au-next-move): the plan alone, a phase prepared, a batch framed
    framed = events.standing_entries(made)
    keyed = (was.endswith("(plan:le-mur)")
             and after and after[0]["text"].endswith("(plan-phase:le-mur/les-fondations)")
             and len(framed) == 1 and framed[0]["text"].endswith("(plan-lot:le-mur/les-fondations/socle)"))
    if keyed:
        held("the line ends with the node's vector", "plan:le-mur while no phase stands, "
             "plan-phase:le-mur/les-fondations once one is prepared, plan-lot:le-mur/les-fondations/socle "
             "once the batch is framed -- the last token is the key of the thread's step")
    else:
        failures.append(f"  ✗ node vector                was={was!r} after={after} framed={framed}")
    cli(engine, key, "-s", "pp-plan", "section", "le-mur/les-fondations/socle", "Delivery", stdin="landed\n")
    cleared = events.standing_entries(made)
    quiet = not any(was in one for one in _lines(env))
    if cleared == [] and quiet:
        held("a done plan cleans its own line",
             "the Delivery of the last batch closes phase and plan by the script's cascade; `::clear` drops "
             "the held entry and the next exchange carries nothing -- the plan that has nothing "
             "to ask for asks for nothing")
    else:
        failures.append(f"  ✗ clearing                   cleared={cleared} quiet={quiet}")
    return 0
