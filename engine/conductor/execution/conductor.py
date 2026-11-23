"""execution.conductor -- the FACADE: the run's shared state, its cycle of life (slot, trace, save, rebind), its
inspection (peek, route) -- and the class every domain's mixin assembles into.
The state lives HERE and nowhere else: a mixin declares no attribute, it reads the
facade's. `revive` is the facade's reader of a saved frame, handed to persistence."""
from __future__ import annotations

import json
import os
import secrets
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from ..packaging import compiling, events
from .. import reading
from ..core import language, messages, navigation
from ..state import context, discovery, instance, log, metrics, persistence, settings
from ..core.errors import Refusal
from ..core.model import Block, Document, Frame, Instruction, Member, Segment, Stack
from ..reading import Reading
from .revive import revive   # noqa: F401 -- the facade's reader of a saved frame, re-exported
from .advancing import Advancing
from .blocks import Assembling
from .boot import Booting
from .entry import Entering
from .gestures import Gesturing
from .hosting import Hosting
from .judgment import Judging
from .stepping import Stepping



class Conductor(Advancing, Booting, Gesturing, Stepping, Judging, Hosting, Assembling, Entering, Reading):
    """Holds the procedure, the stack and the initiative; the agent only ever infers.

A conductor stands on ONE member -- the workspace the engine was launched on -- and
knows no neighbour: the members beside it are the discovery's business
(`state/discovery.py`), read by the skills that need them, never by a run."""

    def __init__(self, member: Member, script: Path, run: str | None = None) -> None:
        self.member = member
        self._launch = member
        self._script = script
        self._served: dict[str, int] = {}
        self._proven: set[str] = set()     # the readings proven by content this run:
                                           # a document is served once, never twice
        self._served_tacit: dict[str, str] = {}  # path -> the place of a file served from the RUN's own
                                                 # tree, by a row that named none: the ledger's alone
        self._served_from: dict[str, str] = {}   # path -> the MATERIAL it was served from,
                                       # when that is not the repository: the title and
                                       # the ledger say it; the memo lives the process
        self._staged: list[str] = []       # the readings of the output being built: DEMOTED
                                           # from the proofs when the output is cut, back when
                                           # their last chunk leaves -- proven by delivery
        self._fresh: set[str] = set()      # the readings this call serves for the FIRST time:
                                           # never proven before -- what the agent has not read
        self._payloads: list[tuple[str, str]] = []
        self._proper: set[str] = set()   # among the readings that wait for their block, the subjects
                                       # PROPER to the step that will carry them (`_own`)
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
        self._reask = False        # set by a proof that breaks its form, consumed by submit:
                                   # the same proof step asked again, nothing replayed
        self._asked_again = False  # the output under way asks the same proof again: its
                                   # heading carries no REPAIR mark, nothing replays
        self._replaying = False    # the output under way renders again what the agent read
                                   # (`_replayed`): its blocks carry `replay`
        self._gaps: list[tuple[str, str]] = []   # the gaps a proof declared in THIS call --
                                   # (code, what is missing): the next closing says them
        self._run = run                # the id the CONVERSATION named (`-run`), if any
        self._run_id: str | None = None   # the id of the RESOLVED run
        self._session: Path | None = None  # the resolved slot -- `_slot()` owns it
        self._log: str | None = None   # the run's own session-<UTC>.jsonl -- state names it
        self._turns = 0                # completed exchanges -- what a `^ @Doc.field` guard paces on
        self._dry = False              # a PEEK plays on a throwaway restore: 0 save, 0 trace
        self._stacked: list[Segment] = []   # the FUSED segments of the output being built:
                                       # each keeps its blocks, rendered once where the
                                       # output closes
        self._caught = False           # the call under way was CAUGHT: a print missed, its block a view
        self._owing: list[Block] = []  # the steps this output said on `terminal`: due to print
                                       # from its close, where the state takes them
        self._fused = 0                # yields rendered in this output -- the cap counts these
        self._output_clock = ""        # the hour of the output being built: read at its first
                                       # block, written on the output's own heading, once
        self._emitted: set[str] = set()   # codes said VERBATIM in this output (D-d)
        self._emitted_run: set[str] = set()   # the codes-mode LEDGER: laws whose text
                                       # this RUN has rendered once -- first emission
                                       # verbatim, codes after; persisted at the slot,
                                       # cleared by `-compacted` (the texts return)
        self._seg_scope: tuple | None = None   # the scope of the output's last segment (`_scope`): a
                                       # block of that scope joins it, any other opens the next
        self._segmap: list[dict] = []  # the output's OFFER MAP -- one entry per heading
                                       # (ordinal, frame, stack, tools, constraint lines):
                                       # what a `-s` call routes against once the
                                       # segment's frame is resolved or popped
        self._remap = False            # only a MUTATING advance replaces the persisted
                                       # map -- a re-show (resume, peek) keeps the
                                       # standing addresses: they live with their output
        self._route_note = ""          # `[n] FRAME` -- said once, on the entry heading
        self._traced_in_call = 0       # the trace lines the call under way wrote (`_advancing`)
        self._unplayed = 0             # the trace lines of the call a refusal just ended: what the
                                       # console's note of that refusal says was not played
        self._holding = False          # the principal's call holds its output OPEN (`open_output`): the
                                       # message it carries opens the exchange and renders no block
        self._said_open = ""           # what such a call prints: the output's heading, its act's line

    @classmethod
    def here(cls, script: Path, run: str | None = None, home: Path | None = None) -> "Conductor":
        """The facade at the console: the member is the instance ADDRESSED (`home`) when
        one was given, the one the engine is installed in otherwise -- `script` stays the
        engine invoked, whose card `card-drift` compares."""
        member = discovery.member_at(home) if home is not None else discovery.installed_member(script)
        return cls(member, script, run)

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
                          messages.refusal_run_ambiguous(len(found)))
        if found:
            self._run_id = persistence.run_id_of(found[0])
            return self._bind(found[0])
        return None

    def switch_state(self) -> tuple:
        """-> the packages' state as an output's heading says it, for a view that has no
        block to carry it: one (package, state) pair per pin beyond the base."""
        return self._switch_state()

    def _bind(self, slot: Path) -> Path:
        """The slot resolved: its SWITCHES enter the play before anything reads the
        composition -- what the launcher gave this run and what its words switched since
        play as the run says, over SETTINGS, for this process and this instance alone --
        and its TRACE is where this process writes, whatever
        verb resolved the slot. Its ROOT OF DOCUMENTS enters the same way: the one the run
        was given at `-new`, read at the slot; a call that names another refuses
        `documents-fixed`, nothing played."""
        root = persistence.documents_of(slot)
        asked = os.environ.get(context.DOCUMENTS, "").strip()
        if asked and Path(asked) != Path(root or "."):
            raise Refusal("documents-fixed",
                          messages.refusal_documents_fixed(context.DOCUMENTS, asked, persistence.run_id_of(slot), root or 'none'))
        self._session = slot
        self._log = self._log or persistence.trace_of(slot)
        instance.play_switches(self._launch.meta, persistence.switches_of(slot))
        instance.play_documents(self._launch.meta, root)
        # the run named in THIS process's environment: every script it launches inherits
        # it, a gesture played in-process reads it -- one site, every path
        os.environ[context.VARIABLE] = persistence.run_id_of(slot)
        return slot

    def switch(self, name: str, off: bool, agents: bool = False) -> str:
        """The switch of one package, for THIS run: `off` takes it out of the play --
        nothing of it is served or played, its dependents leave with it -- and `on`
        brings it back; both are written at the run's own switches, which beat the hard
        switch of SETTINGS name by name, and every reader filters at ONE point. The run
        does not move: a switch is the operator's word, never a step, so the answer is
        the block that STANDS.
        -> the fact, then that block, through the seam (`delivered`): the fact is the
        switch's answer, the block what it serves."""
        slot = self._slot()
        if slot is None or not slot.exists():
            raise Refusal("no-run", messages.refusal_no_run())
        meta = self.member.meta
        if name == instance.base_of(meta):
            raise Refusal("package-base",
                          messages.refusal_package_base_off(name))
        if name not in instance.pins(meta):
            raise Refusal("package-unpinned",
                          messages.refusal_package_unpinned_here(name))
        held = persistence.switches_of(slot)
        if off:
            flight = self._in_flight(name, slot)
            if flight:
                raise Refusal("package-in-flight",
                              messages.refusal_package_in_flight(name, ', '.join(flight)))
        held[name] = "off" if off else "on"
        persistence.set_switches(slot, held)
        instance.play_switches(meta, held)
        self._trace("switch", package=name, off=off)   # the word is written where it happened
        block = self.peek()
        fact = messages.switched(name, off)
        return self.delivered(block, agents, lead=fact, act="switch", view=True)

    def _in_flight(self, name: str, slot: Path) -> list[str]:
        """-> what of `name` the run HOLDS: a frame of the stack, said by its file's name,
        or a standing mount, said by its ADDRESS as the slot keeps it -- every form read
        by the one mount reader (`_mount_path`), so a manual mounted by its skill's name
        and a `<package>:<path>` count like a document mounted by its own; an address
        no file answers any more is not in flight. Read before the switch, while the
        package still resolves."""
        found = []
        for one in persistence.paths_of(slot):
            path = Path(one)
            if not path.is_absolute():
                try:
                    path = self._mount_path(one)
                except Refusal:
                    continue
            kind, segment = instance.machine_part(self._launch.meta, path)
            if kind == "vendor" and (segment or "").split("@")[0] == name:
                found.append(path.name if Path(one).is_absolute() else one)
        return found

    def _mint(self) -> str:
        """-> a short run id, its slot RESERVED: no other opening can claim it. A key whose
        slot stands -- a run's, or a launcher's reservation -- draws another."""
        while True:
            candidate = secrets.token_hex(3)
            if persistence.reserve(self._launch.meta, candidate):
                return candidate

    @property
    def run_id(self) -> str | None:
        """-> the resolved run's id, once a call resolved one."""
        return self._run_id

    def resolved(self) -> str:
        """-> the id of the run this conversation talks to, resolved now (`_slot`); empty when none
        stands. A read: nothing written."""
        self._slot()
        return self._run_id or ""

    def renewal(self) -> dict | None:
        """-> the renewal mark the resolved slot holds -- an upgrade renewed the run, its
        next keyed call reopens it -- or None for a run, or no slot. A read: nothing written."""
        slot = self._slot()
        return persistence.renewed(slot) if slot is not None else None

    def _cap(self) -> int:
        """-> the cap the resolved run's outputs are cut under: the cap the launcher names on its
        call (`PP_PROMPT_CAP`), else the instance's setting raised to the floor
        (`settings.served_cap`)."""
        return settings.served_cap(self._settings.harness_cap, True,
                                   context.prompt_cap(self._run_id or ""))

    def _receiving(self) -> str:
        """-> the CHANNEL an output of this run reaches the agent by: the prompt of a launch, its
        principal making the run advance -- `closing` deduces the foot from the channel and what
        the stack awaits. A view, a manual and an inline answer reach the agent by the tool
        (`language.TOOL`)."""
        return language.PROMPT

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
        package, the PLACE it was served from -- the MATERIAL's name when a row named one
        and it answered, `instance` for the operator's own directory, `machine` for `.sys/`,
        `repository` for the workspace around the instance -- and empty where there is no
        document to attribute."""
        if path is None:
            return ""
        if str(path) in self._served_from:
            return self._served_from[str(path)]   # a material's tree: named as the row named it
        if str(path) in self._served_tacit:
            return self._served_tacit[str(path)]  # the run's own tree, as its slot names it
        root = instance.package_of(Path(path))
        if root is None:
            meta = self.member.meta
            if not Path(path).is_relative_to(meta):
                # the engine's files are the machine's; anything else is the repository
                return "machine" if instance.machine_part(meta, path)[0] == "engine" else "repository"
            return "machine" if Path(path).is_relative_to(meta / instance.SYS) else "instance"
        try:
            return str(instance.manifest_of(root).get("name") or root.name.split("@")[0])
        except Refusal:
            return root.name.split("@")[0]

    def noted(self, refusal: Refusal) -> None:
        """Best-effort: the refusal arrives in the run's log when one is open --
        a refusal before any run is resolved has no home, and that is said. The line
        carries `unplayed`, the count of the lines the refused call traced before it
        refused: the journal keeps what the call attempted, and the readers that count
        the trace leave those lines out (`_count_traced`)."""
        if self._log:
            unplayed, self._unplayed = self._unplayed, 0
            log.record(self._session.parent / self._log, "refusal",
                       code=refusal.code, detail=str(refusal),
                       **({"unplayed": unplayed} if unplayed else {}))
            if self._count_traced("refusal", "code", refusal.code) >= 2:
                self._signal("engine", "refused", evidence=refusal.code)

    def _trace(self, kind: str, **data) -> None:
        if self._log and not self._dry:
            log.record(self._session.parent / self._log, kind, **data)
            self._traced_in_call += 1

    def _signal(self, source: str, signal: str, vector: str = "",
                door: str = "", evidence: str = "", way: str = "") -> None:
        """A motor's push, from a moment the conductor owns: the sink shapes it, a
        crossing latches the run at once -- and a push never breaks the turn. A signal
        declaring a LEVEL is also said in the block: `way` is the way out the diagnostic
        names when the push carries no door of its own."""
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
        self._diagnose(source, signal, evidence, way or door)

    def _diagnose(self, source: str, signal: str, fact: str, way: str) -> None:
        """A signal with a LEVEL becomes ONE diagnostic line -- `<signal> · <level> · <fact>
        -- <way out>` -- formed here, the one site that holds the evidence (the bus keeps
        none), traced once per run and per fact, and rendered by the next block assembled
        (`_due_diagnostics`). A view (`-peek`) forms none."""
        if self._dry:
            return
        spec = events.spec_of(self.member.meta, source, signal)
        level = str(spec.get("level") or "")
        if not level:
            return
        fact = " ".join(str(fact).split()) or signal
        way = " ".join(str(way or spec.get("door") or "").split())
        key = f"{signal}|{fact}"
        if self._count_traced("diagnostic", "key", key):
            return
        line = messages.diagnostic(signal, level, fact, way)
        self._trace("diagnostic", key=key, signal=signal, level=level, fact=fact, line=line)

    def _due_diagnostics(self) -> tuple[tuple[str, str], ...]:
        """-> (key, line) of every diagnostic this run formed and no block rendered yet --
        read off the trace, the run's own memory: a refusal met outside any block is said
        by the next one, whatever process assembles it. A view reads nothing."""
        if self._dry or not (self._session and self._log):
            return ()
        path = self._session.parent / self._log
        if not path.is_file():
            return ()
        formed: dict[str, str] = {}
        rendered: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if '"diagnostic' not in line:      # neither a formed line nor a block that rendered one
                continue
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("kind") == "diagnostic":
                formed[str(event.get("key", ""))] = str(event.get("line", ""))
            elif event.get("kind") == "block":
                rendered.update(str(one) for one in (event.get("diagnostics") or ()))
        return tuple((key, text) for key, text in formed.items() if key not in rendered)

    def _count_traced(self, kind: str, field: str, value: str) -> int:
        """-> occurrences in THIS run's own trace -- the session scope, no new state. The lines
        a refused call traced before it refused are not PLAYED: the refusal's own line says how
        many (`unplayed`), and they count for nothing here -- a `repair`, a `mounted`, a
        `diagnostic` of a call that wrote no state never happened to the run."""
        if not (self._session and self._log):
            return 0
        path = self._session.parent / self._log
        if not path.is_file():
            return 0
        found: list[int] = []
        for at, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("kind") == "refusal" and event.get("unplayed"):
                found = [one for one in found if one < at - int(event["unplayed"])]
            if event.get("kind") == kind and event.get(field) == value:
                found.append(at)
        return len(found)

    def _save(self, stack: Stack) -> None:
        """The run's state, saved: under the transaction of the call under way (`_advancing`) it
        is staged, and the call's end writes it once -- or not at all when the call refuses."""
        if self._dry:
            return
        persistence.save(self._session, self.member.name, stack, self._served,
                         self._log, self._turns,
                         segments=self._segmap if self._remap else None,
                         proven=sorted(self._proven),
                         emitted=sorted(self._emitted_run))

    def _consumer(self, stack: Stack, frame: Frame,
                  instruction: Instruction) -> tuple[bool, str]:
        """-> (is the ADJACENT next instruction a consumer, the input it declares).
        A CALL whose callee declares `input:` consumes. A LAST instruction's
        production flows out with its frame's pop -- to the SUCCESSORS its document
        declares under `next:` when one of them declares `input:`, else to the
        CALLER's own continuation, recursively. A document
        DECLARING a `sink:` consumes its own production -- it goes to the skill the
        declaration names, never to the principal. Anything else and the production is
        the response's: forgotten downstream, by design."""
        if (str(frame.document.front.get("sink", "")).strip()
                and instruction.keyword in language.FREE):
            return True, ""
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        if not following:
            needs = sorted({instance.declared(self.member.meta, self._resolve(name), "input") or ""
                            for name in reading.nexts(frame.document)} - {""})
            if needs:
                return True, needs[0] if len(needs) == 1 else "any"
            if frame.caller is None:
                return False, ""
            below = stack.frames[stack.frames.index(frame) - 1]
            return self._consumer(stack, below, frame.caller)
        nxt = following[0]
        if nxt.keyword in ("PROVE", "SERVE", "HOOK"):
            # checkpoints and pure chaining sit ON the flow, not in it: consumption
            # computes THROUGH them; the end of the passage delivers the response
            return self._consumer(stack, frame, nxt)
        if nxt.keyword == "PICK":
            # the pipeline feeds the ELECTION: a PICK's options ARE the upstream
            # production -- it consumes, with no declared input to match
            return True, ""
        if nxt.keyword in ("CALL", language.OPEN):
            path = self._resolve(nxt.argument)
            if path.is_file():
                declared = instance.declared(self.member.meta, path, "input")
                if declared:
                    return True, declared
        return False, ""

    def _elects(self, stack: Stack, frame: Frame, instruction: Instruction) -> bool:
        """-> whether the step that consumes this production is a PICK -- the same
        walk as `_consumer` (through a checkpoint, a SERVE, a HOOK, the pop of a
        callee), answering the one question the capture asks: is this list the
        OPTIONS of an election, to be judged on its form before it renders. A `sink:`
        takes the production first; a CALL's seed is the assembly guard's business."""
        if str(frame.document.front.get("sink", "")).strip():
            return False
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        if not following:
            if frame.caller is None:
                return False
            below = stack.frames[stack.frames.index(frame) - 1]
            return self._elects(stack, below, frame.caller)
        nxt = following[0]
        if nxt.keyword in ("PROVE", "SERVE", "HOOK"):
            return self._elects(stack, frame, nxt)
        return nxt.keyword == "PICK"

    def _output_of(self, frame: Frame) -> str:
        return instance.declared(self.member.meta, frame.document.path, "output") or "any"

    def _form_of(self, stack: Stack, frame: Frame, instruction: Instruction) -> str:
        """-> the form THIS step produces: the list when a PICK elects from it -- the
        engine's form, whatever the document's `output:` says --, the document's own
        otherwise."""
        if instruction.keyword in language.FREE and self._elects(stack, frame, instruction):
            return language.LIST
        return self._output_of(frame)

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
        self._emitted, self._seg_scope = set(), None
        self._segmap = []
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return None
        self._dry = True
        return self._standing(self._rebind(restored))

    def viewed_map(self) -> None:
        """The VIEW just rendered is the agent's current output: the offer map keeps the
        segment of the step that stands, the one the view shows -- an address read on the
        screen is the one the router judges, and an earlier segment's is stale."""
        slot = self._slot()
        segments = persistence.segments_of(slot) if slot else []
        if len(segments) > 1:
            persistence.set_segments(slot, segments[-1:])

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
        matter, steps, foot = rendering.pieces(block)
        head = rendering.head(block)
        slot = self._slot()
        cap = self._cap()
        opening = f"{lead}\n" if lead else ""
        self._asked_last(block)
        if self._dry or slot is None or not slot.exists() or cap <= 0:
            return opening + rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        if lead and len(opening) > cap // 2:
            matter, opening = "\n\n".join(one for one in (lead, matter) if one), ""
        if self.pending():
            # a reading of another output still waits at the run: this text (a view a gesture
            # mounted while the chunk waited) takes no rest slot -- clipped under the cap, the
            # clip said by its fact, nothing kept, the waiting reading untouched
            return opening + self._clip(head, matter, steps, foot, cap - len(opening))
        text, rest = self._chunked(head, matter, steps, foot, cap - len(opening), document=block.document,
                                   later=cap)
        text = opening + text
        if not rest:
            persistence.set_pending(slot, {})
            self._staged = []
            return text
        # the head waits with the rest; the readings of this output are DEMOTED from the
        # run's proofs until their last chunk leaves -- a document is proven by its
        # delivery, never by its composition alone
        staged = sorted(set(self._staged))
        self._proven.difference_update(staged)
        persistence.remove_proven(slot, staged)
        persistence.set_pending(slot, {**rest, "staged": staged, "document": block.document, "cap": cap})
        self._staged = []
        self._trace("cut", left=self._left(rest))
        return text

    # the acts that ANSWER the agent's call: they move nothing
    # the principal relays -- a view (`-peek`, a denied offer, a switch) and the manual a bare
    # script mounts come back in the tool return, cut under the host's cap
    ANSWERED = frozenset({"view", "denied", "switch", "manual"})

    def open_output(self) -> None:
        """The principal's call asks its output HELD OPEN (`PP_HOLD_OUTPUT`, read by the console): said
        before an opening plays, so the run it opens stands on its first exchange and renders no
        block (`_held_open`)."""
        self._holding = True

    def said_open(self) -> str:
        """-> what a call that opened an exchange under an output held open prints: the output's
        heading, then the line of its act; "" for any other call."""
        return self._said_open

    def delivered(self, block: Block | None, agents: bool = False, lead: str = "",
                  act: str = "value", view: bool = False, gesture: bool = False) -> str:
        """The ONE seam a block leaves the engine by on a keyed call -> the text the call
        prints. What the engine renders of a block is SERVED: it goes to the run's principal.
        On the principal's own call that is this call's output -- `rendered` (`shown` for a
        VIEW, which keeps nothing). On the agent's call, a block never served -- a reading, a
        law or a step the agent has not read -- is HELD at the run (`hold`, its `act` kept),
        whatever its step asks, and the call prints only what the act ANSWERS (`lead`: a
        script's own text, a switch's fact) and one neutral line telling the agent to end its
        message; the principal's bare call serves the block (`release`). Only a block the agent
        has already read comes back in the call's result (`inline`): a REPLAY (`Block.replay`:
        a repair, a proof asked again, a repair in place) that serves no reading for the first
        time (`_fresh` -- a payload rendered anew is one) and whose step asks the agent a VALUE.
        `agents` is what the console read on the call (`context.agents`) -- the facade reads
        no environment.

        A VIEW and the MANUAL of a bare script ANSWER the agent's call: they move
        nothing the principal relays, so nothing waits for the principal -- the text comes back
        in the tool return, cut under the HOST's cap (a tool result, not the harness's stdin),
        the rest served by the agent's bare keyed call (`viewed`, `next_view`).

        A GESTURE of the principal (`-open`, `-close`, between two exchanges) moves the run to a
        block the AGENT owes: on the principal's call it is held like the agent's own, and the
        principal's bare call serves it whole -- the fused segments with it."""
        if block is None:
            return lead
        if not agents and gesture:
            self._dry = False
            self.hold(block, act)
            return messages.held(act, principal=True)
        if agents:
            if view or act in self.ANSWERED:
                shown = self.viewed(block)
                return f"{lead}\n\n{shown}" if lead else shown
            self._dry = False
            if block.replay and not self._fresh & set(self._staged) and language.valued(block.channel):
                # a replay the agent has read whole, its value asked again -- the block comes
                # back in the tool result, as a view does, and nothing waits for the principal
                shown = self.inline(replace(block, response=""), act)   # a tool result asks no last message
                return f"{lead}\n\n{shown}" if lead else shown
            self.hold(block, act)
            said = messages.held(act)
            return f"{lead}\n{said}" if lead else said
        if view:
            shown = self.shown(block)
            return f"{lead}\n\n{shown}" if lead else shown
        return self.rendered(block, lead)

    def denied(self, block: Block, name: str, agents: bool = False) -> str:
        """The out-of-turn catch -> the text the call prints: `name` is offered by no segment of
        the output that stands, so the pending block answers, its DEVIATION naming the ask as not
        played -- dry, no repair counted (a repair is for a WATCHED answer that missed), the run
        untouched. The trace says `offer-absent` with the name, once, at the site of the act; the
        block leaves by the seam of every view (`delivered`, `act` denied)."""
        import dataclasses
        self._dry = False              # the block was peeked dry: the act is traced all the same
        self._trace("offer-absent", name=name)
        answered = dataclasses.replace(
            block, deviation=messages.not_offered(name))
        return self.delivered(answered, agents, act="denied", view=True)

    def inline(self, block: Block, act: str = "value") -> str:
        """-> the block's TEXT answering the agent's call, when it REPLAYS a block the agent has
        read whole and its step asks the agent a value: the block is SERVED -- what it reads
        again stays proven, its weight on the trace as `inline` with the act that rendered
        it --, cut under the HOST's cap (a tool result, never the harness's stdin), the rest
        kept at the slot (`viewing`) for the agent's bare keyed call alone, chunk by chunk
        (`next_view`). A prior view's rest is forgotten, as a hold forgets it."""
        from .. import rendering
        matter, steps, foot = rendering.pieces(block)
        head = rendering.head(block)
        slot = self._slot()
        whole = rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        self._trace("inline", act=act, weight={"chars": len(whole), "tokens": metrics.tokens(whole)})
        cap = settings.served_cap(self._settings.harness_cap, False)
        if slot is None or not slot.exists() or cap <= 0:
            return whole
        text, rest = self._chunked(head, matter, steps, foot, cap, language.TOOL)
        if rest:
            persistence.set_viewing(slot, rest)
        elif persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})
        return text

    def _asked_last(self, block: Block) -> None:
        """Traces how the output that LEAVES asks its last message -- `response` when its last said
        step carries it, `response-added` when the engine added the line; an output that asks none
        says nothing. Written where an output is served or held, never where it is assembled: a
        view and an inline answer trace none."""
        if block.response:
            self._trace("response" if block.response == language.STEP else "response-added",
                        document=block.document)

    def held(self) -> bool:
        """-> whether an output waits for the principal's call: the agent's value was judged,
        its answer stands at the slot, nothing has left the tool."""
        slot = self._slot()
        return bool(slot and persistence.held_of(slot))

    def viewed(self, block: Block) -> str:
        """-> the block's TEXT for a view or a manual ANSWERING the agent's call: cut under the HOST's cap -- the instance's setting, never the
        principal's floor: the text lands in a tool result --, the rest kept at the slot
        (`viewing`) for the agent's bare keyed call alone (`next_view`); a view that fits
        leaves nothing. Any other act of either caller forgets the rest."""
        from .. import rendering
        matter, steps, foot = rendering.pieces(block)
        head = rendering.head(block)
        slot = self._slot()
        cap = settings.served_cap(self._settings.harness_cap, False)
        if slot is None or not slot.exists() or cap <= 0:
            return rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        text, rest = self._chunked(head, matter, steps, foot, cap, language.TOOL)
        if rest:
            persistence.set_viewing(slot, rest)
        elif persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})
        return text

    def viewing(self) -> bool:
        """-> whether the rest of a view waits for the agent's bare keyed call."""
        slot = self._slot()
        return bool(slot and self._left(persistence.viewing_of(slot)))

    def next_view(self) -> str:
        """-> the next chunk of a cut view, the rest consumed as it goes: the last one carries
        the block's own closing back; nothing is traced, a view writes no state of the run."""
        slot = self._slot()
        waiting = persistence.viewing_of(slot) if slot else {}
        cap = settings.served_cap(self._settings.harness_cap, False)
        text, rest = self._chunked(*self._waiting(waiting), cap, language.TOOL)
        persistence.set_viewing(slot, rest or {})
        return text

    def hold(self, block: Block, act: str = "value") -> None:
        """HOLDS the output the agent's call rendered: the act has played in full -- the value
        judged, the mount written, the door pushed --, but its text leaves by the principal's call alone (`release`),
        never by the tool return. The pieces kept are a cut's -- head, matter, tail, the
        readings staged --, so the release cuts under the cap as if the output left then; the
        staged readings are demoted from the run's proofs until their last chunk leaves, as
        `rendered` does. `act` names what was held, at the slot and on the trace. A second
        hold -- a script's second `::mount`, a view a gesture mounted over an output that waits
        -- joins the first, and a step is said ONCE: when the block rendered again carries the
        step the output that waited closed on, it takes that step's place -- its heading, its
        offers and its laws as they are now, what the step read then with what it reads now, its
        line once; what stood before the step stays. A block of another step follows the output
        that waited, whose closing lines leave with its foot. The newest head and closing stand."""
        from .. import rendering
        slot = self._slot()
        staged = sorted(set(self._staged))
        self._staged = []
        if slot is None or not slot.exists():
            return
        if persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})   # a hold forgets the rest of a view
        # a hold already standing -- this process's earlier `::mount`, or an output held before a
        # gesture of the agent mounted over it -- takes this one in
        prior = persistence.held_of(slot)
        if prior.get("open"):
            # an output held open closes on this block: the readings that waited are its matter
            prior = {**prior, "matter": "\n\n".join(
                rendering.section(language.INFORMATION, text, subject=subject)
                for subject, text in prior.get("payloads", []))}
        step, ahead, behind = self._closed_on(block)
        waited = prior.get("closing") or {}
        if step is block and waited.get("step") == self._step_of(step):
            # the same step rendered again: one block for it, what it read then and now
            block = self._rejoined(block, waited)
            step, stood = block, str(prior.get("before", ""))
        elif prior:
            # another step: what the output that waited read stays, the lines its closing block
            # asked leave with its foot -- the newest block says what is asked now
            read = [list(one) for one in prior.get("steps", [])]
            asks = int(prior.get("asks", 0))
            if read and asks:
                read[-1] = [read[-1][0], read[-1][1], read[-1][2][:-asks]]
            stood = "\n\n".join(one for one in (prior.get("matter", ""),
                                                 *(rendering.group(one) for one in read)) if one)
        else:
            stood = ""
        matter, steps, foot = rendering.pieces(block)
        head = rendering.head(block)
        matter = "\n\n".join(one for one in (stood, matter) if one)
        if prior:
            staged = sorted(set(prior.get("staged", [])) | set(staged))
        self._proven.difference_update(staged)
        persistence.remove_proven(slot, staged)
        whole = rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        self._asked_last(block)
        asks = (1 if block.command else 0) + (1 if block.response == language.ADDED else 0)
        persistence.set_held(slot, {"matter": matter, "steps": steps, "tail": foot, "head": head,
                                    "asks": asks, "staged": staged,
                                    "act": act, "document": block.document,
                                    "before": "\n\n".join(one for one in (
                                        stood, *(rendering.segment(one) for one in ahead)) if one),
                                    "closing": self._closing_kept(step, behind, block),
                                    "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                    "chars": len(whole)})
        self._trace("held", act=act, weight={"chars": len(whole), "tokens": metrics.tokens(whole)})

    @staticmethod
    def _step_of(block: Block) -> list:
        """-> what names the step a block renders: its document, its position, its instruction."""
        return [block.document, block.position, str(block.instruction)]

    @staticmethod
    def _closed_on(block: Block) -> tuple[Block | None, tuple[Segment, ...], tuple[Block, ...]]:
        """-> the step the output `block` closes ASKS, as a held output keeps it: (the block that
        renders it, the segments that stand before it, the blocks behind it). The block itself when
        it renders a step; behind an order block, the last step said under the last segment -- the
        step handed back to the agent --, that segment without it; None when the output asks no
        step."""
        if block.command:
            return block, tuple(block.stacked), ()
        last = block.stacked[-1] if block.stacked else None
        if last is None or not last.blocks or not last.blocks[-1].command:
            return None, tuple(block.stacked), ()
        rest = replace(last, blocks=last.blocks[:-1])
        rest = (replace(rest, reach=rest.stretch),) if rest.blocks else ()
        return last.blocks[-1], tuple(block.stacked[:-1]) + rest, (block,)

    def _closing_kept(self, step: Block | None, behind: tuple[Block, ...], closing: Block) -> dict:
        """-> what a held output keeps of the step it closes on, for a block that renders that step
        again (`_rejoined`): what names the step, what it read -- with what the blocks behind it
        brought --, a deviation, the diagnostics, the facts of the closing; {} when it asks no step."""
        if step is None:
            return {}
        carried = (step, *behind)
        return {"step": self._step_of(step),
                "payloads": [list(one) for each in carried for one in each.payloads],
                "proper": [one for each in carried for one in each.proper],
                "deviation": next((each.deviation for each in carried if each.deviation), ""),
                "diagnostics": [one for each in carried for one in each.diagnostics],
                "gaps": [list(one) for one in closing.gaps]}

    @staticmethod
    def _rejoined(block: Block, waited: dict) -> Block:
        """-> the block that renders again the step a held output closed on, with what that output
        kept of the step (`_closing_kept`): each reading once, the first served kept; the deviation,
        the diagnostics and the facts of the closing that waited."""
        read = [tuple(one) for one in waited.get("payloads", [])]
        seen = {subject for subject, _ in read}
        fresh = [one for one in block.payloads if one[0] not in seen]
        return replace(
            block, payloads=tuple(read + fresh),
            proper=tuple(dict.fromkeys([*waited.get("proper", []), *block.proper])),
            deviation=block.deviation or str(waited.get("deviation") or ""),
            diagnostics=tuple(dict.fromkeys([*waited.get("diagnostics", []), *block.diagnostics])),
            gaps=tuple(dict.fromkeys([*(tuple(one) for one in waited.get("gaps", [])), *block.gaps])))

    def release(self) -> str:
        """-> the held output, as the principal's bare call serves it: the first chunk under
        the cap, the rest waiting at the run like any cut block's (the principal's next
        bare calls serve it); the slot forgets the hold. Traced `advance` with `held: true`."""
        slot = self._slot()
        held = persistence.held_of(slot) if slot else {}
        if not held:
            return ""
        if held.get("open"):
            return self._released_open(slot, held)
        persistence.set_held(slot, {})
        if persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})   # the principal's call forgets the rest of a view
        self._trace("advance", held=True, prompt=False)
        head, matter, steps, foot = self._waiting(held)
        staged = list(held.get("staged", []))
        cap = self._cap()
        if cap <= 0:
            self._proven.update(staged)
            persistence.add_proven(slot, staged)
            from .. import rendering
            return rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        document = held.get("document", "")
        text, rest = self._chunked(head, matter, steps, foot, cap, document=document)
        if rest:
            persistence.set_pending(slot, {**rest, "staged": staged, "document": document, "cap": cap})
            self._trace("cut", left=self._left(rest))
            return text
        persistence.set_pending(slot, {})
        self._proven.update(staged)
        persistence.add_proven(slot, staged)
        return text

    def _held_open(self, stack: Stack, act: str, wrong: str = "", word: str = "",
                   advance: bool = True) -> None:
        """The exchange is OPENED under an output its principal holds open: the stack has not
        advanced and no block is rendered -- the mounts the principal plays next pose the context
        of the exchange, and its bare call plays it and renders it once (`_released_open`). What
        the first block rendered will carry waits with the hold: the readings composed so far and
        their lines of the ledger, the gaps, a deviation (`wrong`), the first
        output's reminder, the word that takes up a run stopped at the repair bound (`word`).
        `advance` says the release plays the exchange from where the stack stands; without it the
        run stands on a step an earlier output asked, and the release renders that step. The call
        prints the output's heading -- an opening reads its key there -- then the line of its act
        (`said_open`)."""
        slot = self._slot()
        if persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})   # a hold forgets the rest of a view
        persistence.set_held(slot, {
            "open": True, "act": act, **({"advance": True} if advance else {}),
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "payloads": [list(one) for one in self.drain()],
            "proper": sorted(self._proper),
            "ledger": [dict(one) for one in self._ledger],
            "gaps": [list(one) for one in self._gaps],
            "deviation": wrong, "word": word,
            "fusion": bool(getattr(self, "_first_output", False)),
            "staged": sorted(set(self._staged))})
        self._proper, self._ledger, self._gaps, self._staged = set(), [], [], []
        self._first_output = False
        self._trace("held", act=act, open=True)
        self._say_open(stack, "reopened" if act == "reopened" else "opened")

    def _say_open(self, stack: Stack, state: str) -> None:
        """Composes what a call that renders no block prints (`said_open`): the heading of the output
        the run holds open, then the line of what the call did (`messages.OPENED`)."""
        from .. import rendering
        head = rendering.heading(self._say_key(), self._fed(stack)[0] if stack.frames else "",
                                 False, self._clock_mark(), self._switch_state())
        said = messages.opened(state)
        self._said_open = f"{head}\n{said}" if head else said

    def _joined_open(self, stack: Stack, frame: Frame, slot: Path, prior: dict, lead: str, act: str,
                     posed: list[str]) -> str:
        """A MOUNT is POSED on the output held open -> the line the call prints (`lead`, the script's
        own text, first: it answers the call and is kept nowhere). Nothing is rendered: the entries
        are in the view -- their laws and their offers in force --, their readings and their lines of
        the ledger wait behind the readings the first block rendered will carry (`_released_open`).
        An exchange that has not advanced keeps the offer map it has. On a run that stands on a step
        an earlier output asked, the entry of that step's segment keeps the offers of its steps, takes
        the ones the mount brings behind them, and the laws now in force.
        `posed` names the addresses this call brought into the view: the hold keeps them, and a
        mount that names one again serves nothing more."""
        segments = [] if prior.get("advance") else persistence.segments_of(slot)
        if segments:
            offered = [*segments[-1].get("tools", []), *(one.name for one in self._tools_in_force(frame))]
            self._segmap = [*segments[:-1], {**segments[-1],
                                             "tools": list(dict.fromkeys(offered)),
                                             "constraints": [one.wire() for one in self._held_laws(frame)]}]
            self._remap = True
        else:
            self._segmap, self._remap = [], False
        payloads, ledger = self.drain(), self._ledger
        staged = sorted(set(prior.get("staged", [])) | set(self._staged))
        proper = sorted(set(prior.get("proper", [])) | self._proper)
        self._stacked, self._ledger, self._staged, self._proper = [], [], [], set()
        self._dry = False
        self._save(stack)
        if persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})
        persistence.set_held(slot, {
            **{key: prior[key] for key in ("gaps", "deviation", "fusion", "advance", "word")
               if key in prior},
            "open": True, "act": prior.get("act", act),
            "at": prior.get("at") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "posed": list(prior.get("posed", [])) + posed,
            "payloads": prior.get("payloads", []) + [list(one) for one in payloads],
            "proper": proper,
            "ledger": prior.get("ledger", []) + ledger, "staged": staged})
        self._trace("held", act=act, open=True)
        said = messages.held(act, "mount", principal=True)
        return f"{lead}\n{said}" if lead else said

    def _released_open(self, slot: Path, held: dict) -> str:
        """-> the output held OPEN, as the principal's bare call serves it: ONE output, rendered
        once. An exchange that has not advanced (`advance`) is PLAYED now, from where the stack
        stands -- the boot of an opening, the passage a message opened, the step the principal's
        word takes up at the repair bound, the re-serve a declared compaction owes --, every block
        with the laws then in force; on a run that stands on a step an earlier output asked, that
        step is rendered. The readings that waited are the first block's, at the head of its
        segment. Its offer map written, cut under the cap like any output. Traced: each block's own
        line, then `advance` with `held: true`. The hold leaves the slot with the call's one write:
        a release that fails serves nothing, traces no `advance` and keeps the output open at the
        run."""
        with self._advancing():
            restored = persistence.restore(slot, revive)
            if restored is None:
                persistence.set_held(slot, {})
                return ""
            stack = self._rebind(restored)
            self._dry = False
            self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT
            self._resolved = {}
            self._emitted, self._seg_scope = set(), None
            self._segmap, self._remap = [], True
            self._payloads = [tuple(one) for one in held.get("payloads", [])]
            self._proper = set(held.get("proper", []))
            self._ledger = [dict(one) for one in held.get("ledger", [])]
            self._gaps = [tuple(one) for one in held.get("gaps", [])]
            self._first_output = bool(held.get("fusion"))
            self._staged = list(held.get("staged", []))
            wrong = str(held.get("deviation") or "")
            mark = persistence.stopped_of(slot)
            if not held.get("advance"):
                block = self._standing(stack)
            elif persistence.compacted_of(slot):
                block = self._reserved(stack)
            elif mark:
                block = self._taken_up(stack, mark, str(held.get("word") or ""))
            else:
                block = self._advance(stack, wrong)
            persistence.set_held(slot, {})
            if persistence.viewing_of(slot):
                persistence.set_viewing(slot, {})   # the principal's call forgets the rest of a view
            self._trace("advance", held=True, prompt=False)
            if block is not None and wrong and not block.deviation:
                block = replace(block, deviation=wrong)
        return self.rendered(block) if block is not None else ""

    def gestured(self, text: str, head: str) -> str:
        """-> what a GESTURE's script printed, cut under the host's cap at the seam of every
        output. Under the cap the text leaves as the script wrote it: no heading, nothing
        kept. Over it, each chunk opens on the output's heading and the rest waits at the
        run like a block's -- the bare call serves it, any other call bounces. A gesture is
        no step: no tail rides the last chunk, no reading is staged, the run does not move."""
        slot = self._slot()
        cap = self._cap()
        if slot is None or not slot.exists() or cap <= 0 or len(text) <= cap:
            return text
        if self.pending():
            # a reading still waits at the run: the gesture's text takes no rest slot -- clipped,
            # the clip said, the waiting reading untouched
            return self._clip(head, text, [], "", cap)
        chunk, rest = self._chunked(head, text, [], "", cap)
        persistence.set_pending(slot, {**rest, "staged": [], "cap": cap})
        self._trace("cut", left=self._left(rest))
        return chunk

    @staticmethod
    def _waiting(kept: dict) -> tuple[str, str, list, str]:
        """-> (head, matter, steps, foot) of an output that waits at the run -- held, cut or
        viewed: the pieces a cut keeps."""
        return (kept.get("head", ""), kept.get("matter", ""),
                [list(one) for one in kept.get("steps", [])], kept.get("tail", ""))

    @staticmethod
    def _left(kept: dict) -> int:
        """-> the characters of an output that still wait: all that is left to read -- its matter
        and the groups of its steps --, or its foot when it waits alone: a foot that waits is an
        output that waits."""
        from .. import rendering
        return (len(kept.get("matter", "")) + sum(len(rendering.group(one)) for one in kept.get("steps", []))
                or len(kept.get("tail", "")))

    def _chunks(self, rest: dict, cap: int, channel: str, document: str) -> int:
        """-> the chunks an output that waits still needs: its pieces cut as the bare calls will
        cut them, counted and never rendered."""
        count = 0
        while rest:
            _, rest = self._chunked(*self._waiting(rest), cap, channel, document, counted=True)
            count += 1
        return count

    def _chunked(self, head: str, matter: str, steps: list, foot: str, cap: int,
                 channel: str = "", document: str = "", counted: bool = False,
                 later: int = 0) -> tuple[str, dict]:
        """-> (the output's text, what is left -- the pieces of a cut, {} when nothing is). The
        cap is ALWAYS held. The whole output when it fits. Else an INTERMEDIATE chunk -- the head,
        what fits, and the foot of a reading that continues (`closing`, `language.READING_ON`):
        by the tool `CONTINUE` and the bare call that alone serves the rest, at the prompt `MORE`
        and no call, the fact on both: all that is left to read, the matter and the steps, and
        the chunks still needed (`_chunks`; a call that only counts, `counted`, renders none),
        counted under the cap the bare calls will have -- `later`, when this chunk is cut under a
        smaller one behind the text a script printed; this chunk's own, else:
        - while matter is left, the matter that fits, cut at a seam (`rendering.cut`); the groups
          of the steps follow its last piece, whole when they fit with it, in the next chunk else;
        - the matter gone, the groups that fit, cut BETWEEN two steps alone: what a step reads,
          its OPTIONS and its lines stay in one chunk, in whatever segment the step stands -- the
          head of a later segment is a piece among the groups, one that asks nothing;
        - a group larger than a chunk: what it reads is cut as a reading is, and its OPTIONS and
          its lines follow the last piece; with nothing to read, its OPTIONS are cut the same way
          and its lines follow their last piece. A piece that is not the last leaves a line of its
          text behind, so the last one rides with what follows it.
        The output's own foot rides the LAST chunk only: nothing is due before the output is
        whole. `channel` names where the chunk goes; empty, the output's own (`_receiving`). At
        the prompt a chunk of the output of `document` asks its last message like any output that
        arrives there: the line of the form `empty` stands last over its `MORE`."""
        from .. import rendering
        channel = channel or self._receiving()
        whole = rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        if len(whole) <= cap:
            return whole, {}
        room = cap - len(head) - 2
        # a piece is sized under the WIDEST fact this output can say, so where a chunk ends never
        # depends on the counts its fact carries: the chunks counted are the chunks served
        widest = len(matter) + sum(len(rendering.group(one)) for one in steps) + len(foot)

        def chunk(piece: str, groups: list, rest: dict, sizing: bool = True) -> str:
            left = widest if sizing else self._left(rest)
            more = widest if sizing else self._chunks(rest, later or cap, channel, document)
            label, call, fact = self.closing(language.READING_ON, channel, left=left, more=more)
            said = [[read, options, list(lines)] for read, options, lines in groups]
            return rendering.joined(rendering.under(head, piece),
                                    rendering.tail_of(said, rendering.foot(label, call, (fact,))))

        def fitted(text: str, part: int | None = None) -> tuple[str, dict]:
            """-> (the chunk, what is left) for the largest piece of `text` a seam allows under the
            cap, the closing's own length counted: a piece of the matter (`part` None), or of what
            the first group reads (0) or of its OPTIONS (1) -- that piece leaves a line behind."""
            budget = room if part is None else min(room, len(text) - 1)
            for _ in range(4):          # the closing's own length varies by a few digits
                piece, left = rendering.cut(text, max(1, budget))
                if part is None:
                    rest = {"head": head, "matter": left, "steps": steps, "tail": foot}
                    said = chunk(piece, [], rest)
                else:
                    first = list(steps[0])
                    first[part], shown = left, ["", "", []]
                    shown[part] = piece
                    rest = {"head": head, "matter": "", "steps": [first, *steps[1:]], "tail": foot}
                    said = chunk("", [shown], rest)
                if len(said) <= cap:
                    break
                budget = len(piece) - (len(said) - cap)
            if part is None:
                return served(piece, [], rest), rest
            return served("", [shown], rest), rest

        def served(piece: str, groups: list, rest: dict) -> str:
            """-> the chunk as it leaves, its fact counting what is left; nothing for a call that counts."""
            return "" if counted else chunk(piece, groups, rest, sizing=False)

        if matter:
            return fitted(matter)
        taken: list = []
        while len(taken) < len(steps) - 1:
            rest = {"head": head, "matter": "", "steps": steps[len(taken) + 1:], "tail": foot}
            if len(chunk("", steps[:len(taken) + 1], rest)) > cap:
                break
            taken = steps[:len(taken) + 1]
        if taken:
            rest = {"head": head, "matter": "", "steps": steps[len(taken):], "tail": foot}
            return served("", taken, rest), rest
        # the first group alone is larger than a chunk: what it reads is cut as a reading is, then
        # its OPTIONS; its lines follow the last piece
        read, options, lines = steps[0]
        if read:
            return fitted(read, 0)
        if options:
            return fitted(options, 1)
        # nothing left to cut in it: its lines leave, what follows waits -- the foot alone, at the last
        rest = {"head": head, "matter": "", "steps": steps[1:], "tail": foot}
        return served("", [steps[0]], rest), rest

    def _clip(self, head: str, matter: str, steps: list, foot: str, cap: int) -> str:
        """-> a text CLIPPED under the cap, nothing kept: the head, what fits, the foot and ONE fact
        at the foot saying how much was not shown -- the same text whatever the mode. The matter is
        cut first: the steps stand whole behind the piece of it that fits. Steps that do not fit by
        themselves show none of the matter and have what they read cut, each in its turn; their
        OPTIONS and their lines are kept. What a view that keeps nothing (`shown`), and a text that
        cannot take the run's rest slot because a reading already waits there, come back as."""
        from .. import rendering
        whole = rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        if len(whole) <= cap:
            return whole
        fact = "a view cut under the cap: {n} characters not shown"
        room = cap - len(head) - len(fact) - 16

        def piece(text: str, budget: int) -> tuple[str, str]:
            return rendering.cut(text, budget) if budget > 0 else ("", text)

        if len(rendering.tail_of(steps, foot)) <= room:
            chunk, rest = piece(matter, room - len(rendering.tail_of(steps, foot)))
            shown, hidden = steps, len(rest)
        else:
            chunk, shown, hidden = "", [], len(matter)
            budget = room - len(rendering.tail_of([["", options, lines] for _, options, lines in steps], foot))
            for read, options, lines in steps:
                kept, rest = piece(read, budget)
                budget -= len(kept) + len(rendering.SEAM)
                hidden += len(rest)
                shown.append([kept, options, lines])
        tail = rendering.tail_of(shown, foot)
        said = rendering.foot("", "", (fact.format(n=hidden),))
        return rendering.joined(rendering.under(head, chunk), (tail + "\n" + said.strip("\n")) if tail else said)


    def shown(self, block: Block) -> str:
        """-> the block's TEXT for a VIEW that advances nothing -- the keyless look, `-peek`,
        an ask denied out of turn. Cut under the host's cap at the very seam every output
        uses; what is left is NOT kept, because a view writes no state: a fact at the foot
        says how much was not shown (`_clip`).

        documentary: one seam for every text the engine hands over (`rendering.cut`); an
        output and a view differ only in whether the rest waits at the run."""
        from .. import rendering
        matter, steps, foot = rendering.pieces(block)
        head = rendering.head(block)
        cap = self._cap()
        if cap <= 0:
            return rendering.joined(rendering.under(head, matter), rendering.tail_of(steps, foot))
        return self._clip(head, matter, steps, foot, cap)

    def pending(self) -> bool:
        """-> whether a cut block still has matter waiting: the next bare call serves it
        BEFORE the flow advances."""
        slot = self._slot()
        return bool(slot and self._left(persistence.pending_of(slot)))

    def drop_pending(self) -> str:
        """-> what follows a cut output's matter, the matter that waits DROPPED on the caller's
        word, and it alone: what stands before the first step, and the head of every later segment
        -- its heading, its readings, its offers, its laws --, a piece among the steps that asks
        nothing. That matter is never served and the readings it staged stay unproven -- they were
        not delivered whole --; the trace says `chunk-dropped` with the matter left. The groups of
        the steps that wait are served by the same cut as any output, under the cap: the first
        chunk here, the rest on the bare calls; the output's foot rides the last, and the flow
        resumes where the block stood."""
        from .. import rendering
        slot = self._slot()
        held = persistence.pending_of(slot) if slot else {}
        persistence.set_pending(slot, {})
        head, matter, steps, foot = self._waiting(held)
        heads = [one for one in steps if not (one[1] or one[2])]
        steps = [one for one in steps if one[1] or one[2]]
        self._trace("chunk-dropped", left=len(matter) + sum(len(rendering.group(one)) for one in heads))
        cap = self._rest_cap(held)
        if cap <= 0:
            return rendering.joined(head, rendering.tail_of(steps, foot))
        document = held.get("document", "")
        text, rest = self._chunked(head, "", steps, foot, cap, document=document)
        if rest:
            persistence.set_pending(slot, {**rest, "staged": [], "document": document, "cap": cap})
        return text

    def _rest_cap(self, held: dict) -> int:
        """-> the cap the rest of a cut output is served under: the cap its first chunk was cut
        under (`cap`, kept with the rest), never above the cap of the call that serves it -- a
        reading cut for a tool result comes in chunks of that size at the prompt too."""
        return min(self._cap(), held["cap"])

    def next_chunk(self) -> str:
        """-> the next chunk of a cut block, the state consumed as it goes, under the cap of its
        first chunk (`_rest_cap`): the last one carries the block's own closing back, so the
        flow resumes where it stood."""
        slot = self._slot()
        held = persistence.pending_of(slot) if slot else {}
        staged = list(held.get("staged", []))
        cap = self._rest_cap(held)
        document = held.get("document", "")
        text, rest = self._chunked(*self._waiting(held), cap, document=document)
        if rest:
            persistence.set_pending(slot, {**rest, "staged": staged, "document": document, "cap": cap})
            self._trace("chunk", left=self._left(rest))
            return text
        persistence.set_pending(slot, {})
        self._trace("chunk", left=0)
        # the last chunk has left: the output's readings are PROVEN for the run
        self._proven.update(staged)
        persistence.add_proven(slot, staged)
        return text

    def route(self, name: str, at: int | None = None, verb: str = "-s") -> dict | None:
        """-> the CURRENT OUTPUT's segment entry `name` routes to -- the scope kept
        PER SEGMENT, consulted one list at a time, never their union. Bare: exactly
        one owning segment routes; several REFUSE asking for the address under the
        caller's own `verb` -- but `-open`, which routes to the LAST owner, the segment
        of the pending step: a name resolves one document whatever the segment, and a
        space inherits the laws of the step it opens on; none is None (the caller's
        unchanged refusal). Addressed (`@n`): that segment or a named refusal --
        addresses live with their output."""
        slot = self._slot()
        segments = persistence.segments_of(slot) if slot else []
        owners = [one for one in segments if name in one.get("tools", [])]
        if at is not None:
            hit = next((one for one in owners if one.get("ordinal") == at), None)
            if hit is None:
                raise Refusal("address-stale",
                              messages.refusal_address_stale(at, name))
            return hit
        if len(owners) > 1 and verb == "-open":
            return owners[-1]
        if len(owners) > 1:
            where = ", ".join(str(one["ordinal"]) for one in owners)
            raise Refusal("address-ambiguous",
                          messages.refusal_address_ambiguous(name, where, verb, name))
        return owners[0] if owners else None

    def unplayed(self) -> bool:
        """-> whether an output waits OPEN at the run for an exchange that has not been played: no
        block of that exchange is rendered, so no segment of it stands to offer a door or a space."""
        slot = self._slot()
        held = persistence.held_of(slot) if slot else {}
        return bool(held.get("open") and held.get("advance"))

    def rooted(self, name: str) -> dict | None:
        """-> the entry a SCRIPT the principal plays routes to under the output it holds open: the
        offer is read where the exchange finds it -- the root of the passage, the document the
        message feeds, with its overlays and what its frame carries (`_fed`) --, whatever waits
        at the run: an open output that has rendered no block, where no segment stands to offer
        `name`, or a closed one, where several may. Nothing is rendered. None when the root does
        not offer `name`: the caller's unchanged refusal."""
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return None
        stack = self._rebind(restored)
        document, tools = self._fed(stack)
        if name not in {one.name for one in tools}:
            return None
        return {"frame": document, "stack": navigation.render(stack), "tools": [one.name for one in tools]}

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
        self._emitted, self._seg_scope = set(), None
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        return restored[2] if restored else {}

    def _rebind(self, restored: tuple[str, Stack, dict, str | None, int, list, list]) -> Stack:
        """Keeps the member we were launched on: a slot saved under another name is
        resumed here all the same, and the trace says so -- no lookup beside, which
        would lose a worktree for its main checkout."""
        member, stack, self._served, self._log, self._turns, proven, emitted = restored
        self._proven = set(proven)
        self._emitted_run = set(emitted)
        if member != self.member.name:
            self._trace("member-moved", was=member, now=self.member.name)
        return stack
