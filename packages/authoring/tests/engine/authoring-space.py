"""Scenario `authoring-space` -- the authoring package's offer, on the boot and the turn:
- the boot offers AUTHOR, the turn AUTHOR and `pp-authoring`; no door of yesterday rides; the
  package's two signals point to AUTHOR
- `-open AUTHOR` opens the hall as the root: AUTHOR-TABLE plays first, the catalogue of the
  patterns is served
- from the hall, `-open AUTHOR-RULES` stacks the craft as the root; its work proven, the run
  parks in it, and the next message replays the craft without the table
- inside the craft, `pp-authoring section constrain` writes a law the build reads back
- `-close` leaves the craft for the hall, `-close` again gives the turn back
- under the principal's conduction the hall and the craft open and close the same
- the kit alone offers neither AUTHOR nor `pp-authoring`

Two houses: the instance with authoring, and the kit alone for the absence.
"""
from __future__ import annotations

import json

from conductor import compiling, events, reading, render
from tests.harness import cli, principal

CRAFTS = ("AUTHOR-MEMBER", "AUTHOR-RULES", "AUTHOR-OFFERS", "AUTHOR-MIGRATE", "AUTHOR-DESIGN")
GONE = ("PP-MEMBER", "PP-RULES", "PP-OFFERS", "PP-MIGRATE", "PP-DESIGN")
CATALOGUE = "engine/patterns/README.md"
DEMO = "---\nname: DEMO\nkind: proc\ndescription: a document the craft writes into\nproc: |\n  WORK\n---\n\nDo it.\n"


def _names(block) -> set[str]:
    return {one.name for one in block.tools} if block is not None else set()


def _proof(block, evidence: str) -> str:
    return json.dumps([{"code": one.code, "evidence": evidence, "verdict": "ok"}
                       for one in block.constraints])


