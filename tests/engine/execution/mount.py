"""Scenario `mount` -- a mount re-shows the standing step: the pointer stands.
The mount itself -- its view, its proof, its sweep, its refusals and the `::mount` directive -- is
the pattern `composition/mount`; a mounted document's overlay is `composition/overlay`; the
readings a mount serves and its selections are `context/serve`; the lint of a `proc:` outside a
played kind is `context/doc`.
A mount makes NO segment: the view a mount shows counts the segments the view counted before it,
the body it serves a reading at the head of the segment of the step that stands, its laws and its
offers in that segment's; an entry that carries the key `scope` -- whatever its value, by the
facade or by a script's `::mount` -- refuses `mount-invalid`, nothing written at the run.
What crosses a mount: a door routed from the segment a mount's offer stands in keeps the sections
of its laws (its behavior law never asked at the PROVE); a `+name` a mounted document offers is
adopted, bare; a door played on a parked run leaves no mount of its socket behind.
The closing of a passage played under a mount that carries a law stands in the segment of its steps: the
sweep of the passage's mounts opens no segment -- a door opened on the pending step says the last step of
the passage.
A batch mounted in place of another (s.1581): the laws of the new batch reach the agent as text once, then
as codes -- an order block that carries a mount's readings without its laws counts none of them said.
The system laws are in force at every block -- the boot and the TURN, a mount, a routed door, its repair, an
open space --, each output saying them whole; the proof names the system law of production, never one of
behavior; a mounted document that declares a system law's code refuses `mount-collision`.
"""
from __future__ import annotations

import json

from conductor.core import messages
from conductor import Conductor, compiling, context, navigation, persistence, render, revive
from conductor.core import language
from tests.harness import printed, stepped, support, titled, titles

run = support(__file__, "run")

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
    rch_out = rch_c().mount([{"doc": "RICH.md", "body": True}])
    rch_after = rch_c()._rebind(persistence.restore(rch_slot, revive))
    rch_frame_after = navigation.current(rch_after)
    rch_pos_after = (rch_frame_after.document.name, navigation.position(rch_frame_after))
    rch_shown = rch_c().peek()
    rch_routed = rch_c().route("RICHTOOL")      # offered by the one segment of the step that stands
    rch_next = printed(env, "t")                # the WORK handed: its print crosses the `§`
    if (rch_pos_before == rch_pos_after and rch_pos_before[0] == "TURN"
            and titled(language.INFORMATION, "RICH") in titles(rch_out) and "The richer context." in rch_out
            and "WORK" in rch_out and "proof" not in rch_out
            and rch_shown is not None and rch_shown.command == "WORK"
            and rch_routed is not None
            and rch_next is not None and rch_next.instruction.keyword == "PROVE"):
        held("a mount re-shows the standing step",
             "the pointer stands at the `§`, WORK re-shown with the mounted matter, the "
             "offer routes -- the bare call after it crosses to the checkpoint")
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

    # --- a door routed from the segment of a mount's offer keeps the sections of its laws -------
    c().start(c().boot("WORKP.md"))
    c().mount([{"doc": "NESTED.md"}])
    entry = c().route("DOORN")
    door = c().play("DOORN", route=entry) if entry is not None else None
    hops = 0
    while door is not None and door.instruction.keyword != "PROVE" and not door.wait and hops < 4:
        door = c().forward("")
        hops += 1
    lines = entry.get("constraints", []) if entry is not None else []
    if (any(line.startswith("behavior:") and "NB1" in line for line in lines)
            and door is not None and list(door.judged) == ["DN1"]):
        held("a routed door keeps the sections of its laws", "the segment of the mount's offer maps NB1 "
             "as a behavior law; the door's PROVE asks DN1 alone")
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
    c().start(c().boot("PARKS.md"))                  # its INFER stands pending: the principal's call parks it
    parked = stepped(lambda: c())
    played = c().play("DOORS")
    hops = 0
    while played is not None and not played.wait and hops < 4:
        played = stepped(lambda: c(), by="forward")    # the door's line handed, then the principal's bare call
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


CUT = "---\nname: SETTINGS\nkind: doc\nverbatim_constraints: false\ninstructions_fusion: max\n---\n"
PROMPT_CAP = {context.PROMPT_CAP: "2000"}   # the cap the launcher names for the prompt: the outputs cut under it
LOTA = ("---\nname: LOTA\nkind: doc\nconstraints.production: |\n  LA1  the first batch's law holds.\n---\n\n"
        + "\n".join(f"the first batch, line {n}" for n in range(120)) + "\n")
