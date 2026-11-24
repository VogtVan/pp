"""The data of a run. This module imports NOTHING from the package.

That is what lets these objects cross every layer: a reader builds them, a runner
advances them, a session writes them, a block formats them -- none of it lives here.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

Data = list | str | None      # a list feeds a choice, a scalar feeds an action


def console_command(windows: bool | None = None) -> str:
    """-> how a block re-invokes the conductor: the console script at the member
    root, spelled the way the running platform executes it."""
    on_windows = (os.name == "nt") if windows is None else windows
    return ".\\pp" if on_windows else "./pp"


@dataclass
class Instruction:
    """One step of a run: what it says, what it took, what it produced."""

    keyword: str
    argument: str
    taken: Data = None
    given: Data = None
    done: bool = False
    offset: int = 0            # how much of the CURRENT slot's document has been delivered
    slot: int = 0              # which document of a SERVE's ROW is being served
    repairs: int = 0          # how many times the agent was asked to try again
    injected: bool = False     # born at runtime (a HOOK expanded), never written in the document
    site: str = ""             # the PATH an injected CALL enters its document by -- `socket`,
                               # `cadence`, `successor`, `door`; empty for a CALL a proc writes.
                               # The entry table (execution/entry.py) says what each applies
    barrier: bool = False      # a `§` line precedes it in the proc: fusion never crosses it
    asked: bool = False        # its block was rendered and awaits the answer (a terminal)
    routed: tuple[str, ...] = ()   # an agent-opened CALL routed to a PAST segment: the
                               # owning frame's constraint lines, snapshotted -- the callee
                               # inherits THESE, not the pending frame's
    guard: str = ""            # `^ @Doc.field` -- plays only as often as that value says;
                               # ONE tag, no composition: the algebra would be the factory
    refit: tuple = ()          # a checkpoint repairing IN PLACE: the failed codes whose
                               # mini-proof is owed next -- empty, the proof is whole

    def __str__(self) -> str:
        return f"{self.keyword} {self.argument}"

    @property
    def options(self) -> list[str]:
        """-> the choices its input offers: a list input, never a scalar -- each element
        as its TEXT, the token the agent answers verbatim (`[1, 2]` offers `1` and `2`)."""
        return [str(one) for one in self.taken] if isinstance(self.taken, list) else []


@dataclass(frozen=True)
class Constraint:
    """A law in force. Its TEXT travels -- an id alone is a dead letter twenty turns
    later. Its SECTION says what it is to the proof: `production` (what the agent
    makes -- proven at every checkpoint) or `behavior` (what it does, says or reads --
    served at every block, never proven)."""

    code: str
    text: str
    section: str = "production"

    def __str__(self) -> str:
        return f"{self.code}  {self.text}"

    def wire(self) -> str:
        """-> the line a snapshot stores: the section rides as a prefix when it is
        not the default, so a routed frame rebuilds the same laws."""
        return str(self) if self.section == "production" else f"{self.section}:{self}"

    @staticmethod
    def parse(line: str) -> "Constraint":
        """-> the Constraint a `wire()` line round-trips to -- a bare `str(one)` line
        (an older snapshot) reads as production."""
        section = "production"
        if line.startswith("behavior:"):
            section, line = "behavior", line[len("behavior:"):]
        code, _, text = line.partition("  ")
        return Constraint(code=code, text=text, section=section)


@dataclass(frozen=True)
class Tool:
    """A skill or proc the agent MAY use here. Its description travels, same reason as a
    Constraint -- and its CONTRACT's path travels too: what is handed to the agent's free
    will must be readable in full, not known by its menu line."""

    name: str
    description: str
    contract: str = ""

    def __str__(self) -> str:
        where = f"\n    contract: {self.contract}" if self.contract else ""
        return f"{self.name}  {self.description}{where}"


@dataclass
class Procedure:
    """The instruction stack: ordered, and stateful once a run touches it."""

    instructions: list[Instruction] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.instructions)


@dataclass(frozen=True)
class Document:
    """A markdown file whose front matter carries the procedure the conductor plays."""

    name: str
    front: dict[str, object]
    path: Path


@dataclass
class Frame:
    """One document being executed. Its state lives in the instructions."""

    document: Document
    procedure: Procedure
    constraints: tuple[Constraint, ...] = ()
    tools: tuple[Tool, ...] = ()
    caller: Instruction | None = None   # the CALL, in the frame below, that opened this one
    cycle: bool | str = False  # False: no cycle (the ROOT of a passage replays by itself, parked);
                               # a token: `cycle: <token>`, exhausted asks the token -- a lap, or the exit;
                               # language.FIELD: the DESCRIBED door -- exhausted, the next element of `field`
    field: list | None = None  # the described door's FIELD: what remains DUE, the head served each lap,
                               # dropped when the lap closes; None until the agent rendered it -- the
                               # frame's own, never an instruction's (a rewind resets instructions)
    seed: Data = None          # the caller's captured production -- opens this frame's pipeline
    routed: tuple[Constraint, ...] | None = None   # inherited from a routed segment's
                               # snapshot instead of the caller chain -- persisted, so a
                               # restore rebuilds the same laws
    declared: Procedure | None = None   # what the document declares NOW when it no longer matches
                               # the steps the frame plays -- the passage ends on its own steps,
                               # the next opening reseats the frame on this; never saved


@dataclass
class Stack:
    """The frames in flight, innermost last."""

    frames: list[Frame] = field(default_factory=list)


INSTANCE_DIRECTORY = ".pp"   # the instance directory's name -- the product installs it,
                             # every member and its siblings assume it unless told otherwise


@dataclass(frozen=True)
class Member:
    """One workspace: a directory carrying an INSTANCE. `path` is the
    workspace to work in -- a worktree counts; `meta_name` is the instance directory's
    name, INSTANCE_DIRECTORY unless an instance was installed under another one.
    """

    path: Path
    name: str
    meta_name: str = INSTANCE_DIRECTORY

    @property
    def meta(self) -> Path:
        return self.path / self.meta_name

    def document(self, name: str) -> Path:
        return self.meta / name

    def command(self) -> str:
        """-> how to re-invoke the conductor, addressed from this member's root:
        the console the install writes there -- machine-owned, self-repairing."""
        return console_command()


@dataclass(frozen=True)
class Siblings:
    """The sibling workspaces: the directories under `root` that carry an instance
    named `meta_name` -- an instance is what makes a member, nothing else does. A
    repository sitting nearby without one is not a sibling.
    """

    root: Path
    meta_name: str = INSTANCE_DIRECTORY


@dataclass(frozen=True)
class Block:
    """The only thing the agent ever sees of a run -- data, and how to lay it out."""

    document: str
    instruction: Instruction
    command: str
    position: int
    total: int
    options: tuple[str, ...]
    constraints: tuple[Constraint, ...]
    tools: tuple[Tool, ...]
    payloads: tuple[tuple[str, str], ...]
    output: str
    next_call: str
    stack: str
    channel: str = ""         # where the production goes -- terminal · response · tool ·
                              # tool_heredoc; DERIVED by the conductor, never declared: rendered
                              # as the instruction line's `form => channel` suffix; `response` is
                              # given where the output closes, to the last production it says
    owed: tuple[str, ...] = ()   # the lines of the steps an EARLIER output said on `terminal`,
                              # still due to print: rendered above this block's own line
    response: str = ""        # how the output this block closes asks its LAST message: `step`
                              # (its last said step goes `=> response`), `added` (the engine adds
                              # the line `INFER empty => response` behind a value, or on a bare
                              # AWAIT), "" when the output asks none -- a rendering, never a step
    deviation: str = ""       # what the move missed -- a watched answer (a REPAIR) or an
                              # out-of-turn ask (caught, never counted)
    diagnostics: tuple[str, ...] = ()   # what the ENGINE found wrong with the conduction
                              # itself -- `<signal> · <level> · <fact> -- <way out>`, one line
                              # each, said once per run: the DIAGNOSTIC section
    repair: int = 0           # the REPAIR ordinal shown when > 0 -- document-scoped: the
                              # count may belong to a LATER instruction than the one reopened
    replay: bool = False      # the block renders AGAIN what the agent read: a repair, a proof
                              # asked again, a repair in place -- marked by those sites alone
    wait: bool = False        # the run PARKS with this block: the root of the passage is
                              # exhausted, the principal's message opens the next one
    label: str = ""           # the word of the CLOSING: CONTINUE, AWAIT, MORE, or "" when the
                              # output owes no closing -- decided by `blocks.closing` from what
                              # the stack awaits and the channel, rendered as `▶ <label>`
    fact: str = ""            # the FACT of the foot the closing carries -- a reading that
                              # continues --, rendered `   (pp: <fact>)` under it; the gaps are
                              # facts too (`gaps`)
    verbatim_constraints: bool = True   # CONSTRAINTS render as their full text; False =
                                        # the codes alone -- the instance's own opt-out
    context: str = ""            # the title whose payload IS the pending instruction's
                                 # privileged context -- the proc-carrying document's own
                                 # body, never a mere reference reading
    proper: tuple[str, ...] = () # the subjects of the readings PROPER to this block's step --
                                 # the element of a lap, whatever name it is served under, the
                                 # production its document opens on: they read in the step's
                                 # group, every other reading at the head of the segment
    run_key: str = ""               # said on EVERY output's heading (`▌ pp · run <key> · ...`):
                                    # the closing sits outside a harness preview, the head inside
    root: str = ""                  # the ROOT of the passage where the block stands: the document
                                    # the next message feeds -- the floor's root, or the space open
    stacked: tuple[Segment, ...] = ()   # the segments of the output that stand before this
                                    # block, in order -- one output, one closing (the batch)
    merged: bool = False            # of the scope of the last segment of this output: its
                                    # TOOLS and CONSTRAINTS are that segment's, and it joins
                                    # that segment's steps -- but a repair, which keeps a heading
    coded: tuple[str, ...] = ()     # codes already emitted verbatim IN THIS OUTPUT --
                                    # rendered as codes, the texts said once per output
    system: tuple[Constraint, ...] = ()   # the SYSTEM LAWS this block says whole, at the head of
                                    # each group of its CONSTRAINTS: the first block of the output
                                    # that says its laws carries them, no later one
    gaps: tuple = ()                # the gaps a proof declared in the call that renders
                                    # this closing: (code, what is missing), said under it
    switches: tuple = ()            # one (package, state) pair per pin beyond the base, in
                                    # the pin order: "" plays, the package's own name says it
                                    # is switched off, another name says the dependency that
                                    # took it out -- said UNDER the output's heading, once
    clock: str = ""                 # the clock mark of the OUTPUT's heading: the local time
                                    # (HH:MM:SS) and the time elapsed since the run's -new --
                                    # once per output, on that line and nowhere else
    fusion: bool = False            # the run's FIRST output under fusion: its heading recalls
                                    # that a segment is addressed `@n` -- a reminder, not a banner
    judged: tuple[str, ...] = ()    # a CHECKPOINT's own codes: the laws of PRODUCTION in force,
                                    # named on the instruction line with the plate they cover
    segment: bool = False           # this block is rendered to be STACKED in a fused output:
                                    # its text carries no output heading, the closing block's does
    ordinal: int = 0                # this block's segment number in a MULTI-heading
                                    # output -- `[n]` on the heading; 0 = unnumbered
    routed: str = ""                # an agent-opened door routed to a past segment:
                                    # `[n] FRAME`, said once on the entry heading


    def holds(self, answer: str) -> bool:
        return answer in self.options

    @property
    def headed(self) -> bool:
        """Whether the block opens a segment under its own heading: every block the one above
        does not take in, and a repair, whose heading is never elided."""
        return not self.merged or bool(self.repair)


@dataclass(frozen=True)
class Segment:
    """One SEGMENT of an output: what stands under one heading. It keeps the blocks its
    heading stands for -- the opener, then every block of its scope merged under it -- and its
    text is rendered once, where the output closes."""

    position: int = 0                # the step its opener stands on
    document: str = ""               # the document of its opener's frame
    blocks: tuple[Block, ...] = ()   # the opener, then the blocks merged under it
    ordinal: int = 0                 # its number in a MULTI-heading output -- `[n]` on the
                                     # heading; 0 = unnumbered
    reach: int = 0                   # the last step its heading stands for when the merge ran
                                     # past its opener -- the range `{i-j/m}`; 0 = the opener alone

    @property
    def headed(self) -> bool:
        """Whether the segment stands under a heading of its own."""
        return bool(self.blocks) and self.blocks[0].headed

    @staticmethod
    def trail(stack: str) -> str:
        """-> the frames a block's stack names, its pointer left out: what two steps of one frame share."""
        return stack.rpartition("{")[0] or stack

    @property
    def stretch(self) -> int:
        """The last step of the opener's own frame merged under it -- what the heading's range
        reaches by the segment's blocks; a step of another frame merged there is said by its line
        and reaches nothing; 0 for the opener alone."""
        if not self.blocks:
            return 0
        own = self.trail(self.blocks[0].stack)
        same = [one.position for one in self.blocks[1:] if one.command and self.trail(one.stack) == own]
        return same[-1] if same else 0
