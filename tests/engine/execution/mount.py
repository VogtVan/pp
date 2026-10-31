"""Scenario `mount` -- a mount re-shows the standing step: the pointer stands.
The mount itself -- its view, its proof, its sweep, its nested scope, its refusals and the
`::mount` directive -- is the pattern `composition/mount`; a mounted document's overlay is
`composition/overlay`; the readings a mount serves and its selections are `context/serve`; the
lint of a `proc:` outside a played kind is `context/doc`.
What crosses a mount: a door routed from a nested mount keeps the sections of its laws (its
behavior law never asked at the PROVE); a `+name` a mounted document offers is adopted, bare;
a door played on a parked run leaves no mount of its socket behind.
"""
from __future__ import annotations

from conductor import Conductor, navigation, persistence, render, revive

FUSED = "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n"
WORKP = "---\nname: WORKP\nkind: proc\nproc: |\n  WORK\n  §\n  PROVE\n---\nwork\n"
NESTED = ("---\nname: NESTED\nkind: doc\nconstraints.behavior: |\n  NB1  behave plainly.\n"
          "tools: |\n  DOORN\n---\n\nthe nested scope\n")
DOORN = ("---\nname: DOORN\nkind: proc\ndescription: a door the nested scope offers\n"
         "constraints.production: |\n  DN1  the door's line lands.\nproc: |\n  INFER\n  PROVE\n---\ndoor\n")
OFFERER = "---\nname: OFFERER\nkind: doc\ntools: |\n  +revue\n---\n\noffers a harness skill\n"
REVUE = "---\nname: revue\ndescription: a review from the harness\n---\nreview the work\n"
PARKS = "---\nname: PARKS\nkind: proc\nproc: |\n  INFER\n---\nparks\n"
DOORS = ("---\nname: DOORS\nkind: proc\ndescription: a door that hooks\nproc: |\n"
         "  HOOK doors.open\n  INFER\n---\nthe door\n")
SOCKM = ("---\nname: SOCKM\nkind: doc\nmount: doors.open\nconstraints.behavior: |\n"
         "  SM1  the socket's law.\n---\n\nthe socket's matter\n")


def recharge(bench) -> None:
    """A mount re-shows the standing step: at the TURN the output closes at the `§` after
    WORK; the mount re-shows the asked step in the richer context, the pointer where it was,
    the `@n` addresses routing, and the next bare call is the one that crosses."""
    held, failures = bench.held, bench.failures
    env = bench.env("rechw")
    env.write("SETTINGS.md", "---\nname: SETTINGS\nkind: doc\ninstructions_fusion: max\n---\n")
    env.write("RICH.md", "---\nname: RICH\nkind: doc\nconstraints.production: |\n  R1  the richer law binds.\n"
                         "tools: |\n  RICHTOOL\n---\n\nThe richer context.\n")

    def rch_c() -> Conductor:
        return env.conductor("t")

    rch_c().start(rch_c().boot("BOOT.md"))     # the boot flows into the TURN, closed at the `§`
    rch_slot = persistence.slot_of(env.made, "t")
    rch_before = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_before = navigation.current(rch_before)
    rch_pos_before = (rch_frame_before.document.name, navigation.position(rch_frame_before))
    rch_out = rch_c().mount([{"doc": "RICH.md", "scope": "nested", "body": True}])
    rch_after = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_after = navigation.current(rch_after)
    rch_pos_after = (rch_frame_after.document.name, navigation.position(rch_frame_after))
    rch_shown = rch_c().peek()
    rch_routed = rch_c().route("RICHTOOL", 1)   # offered by [1] RICH and [2] TURN: addressed
    rch_next = rch_c().forward("")              # the bare call crosses the `§`
    if (rch_pos_before == rch_pos_after and rch_pos_before[0] == "TURN"
            and "▸ RICH" in rch_out and "The richer context." in rch_out
            and "WORK" in rch_out and "proof" not in rch_out
            and rch_shown is not None and rch_shown.command == "WORK"
            and rch_routed is not None
            and rch_next is not None and rch_next.instruction.keyword == "PROVE"):
        held("a mount re-shows the standing step",
             "the pointer stands at the `§`, WORK re-shown with the mounted scope, the "
             "address routes -- the bare call after it crosses to the checkpoint")
    else:
        failures.append(f"  ✗ mount recharge              before={rch_pos_before} after={rch_pos_after} "
                        f"shown={rch_shown and rch_shown.command!r} routed={rch_routed is not None} "
                        f"next={rch_next and rch_next.instruction.keyword!r} "
                        f"out={rch_out[:200]!r}")


