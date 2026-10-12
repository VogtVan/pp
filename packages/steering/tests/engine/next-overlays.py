"""Scenario `next-overlays` -- the base document takes its clients' semantics by
composition (plan pp-split, phase steering, batch les-overlays-de-pilotage):
- the base alone says the generic steering and names no client
- a witness overlay puts its law in force and lands its prose AFTER the base's
"""
from __future__ import annotations

from conductor import compiling, instance, reading


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    env = bench.env("ovnext", packages=("steering",))
    conductor = env.conductor("t")
    base = instance.resolve(env.made, "NEXT.md")

    # --- the base alone: the generic surface, no client's word ---------------------------
    alone_text, alone_hash = conductor._composed(base)
    absent = [word for word in ("served", "confederation", "@<member>") if word in alone_text.lower()]
    # the base's own last line, read at run time: the line the order case compares against
    tail = alone_text.rstrip().splitlines()[-1]
    if not absent and (alone_text, alone_hash) == reading.served(base):
        held("the base alone names no client",
             "no client vocabulary survives the document; with no overlay the served bytes are its own")
    else:
        failures.append(f"  ✗ base alone                 client words={absent}")

    # --- a witness overlay: its law binds, its prose lands after the base's ---------------
    (env.made / "procs").mkdir(exist_ok=True)
    (env.made / "procs" / "NEXT.md").write_text(
        "---\nname: NEXT\nconstraints.behavior: |\n  ZZ9  the client's own semantics ride here.\n---\n\n"
        "The client's paragraph lands after the base.\n", encoding="utf-8")
    over = instance.resolve(env.made, "NEXT.md")
    laws = [one.code for one in compiling.effective(env.made, reading.read(over))[0]]
    over_text, over_hash = conductor._composed(over)
    ordered = over_text.find(tail) < over_text.find("The client's paragraph lands after the base.")
    if ("ZZ9" in laws and {"NX1"} <= set(laws) and ordered
            and over_text.endswith("The client's paragraph lands after the base.\n")
            and over_hash != alone_hash):
        held("a client's overlay composes onto the base",
             "its law joins NX1, its prose lands after the base's, one hash over the whole")
    else:
        failures.append(f"  ✗ overlay composes           laws={laws} ordered={ordered} "
                        f"tail={over_text[-80:]!r}")
    return 0
