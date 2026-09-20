"""Scenario `next-at-turn-end` -- the steering surface attaches to the turn (plan
pp-split, phase steering, batch le-hook-de-pilotage):
- the kit alone closes an exchange on the work: no block at the empty socket, no NEXT
- kit + steering opens NEXT after the work, in its own output, before the closing
- a second contributor of the same socket stands beside NEXT in one exchange; which one
  first is nobody's business here -- the socket's order is the engine's, asserted nowhere
- the surface reads its OWN front: on kit + steering alone, the NEXT block carries the
  `steering-threads` table with the open thread (batch steering / le-proc-next /
  le-front-au-next)
"""
from __future__ import annotations

import re

from conductor import compiling, instance, render
from tests.harness import SOURCE, kept_document, load_script, na_proof


def _exchanges(env, count: int) -> list[list]:
    """Drives `count` exchanges after the boot; -> the blocks of each exchange, from the
    work's own output to the closing -- every turn.end contributor stands among them."""
    all_blocks = []
    opener = env.conductor("t")
    opener.start(opener.boot("BOOT.md"))            # the boot fuses up to the WORK step
    for n in range(1, count + 1):
        if n > 1:
            env.conductor("t").submit("a message")   # the operator's message: the WORK
        blocks, pending, steps = [], env.conductor("t").submit(""), 0
        while pending is not None and steps < 8:
            steps += 1
            blocks.append(pending)
            if "INFER proof" in render(pending):
                env.conductor("t").submit(na_proof(pending))   # the checkpoint: proven n/a
                break
            if "FINAL" in (pending.next_call or ""):
                break
            pending = env.conductor("t").submit("")
        all_blocks.append(blocks)
    return all_blocks


def _documents(blocks) -> set:
    return {one.document for one in blocks if one is not None}


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- the kit alone: the socket is empty, the turn goes from the work to the closing ------
    bare = bench.env("nxkit")
    exchanges = _exchanges(bare, 3)
    documents = set().union(*(_documents(one) for one in exchanges))
    tables = [render(one) for group in exchanges for one in group if "| thread" in render(one)]
    if "NEXT" not in documents and not tables:
        held("the kit alone closes without NEXT",
             "three exchanges: no block at the empty socket, no threads table -- FINAL stands on its own")
    else:
        failures.append(f"  ✗ kit alone                  {sorted(documents)} tables={len(tables)}")

    # --- kit + steering: NEXT opens after the work ---------------------------------------------
    steer = bench.env("nxsteer", packages=("steering",))
    opened = ["NEXT" in _documents(one) for one in _exchanges(steer, 3)]
    if all(opened):
        held("kit + steering opens NEXT after the work",
             "every exchange: the turn.end contributor renders its own output before the closing")
    else:
        failures.append(f"  ✗ next at turn.end           {opened}")

    # --- two contributors stand together, in whichever order the engine gives them ------------
    both = bench.env("nxboth", packages=("steering",))
    # the witness is the instance's own document: the area composes nothing it does not require
    both.write("procs/ZWITNESS.md",
               "---\nname: ZWITNESS\nkind: proc\ndescription: a witness attached at turn.end\n"
               "attach: turn.end\noutput: line\nproc: |\n  WORK\n---\n\nZWITNESS says hi\n")
    compiling.build_tools(both.made)
    attached = set(instance.attached(both.made, "turn.end"))
    together = _documents(_exchanges(both, 1)[0])
    if attached == {"THREADS.md", "ZWITNESS.md"} and {"NEXT", "ZWITNESS"} <= together:
        held("two contributors of turn.end render",
             "the surface and a witness open in the same exchange -- the order is the engine's, asserted nowhere")
    else:
        failures.append(f"  ✗ two contributors           attached={sorted(attached)} together={sorted(together)}")

    # --- the surface reads its own FRONT: kit + steering, no other consumer of the token -------
    front = bench.env("nxfront", packages=("steering",))
    keeper = load_script(next((front.made / ".sys" / "vendor").glob("steering@*"))
                         / "skills" / "pp-steering" / "pp-steering.py")
    keeper.open_thread(front.made, "le-fil-du-front", "le-pas-du-front | the step the surface must show\n")
    surface = [render(one) for one in _exchanges(front, 1)[0] if one.document == "NEXT"]
    shown = surface[0] if surface else ""
    if ("INFORMATION — steering-threads" in shown and "| le-fil-du-front |" in shown
            and "| `le-pas-du-front` |" in shown and "| threads | shipped |" not in shown
            and "the step the surface must show" not in shown):
        held("the surface reads its own front",
             "kit + steering alone: the NEXT block carries `steering-threads` -- the table with the open "
             "thread and the NAME of its pointed step, its text left out -- with no improvement or "
             "federation to consume the token")
    else:
        failures.append(f"  ✗ the surface reads its own front   {(shown[:200] if shown else 'no NEXT block')!r}")

    # --- the front of the moment at the NEXT block: a thread whose steps all wait has no row --
    # its waiting step reaches the ⏸ line with its reason; the thread with a step to do keeps its row
    waiting = bench.env("nxwait", packages=("steering",))
    keeper = load_script(next((waiting.made / ".sys" / "vendor").glob("steering@*"))
                         / "skills" / "pp-steering" / "pp-steering.py")
    keeper.open_thread(waiting.made, "le-fil-actif", "a-un | the step to do\n", note="the thread of the moment")
    keeper.open_thread(waiting.made, "le-fil-en-attente", "w-un | the waiting step\n")
    record = keeper.load(waiting.made)
    parked = next(tid for tid, one in record["threads"].items() if one["name"] == "le-fil-en-attente")
    keeper.block(waiting.made, parked, record["threads"][parked]["steps"][0], "waits for the release")
    shown = next((render(one) for one in _exchanges(waiting, 1)[0] if one.document == "NEXT"), "")
    rows = [line for line in shown.splitlines() if line.startswith("| ") and not line.startswith("| initiative |")]
    if (any(row.startswith("| le-fil-actif | the thread of the moment |") for row in rows)
            and not any(row.startswith("| le-fil-en-attente |") for row in rows)
            and "⏸ le-fil-en-attente › `w-un` (waits for the release)" in shown):
        held("the front of the moment at the NEXT block",
             "the thread with a step to do keeps its row and its note; the thread whose steps all wait "
             "has none, its step reaches the ⏸ line with its reason")
    else:
        failures.append(f"  ✗ the front of the moment     rows={rows} {shown[-300:]!r}")
    return 0
