"""Scenario `motif` -- 4 case(s):
- la-soudure: a section is separated from the next by a BLANK line, the tail included
- la-section-dite: a law says its section whether or not the other group stands
- le-canal-tool-ne-fusionne-pas: a step that renders to the tool ends its output
- l-etat-des-packages: the state line says on, off and the cause, and belongs to the output's heading
"""
from __future__ import annotations

from conductor import Conductor, render, discovery
from conductor.core import language, model


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    # --- la-soudure: the weld keeps the motif's blank line ----------------------------
    made = bench.env("motif").made
    member = discovery.instance_member(made / ".sys" / "engine" / "pp.py")
    conductor = Conductor(member, discovery.siblings_around(member),
                          made / ".sys" / "engine" / "pp.py")
    booted = render(conductor.resume(conductor.boot("BOOT.md")))
    marked = [one for one in booted.splitlines()
              if one.startswith((model.Block.MARK, model.Block.SIGNAL))]
    glued = marked[1:]        # the output's FIRST line has nothing above it to part from
    seams = [f"\n\n{one}" in booted for one in glued]
    if glued and all(seams):
        held("every section opens on a blank line",
             f"{len(glued)} marked lines, none welded to what stands above -- the "
             "INSTRUCTION and the closing come through the same weld as the rest")
    else:
        missing = [one for one, ok in zip(glued, seams) if not ok]
        failures.append(f"  ✗ la soudure                  {missing[:3]!r}")

    # --- la-section-dite: a lone group wears its label all the same -------------------
    sections = [one.split(model.Block.MARK)[0].strip().splitlines()
                for one in booted.split(f"{model.Block.MARK} CONSTRAINTS")[1:]]
    labelled = [one[0] for one in sections if one]
    if labelled and all(one.startswith(("production:", "behavior:")) for one in labelled):
        held("a rendered law says its section",
             f"{len(labelled)} CONSTRAINTS section(s), each opening on its group's label "
             "whether or not the other stands: the agent reads what the checkpoint will "
             "ask for, never guesses it")
    else:
        failures.append(f"  ✗ la section dite             {labelled[:3]!r}")

    # --- le-canal-tool-ne-fusionne-pas: what renders to the tool ends its output ------
    to_tool = {one for one in language.YIELDING if one not in language.FREE}
    if (to_tool == {"PICK", "PROVE", "FIELD", "NEXT"} and "INFER" in language.FREE
            and "WORK" in language.FREE):
        held("the tool's channel never fuses",
             "the fusion takes FREE productions alone, and a channel reads `tool` for a "
             "PICK, a checkpoint, a described door's field, a leaving document's successor "
             "or a CONSUMED production -- "
             "exactly what it refuses to fuse: the closing's command always answers the "
             "LAST step rendered")
    else:
        failures.append(f"  ✗ le canal tool               {sorted(to_tool)!r}")

    # --- l-etat-des-packages: the line the heading carries, and what each cell says ----
    from dataclasses import replace
    from conductor import rendering
    cells = rendering.packages((("alpha", ""), ("beta", "alpha"), ("gamma", "gamma")))
    switched = replace(conductor.resume(conductor.boot("BOOT.md")),
                       switches=(("alpha", ""), ("beta", "alpha")))
    heading = rendering.head(switched)
    lines = heading.splitlines()
    if (cells == f"{model.Block.MARK} alpha on · beta off (<- alpha) · gamma off"
            and rendering.packages(()) == ""
            and len(lines) == 2 and lines[0].startswith(f"{model.Block.MARK} pp · ")
            and lines[1] == f"{model.Block.MARK} alpha on · beta off (<- alpha)"
            and f"{model.Block.MARK} pp · " not in lines[1]):
        held("the packages' state says itself",
             "one cell per package: `on` where it plays, `off` where a switch took it out, "
             "`off (<- <dependency>)` where its requirement did -- and the line sits UNDER the "
             "output's own heading, the two welded by a single newline: one heading, two lines; "
             "nothing to say, no line")
    else:
        failures.append(f"  ✗ l-etat-des-packages         {cells!r} {lines[-1:]!r}")
    return 0