def _served(block) -> list[str]:
    return [subject for subject, _ in block.payloads] if block is not None else []


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("space", packages=("authoring",))
    env.write("procs/DEMO.md", DEMO)
    compiling.build_tools(env.made)

    def c():
        return env.conductor("t")

    # --- the offer: the hall on the boot and the turn, no door of yesterday -----------
    c().forget()
    boot = c().start(c().boot("BOOT.md"))
    turn = c().submit("")
    offered = _names(boot) | _names(turn)
    if "AUTHOR" in _names(boot) and {"AUTHOR", "pp-authoring"} <= _names(turn) and not offered & set(GONE):
        held("the hall rides the boot and the turn", "AUTHOR offered on both, pp-authoring on the turn, "
             "none of the five doors")
    else:
        failures.append(f"  ✗ the offer                   boot={sorted(_names(boot))} turn={sorted(_names(turn))}")

    doors = {signal: str(events.spec_of(env.made, "authoring", signal).get("door", ""))
             for signal in ("member-bare", "offers-idle")}
    if doors == {"member-bare": "AUTHOR", "offers-idle": "AUTHOR"}:
        held("the signals point to the hall", "member-bare and offers-idle declare door AUTHOR")
    else:
        failures.append(f"  ✗ the signals                 {doors}")

    # --- the hall: the root, its table first, the catalogue served ---------------------
    hall = c().open("AUTHOR")
    shown = render(hall) if hall is not None else ""
    if (hall is not None and hall.root == "AUTHOR" and "AUTHOR-TABLE" in shown
            and any(CATALOGUE in one for one in _served(hall)) and set(CRAFTS) <= _names(hall)):
        held("the hall opens as the root", "root AUTHOR, AUTHOR-TABLE in the output, the catalogue served, "
             "the five crafts offered")
    else:
        failures.append(f"  ✗ the hall                    root={hall and hall.root!r} served={_served(hall)} "
                        f"tools={sorted(_names(hall))}")

    # --- a craft: stacked as the root, proven, parked, replayed without the table ----
    standing = hall
    for _ in range(3):                    # the table said, the hall's WORK pending
        if standing is None or "AUTHOR-TABLE" not in standing.stack:
            break
        standing = c().submit("")
    craft = c().open("AUTHOR-RULES")
    proving = c().submit("")
    parked = c().submit(_proof(proving, "held while drafting")) if proving is not None else None
    again = c().submit("a second message")
    if (craft is not None and craft.root == "AUTHOR-RULES"
            and proving is not None and proving.instruction.keyword == "PROVE"
            and parked is not None and parked.wait
            and again is not None and again.root == "AUTHOR-RULES" and "AUTHOR-TABLE" not in render(again)):
        held("a craft holds the dialogue", "AUTHOR-RULES the root, its PROVE asked, the run parked in it; the "
             "next message replays the craft, the table stays in the hall")
    else:
        failures.append(f"  ✗ the craft                   craft={craft and craft.root!r} "
                        f"proving={proving and proving.instruction} parked={parked and parked.wait} "
                        f"again={again and again.root!r} stack={again and again.stack!r}")

    # --- inside the craft, pp-authoring writes a law the build reads back --------------
    written = cli(env.engine, "t", "-s", "pp-authoring", "section", "constrain", "procs/DEMO.md",
                  "--section", "production", cwd=env.root, stdin="the demo holds its line\n")
    compiling.build_tools(env.made)
    laws = [one.code for one in reading.constraints(reading.read(env.made / "procs" / "DEMO.md"))]
    if written.returncode == 0 and laws:
        held("the craft writes through pp-authoring", f"section constrain from the craft: {laws} in DEMO, the "
             "build passes")
    else:
        failures.append(f"  ✗ the writing                 rc={written.returncode} {written.stderr[-200:]!r} {laws}")

    # --- -close twice: the hall, then the turn ------------------------------------------
    back_hall = c().close()
    back_turn = c().close()
    if (back_hall is not None and back_hall.root == "AUTHOR"
            and back_turn is not None and back_turn.root not in ("AUTHOR", "AUTHOR-RULES")
            and "AUTHOR" not in back_turn.stack):
        held("-close twice gives the turn back", f"the craft leaves for the hall, the hall for the root "
             f"{back_turn.root}")
    else:
        failures.append(f"  ✗ the closing                 {back_hall and back_hall.root!r} "
                        f"{back_turn and back_turn.root!r}")
    c().forget()

    # --- the principal's conduction: the same spaces -----------------------------------
    opener = env.conductor()
    opener.forget()
    principal(lambda: opener.start(opener.boot("BOOT.md")))
    key = opener.run_id
    principal(lambda: env.conductor(key).submit(""))
    led_hall = principal(lambda: env.conductor(key).open("AUTHOR"))
    led_craft = principal(lambda: env.conductor(key).open("AUTHOR-MEMBER"))
    led_back = principal(lambda: env.conductor(key).close())
    if (led_hall is not None and led_hall.root == "AUTHOR" and led_craft is not None
            and led_craft.root == "AUTHOR-MEMBER" and led_back is not None and led_back.root == "AUTHOR"):
        held("both conductions open the same spaces", "under the principal: AUTHOR, then AUTHOR-MEMBER, "
             "-close back to the hall")
    else:
        failures.append(f"  ✗ the principal's spaces      {led_hall and led_hall.root!r} "
                        f"{led_craft and led_craft.root!r} {led_back and led_back.root!r}")
    env.conductor(key).forget()

    # --- the kit alone: the absence ------------------------------------------------------
    bare = bench.env("space-kit")
    runner = bare.conductor("k")
    runner.forget()
    bare_boot = runner.start(runner.boot("BOOT.md"))
    bare_turn = bare.conductor("k").submit("")
    if not ((_names(bare_boot) | _names(bare_turn)) & {"AUTHOR", "pp-authoring"}):
        held("the kit alone offers no author tool", "neither AUTHOR nor pp-authoring")
    else:
        failures.append(f"  ✗ the absence                 {sorted(_names(bare_boot) | _names(bare_turn))}")
    bare.conductor("k").forget()
    return 0