LOTB = ("---\nname: LOTB\nkind: doc\nconstraints.production: |\n  LB1  the replacing batch's law holds.\n---\n\n"
        + "\n".join(f"the replacing batch, line {n}" for n in range(120)) + "\n")


def replaced(bench) -> None:
    """A batch mounted in place of another, in the codes mode, under a cap (s.1581): each mount re-shows the
    step that stands, an order block that carries the batch's body and none of its laws, its output cut and
    its rest served chunk by chunk. LOTB mounts in place of LOTA (`replaces`); the text of LB1 reaches the
    agent once -- in the first output whose CONSTRAINTS carry it --, then its code alone."""
    held, failures = bench.held, bench.failures
    env = bench.env("mreplaced")
    env.write("SETTINGS.md", CUT)
    env.write("procs/WORKP.md", WORKP)
    env.write("LOTA.md", LOTA)
    env.write("LOTB.md", LOTB)
    law = "LB1  the replacing batch's law holds."

    def c() -> Conductor:
        return env.conductor("t")

    def drained(first: str) -> list[str]:
        out, hops = [first], 0
        while c().pending() and hops < 20:
            out.append(c().next_chunk())
            hops += 1
        return out

    def played():
        c().start(c().boot("WORKP.md"))
        said = drained(c().mount([{"doc": "LOTA.md", "body": True}]))
        swapped = drained(c().mount([{"doc": "LOTB.md", "body": True, "replaces": ["LOTA.md"]}]))
        said += swapped
        crossed = c().forward("")
        said.append(c().rendered(crossed) if crossed is not None else "")
        return said, swapped, c().peek()

    said, swapped, after = run.under(PROMPT_CAP, played)
    later = render(after) if after is not None else ""
    texts = [one for one in said if law in one]
    first = next((rank for rank, one in enumerate(said) if "LB1" in one), None)
    mounted = [one.get("doc") for one in persistence.mounted_of(persistence.slot_of(env.made, "t"))]
    if (mounted == ["LOTB.md"] and len(swapped) > 1 and len(texts) == 1 and first is not None
            and law in said[first] and "LB1" in later and law not in later):
        held("a batch mounted in place of another says its laws once",
             f"LOTB replaces LOTA, its output cut in {len(swapped)} chunks without its laws: LB1's text reaches "
             f"the agent once, in output {first + 1} of {len(said)}, then its code alone")
    else:
        failures.append(f"  ✗ replaced batch laws         mounted={mounted} chunks={len(swapped)} texts={len(texts)} "
                        f"first={first} code_later={'LB1' in later} text_later={law in later} outputs={len(said)}")
    c().forget()


RICH = ("---\nname: RICH\nkind: doc\nconstraints.production: |\n  R1  the richer law binds.\n"
        "tools: |\n  RICHTOOL\n---\n\nThe richer context.\n")
OTHER = "---\nname: OTHER\nkind: doc\n---\n\nanother matter\n"
DIRECTIVE = "def main(argv):\n    print('::mount ' + argv[0])\n    return 0\n"


def _headings(shown: str) -> list[str]:
    """-> the headings of a rendering's segments: its marked lines that open no section of the engine's list."""
    mark = f"{messages.MARK} "
    return [one for one in titles(shown)
            if one.startswith(mark) and not language.section_of(one.removeprefix(mark))[0]]


