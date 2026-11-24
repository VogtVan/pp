"""rendering.render -- a Block becomes TEXT. The serialization of the engine's output:
the process renders through it (a fused segment, the mount's answer, the served
weight), the console prints what it returns; it reads the model and nothing above."""
from __future__ import annotations

from ..core import language, messages
from ..core.model import Block, Segment


# the FOOT of an output: the closing `blocks.closing` decided -- its label over its call, when one is
# owed -- then the facts, one per line between parentheses; an output that owes no closing and says
# no fact ends on its last section


def render(block: Block) -> str:
    """-> the block's text: the motif -- the bar opens each titled section, the arrow
    the closing -- written here and nowhere else, byte for byte what the agent reads."""
    matter, tail = parts(block)
    return joined(under(head(block), matter), tail)


def head(block: Block) -> str:
    """-> the OUTPUT's own heading: the run's key, the root of the passage, the reminder that
    a segment is addressed when the run fuses, and the hour. One line says ONE thing -- this one
    says the output, the headings below say where each segment stands.

    documentary: a segment rendered to be stacked carries none -- the output's closing
    block writes the line once, and every chunk of a cut block opens on it."""
    if block.segment:
        return ""
    return heading(block.run_key, block.root, block.fusion, block.clock, block.switches)


def heading(run_key: str, root: str, fusion: bool, clock: str, switches: tuple) -> str:
    """-> the heading of an OUTPUT from what it says: the run's key, the root of the passage, the
    reminder of the fusion, the hour, then the packages' line. A block's heading (`head`), and the
    one a call prints when it opens an exchange and renders no block."""
    said = [messages.run_cell(run_key)] if run_key else []
    if root:
        said.append(messages.root_cell(root))
    if fusion:
        said.append(messages.FUSION)
    if clock:
        said.append(clock)
    opened = messages.opening(said) if said else ""
    state = packages(switches)
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
        said.append(messages.pin_off(name, cause) if cause else messages.pin_on(name))
    return messages.pins(said)


def renewed(key: str, mark: dict) -> str:
    """The line a look renders on a RENEWED run -- an upgrade left its key, not its state: the
    versions that moved, and the fact that nothing was written; the run reopens on its boot under
    the same key, which is the standing orders' to say."""
    moved = mark.get("renewed") or {}
    before, after = moved.get("from") or {}, moved.get("to") or {}
    said = ", ".join(f"{name} {before.get(name, '?')} -> {after[name]}" for name in sorted(after))
    return messages.renewed(key, said)


def last_line(document: str) -> str:
    """-> the INSTRUCTION line the engine ADDS where an output asks its last message and no step of
    it says one: an `INFER` of the form `empty`, on the channel `response`, named after the document
    of the block that closes the output. A rendering: no step of the stack stands behind it."""
    return f"INFER {language.EMPTY} => {language.RESPONSE}  ({document})"


def foot(label: str, call: str, facts: tuple[str, ...] = ()) -> str:
    """-> the FOOT of an output as text, the motif's: a blank line, `▶ <label>` over its call when a
    closing is owed, then one line per fact, `   (<fact>)`; empty when nothing is owed and nothing is
    said. The one writer of the foot: a block's own (`parts`) and a chunk's (`Conductor._chunked`)
    pass through it."""
    lines: list[str] = []
    if label:
        lines += ["", messages.closing(label)] + ([call] if call else [])
    if facts:
        if not label:
            lines.append("")
        lines += [messages.fact(one) for one in facts]
    return "\n".join(lines)


def section(title: str, *content: str, subject: str = "") -> str:
    """-> one SECTION: the mark and the title -- a name of the engine's list
    (`language.BLOCK_SECTIONS`, `language.STEP_SECTIONS`), with the subject it serves when it
    serves one --, then its content. The one writer of a titled section."""
    return "\n".join([messages.title(messages.titled(title, subject)), *content])


def ordered(level: tuple[str, ...], carried: dict[str, list[str]]) -> list[str]:
    """-> the sections a level carries, in the order the engine's list says for that level
    (`language.BLOCK_SECTIONS`, `language.STEP_SECTIONS`) -- the one site that orders them."""
    return [one for name in level for one in carried.get(name, ())]


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
    return messages.anchor(ordinal, stack)


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


