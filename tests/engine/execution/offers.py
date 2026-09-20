"""Scenario `offers` -- 1 case(s), in the monolith's order:
- R7.11 l-offre-suit-la-section: the offer lives with its OUTPUT
"""
from __future__ import annotations

import re

from pathlib import Path
from conductor import Conductor, render, revive, discovery, persistence


def scenario(bench) -> int:
    held, expect, failures = bench.held, bench.expect, bench.failures
    # --- R7.11 l-offre-suit-la-section: the offer lives with its OUTPUT --------------
    rt_made = bench.env("rt", pin=False).made
    rt_member = discovery.instance_member(rt_made / ".sys" / "engine" / "pp.py")
    rt_engine = rt_made / ".sys" / "engine" / "pp.py"

    def rt_c() -> Conductor:
        return Conductor(rt_member, discovery.siblings_around(rt_member), rt_engine, "t")

    (rt_made / "DOOR.md").write_text(
        "---\nname: DOOR\nkind: proc\ndescription: a door\nconstraints.behavior: |\n"
        "  D1  the door law\nproc: |\n  INFER\n---\nthe door speaks\n",
        encoding="utf-8")
    (rt_made / "RINNER.md").write_text(
        "---\nname: RINNER\nkind: proc\ndescription: inner\nconstraints.behavior: |\n"
        "  I1  the inner law\ntools: |\n  note-taker\nproc: |\n  INFER\n---\n"
        "inner speaks\n", encoding="utf-8")
    (rt_made / "ROUTER.md").write_text(
        "---\nname: ROUTER\nkind: proc\ndescription: outer\nconstraints.behavior: |\n"
        "  O1  the outer law\ntools: |\n  DOOR\nproc: |\n  INFER\n  CALL RINNER.md\n"
        "  FINAL\n---\nspeak then call\n", encoding="utf-8")
    routed_out = rt_c().start(rt_made / "ROUTER.md")
    routed_text = render(routed_out)
    if ("▌ pp · run t · " in routed_text                # the output's heading says its key
            and "▌ [1] ROUTER{" in routed_text
            and "▌ [2] ROUTER ▸ RINNER{" in routed_text):
        held("a multi-heading output numbers its segments", "`[n]` on each heading -- "
             "the address a `-s` gesture routes by; a single-heading output stays bare")
    else:
        failures.append(f"  ✗ segment numbering           {routed_text.splitlines()[0]!r}")
    rt_hit = rt_c().route("note-taker")
    if (rt_hit is not None and rt_hit["ordinal"] == 2 and rt_hit["frame"] == "RINNER"
            and any(one.endswith("I1  the inner law") for one in rt_hit["constraints"])   # the wire form: the section rides the snapshot
            and rt_c().route("absent-name") is None):
        held("a single owner routes without a number", "the popped segment's own list "
             "answers -- scope PER SEGMENT, never a union; offered nowhere stays None")
    else:
        failures.append(f"  ✗ route single owner          {rt_hit!r}")
    expect("address-ambiguous", lambda: rt_c().route("DOOR"))
    rt_at = rt_c().route("DOOR", at=1)
    if rt_at is not None and rt_at["frame"] == "ROUTER":
        held("the number departages", "DOOR lives in [1] and inherited in [2] -- bare "
             "refuses naming both, `@1` settles it")
    else:
        failures.append(f"  ✗ route addressed             {rt_at!r}")
    rt_c().resume(rt_made / "ROUTER.md")
    if rt_c().route("note-taker") is not None:
        held("a re-show keeps the addresses", "resume replaces nothing -- the map lives "
             "with its output, not with the process")
    else:
        failures.append("  ✗ resume keeps map")
    rt_entry = rt_c().route("note-taker")
    rt_door = rt_c().play("DOOR", route=rt_entry)
    rt_door_text = render(rt_door) if rt_door else ""
    rt_state = persistence.restore(persistence.slot_of(rt_member.meta, "t"), revive)
    rt_call = next(one for one in rt_state[1].frames[0].procedure.instructions
                   if one.keyword == "CALL" and one.argument == "RINNER.md")
    if ("(routed from [2] RINNER)" in rt_door_text
            and re.search(r"\bI1\b", rt_door_text)   # the inherited law: its text, or its code under medium (codes after the first emission)
            and rt_call.done):
        held("a routed door stacks at the pending step", "0 unwind -- the crossed CALL "
             "stays resolved; the door inherits the OWNING segment's snapshotted laws "
             "(the popped frame's own), and its entry heading says the route")
    else:
        failures.append(f"  ✗ routed door                 call_done={rt_call.done} "
                        f"{rt_door_text.splitlines()[:1]!r}")
    expect("address-stale", lambda: rt_c().route("note-taker", at=2))
    held("addresses live with their output", "the door rendered a fresh output: the old "
         "map is gone -- a kept number refuses by name, never lands elsewhere")

    barred_doc = rt_made / "BARRED.md"
    barred_doc.write_text(
        "---\nname: BARRED\nkind: proc\ndescription: strict order\ntools: |\n  DOOR\n"
        "proc: |\n  INFER\n  §\n  INFER\n  FINAL\n---\nspeak twice\n",
        encoding="utf-8")
    rt_c().forget()
    barred = rt_c().start(barred_doc)
    rt_bar = rt_c().route("DOOR")
    if (barred is not None and "[1]" not in render(barred)
            and rt_bar is not None and rt_bar["ordinal"] == 1):
        held("the author's § holds the offer at the seam", "the output closes at the "
             "barrier and the offering step's own list answers the gesture there -- "
             "a single-heading output carries no number")
    else:
        failures.append(f"  ✗ barrier strict order        {rt_bar!r} "
                        f"{barred and render(barred)[:60]!r}")
    return 0