def no_segment(bench) -> None:
    """A mount makes no segment, and the key `scope` is refused."""
    import pp                                                                 # noqa: PLC0415
    held, expect, failures = bench.held, bench.expect, bench.failures
    env = bench.env("mflat")
    env.write("SETTINGS.md", FUSED)
    env.write("RICH.md", RICH)
    env.write("OTHER.md", OTHER)
    probe = env.write("probe-mount.py", DIRECTIVE)

    def c() -> Conductor:
        return env.conductor("t")

    c().start(c().boot("BOOT.md"))             # the boot flows into the TURN: its WORK stands
    standing = c().peek()
    before = render(standing) if standing is not None else ""
    out = c().mount([{"doc": "RICH.md", "body": True}])
    shown = titles(out)
    reading = titled(language.INFORMATION, "RICH")
    order = [shown.index(one) if one in shown else -1
             for one in (reading, titled(language.TOOLS), titled(language.CONSTRAINTS), titled(language.INSTRUCTION))]
    lines = out.splitlines()
    offered = next((one for one in lines if one.startswith("[") and "RICHTOOL" in one.strip("[]").split()), "")
    if (len(_headings(before)) == 1 and len(_headings(out)) == 1
            and order == sorted(order) and order[0] > 0 and shown.count(reading) == 1
            and [one for one in lines if one.startswith("R1 ")] and offered
            and len(persistence.segments_of(persistence.slot_of(env.made, "t"))) == 1):
        held("a mount makes no segment", f"`{_headings(out)[0]}` before the mount and after it: RICH's body a "
             "reading at the head of that segment, RICHTOOL in its offers, R1 in its laws, one entry in the "
             "offer map")
    else:
        failures.append(f"  ✗ a mount and its segment     before={_headings(before)} after={_headings(out)} "
                        f"order={order} offered={offered!r} {shown}")

    # --- the key `scope` is refused, whatever it says, and nothing is written -----------------------
    slot = persistence.slot_of(env.made, "t")
    frozen = slot.read_bytes()

    def directive(entries: list) -> None:
        pp._played(c(), probe, [json.dumps(entries)], "probe-mount")

    expect("mount-invalid", lambda: c().mount([{"doc": "OTHER.md", "scope": "own", "body": True}]))
    expect("mount-invalid", lambda: directive([{"doc": "OTHER.md", "scope": "stacked"}]))
    mounted = [one.get("doc") for one in persistence.mounted_of(slot)]
    if slot.read_bytes() == frozen and mounted == ["RICH.md"]:
        held("a refused entry writes nothing", "the slot byte for byte after the two refusals, RICH alone mounted")
    else:
        failures.append(f"  ✗ a refused entry             same={slot.read_bytes() == frozen} mounted={mounted}")
    c().forget()


HOSTP = "---\nname: HOSTP\nkind: proc\ntools: |\n  SIDED\nproc: |\n  WORK\n---\nhost\n"
SIDED = ("---\nname: SIDED\nkind: proc\noutput: any\ndescription: a door that does the work of the step that "
         "opens it\nproc: |\n  WORK\n---\nside\n")
LAWED = "---\nname: LAWED\nkind: doc\nconstraints.behavior: |\n  LW1  the mounted law binds.\n---\n\nlawed\n"


def _asked(shown: str) -> list[str]:
    """-> the document each step line of a rendering names, in order."""
    return [one.rsplit("(", 1)[-1].rstrip(")") for one in shown.splitlines()
            if one.startswith(("INFER ", "WORK ")) and one.endswith(")")]


def closing_scope(bench) -> None:
    """The closing of a passage is judged under the scope of the passage: played under a mount that carries a
    law, it joins the segment of its steps."""
    held, failures = bench.held, bench.failures
    env = bench.env("mclose")
    env.write("SETTINGS.md", FUSED)
    for name, text in (("HOSTP", HOSTP), ("SIDED", SIDED), ("LAWED", LAWED)):
        env.write(f"{name}.md", text)

    led = env.conductor()
    led.forget()
    led.start(env.made / "HOSTP.md")                       # the WORK stays pending for the principal
    led_key = led.run_id
    env.conductor(led_key).mount([{"doc": "LAWED.md"}])
    door = env.conductor(led_key).play("SIDED", route=env.conductor(led_key).route("SIDED"))
    at_prompt = render(door) if door is not None else ""
    swept = persistence.mounted_of(persistence.slot_of(env.made, led_key))
    signal = f"{messages.SIGNAL} {language.AWAIT}"
    if (door is not None and door.wait and swept == []
            and len(_headings(at_prompt)) == 1 and _asked(at_prompt) == ["SIDED"]
            and at_prompt.rstrip().splitlines()[-1] == signal
            and len([one for one in at_prompt.splitlines()
                     if one.startswith("LW1 ") or "LW1" in one.strip("[]").split()]) == 1):
        held("the closing of a passage stands in the segment of its steps", f"under LAWED's law: "
             f"`{_headings(at_prompt)[0]}` carries the door's step and the AWAIT, no call under it; LW1 said once, "
             "the mount swept, no segment without a step")
    else:
        failures.append(f"  ✗ the closing under a mount   prompt={_headings(at_prompt)} {_asked(at_prompt)} swept={swept} "
                        f"{at_prompt.rstrip().splitlines()[-2:]!r}")
    env.conductor(led_key).forget()


SPACEP = "---\nname: SPACEP\nkind: proc\ndescription: a space\nproc: |\n  INFER\n---\nthe space\n"


