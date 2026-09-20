"""rendering.render -- a Block becomes TEXT. The serialization of the engine's output:
the process renders through it (a fused segment, the mount's answer, the served
weight), the console prints what it returns; it reads the model and nothing above."""
from __future__ import annotations

from ..core.model import Block


FUSION = "fusion · address a segment with @n when needed"
AREAS = "on all produced areas"   # the plate a checkpoint judges, until a law declares its own


def render(block: Block) -> str:
    """-> the block's text: the motif -- the bar opens each titled section, the arrow
    the closing -- written here and nowhere else, byte for byte what the agent reads."""
    matter, tail = parts(block)
    return joined(under(head(block), matter), tail)


def head(block: Block) -> str:
    """-> the OUTPUT's own heading: the run's key, the reminder that a segment is
    addressed when the run fuses, and the hour. One line says ONE thing -- this one
    says the output, the headings below say where each segment stands.

    documentary: a segment rendered to be stacked carries none -- the output's closing
    block writes the line once, and every chunk of a cut block opens on it."""
    if block.segment:
        return ""
    said = [f"run {block.run_key}"] if block.run_key else []
    if block.fusion:
        said.append(FUSION)
    if block.clock:
        said.append(block.clock)
    opened = f"{Block.MARK} pp · " + " · ".join(said) if said else ""
    state = packages(block.switches)
    return f"{opened}\n{state}" if opened and state else (opened or state)


def packages(switches: tuple) -> str:
    """-> what the run PLAYS of its packages: one cell per pin beyond the base, in the
    pin order -- `on`, `off`, or `off (<- <dependency>)` where a requirement took it
    out. The line sits under the output's own heading and comes with every chunk of a
    cut one; an instance that pins nothing beyond its base says nothing. It takes the
    PAIRS, so a view with no block to carry them says the same line."""
    if not switches:
        return ""
    said = []
    for name, cause in switches:
        if not cause:
            said.append(f"{name} on")
        else:
            said.append(f"{name} off" if cause == name else f"{name} off (<- {cause})")
    return f"{Block.MARK} " + " · ".join(said)


def under(heading: str, matter: str) -> str:
    """-> the matter under the output's heading, the motif's blank line between them.
    The heading comes with every CHUNK of a cut block, so it takes the matter it is
    handed: the whole of it, or the piece that fits."""
    if not heading:
        return matter
    return f"{heading}\n\n{matter}" if matter else heading


def anchor(ordinal: int, stack: str) -> str:
    """-> the ONE line a GESTURE renders: the heading of the segment the call hooked
    into, and nothing else -- no clock, no laws, no tools, no instruction, no closing.
    A gesture is not a step, so it renders no block; the line only says WHERE it landed.

    documentary: the mark points BACK because the segment is already on screen -- the
    call does not move the flow forward, it reaches into what was rendered."""
    return f"{Block.ANCHOR} pp · [{ordinal}] {stack}"


def joined(matter: str, tail: str) -> str:
    """-> the two pieces welded by ONE newline. A tail that opens a section already
    carries the newline `section()` puts in front of it, so the weld makes the BLANK
    LINE the motif asks for; a merged instruction line, which comes with the section
    already open, simply lands on the next line.

    documentary: the weld is where the motif could silently lose a blank line -- one
    rule for both tails, never a test on their shape."""
    if not matter or not tail:
        return matter + tail
    return f"{matter}\n{tail}"


SEAM = "\n\n"          # between two sections: where a cut reads best


def cut(matter: str, room: int) -> tuple[str, str]:
    """-> (what fits under `room`, what is left) -- the matter alone, never the tail.
    The seam is a SECTION boundary when one fits, a line boundary otherwise; a single
    section larger than the room still cuts at a line, and a line larger than the room
    cuts raw: some chunk must happen.

    documentary: the concatenation of the chunks is the matter, byte for byte -- what
    the seam removes from the head of a chunk opens the next one."""
    if room <= 0 or len(matter) <= room:
        return matter, ""
    piece = matter[:room]
    at = piece.rfind(SEAM)
    if at <= 0:
        at = piece.rfind("\n")
    if at <= 0:
        return piece, matter[len(piece):]
    return matter[:at], matter[at:]