def crossings(bench) -> None:
    """What crosses a mount, and what a parked run keeps: the sections of a routed door's laws,
    the `+name` of a mounted document, the socket mount of a door played on a parked run."""
    held, failures = bench.held, bench.failures
    env = bench.env("mcross")
    env.write("SETTINGS.md", FUSED)
    for name, text in (("WORKP", WORKP), ("DOORN", DOORN), ("PARKS", PARKS), ("DOORS", DOORS),
                       ("SOCKM", SOCKM)):
        env.write(f"procs/{name}.md", text)
    env.write("NESTED.md", NESTED)
    env.write("OFFERER.md", OFFERER)
    harness = env.root / ".claude" / "skills" / "revue"
    harness.mkdir(parents=True)
    (harness / "SKILL.md").write_text(REVUE, encoding="utf-8")

    def c() -> Conductor:
        return env.conductor("t")

    # --- a door routed from a nested mount keeps the sections of its laws ----------------------
    c().start(c().boot("WORKP.md"))
    c().mount([{"doc": "NESTED.md", "scope": "nested"}])
    entry = c().route("DOORN")
    door = c().play("DOORN", route=entry) if entry is not None else None
    hops = 0
    while door is not None and door.instruction.keyword != "PROVE" and not door.wait and hops < 4:
        door = c().forward("")
        hops += 1
    lines = entry.get("constraints", []) if entry is not None else []
    if (any(line.startswith("behavior:") and "NB1" in line for line in lines)
            and door is not None and list(door.judged) == ["DN1"]):
        held("a routed door keeps the sections of its laws", "the nested segment maps NB1 as a "
             "behavior law; the door's PROVE asks DN1 alone")
    else:
        failures.append(f"  ✗ routed sections             {lines} judged={door and list(door.judged)}")
    c().forget()

    # --- a `+name` a mounted document offers is adopted, bare ----------------------------------
    c().start(c().boot("WORKP.md"))
    shown = c().mount([{"doc": "OFFERER.md"}])
    offered = c().route("revue")
    opened = c().play("revue", route=offered) if offered is not None else None
    if (offered is not None and "+revue" not in shown and opened is not None
            and "▸ revue{" in render(opened)):
        held("a mounted `+name` is adopted", "OFFERER offers `+revue`: the block offers `revue`, "
             "the route finds it, the harness skill opens as a frame")
    else:
        failures.append(f"  ✗ mounted offer               route={offered} "
                        f"{[one for one in shown.splitlines() if 'revue' in one]} {opened and opened.stack!r}")
    c().forget()

    # --- a door played on a parked run leaves no mount of its socket behind --------------------
    parked = c().start(c().boot("PARKS.md"))
    played = c().play("DOORS")
    hops = 0
    while played is not None and not played.wait and hops < 4:
        played = c().forward("")
        hops += 1
    left = [one.get("doc") for one in persistence.mounted_of(persistence.slot_of(env.made, "t"))]
    standing = c().peek()
    if (parked is not None and parked.wait and played is not None and played.wait
            and "SOCKM.md" not in left and standing is not None and "SM1" not in render(standing)):
        held("a door on a parked run leaves no mount", "DOORS mounts SOCKM at its socket and leaves; "
             "the run parks again with nothing mounted, its AWAIT without SM1")
    else:
        failures.append(f"  ✗ parked door mount           mounted={left} wait={played and played.wait}")
    c().forget()


def scenario(bench) -> int:
    recharge(bench)
    crossings(bench)
    return 0