def everywhere(bench) -> None:
    """The system laws are in force at every block, whatever the stack: the boot and the TURN, a
    mount, a routed door, its repair, an open space -- each output says them whole, never a code,
    and alike under `verbatim_constraints` true and false; the proof names the system law of
    production, never one of behavior."""
    held, failures = bench.held, bench.failures
    said: dict[bool, dict[str, list[str]]] = {}
    for verbatim in (True, False):
        env = bench.env(f"msys-{str(verbatim).lower()}")
        env.write("SETTINGS.md", FUSED.replace("\n---\n", f"\nverbatim_constraints: {str(verbatim).lower()}\n---\n"))
        for name, text in (("WORKP", WORKP), ("DOORN", DOORN), ("SPACEP", SPACEP)):
            env.write(f"procs/{name}.md", text)
        env.write("NESTED.md", NESTED)
        env.write_system(production="SYS7  the system's production law holds.",
                         behavior="SYS8  the system's behavior law holds.")
        system = compiling.system_laws(env.made)

        def c() -> Conductor:
            return env.conductor("t")

        seen: dict[str, str] = {}
        booted = c().start(c().boot("BOOT.md"))
        seen["boot and TURN"] = render(booted) if booted is not None and "TURN" in booted.stack else ""
        c().forget()
        c().start(c().boot("WORKP.md"))
        seen["mount"] = c().mount([{"doc": "NESTED.md"}])
        entry = c().route("DOORN")
        door = c().play("DOORN", route=entry) if entry is not None else None
        seen["routed door"] = render(door) if door is not None and "routed from" in render(door) else ""
        hops = 0
        while door is not None and door.instruction.keyword != "PROVE" and not door.wait and hops < 4:
            door = c().forward("")
            hops += 1
        judged = list(door.judged) if door is not None else []
        failed = json.dumps([{"code": code, "evidence": "missed", "verdict": "fail"} for code in judged])
        for due in c().prints_due():                 # the door's line, said before its proof
            c().printed(due, "said")
        repaired = c().submit(failed) if judged else None
        seen["repair"] = render(repaired) if repaired is not None and repaired.repair else ""
        c().forget()
        c().start(c().boot("WORKP.md"))
        opened = c().open("SPACEP")
        seen["space"] = render(opened) if opened is not None and "SPACEP" in opened.stack else ""
        c().forget()
        said[verbatim] = {where: [line for line in text.splitlines() if any(line == str(law) for law in system)]
                          for where, text in seen.items()}
        coded = [where for where, text in seen.items() for line in text.splitlines()
                 if line.startswith("[") and any(law.code in line for law in system)]
        missing = [where for where, lines in said[verbatim].items()
                   if not seen[where] or sorted(lines) != sorted(str(law) for law in system)]
        mode = f"verbatim {str(verbatim).lower()}"
        if not missing and not coded:
            held(f"the system laws in force at every block, {mode}", f"{', '.join(seen)}: each output says "
                 f"{' '.join(law.code for law in system)} whole, never a code")
        else:
            failures.append(f"  ✗ system laws everywhere, {mode} missing at {missing} coded at {coded}")
        production = [law.code for law in system if law.section == "production"]
        behavior = [law.code for law in system if law.section == "behavior"]
        if judged and all(code in judged for code in production) and not any(code in judged for code in behavior):
            held(f"the proof names the system law of production, {mode}", f"the door's PROVE asks {judged}: "
                 f"{' '.join(production)} among them, none of {' '.join(behavior)}")
        else:
            failures.append(f"  ✗ system laws at the proof, {mode} judged={judged}")
    if said[True] == said[False]:
        held("the system laws read alike under both settings", "boot and TURN, mount, routed door, repair, "
             "space: the same system lines under verbatim true and false")
    else:
        failures.append(f"  ✗ system laws alike           {said!r}")


def system_collision(bench) -> None:
    """A mounted document that declares the code of a system law refuses `mount-collision`: no law
    wins in silence."""
    env = bench.env("msys-collision")
    env.write("procs/WORKP.md", WORKP)
    env.conductor("t").start(env.conductor("t").boot("WORKP.md"))
    code = compiling.system_laws(env.made)[0].code
    env.write("SYSDOC.md", f"---\nname: SYSDOC\nkind: doc\nconstraints.behavior: |\n  {code}  a document's law.\n---\n\nx\n")
    bench.expect("mount-collision", lambda: env.conductor("t").mount([{"doc": "SYSDOC.md"}]))
    env.conductor("t").forget()


def scenario(bench) -> int:
    system_collision(bench)
    everywhere(bench)
    no_segment(bench)
    closing_scope(bench)
    recharge(bench)
    crossings(bench)
    replaced(bench)
    return 0
