"""Scenario `mount-overlays` -- 5 case(s): a MOUNTED document puts in force what a frame on it
would -- the base's sections and the deltas of its overlays:
- a stacked mount carries the law and the offer its overlay adds, and drops the law it removes
- a nested mount shows the same in its own segment
- the overlay's law is owed at the proof like any mounted law
- the BASE guard: a homonym mounted by its path, outside the name's chain, takes no delta
- the collision looks at the effective laws: an overlay's law already in force refuses
Witness documents written at run -- no package of the product.
"""
from __future__ import annotations

from conductor import Conductor, discovery, navigation, persistence, revive
from tests.harness import document, session_of

BASE = ("---\nname: WNODE\nkind: doc\nconstraints.production: |\n  W1  the base law binds.\n"
        "  W2  the base law an overlay lifts.\ntools: |\n  WBASE\n---\n\nThe witness node.\n")
OVERLAY = ("---\nname: WNODE\nconstraints.production: |\n  -W2\n  W3  the overlay law binds.\n"
           "tools: |\n  +WOVER\n---\n")
HOMONYM = ("---\nname: WNODE\nkind: doc\nconstraints.production: |\n  H1  the homonym's own law.\n"
           "---\n\nA node that only shares the file name.\n")


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    siblings = bench.town(["core"]).siblings
    home = discovery.member(siblings, "core")
    script = home.meta / ".sys" / "engine" / "pp.py"
    meta = home.meta

    def c() -> Conductor:
        return Conductor(home, siblings, script, "t")

    (meta / "procs").mkdir(exist_ok=True)
    (meta / "procs" / "WNODE.md").write_text(BASE, encoding="utf-8")        # the base of the name
    (meta / "WNODE.md").write_text(OVERLAY, encoding="utf-8")                # its overlay, nearer
    (meta / "elsewhere").mkdir()
    (meta / "elsewhere" / "WNODE.md").write_text(HOMONYM, encoding="utf-8")  # outside the chain
    (meta / "MFORMS.md").write_text(
        "---\nname: MFORMS\ndescription: bench formats\nformats: |\n"
        "  json  inline  one valid JSON value\n---\n", encoding="utf-8")
    floor = document("---\nname: MJOB\ncycle: true\noutput: json\nproc: |\n  INFER\n  PICK member\n---\n", at=meta)

    def sweep() -> None:
        """One exchange played out: the cycling floor exhausts and its rewind sweeps the mounts."""
        c().submit('["a", "b"]')
        c().submit("a")

    # --- a stacked mount carries its overlay's deltas ----------------------------------------
    c().start(floor)
    c().mount([{"doc": "procs/WNODE.md"}])
    block = c().peek()
    codes = [one.code for one in block.constraints]
    tools = [one.name for one in block.tools]
    if "W1" in codes and "W3" in codes and "W2" not in codes and {"WBASE", "WOVER"} <= set(tools):
        held("a stacked mount carries its overlay's deltas",
             "the base's law, the overlay's added law and offer in force; the lifted law gone")
    else:
        failures.append(f"  ✗ stacked deltas             codes={codes} tools={tools}")

    # --- the overlay's law is owed at the proof ------------------------------------------------
    judge = c()
    stack = judge._rebind(persistence.restore(session_of(meta), revive))
    frame = navigation.current(stack)
    fine = judge._check_prove(stack, frame, navigation.peek(frame),
                              '[{"code": "W3", "evidence": "held", "verdict": "ok"}]')
    lifted = judge._check_prove(stack, frame, navigation.peek(frame),
                                '[{"code": "W2", "evidence": "held", "verdict": "ok"}]')
    if fine == "" and "W2" in lifted and "not in force" in lifted:
        held("the overlay's law is judged at the proof",
             "W3 passes as a law in force; W2, lifted by the overlay, is refused as a stranger")
    else:
        failures.append(f"  ✗ overlay proof              fine={fine!r} lifted={lifted!r}")

    # --- the collision looks at the effective laws ---------------------------------------------
    (meta / "procs" / "WOTHER.md").write_text(
        "---\nname: WOTHER\nkind: doc\n---\n\nquiet\n", encoding="utf-8")
    (meta / "WOTHER.md").write_text(
        "---\nname: WOTHER\nconstraints.production: |\n  W3  the same code again.\n---\n", encoding="utf-8")
    expect("mount-collision", lambda: c().mount([{"doc": "procs/WOTHER.md"}]))

    # --- a nested mount shows the same in its own segment ------------------------------------
    sweep()
    out = c().mount([{"doc": "procs/WNODE.md", "scope": "nested"}])
    segment = out.split("▌ [2]")[0]
    if ("▸ WNODE" in segment and "WBASE WOVER" in segment and "W3  the overlay law binds." in segment
            and "W1  the base law binds." in segment and "W2  the base law" not in segment):
        held("a nested mount shows its overlay's deltas",
             "its own heading, the two offers, the base's and the overlay's laws verbatim, the lifted one absent")
    else:
        failures.append(f"  ✗ nested deltas              {segment[:300]!r}")

    # --- the BASE guard: a homonym outside the chain takes no delta -----------------------------
    sweep()
    c().mount([{"doc": "elsewhere/WNODE.md"}])
    block = c().peek()
    codes = [one.code for one in block.constraints]
    tools = [one.name for one in block.tools]
    if "H1" in codes and "W3" not in codes and "WOVER" not in tools:
        held("a homonym outside the chain takes no delta",
             "mounted by its path, it is not the base of its name: its own law alone, no overlay's law or offer")
    else:
        failures.append(f"  ✗ base guard                 codes={codes} tools={tools}")
    return 0