def heading_of(block: Block, ordinal: int = 0, reach: int = 0) -> str:
    """-> the heading of the segment `block` opens: its number in a multi-heading output, its
    stack -- the active frame's pointer widened to the range `{i-j/m}` when the merge ran past
    its step --, the segment a door was routed from, its repair."""
    stack = block.stack
    trail, pointed, pointer = stack.rpartition("{")
    if pointed and reach > block.position:
        total = pointer.rstrip("}").partition("/")[2]
        # an injected checkpoint may grow the frame after its opener stood: the total follows
        grown = max(int(total), reach) if total.isdigit() else total
        stack = f"{trail}{{{block.position}-{reach}/{grown}}}"
    return messages.segment(stack, ordinal, block.routed, block.repair)


def laws_of(block: Block) -> list[str]:
    """-> the lines of a block's CONSTRAINTS: the laws GROUPED by section -- production (proven)
    first, behavior (served) after; every group wears its label, alone or not, its SYSTEM laws
    first and whole (`block.system`), and the ledger (`block.coded`) says which laws of the
    documents already rendered their text -- those come back as codes."""
    lines: list[str] = []
    for name in ("production", "behavior"):
        system = [one for one in block.system if one.section == name]
        laws = [one for one in block.constraints if one.section == name]
        if not laws and not system:
            continue
        lines.append(f"{name}:")
        lines += [str(one) for one in system]
        lines += [str(one) for one in laws if one.code not in block.coded]
        held = [one.code for one in laws if one.code in block.coded]
        if held:
            lines.append(f"[{' '.join(held)}]")
    return lines


def line_of(block: Block) -> str:
    """-> the INSTRUCTION line of a block's step, "" for a block that asks nothing. The line SAYS
    what it asks: the form, the laws a checkpoint judges with the plate they cover, the channel
    the production travels by, then the document whose step it is."""
    if not block.command:
        return ""
    line = block.command + (f" {block.output}" if block.output else "")
    if block.judged:
        line += f" [{' '.join(block.judged)}] {messages.AREAS}"
    if block.output and block.channel:
        line += f" => {block.channel}"
    return line + f"  ({block.document})"


def _readings(block: Block) -> tuple[list, list]:
    """-> (the readings the block brings to the head of its segment, the readings of its own step),
    each (section, subject, text). A step keeps what is proper to it: its context -- the brief of
    its document, of a described field or of a fork, the ask -- and the readings the block itself
    says proper (`block.proper`); every other reading stands at the head, whichever step brings
    it. A block that asks nothing has no step to keep one."""
    contexts = (block.context, language.ASK) if block.command else ()
    proper = block.proper if block.command else ()
    above = [(language.INFORMATION, subject, text) for subject, text in block.payloads
             if subject not in contexts and subject not in proper]
    own = [(language.CONTEXT if subject in contexts else language.INFORMATION, subject, text)
           for subject, text in block.payloads if subject in contexts or subject in proper]
    return above, own


def laid(blocks: tuple[Block, ...], ordinal: int = 0, reach: int = 0) -> tuple[list[str], list[list]]:
    """-> ONE segment laid out by the engine's list, in two pieces: its HEAD -- the heading of the
    block that opens it, then the sections in the order of `language.BLOCK_SECTIONS`: the readings
    of every block, TOOLS the union of their offers, each name once in the order it first came,
    CONSTRAINTS said once, the opener's -- every block of a segment is of its scope; a heading
    opened under the scope of the segment above, a repair's, says neither again -- and its STEPS, one GROUP
    each in the order of the steps, a group reading in the order of `language.STEP_SECTIONS`:
    [what the step reads before its ask, its OPTIONS, the lines under its INSTRUCTION title]. A
    step that brings nothing of its own joins the title open above it, and the line the engine
    adds stands last under the last title."""
    opener = blocks[0]
    carried: dict[str, list[str]] = {name: [] for name in language.BLOCK_SECTIONS}
    steps: list[list] = []
    said = opener.merged                 # its scope said its offers and its laws in the segment above
    offered = [] if said else list(dict.fromkeys(one.name for block in blocks for one in block.tools))
    if offered:
        carried[language.TOOLS].append(section(language.TOOLS, f"[{' '.join(offered)}]"))
    if (opener.constraints or opener.system) and not said:
        carried[language.CONSTRAINTS].append(section(language.CONSTRAINTS, *laws_of(opener)))
    missed = [one.deviation for one in blocks if one.deviation]
    if missed:
        carried[language.DEVIATION].append(section(language.DEVIATION, *missed))
    faults = [line for one in blocks for line in one.diagnostics]
    if faults:
        carried[language.DIAGNOSTIC].append(section(language.DIAGNOSTIC, *faults))
    for block in blocks:
        above, own = _readings(block)
        carried[language.INFORMATION] += [section(name, text, subject=subject) for name, subject, text in above]
        lines = [*block.owed, *filter(None, [line_of(block)])]
        if lines:
            stepped: dict[str, list[str]] = {name: [] for name in language.STEP_SECTIONS}
            for name, subject, text in own:
                stepped[name].append(section(name, text, subject=subject))
            if block.options:
                stepped[language.OPTIONS].append(section(language.OPTIONS, *block.options))
            if not any(stepped.values()) and steps:
                steps[-1][2] += lines             # nothing parts them from the line above
            else:
                asked = language.STEP_SECTIONS.index(language.OPTIONS)     # where the ask opens
                steps.append([SEAM.join(ordered(language.STEP_SECTIONS[:asked], stepped)),
                              SEAM.join(stepped[language.OPTIONS]), lines])
        if block.response == language.ADDED:
            # the last message the output asks, when no step of it says one
            if steps:
                steps[-1][2].append(last_line(block.document))
            else:
                steps.append(["", "", [last_line(block.document)]])
    head = ([heading_of(opener, ordinal, reach)] if opener.headed else []) + ordered(language.BLOCK_SECTIONS, carried)
    return head, steps


