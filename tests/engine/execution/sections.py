"""Scenario `sections` -- 3 case(s):
- the block renders ONE CONSTRAINTS title, production first then behavior, each group
  labelled when the other exists; the proof hint says how many production laws are owed
- the judge asks the production laws alone: a proof missing a behavior law passes, one
  missing a production law reopens the document
- an overlay adds in the section of its key, and the law is in force with it
- no law of production in force: an armed document owes no checkpoint, the closing says so
"""
from __future__ import annotations

from conductor import Conductor, render, discovery, compiling, reading, instance
from tests.harness import document


def scenario(bench) -> int:
    held, over, failures = bench.held, bench.over, bench.failures
    town = bench.town(["sect"])
    home, script = town["sect"].member, town["sect"].engine

    def conductor() -> Conductor:
        return Conductor(home, town.siblings, script, "t")

    doc = document(
        "---\nname: TWO\nkind: proc\ndescription: two sections\n"
        "constraints.production: |\n  P1  the line is under ten words\n"
        "constraints.behavior: |\n  H1  say what you do before you do it\n"
        "proc: |\n  INFER\n---\nwrite one line\n", at=home.meta)

    # --- one title, two groups, the codes on the instruction line -----------------------
    opening = conductor().start(doc)
    shown = render(opening)
    proof_block = conductor().submit("")          # the chat-bound INFER: said there, the key alone
    if (shown.count("▌ CONSTRAINTS") == 1
            and "production:\nP1  the line is under ten words\nbehavior:\nH1  say what" in shown
            and "INFER proof [P1] on all produced areas" in render(proof_block)
            and "law(s) owed" not in proof_block.next_call
            and proof_block.command == "INFER" and proof_block.output == "proof"):
        held("one title, production first, the codes on the line",
             "P1 under `production:`, H1 under `behavior:`; the checkpoint NAMES P1 and "
             "its plate, and the hint keeps the way back alone")
    else:
        failures.append(f"  ✗ sections rendered          {shown!r} {proof_block.next_call!r}")

    # --- the judge asks the production laws alone ----------------------------------------------
    behavior_only = conductor().submit('[{"code": "H1", "evidence": "said first", "verdict": "ok"}]')
    conductor().submit("")                       # the reopened INFER, said in chat again
    production_only = conductor().submit('[{"code": "P1", "evidence": "wc -w -> 4", "verdict": "ok"}]')
    if (behavior_only.deviation and "names no law of production" in behavior_only.deviation
            and over(production_only)):
        held("the proof asks the production laws alone",
             "H1 alone names no law of production; P1 alone lets the run out -- a behavior "
             "law is never owed")
    else:
        failures.append(f"  ✗ proof filter               {behavior_only.deviation!r} "
                        f"{production_only and production_only.command!r}")
    conductor().forget()

    # --- an overlay adds in the section of its key ---------------------------------------------
    meta = home.meta
    (meta / "procs").mkdir(exist_ok=True)
    (meta / "procs" / "TURN.md").write_text(
        "---\nname: TURN\nconstraints.behavior: |\n  +TB9  the overlay's way of doing\n"
        "constraints.production: |\n  +TP9  the overlay's rendered fact\n---\n", encoding="utf-8")
    laws, _ = compiling.effective(meta, reading.read(instance.resolve(meta, "TURN.md")))
    by_code = {one.code: one.section for one in laws}
    if by_code.get("TB9") == "behavior" and by_code.get("TP9") == "production" \
            and by_code.get("T4") == "behavior":
        held("an overlay adds in the section of its key",
             "TB9 behavior, TP9 production, the kit's T4 migrated to behavior")
    else:
        failures.append(f"  ✗ overlay sections           {by_code}")
    (meta / "procs" / "TURN.md").unlink()

    # --- no law of production in force: no checkpoint -------------------------------------------
    quiet = document(
        "---\nname: QUIET\nkind: proc\ndescription: behavior alone\n"
        "constraints.behavior: |\n  H2  say what you do before you do it\n"
        "proc: |\n  INFER\n  FINAL\n---\nwrite one line\n", at=home.meta)
    first = conductor().start(quiet)
    closing = first if first.wait else conductor().submit("")   # fused, or one step later
    if (first.command == "INFER" and "[-sp]" not in first.next_call
            and closing is not None and closing.wait and closing.output != "proof"
            and "no law of production in force" in render(closing)):
        held("no production law, no checkpoint", "an armed document with behavior laws alone "
             "reaches its FINAL without a proof block; the closing says why")
    else:
        failures.append(f"  ✗ quiet checkpoint           {first.next_call!r} "
                        f"{closing and (closing.output, closing.wait, render(closing)[-160:])!r}")
    conductor().forget()
    return 0