def parts(block: Block) -> tuple[str, str]:
    """-> the block in TWO pieces: its MATTER (segment headings, tools, payloads,
    constraints, deviation, options) and its TAIL (the INSTRUCTION and the closing). A
    block over the host's cap is cut in its matter alone -- the tail comes with every
    chunk, so each one says what it expects and how to come back, and so does the
    output's heading (`head`), which stands outside the matter for that very reason.

    documentary: the split is the renderer's business because the seams are the
    renderer's motif; deciding WHERE to cut is the engine's, and it reads the cap."""
    def section(title: str, *content: str) -> list[str]:
        return ["", f"{block.MARK} {title}", *content]
    heading = (f"{block.MARK} "
               + (f"[{block.ordinal}] " if block.ordinal else "")
               + block.stack)
    if block.routed:
        heading += f"   (routed from {block.routed})"
    if block.repair:
        heading += f" · REPAIR {block.repair}"
    body: list[str] = []

    def emit(text: str) -> None:
        """A fresh `▌` section separates from what stands; a bare instruction
        line comes with the section already open -- steps of one frame with
        nothing between them collapse under ONE INSTRUCTION title."""
        if body and text.startswith(block.MARK):
            body.append("")
        body.append(text)

    for segment in block.stacked:
        emit(segment)
    if not block.merged or block.repair:
        emit(heading)           # a REPAIR heading is never elided, merged or not
    if not block.merged and block.tools:
        body += section("TOOLS", f"[{' '.join(one.name for one in block.tools)}]")
    for subject, text in block.payloads:
        body += section(("NEXT INSTRUCTION CONTEXT — " if subject == block.context
                         else "INFORMATION — ") + subject, text)
    # everything below sits CLOSE to the instruction it governs -- a rule read
    # a screen away from the ask it constrains is a rule the model has drifted past
    if block.constraints and not block.merged:
        # one title, the laws GROUPED by section -- production (proven) first, behavior
        # (served) after; EVERY group wears its label, alone or not, and the LEDGER
        # (`block.coded`) says which laws already rendered their text -- those come
        # back as codes, whatever the emission regime
        groups = [(name, [one for one in block.constraints if one.section == name])
                  for name in ("production", "behavior")]
        groups = [(name, laws) for name, laws in groups if laws]
        lines = []
        for name, laws in groups:
            lines.append(f"{name}:")
            lines += [str(one) for one in laws if one.code not in block.coded]
            held = [one.code for one in laws if one.code in block.coded]
            if held:
                lines.append(f"[{' '.join(held)}]")
        body += section("CONSTRAINTS", *lines)
    if block.deviation:
        body += section("DEVIATION", block.deviation)
    if block.options:
        body += section("OPTIONS", *block.options)
    matter = "\n".join(body)
    body = []
    if block.command:            # a mid-reading block asks nothing: the closing says it
        # the line SAYS what it asks: the form, the laws a checkpoint judges with the
        # plate they cover, then the channel the production travels by
        line = block.command + (f" {block.output}" if block.output else "")
        if block.judged:
            line += f" [{' '.join(block.judged)}] {AREAS}"
        if block.output and block.channel:
            line += f" => {block.channel}"
        if (block.merged and not block.repair and not block.payloads
                and not block.options and not block.deviation):
            emit(line)          # nothing of its own on screen: the line joins
        else:                   # the INSTRUCTION section already open above it
            body += section("INSTRUCTION", line)
    if block.next_call:
        note = "once the operator replies" + (f" -- {block.foresee}" if block.foresee else "")
        label = ((f"FINAL ephemerals => chat ({' · '.join(block.drafts)})" if block.drafts
                  else "FINAL") if block.wait else "CONTINUE")
        body += ["", f"{block.SIGNAL} {label}", block.next_call]
        if block.wait:              # the note on its own line: the command stays copyable
            body.append(f"   ({note})")
    elif block.end:
        body += section("END", block.end)
    return matter, "\n".join(body)