def segment(one: Segment) -> str:
    """-> the text of a segment that stands whole in an output, laid out by the list: its head,
    then its steps."""
    head, steps = laid(one.blocks, one.ordinal, one.reach)
    return SEAM.join(head + [group(step) for step in steps])


def group(step: list) -> str:
    """-> the text of ONE step's group: what it reads, its OPTIONS, then its lines under the
    INSTRUCTION title -- a group cut short of its lines (a chunk) carries no title."""
    read, options, lines = step
    return SEAM.join(text for text in (read, options, section(language.INSTRUCTION, *lines) if lines else "")
                     if text)


def pieces(block: Block) -> tuple[str, list[list], str]:
    """-> the output `block` closes, in THREE pieces: its MATTER -- what stands before its first
    step: the segments that ask nothing, then the head of the first one that does --, its STEPS --
    every piece from that step on, in order: the GROUP of each step, whatever its segment, and
    between two steps of different segments the head of the later one, a piece that asks nothing
    (`[head, "", []]`) --, and the FOOT. The block joins the segment above it when that one takes
    it in (`merged`); else it is the last segment by itself."""
    before = list(block.stacked)
    blocks, ordinal, reach = (block,), block.ordinal, 0
    if not block.headed and before:
        last = before.pop()
        blocks, ordinal, reach = last.blocks + (block,), last.ordinal, last.reach
    run: list = []                       # the output in order: a text that asks nothing, or a step's group
    for one in before:
        head, steps = laid(one.blocks, one.ordinal, one.reach)
        run += [SEAM.join(head), *steps]
    head, steps = laid(blocks, ordinal, reach)
    run += [SEAM.join(head), *steps]
    run = [one for one in run if one]
    first = next((rank for rank, one in enumerate(run) if not isinstance(one, str)), len(run))
    matter = SEAM.join(run[:first])
    facts = (((block.fact,) if block.fact else ())
             + tuple(messages.gap_declared(code, text) for code, text in block.gaps))
    return (matter, [[one, "", []] if isinstance(one, str) else one for one in run[first:]],
            foot(block.label, block.next_call, facts))


def tail_of(steps: list[list], closing: str) -> str:
    """-> the TAIL of an output: the groups of its steps, each section parted by the motif's blank
    line, then the foot. It opens on the newline the weld (`joined`) turns into that blank line."""
    read = SEAM.join(text for text in (group(step) for step in steps) if text)
    if not read:
        return closing
    return f"\n{read}" + (f"\n{closing}" if closing else "")


def parts(block: Block) -> tuple[str, str]:
    """-> the output in TWO pieces: its MATTER (what stands before its first step: the segments
    that ask nothing, then the heading, readings, tools, laws, deviation and diagnostics of the
    first one that does) and its TAIL (every step from there on, each with its context, its
    OPTIONS and its line, the head of each later segment before its steps, then the closing). The
    output's heading (`head`) stands outside the matter: it comes with every chunk of a cut output.

    documentary: the split is the renderer's business because the seams are the
    renderer's motif; deciding WHERE to cut is the engine's, and it reads the cap."""
    matter, steps, closing = pieces(block)
    return matter, tail_of(steps, closing)
