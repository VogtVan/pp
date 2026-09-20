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
    socket: bool = False       # opened by a SOCKET (a contributor, a cadence): its frame
                               # owes no exit checkpoint -- the turn's own proves the turn
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
        """-> the choices its input offers: a list input, never a scalar."""
        return list(self.taken) if isinstance(self.taken, list) else []


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
    cycle: bool | str = False  # True: `cycle: true`, exhausted REWINDS instead of popping/completing;
                               # a token: `cycle: <token>`, exhausted asks the token -- a lap, or the exit
    seed: Data = None          # the caller's captured production -- opens this frame's pipeline
    routed: tuple[Constraint, ...] | None = None   # inherited from a routed segment's
                               # snapshot instead of the caller chain -- persisted, so a
                               # restore rebuilds the same laws


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
    channel: str = ""         # where the production goes -- chat · tool · tool (heredoc);
                              # DERIVED by the conductor, never declared: rendered as the
                              # instruction line's `form => channel` suffix
    deviation: str = ""       # what the move missed -- a watched answer (a REPAIR) or an
                              # out-of-turn ask (caught, never counted)
    repair: int = 0           # the REPAIR ordinal shown when > 0 -- document-scoped: the
                              # count may belong to a LATER instruction than the one reopened
    wait: bool = False        # `next_call` only fires once the OPERATOR replies -- rendered
                              # as FINAL (the frontier delivers), never "call this now"
    verbatim_constraints: bool = True   # CONSTRAINTS render as their full text; False =
                                        # the codes alone -- the instance's own opt-out
    context: str = ""            # the title whose payload IS the pending instruction's
                                 # privileged context -- the proc-carrying document's own
                                 # body, never a mere reference reading
    end: str = ""                # the closing text of a FINISHED conduction -- rendered
                                 # as the END section; CONTINUE/FINAL/END, nothing else
    run_key: str = ""               # said on EVERY output's heading (`▌ pp · run <key> · ...`):
                                    # the closing sits outside a harness preview, the head inside
    stacked: tuple[str, ...] = ()   # the FUSED segments rendered before this block, in
                                    # order -- one output, one closing (the batch)
    merged: bool = False            # same frame as the previous segment of this output:
                                    # the B-form -- heading, TOOLS and CONSTRAINTS held
                                    # by the first, this one renders its own step alone
    coded: tuple[str, ...] = ()     # codes already emitted verbatim IN THIS OUTPUT --
                                    # rendered as codes, the texts said once per output
    foresee: str = ""               # what the resumed exchange will owe (a FINAL's
                                    # look-ahead) -- comes with the closing's parenthetical
    drafts: tuple[str, ...] = ()    # the documents whose drafts the FINAL delivers, in step
                                    # order -- rendered `FINAL ephemerals => chat (A · B)`;
                                    # empty, the FINAL owes no delivery
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

    MARK = "▌"     # ONE repeating motif: `▌ TITLE`, flush content, a blank line between
                   # sections -- two characters of delimiter, never a wall of them
    SIGNAL = "▶"   # the closing's own mark, once per block, right above the exact command
                   # owed -- CONTINUE/WAIT carry it; END owes no call and keeps the motif
    ANCHOR = "◀"   # a gesture's own mark: the line points BACK, at the segment the call
                   # hooked into -- never a block, never a closing, one line and nothing else

    def holds(self, answer: str) -> bool:
        return answer in self.options
