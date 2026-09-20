"""Scenario `final-names` -- 5 case(s):
- les-noms-dans-l-ordre: three drafts of three documents are named on the FINAL line, in step order
- un-document-un-nom: two consecutive drafts of one document give one name; a return keeps its place
- le-final-nu: a turn whose one step speaks chat closes on a bare FINAL
- l-adjacent-brouillon: a step adjacent to the frontier while a draft stands is a draft, and named
- l-etat-nomme: the slot holds the names, empties at the delivery and after `-compacted`
"""
from __future__ import annotations

import json

from conductor import render

WITNESS = "---\nname: {name}\nkind: proc\ndescription: a witness\nproc: |\n{steps}---\n{name} speaks\n"


def closing(block) -> str:
    """-> the closing line of a rendered block: the one the arrow opens."""
    return next(line for line in render(block).splitlines() if line.startswith("▶ "))


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    env = bench.env("final-names", pin=False)
    for name in ("ALPHA", "BRAVO", "CHARLIE"):
        env.write(f"{name}.md", WITNESS.format(name=name, steps="  INFER\n"))
    env.write("TWICE.md", WITNESS.format(name="TWICE", steps="  INFER\n  INFER\n"))

    def root(name: str, steps: str):
        path = env.write(f"{name}.md", WITNESS.format(name=name, steps=steps))
        env.conductor().forget()
        conductor = env.conductor()
        return conductor.start(path)

    # --- les-noms-dans-l-ordre -----------------------------------------------------------
    trio = root("TRIO", "  CALL ALPHA.md\n  CALL BRAVO.md\n  CALL CHARLIE.md\n  FINAL\n")
    if trio.wait and closing(trio) == "▶ FINAL ephemerals => chat (ALPHA · BRAVO · CHARLIE)":
        held("the FINAL names its drafts", "three documents, three drafts, their names in step order")
    else:
        failures.append(f"  ✗ names in order              {closing(trio)!r}")

    # --- un-document-un-nom ----------------------------------------------------------------
    twice = root("TWICER", "  CALL TWICE.md\n  CALL ALPHA.md\n  FINAL\n")
    back = root("BACK", "  CALL ALPHA.md\n  CALL BRAVO.md\n  CALL ALPHA.md\n  FINAL\n")
    if (closing(twice) == "▶ FINAL ephemerals => chat (TWICE · ALPHA)"
            and closing(back) == "▶ FINAL ephemerals => chat (ALPHA · BRAVO · ALPHA)"):
        held("one document, one name", "two drafts in a row of TWICE are one production; ALPHA "
             "coming back after BRAVO keeps both its places")
    else:
        failures.append(f"  ✗ one name per rendering      {closing(twice)!r} / {closing(back)!r}")

    # --- le-final-nu ------------------------------------------------------------------------
    bare = root("BARE", "  WORK\n  FINAL\n")
    if bare.wait and closing(bare) == "▶ FINAL" and "WORK free => chat" in render(bare):
        held("no draft, a bare FINAL", "the step adjacent to the frontier speaks chat and names nothing")
    else:
        failures.append(f"  ✗ bare FINAL                  {closing(bare)!r}")

    # --- l-adjacent-brouillon ---------------------------------------------------------------
    joined = root("JOINED", "  CALL ALPHA.md\n  INFER\n  FINAL\n")
    if (joined.wait and "INFER free => ephemeral" in render(joined)
            and closing(joined) == "▶ FINAL ephemerals => chat (ALPHA · JOINED)"):
        held("an adjacent draft is named", "a draft stands: the step adjacent to the frontier is a "
             "draft too, and its document closes the list")
    else:
        failures.append(f"  ✗ adjacent draft              {closing(joined)!r}")

    # --- l-etat-nomme: step by step, each draft is closed bare by its own call -----------
    steps = bench.env("final-names-steps")
    for name in ("ALPHA", "BRAVO"):
        steps.write(f"{name}.md", WITNESS.format(name=name, steps="  INFER\n"))

    def drafts() -> object:
        return json.loads(steps.session().read_text(encoding="utf-8")).get("ephemerals")

    conductor = steps.conductor()
    conductor.start(steps.write("PAUSE.md", WITNESS.format(
        name="PAUSE", steps="  CALL ALPHA.md\n  WORK\n  CALL BRAVO.md\n  FINAL\n")))
    key = conductor.run_id
    seen = [drafts()]
    for _ in range(2):
        steps.conductor(key).submit("")
        seen.append(drafts())
    delivered = steps.conductor(key).submit("")
    seen.append(drafts())
    steps.conductor().forget()
    conductor = steps.conductor()
    conductor.start(steps.write("HALF.md", WITNESS.format(
        name="HALF", steps="  CALL ALPHA.md\n  WORK\n  CALL BRAVO.md\n  FINAL\n")))
    steps.conductor(conductor.run_id).submit("")
    before = drafts()
    steps.conductor(conductor.run_id).compacted()
    if (seen == [[], ["ALPHA"], ["ALPHA", "PAUSE"], []]
            and closing(delivered) == "▶ FINAL ephemerals => chat (ALPHA · PAUSE · BRAVO)"
            and before == ["ALPHA"] and drafts() == []):
        held("the slot holds the names", "each draft closed bare joins under its document's "
             "name; the delivery and a compaction empty the list")
    else:
        failures.append(f"  ✗ named state                 {seen!r} / {before!r} -> {drafts()!r} / "
                        f"{closing(delivered)!r}")
    return 0
