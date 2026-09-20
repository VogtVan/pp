"""execution.conductor -- the FACADE: the run's shared state, its cycle of life (slot, trace, save, rebind), its
inspection (peek, route) -- and the class every domain's mixin assembles into.
The state lives HERE and nowhere else: a mixin declares no attribute, it reads the
facade's. `revive` is the facade's reader of a saved frame, handed to persistence."""
from __future__ import annotations

import json
import os
import secrets
from dataclasses import replace
from pathlib import Path
from ..packaging import compiling, events
from .. import reading
from ..core import language
from ..state import context, discovery, instance, log, metrics, persistence, settings
from ..core.errors import Refusal
from ..core.model import Block, Document, Siblings, Frame, Instruction, Member, Stack
from ..reading import Reading
from .revive import revive   # noqa: F401 -- the facade's reader of a saved frame, re-exported
from .blocks import Assembling
from .boot import Booting
from .gestures import Gesturing
from .hosting import Hosting
from .judgment import Judging
from .stepping import Stepping



class Conductor(Booting, Gesturing, Stepping, Judging, Hosting, Assembling, Reading):
    """Holds the procedure, the stack and the initiative; the agent only ever infers.

A run may move to another member and carry on there, on that member's
documents -- but the session file stays with the checkout that opened it."""

    def __init__(self, member: Member, siblings: Siblings, script: Path,
                 run: str | None = None) -> None:
        self.member = member
        self._launch = member
        self.siblings = siblings
        self._script = script
        self._served: dict[str, int] = {}
        self._proven: set[str] = set()     # the readings proven by content this run:
                                           # a document is served once, never twice
        self._staged: list[str] = []       # the readings of the output being built: DEMOTED
                                           # from the proofs when the output is cut, back when
                                           # their last chunk leaves -- proven by delivery
        self._payloads: list[tuple[str, str]] = []
        self._resolved: dict[str, list[dict]] = {}   # the payload TOKENS this output resolved,
                                           # each with what its providers rendered: a second
                                           # consumer in the same output runs no provider --
                                           # never persisted, the facade lives one output
        self._ledger: list[dict] = []      # what the OUTPUT served, in order: one entry per
                                           # service -- its state, where it came from, which
                                           # document asked and from which package. The block
                                           # renders none of it: it goes to the trace alone
        self._reserving = False            # a compaction's re-serve is under way: what it
                                           # serves comes back, and the ledger says so
        self._settings = settings.of(member.meta)   # the instance's tuning, read ONCE
        self._inplace = ()         # set by a fixed-fail proof check, consumed by submit:
                                   # the failed codes whose repair plays in place
        self._run = run                # the id the CONVERSATION named (`-run`), if any
        self._run_id: str | None = None   # the id of the RESOLVED run
        self._session: Path | None = None  # the resolved slot -- `_slot()` owns it
        self._log: str | None = None   # the run's own session-<UTC>.jsonl -- state names it
        self._turns = 0                # completed exchanges -- what a `^ @Doc.field` guard paces on
        self._dry = False              # a PEEK plays on a throwaway restore: 0 save, 0 trace
        self._stacked: list[tuple[int, str]] = []   # the FUSED segments of the output
                                       # being built -- (step position, rendered text):
                                       # only the assembler knows i→j at the closing
        self._fused = 0                # yields rendered in this output -- the cap counts these
        self._output_clock = ""        # the hour of the output being built: read at its first
                                       # block, written on the output's own heading, once
        self._emitted: set[str] = set()   # codes said VERBATIM in this output (D-d)
        self._emitted_run: set[str] = set()   # the codes-mode LEDGER: laws whose text
                                       # this RUN has rendered once -- first emission
                                       # verbatim, codes after; persisted at the slot,
                                       # cleared by `-compacted` (the texts return)
        self._seg_frame: Frame | None = None   # the last segment's frame -- same frame = B-merge
        self._ephemerals: list[str] = []   # the documents of the drafts standing since the
                                       # last frontier, in step order -- what the next FINAL
                                       # delivers and names; crosses pops, so KEPT (the one
                                       # pointer that cannot be derived), persisted
        self._segmap: list[dict] = []  # the output's OFFER MAP -- one entry per heading
                                       # (ordinal, frame, stack, tools, constraint lines):
                                       # what a `-s` call routes against once the
                                       # segment's frame is resolved or popped
        self._remap = False            # only a MUTATING advance replaces the persisted
                                       # map -- a re-show (resume, peek) keeps the
                                       # standing addresses: they live with their output
        self._route_note = ""          # `[n] FRAME` -- said once, on the entry heading

    @classmethod
    def here(cls, script: Path, run: str | None = None) -> "Conductor":
        member = discovery.installed_member(script)
        return cls(member, discovery.siblings_around(member), script, run)

    def effort(self) -> str:
        """-> the instance's conduction EFFORT (light | medium | full, or
        empty) -- one word presetting the weight knobs."""
        return self._settings.effort

    def _slot(self) -> Path | None:
        """-> the slot this conversation talks to: the named one, the only one standing,
        or None when none is -- several unnamed REFUSE: each conversation talks to ITS
        run, and only the conversation knows which one is hers."""
        if self._session is not None:
            return self._session
        if self._run:
            self._run_id = self._run
            return self._bind(persistence.slot_of(self._launch.meta, self._run))
        found = persistence.slots(self._launch.meta)
        if len(found) > 1:
            raise Refusal("run-ambiguous",
                          f"{len(found)} runs are under way -- your conversation's key "
                          "(handed at `-new`) leads every command of this run, "
                          "`./pp <key> ...`; a new conversation opens its own with `-new`")
        if found:
            self._run_id = persistence.run_id_of(found[0])
            return self._bind(found[0])
        return None

    def switch_state(self) -> tuple:
        """-> the packages' state as an output's heading says it, for a view that has no
        block to carry it: one (package, state) pair per pin beyond the base."""
        return self._switch_state()

    def _bind(self, slot: Path) -> Path:
        """The slot resolved: its SOFT SWITCHES enter the play before anything reads
        the composition -- the packages this run took out stay out, for this process
        and this instance alone -- and its TRACE is where this process writes, whatever
        verb resolved the slot."""
        self._session = slot
        self._log = self._log or persistence.trace_of(slot)
        instance.play_off(self._launch.meta, persistence.off_of(slot))
        # the run named in THIS process's environment: every script it launches inherits
        # it, a gesture played in-process reads it -- one site, every path
        os.environ[context.VARIABLE] = persistence.run_id_of(slot)
        return slot

    def switch(self, name: str, off: bool) -> str:
        """The SOFT switch of one package, for THIS run: `off` takes it out of the play
        -- nothing of it is served or played, its dependents leave with it -- and `on`
        brings it back; the hard switch of SETTINGS says the same thing durably, and
        both filter at ONE point. The run does not move: a switch is the operator's
        word, never a step, so the answer is the block that STANDS.
        -> the fact, then that block."""
        slot = self._slot()
        if slot is None or not slot.exists():
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        meta = self.member.meta
        if name == instance.base_of(meta):
            raise Refusal("package-base",
                          f"`{name}` is the base of every instance -- never switched off")
        if name not in instance.pins(meta):
            raise Refusal("package-unpinned",
                          f"`{name}` is not pinned here -- `./pp version` says what this "
                          "instance composes")
        held = set(persistence.off_of(slot))
        if off:
            flight = self._in_flight(name, slot)
            if flight:
                raise Refusal("package-in-flight",
                              f"`{name}` holds the standing view: {', '.join(flight)} -- "
                              "the frame finishes, then the word plays")
            held.add(name)
        else:
            held.discard(name)
        persistence.set_off(slot, sorted(held))
        instance.play_off(meta, held)
        self._trace("switch", package=name, off=off)   # the word is written where it happened
        block = self.peek()
        fact = f"pp: `{name}` {'off' if off else 'on'} for this run"
        return fact if block is None else f"{fact}\n\n{self.shown(block)}"

    def _in_flight(self, name: str, slot: Path) -> list[str]:
        """-> the names of `name`'s documents the run HOLDS -- a frame of the stack or a
        standing mount; read before the switch, while the package still resolves."""
        home = f"{instance.VENDOR}/{name}@"
        found = []
        for one in persistence.paths_of(slot):
            path = Path(one)
            if not path.is_absolute():
                path = instance.resolve(self._launch.meta, one)
            if home in str(path).replace("\\", "/"):
                found.append(path.name)
        return found

    def _mint(self) -> str:
        """-> a short run id no standing slot claims."""
        while True:
            candidate = secrets.token_hex(3)
            if not persistence.slot_of(self._launch.meta, candidate).exists():
                return candidate

    @property
    def run_id(self) -> str | None:
        """-> the resolved run's id, once a call resolved one."""
        return self._run_id

    def forget(self) -> int:
        """Drops runs -- the named one when the conversation named one, ALL otherwise --
        and does NOT open another one. -> how many actually stood."""
        targets = ([persistence.slot_of(self._launch.meta, self._run)] if self._run
                   else persistence.slots(self._launch.meta))
        dropped = sum(1 for slot in targets if self._discard(slot))
        self._session = None
        self._run_id = None
        return dropped

    def note(self, subject: str, text: str, state: str, origin: str, **rest) -> None:
        """ONE line of the LEDGER: what a site served (or spared), where it came from, who
        asked for it. The site KNOWS -- nothing here is inferred from a name; a caller that
        says nothing leaves its key out. `rest` carries `by` (the asking document), `with_`
        (a provider skill), `nature` (a row's declared nature), `at` (a socket), `package`,
        and `spared` (what a spared reading avoided)."""
        entry = {"subject": subject, "state": "reserved" if self._reserving else state,
                 "origin": origin, "chars": len(text), "tokens": metrics.tokens(text)}
        entry.update({("with" if key == "with_" else key): value
                      for key, value in rest.items() if value})
        self._ledger.append(entry)

    def note_package(self, path: Path | None) -> str:
        """-> the package a served document belongs to: its manifest's name; outside any
        package, the PLACE it was served from -- `instance` for the operator's own space,
        `machine` for `.sys/`, `repository` for the workspace around the instance -- and
        empty where there is no document to attribute."""
        if path is None:
            return ""
        root = instance.package_of(Path(path))
        if root is None:
            meta = self.member.meta
            if not Path(path).is_relative_to(meta):
                return "repository"
            return "machine" if Path(path).is_relative_to(meta / instance.SYS) else "instance"
        try:
            return str(instance.manifest_of(root).get("name") or root.name.split("@")[0])
        except Refusal:
            return root.name.split("@")[0]

    def noted(self, refusal: Refusal) -> None:
        """Best-effort: the refusal arrives in the run's log when one is open --
        a refusal before any run is resolved has no home, and that is said."""
        if self._log:
            log.record(self._session.parent / self._log, "refusal",
                       code=refusal.code, detail=str(refusal))
            if self._count_traced("refusal", "code", refusal.code) >= 2:
                self._signal("engine", "refused", evidence=refusal.code)

    def _trace(self, kind: str, **data) -> None:
        if self._log and not self._dry:
            log.record(self._session.parent / self._log, kind, **data)

    def _signal(self, source: str, signal: str, vector: str = "",
                door: str = "", evidence: str = "") -> None:
        """A motor's push, from a moment the conductor owns: the sink shapes it, a
        crossing latches the run at once -- and a push never breaks the turn."""
        try:
            crossed = events.push(self.member.meta, source, signal, vector=vector,
                                   door=door, evidence=evidence)
        except Refusal as refusal:
            self._trace("signal-refused", source=source, signal=signal, code=refusal.code)
            return
        self._trace("signal", source=source, signal=signal, vector=vector)
        slot = self._slot()
        if crossed and slot:
            persistence.latch(slot, crossed)

    def _count_traced(self, kind: str, field: str, value: str) -> int:
        """-> occurrences in THIS run's own trace -- the session scope, no new state."""
        if not (self._session and self._log):
            return 0
        path = self._session.parent / self._log
        if not path.is_file():
            return 0
        found = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("kind") == kind and event.get(field) == value:
                found += 1
        return found

    def _save(self, stack: Stack) -> None:
        if self._dry:
            return
        persistence.save(self._session, self.member.name, stack, self._served,
                         self._log, self._turns, self._ephemerals,
                         segments=self._segmap if self._remap else None,
                         proven=sorted(self._proven),
                         emitted=sorted(self._emitted_run))

    def _draft(self, frame: Frame) -> None:
        """A draft stands: its document joins the names the FINAL delivers -- a draft
        following one of the same document is the same production and adds no name."""
        name = frame.document.name
        if not self._ephemerals or self._ephemerals[-1] != name:
            self._ephemerals.append(name)

    def _consumer(self, stack: Stack, frame: Frame,
                  instruction: Instruction) -> tuple[bool, str]:
        """-> (is the ADJACENT next instruction a consumer, the input it declares).
        A CALL whose callee declares `input:` consumes. A LAST instruction's
        production flows out with its frame's pop --
        so its consumer is the CALLER's own continuation, recursively. A document
        DECLARING a `sink:` consumes its own production -- it goes to the skill the
        declaration names, never to the chat. Anything else and the production is
        the chat's: forgotten downstream, by design."""
        if (str(frame.document.front.get("sink", "")).strip()
                and instruction.keyword in language.FREE):
            return True, ""
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        if not following:
            if frame.caller is None:
                return False, ""
            below = stack.frames[stack.frames.index(frame) - 1]
            return self._consumer(stack, below, frame.caller)
        nxt = following[0]
        if nxt.keyword in ("PROVE", "SERVE", "HOOK"):
            # checkpoints and pure chaining sit ON the flow, not in it: consumption
            # computes THROUGH them -- FINAL does not (the frontier delivers in chat)
            return self._consumer(stack, frame, nxt)
        if nxt.keyword == "PICK":
            # the pipeline feeds the ELECTION: a PICK's options ARE the upstream
            # production -- it consumes, with no declared input to match
            return True, ""
        if nxt.keyword == "CALL":
            path = self._resolve(nxt.argument)
            if path.is_file():
                declared = str(reading.read(path).front.get("input", "")).strip()
                if declared:
                    return True, declared
        return False, ""

    def _output_of(self, frame: Frame) -> str:
        return str(frame.document.front.get("output", "free")).strip() or "free"

    def _frame(self, document: Document) -> Frame:
        """Entering a frame PUSHES what the document puts in force -- overlays merged."""
        laws, tools = compiling.effective(self.member.meta, document)
        return Frame(document, reading.procedure(document), laws, tools,
                     cycle=reading.cycles(document))

    def peek(self) -> Block | None:
        """-> the block that STANDS -- what the last output left, read back from the
        state. DRY: a throwaway restore, nothing saved, nothing traced, the cadence
        untouched. A view is a status check: it shows where the run IS, never a step
        ahead of it, and whether a name is offered is `route()`'s answer alone."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._staged = []
        self._emitted, self._seg_frame = set(), None
        self._segmap = []
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return None
        self._dry = True
        return self._standing(self._rebind(restored))

    def rendered(self, block: Block, lead: str = "") -> str:
        """-> the block's TEXT, cut under the host's cap. The engine measures what it is
        about to hand over -- all of it, whatever the matter -- and closes the output at a
        seam; what is left waits at the run's state and comes back on a bare call.

        `lead` is the text a GESTURE printed before its `::mount`: it belongs to the same
        output, so it counts under the same cap and leaves ONE rest. A short lead opens the
        output as the script wrote it and the block's first chunk takes the room left; a
        lead too long for that joins the matter, under the heading.

        documentary: the cap is a fact of the HOST, not of pp; the engine's business is
        never to exceed it, and never to let a file stand between the block and its reader."""
        from .. import rendering
        matter, tail = rendering.parts(block)
        head = rendering.head(block)
        slot = self._slot()
        cap = self._settings.harness_cap
        opening = f"{lead}\n" if lead else ""
        if self._dry or slot is None or not slot.exists() or cap <= 0:
            return opening + rendering.joined(rendering.under(head, matter), tail)
        if lead and len(opening) > cap // 2:
            matter, opening = "\n\n".join(one for one in (lead, matter) if one), ""
        text, rest = self._chunked(head, matter, tail, cap - len(opening))
        text = opening + text
        if not rest:
            persistence.set_pending(slot, {})
            self._staged = []
            return text
        # the head waits with the tail; the readings of this output are DEMOTED from the
        # run's proofs until their last chunk leaves -- a document is proven by its
        # delivery, never by its composition alone
        staged = sorted(set(self._staged))
        self._proven.difference_update(staged)
        persistence.remove_proven(slot, staged)
        persistence.set_pending(slot, {"matter": rest, "tail": tail, "head": head,
                                       "staged": staged})
        self._staged = []
        self._trace("cut", left=len(rest))
        return text

    def gestured(self, text: str, head: str) -> str:
        """-> what a GESTURE's script printed, cut under the host's cap at the seam of every
        output. Under the cap the text leaves as the script wrote it: no heading, nothing
        kept. Over it, each chunk opens on the output's heading and the rest waits at the
        run like a block's -- the bare call serves it, any other call bounces. A gesture is
        no step: no tail rides the last chunk, no reading is staged, the run does not move."""
        slot = self._slot()
        cap = self._settings.harness_cap
        if slot is None or not slot.exists() or cap <= 0 or len(text) <= cap:
            return text
        chunk, rest = self._chunked(head, text, "", cap)
        persistence.set_pending(slot, {"matter": rest, "tail": "", "head": head, "staged": []})
        self._trace("cut", left=len(rest))
        return chunk

    def _chunked(self, head: str, matter: str, tail: str, cap: int) -> tuple[str, str]:
        """-> (the output's text, what is left). The whole block when it fits under the cap
        with its tail; else an INTERMEDIATE chunk: the head, the matter that fits, and a
        closing that says the reading -- what remains, how many chunks, the bare call that
        alone serves them -- and carries no instruction: the block's own tail (its
        INSTRUCTION, its true closing) rides the LAST chunk only, so nothing invites a
        production before the reading is whole."""
        from .. import rendering
        room = cap - len(tail) - len(head) - 2
        chunk, rest = rendering.cut(matter, room)
        if not rest:
            return rendering.joined(rendering.under(head, chunk), tail), ""
        waiting = self._waiting(len(rest), room)
        for _ in range(2):          # the closing's own length varies by a few digits
            if len(head) + 2 + len(chunk) + 1 + len(waiting) <= cap:
                break
            chunk, rest = rendering.cut(matter, cap - len(waiting) - len(head) - 2)
            waiting = self._waiting(len(rest), room)
        return rendering.joined(rendering.under(head, chunk), waiting), rest

    def _waiting(self, left: int, room: int) -> str:
        """The closing of an intermediate chunk: the reading continues, the bare call alone
        serves it. Any other call BOUNCES at the console (`chunk-pending`)."""
        more = max(1, -(-left // max(room, 1)))
        return (f"\n{Block.SIGNAL} CONTINUE\n./pp {self._run_id or ''}".rstrip()
                + f"   (a reading continues: {left} characters in {more} more chunk(s) -- "
                "the bare call alone serves them; any other call bounces, to be played "
                "after the last)")


    def shown(self, block: Block) -> str:
        """-> the block's TEXT for a VIEW that advances nothing -- the keyless look, `-peek`,
        an ask denied out of turn. Cut under the host's cap at the very seam every output
        uses; what is left is NOT kept, because a view writes no state: the keyed call
        serves the block whole, in chunks, and the note says so.

        documentary: one seam for every text the engine hands over (`rendering.cut`); an
        output and a view differ only in whether the rest waits at the run."""
        from .. import rendering
        matter, tail = rendering.parts(block)
        head = rendering.head(block)
        cap = self._settings.harness_cap
        if cap <= 0:
            return rendering.joined(rendering.under(head, matter), tail)
        note = ("\n\n(this view is cut under the host's cap -- the keyed call serves "
                "the block whole, in chunks)")
        chunk, rest = rendering.cut(matter, cap - len(tail) - len(note) - len(head) - 2)
        if not rest:
            return rendering.joined(rendering.under(head, matter), tail)
        return rendering.joined(rendering.under(head, chunk + note), tail)

    def pending(self) -> bool:
        """-> whether a cut block still has matter waiting: the next bare call serves it
        BEFORE the flow advances."""
        slot = self._slot()
        return bool(slot and persistence.pending_of(slot).get("matter"))

    def next_chunk(self) -> str:
        """-> the next chunk of a cut block, the state consumed as it goes: the last one
        carries the block's own closing back, so the flow resumes where it stood."""
        slot = self._slot()
        held = persistence.pending_of(slot) if slot else {}
        matter, tail, head = held.get("matter", ""), held.get("tail", ""), held.get("head", "")
        staged = list(held.get("staged", []))
        cap = self._settings.harness_cap
        text, rest = self._chunked(head, matter, tail, cap)
        if rest:
            persistence.set_pending(slot, {"matter": rest, "tail": tail, "head": head,
                                           "staged": staged})
            self._trace("chunk", left=len(rest))
            return text
        persistence.set_pending(slot, {})
        self._trace("chunk", left=0)
        # the last chunk has left: the output's readings are PROVEN for the run
        self._proven.update(staged)
        persistence.add_proven(slot, staged)
        return text

    def route(self, name: str, at: int | None = None) -> dict | None:
        """-> the CURRENT OUTPUT's segment entry `name` routes to -- the scope kept
        PER SEGMENT, consulted one list at a time, never their union. Bare: exactly
        one owning segment routes; several REFUSE asking for the address; none is
        None (the caller's unchanged refusal). Addressed (`@n`): that segment or a
        named refusal -- addresses live with their output."""
        slot = self._slot()
        segments = persistence.segments_of(slot) if slot else []
        owners = [one for one in segments if name in one.get("tools", [])]
        if at is not None:
            hit = next((one for one in owners if one.get("ordinal") == at), None)
            if hit is None:
                raise Refusal("address-stale",
                              f"segment [{at}] of the current output does not offer "
                              f"`{name}` -- addresses live with their output")
            return hit
        if len(owners) > 1:
            where = ", ".join(str(one["ordinal"]) for one in owners)
            raise Refusal("address-ambiguous",
                          f"`{name}` is offered by segments [{where}] of the current "
                          f"output -- address it: `-s {name}@<n>`")
        return owners[0] if owners else None

    def anchor_line(self, entry: dict | None) -> str:
        """-> the gesture's anchor line, or NOTHING. The line is owed only when the
        current output carried several segments: with one scope in view the question
        `where did it land` does not arise, and the skill's output speaks alone.

        documentary: the segment map is the same one `route()` consults -- one record
        of what the output offered, read for the address and for the line alike."""
        from .. import rendering
        slot = self._slot()
        segments = persistence.segments_of(slot) if slot else []
        if len(segments) < 2:
            return ""
        hit = entry or segments[-1]
        return rendering.anchor(hit.get("ordinal") or len(segments), hit.get("stack", ""))

    def gesture_trace(self, name: str, entry: dict, said: str | None = None) -> None:
        """A SCRIPT call leaves its attribution in the run's trace --
        call -> owning step, nothing advanced, nothing shown -- and, when the script
        ran, the weight of what it printed: `chars` and `tokens`."""
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return
        self._rebind(restored)
        weight = {} if said is None else {"chars": len(said), "tokens": metrics.tokens(said)}
        self._trace("gesture", name=name, segment=entry.get("ordinal"),
                    frame=entry.get("frame"), **weight)

    def served(self) -> dict[str, int]:
        """-> what this session has been served so far, part by part."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._staged = []
        self._emitted, self._seg_frame = set(), None
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        return restored[2] if restored else {}

    def _rebind(self, restored: tuple[str, Stack, dict, str | None, int, list, list, list]) -> Stack:
        """Keeps the checkout we were launched in -- looking the name up would lose a worktree."""
        member, stack, self._served, self._log, self._turns, self._ephemerals, proven, emitted = restored
        self._proven = set(proven)
        self._emitted_run = set(emitted)
        if member != self.member.name:
            self.member = discovery.member(self.siblings, member)
        return stack
