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
from ..core import language
from ..state import context, discovery, instance, log, metrics, persistence, settings
from ..core.errors import Refusal
from ..core.model import Block, Document, Frame, Instruction, Member, Stack
from ..reading import Reading
from .revive import revive   # noqa: F401 -- the facade's reader of a saved frame, re-exported
from .blocks import Assembling
from .boot import Booting
from .entry import Entering
from .gestures import Gesturing
from .hosting import Hosting
from .judgment import Judging
from .stepping import Stepping



class Conductor(Booting, Gesturing, Stepping, Judging, Hosting, Assembling, Entering, Reading):
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
        self._served_from: dict[str, str] = {}   # path -> the MATERIAL it was served from,
                                       # when that is not the repository: the title and
                                       # the ledger say it; the memo lives the process
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
        self._idle: list[str] = []   # the written PROVEs resolved idle in this call, said at its closing
        self._gaps: list[tuple[str, str]] = []   # the gaps a proof declared in THIS call --
                                   # (code, what is missing): the next closing says them
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
        self._segmap: list[dict] = []  # the output's OFFER MAP -- one entry per heading
                                       # (ordinal, frame, stack, tools, constraint lines):
                                       # what a `-s` call routes against once the
                                       # segment's frame is resolved or popped
        self._remap = False            # only a MUTATING advance replaces the persisted
                                       # map -- a re-show (resume, peek) keeps the
                                       # standing addresses: they live with their output
        self._route_note = ""          # `[n] FRAME` -- said once, on the entry heading

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
        verb resolved the slot. Its ROOT OF DOCUMENTS enters the same way: the one the run
        was given at `-new`, read at the slot; a call that names another refuses
        `documents-fixed`, nothing played."""
        root = persistence.documents_of(slot)
        asked = os.environ.get(context.DOCUMENTS, "").strip()
        if asked and Path(asked) != Path(root or "."):
            raise Refusal("documents-fixed",
                          f"`{context.DOCUMENTS}={asked}` -- run {persistence.run_id_of(slot)} keeps the "
                          f"root of documents it opened with ({root or 'none'}): a run's composition "
                          "never moves; another root opens another run, with `-new`")
        self._session = slot
        self._log = self._log or persistence.trace_of(slot)
        instance.play_off(self._launch.meta, persistence.off_of(slot))
        instance.play_documents(self._launch.meta, root)
        # the run named in THIS process's environment: every script it launches inherits
        # it, a gesture played in-process reads it -- one site, every path
        os.environ[context.VARIABLE] = persistence.run_id_of(slot)
        return slot

    def switch(self, name: str, off: bool, by_principal: bool = False) -> str:
        """The SOFT switch of one package, for THIS run: `off` takes it out of the play
        -- nothing of it is served or played, its dependents leave with it -- and `on`
        brings it back; the hard switch of SETTINGS says the same thing durably, and
        both filter at ONE point. The run does not move: a switch is the operator's
        word, never a step, so the answer is the block that STANDS.
        -> the fact, then that block, through the seam (`delivered`): the fact is the
        switch's answer, the block what it serves."""
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
        return self.delivered(block, by_principal, lead=fact, act="switch", view=True)

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

    def renewal(self) -> dict | None:
        """-> the renewal mark the resolved slot holds -- an upgrade renewed the run, its
        next keyed call reopens it -- or None for a run, or no slot. A read: nothing written."""
        slot = self._slot()
        return persistence.renewed(slot) if slot is not None else None

    def principal(self) -> bool:
        """-> whether the resolved run is conducted by its principal: its launcher makes it
        advance, so no ending that moves it on carries a command. A read: nothing written."""
        slot = self._slot()
        return slot is not None and persistence.mode_of(slot) == persistence.PRINCIPAL

    def _cap(self) -> int:
        """-> the cap the resolved run's outputs are cut under: the instance's setting; in a run
        its principal conducts, the cap the launcher names on its marked call (`PP_PROMPT_CAP`),
        else the floor (`settings.served_cap`)."""
        principal = self.principal()
        return settings.served_cap(self._settings.harness_cap, principal,
                                   context.prompt_cap() if principal else None)

    def _receiving(self) -> str:
        """-> the CHANNEL an output of this run reaches the agent by: the prompt of a launch when
        the run's principal conducts it, the result of the agent's own call otherwise -- the one
        site where the mode of conduction is read for the foot: it chooses the channel, and
        `closing` deduces the foot from the channel and what the stack awaits. A view, a manual
        and an inline answer reach the agent by the tool in both modes (`language.TOOL`)."""
        return language.PROMPT if self.principal() else language.TOOL

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
        and it answered, `instance` for the operator's own space, `machine` for `.sys/`,
        `repository` for the workspace around the instance -- and empty where there is no
        document to attribute."""
        if path is None:
            return ""
        if str(path) in self._served_from:
            return self._served_from[str(path)]   # a material's tree: named as the row named it
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
        line = f"{signal} · {level} · {fact}" + (f" -- {way}" if way else "")
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
        cap = self._cap()
        opening = f"{lead}\n" if lead else ""
        if self._dry or slot is None or not slot.exists() or cap <= 0:
            return opening + rendering.joined(rendering.under(head, matter), tail)
        if lead and len(opening) > cap // 2:
            matter, opening = "\n\n".join(one for one in (lead, matter) if one), ""
        if persistence.pending_of(slot).get("matter"):
            # a reading of another output still waits at the run: this text (a view a gesture
            # mounted while the chunk waited) takes no rest slot -- clipped under the cap, the
            # clip said by its fact, nothing kept, the waiting reading untouched
            return opening + self._clip(head, matter, tail, cap - len(opening))
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

    # what each act tells the agent when its output is held: one line, the act first, the
    # same ending
    HELD_SAID = {      # the verdict alone: the standing orders say where the output comes
        "value": "value judged",
        "mount": "mounted",
        "door": "opened",
        "closed": "closed",
        "compacted": "re-served",
        "reopened": "reopened",
    }
    # the acts that ANSWER the agent's call in a run its principal conducts: they move nothing
    # the principal relays -- a view (`-peek`, a denied offer, a switch) and the manual a bare
    # script mounts come back in the tool return, cut under the host's cap
    ANSWERED = frozenset({"view", "denied", "switch", "manual"})

    def delivered(self, block: Block | None, by_principal: bool = False, lead: str = "",
                  act: str = "value", view: bool = False) -> str:
        """The ONE seam a block leaves the engine by on a keyed call -> the text the call
        prints. What the engine renders of a block is SERVED: it goes to whoever conducts
        the run. In a run the LLM conducts, or on the principal's own (marked) call, that is
        this call's output -- `rendered` (`shown` for a VIEW, which keeps nothing), as ever.
        On the agent's call in a run its principal conducts, the block is HELD at the run
        (`hold`, its `act` kept) and the call prints only what the act ANSWERS (`lead`: a
        script's own text, a switch's fact) and one neutral line telling the agent to end
        its message; the principal's bare call serves the block (`release`). `by_principal`
        is the mark the console read on the call -- the facade reads no environment.

        A VIEW and the MANUAL of a bare script ANSWER the agent's call in both modes: they move
        nothing the principal relays, so nothing waits for the principal -- the text comes back
        in the tool return, cut under the HOST's cap (a tool result, not the harness's stdin),
        the rest served by the agent's bare keyed call (`viewed`, `next_view`)."""
        if block is None:
            return lead
        if self.principal() and not by_principal:
            if view or act in self.ANSWERED:
                shown = self.viewed(block)
                return f"{lead}\n\n{shown}" if lead else shown
            self._dry = False
            if self.hybrid() and block.next_call:
                # `conduction: hybrid`: the closing asks the agent a VALUE -- the block comes back
                # in the tool result, as a view does, and nothing waits for the principal
                shown = self.inline(block, act)
                return f"{lead}\n\n{shown}" if lead else shown
            self.hold(block, act)
            said = f"pp: {self.HELD_SAID.get(act, self.HELD_SAID['value'])}"
            return f"{lead}\n{said}" if lead else said
        if view:
            shown = self.shown(block)
            return f"{lead}\n\n{shown}" if lead else shown
        return self.rendered(block, lead)

    def denied(self, block: Block, name: str, by_principal: bool = False) -> str:
        """The out-of-turn catch -> the text the call prints: `name` is offered by no segment of
        the output that stands, so the pending block answers, its DEVIATION naming the ask as not
        played -- dry, no repair counted (a repair is for a WATCHED answer that missed), the run
        untouched. The trace says `offer-absent` with the name, once, at the site of the act; the
        block leaves by the seam of every view (`delivered`, `act` denied)."""
        import dataclasses
        self._dry = False              # the block was peeked dry: the act is traced all the same
        self._trace("offer-absent", name=name)
        answered = dataclasses.replace(
            block, deviation=(f"`{name}` is not offered at this step -- "
                              "the pending step stands below; the work was NOT done."))
        return self.delivered(answered, by_principal, act="denied", view=True)

    def hybrid(self) -> bool:
        """-> whether the instance plays `conduction: hybrid`: in a run its principal conducts, an
        output whose closing asks the agent a value comes back in its tool result. A read of the
        settings, nothing written; the LLM's mode never asks."""
        return self._settings.conduction == settings.CONDUCTIONS[1]

    def inline(self, block: Block, act: str = "value") -> str:
        """-> the block's TEXT answering the agent's call under `conduction: hybrid`: the block is
        SERVED -- its readings proven as a rendered output's are, its weight on the trace as
        `inline` with the act that rendered it --, cut under the HOST's cap (a tool result, never
        the harness's stdin), the rest kept at the slot (`viewing`) for the agent's bare keyed
        call alone, chunk by chunk (`next_view`), the staged readings proven when the last leaves.
        A prior view's rest is forgotten, as a hold forgets it."""
        from .. import rendering
        matter, tail = rendering.parts(block)
        head = rendering.head(block)
        slot = self._slot()
        staged = sorted(set(self._staged))
        self._staged = []
        whole = rendering.joined(rendering.under(head, matter), tail)
        self._trace("inline", act=act, weight={"chars": len(whole), "tokens": metrics.tokens(whole)})
        cap = settings.served_cap(self._settings.harness_cap, False)
        if slot is None or not slot.exists() or cap <= 0:
            return whole
        text, rest = self._chunked(head, matter, tail, cap, language.TOOL)
        if rest:
            self._proven.difference_update(staged)
            persistence.remove_proven(slot, staged)
            persistence.set_viewing(slot, {"matter": rest, "tail": tail, "head": head, "staged": staged})
        else:
            if persistence.viewing_of(slot):
                persistence.set_viewing(slot, {})
            self._proven.update(staged)
            persistence.add_proven(slot, staged)
        return text

    def held(self) -> bool:
        """-> whether an output waits for the principal's call: the agent's value was judged,
        its answer stands at the slot, nothing has left the tool."""
        slot = self._slot()
        return bool(slot and persistence.held_of(slot))

    def viewed(self, block: Block) -> str:
        """-> the block's TEXT for a view or a manual ANSWERING the agent's call in a run its
        principal conducts: cut under the HOST's cap -- the instance's setting, never the
        principal's floor: the text lands in a tool result --, the rest kept at the slot
        (`viewing`) for the agent's bare keyed call alone (`next_view`); a view that fits
        leaves nothing. Any other act of either caller forgets the rest."""
        from .. import rendering
        matter, tail = rendering.parts(block)
        head = rendering.head(block)
        slot = self._slot()
        cap = settings.served_cap(self._settings.harness_cap, False)
        if slot is None or not slot.exists() or cap <= 0:
            return rendering.joined(rendering.under(head, matter), tail)
        text, rest = self._chunked(head, matter, tail, cap, language.TOOL)
        if rest:
            persistence.set_viewing(slot, {"matter": rest, "tail": tail, "head": head})
        elif persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})
        return text

    def viewing(self) -> bool:
        """-> whether the rest of a view waits for the agent's bare keyed call."""
        slot = self._slot()
        return bool(slot and persistence.viewing_of(slot).get("matter"))

    def next_view(self) -> str:
        """-> the next chunk of a cut view, the rest consumed as it goes: the last one carries
        the block's own closing back; nothing is traced, a view writes no state of the run."""
        slot = self._slot()
        waiting = persistence.viewing_of(slot) if slot else {}
        matter, tail, head = waiting.get("matter", ""), waiting.get("tail", ""), waiting.get("head", "")
        staged = list(waiting.get("staged", []))   # an INLINE output's readings: proven at its last chunk
        cap = settings.served_cap(self._settings.harness_cap, False)
        text, rest = self._chunked(head, matter, tail, cap, language.TOOL)
        persistence.set_viewing(slot, {"matter": rest, "tail": tail, "head": head, "staged": staged}
                                if rest else {})
        if not rest and staged:
            self._proven.update(staged)
            persistence.add_proven(slot, staged)
        return text

    def hold(self, block: Block, act: str = "value") -> None:
        """HOLDS the output the agent's call rendered, in a run its principal conducts: the
        act has played exactly as in the LLM's mode -- the value judged, the mount written,
        the door pushed --, but its text leaves by the principal's call alone (`release`),
        never by the tool return. The pieces kept are a cut's -- head, matter, tail, the
        readings staged --, so the release cuts under the cap as if the output left then; the
        staged readings are demoted from the run's proofs until their last chunk leaves, as
        `rendered` does. `act` names what was held, at the slot and on the trace. A second
        hold in the SAME call -- a script's second `::mount` -- joins the first: its matter
        follows, the newest head and closing stand."""
        from .. import rendering
        matter, tail = rendering.parts(block)
        head = rendering.head(block)
        slot = self._slot()
        staged = sorted(set(self._staged))
        self._staged = []
        if slot is None or not slot.exists():
            return
        if persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})   # a hold forgets the rest of a view
        # a hold already standing -- this process's earlier `::mount`, or an output held before a
        # gesture of the agent mounted over it -- takes this one in: its matter follows
        prior = persistence.held_of(slot)
        if prior:
            matter = "\n\n".join(one for one in (prior.get("matter", ""), matter) if one)
            staged = sorted(set(prior.get("staged", [])) | set(staged))
        self._proven.difference_update(staged)
        persistence.remove_proven(slot, staged)
        whole = rendering.joined(rendering.under(head, matter), tail)
        persistence.set_held(slot, {"matter": matter, "tail": tail, "head": head, "staged": staged,
                                    "act": act,
                                    "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                    "chars": len(whole)})
        self._trace("held", act=act, weight={"chars": len(whole), "tokens": metrics.tokens(whole)})

    def release(self) -> str:
        """-> the held output, as the principal's bare call serves it: the first chunk under
        the cap, the rest waiting at the run like any cut block's (the principal's next
        bare calls serve it); the slot forgets the hold. Traced `advance` with `held: true`."""
        slot = self._slot()
        held = persistence.held_of(slot) if slot else {}
        if not held:
            return ""
        persistence.set_held(slot, {})
        if persistence.viewing_of(slot):
            persistence.set_viewing(slot, {})   # the principal's call forgets the rest of a view
        self._trace("advance", held=True, prompt=False)
        matter, tail, head = held.get("matter", ""), held.get("tail", ""), held.get("head", "")
        staged = list(held.get("staged", []))
        cap = self._cap()
        if cap <= 0:
            self._proven.update(staged)
            persistence.add_proven(slot, staged)
            from .. import rendering
            return rendering.joined(rendering.under(head, matter), tail)
        text, rest = self._chunked(head, matter, tail, cap)
        if rest:
            persistence.set_pending(slot, {"matter": rest, "tail": tail, "head": head,
                                           "staged": staged})
            self._trace("cut", left=len(rest))
            return text
        persistence.set_pending(slot, {})
        self._proven.update(staged)
        persistence.add_proven(slot, staged)
        return text

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
        if persistence.pending_of(slot).get("matter"):
            # a reading still waits at the run: the gesture's text takes no rest slot -- clipped,
            # the clip said, the waiting reading untouched
            return self._clip(head, text, "", cap)
        chunk, rest = self._chunked(head, text, "", cap)
        persistence.set_pending(slot, {"matter": rest, "tail": "", "head": head, "staged": []})
        self._trace("cut", left=len(rest))
        return chunk

    def _chunked(self, head: str, matter: str, tail: str, cap: int,
                 channel: str = "") -> tuple[str, str]:
        """-> (the output's text, what is left). The whole block when it fits under the cap
        with its tail; else an INTERMEDIATE chunk: the head, the matter that fits, and the
        foot of a reading that continues (`closing`, `language.READING_ON`): by the tool
        `CONTINUE` and the bare call that alone serves the rest, at the prompt `MORE` and no
        call, the fact -- what remains, how many chunks -- on both; it carries no instruction
        and no law: the block's own tail (its INSTRUCTION, its true closing) rides the LAST
        chunk only, so nothing invites a production before the reading is whole. `channel`
        names where the chunk goes; empty, the output's own (`_receiving`)."""
        from .. import rendering
        channel = channel or self._receiving()
        room = cap - len(tail) - len(head) - 2
        chunk, rest = rendering.cut(matter, room)
        if not rest:
            return rendering.joined(rendering.under(head, chunk), tail), ""

        def waiting_of(left: int) -> str:
            more = max(1, -(-left // max(room, 1)))
            label, call, fact = self.closing(language.READING_ON, channel, left=left, more=more)
            return rendering.foot(label, call, (fact,))

        waiting = waiting_of(len(rest))
        for _ in range(2):          # the closing's own length varies by a few digits
            if len(head) + 2 + len(chunk) + 1 + len(waiting) <= cap:
                break
            chunk, rest = rendering.cut(matter, cap - len(waiting) - len(head) - 2)
            waiting = waiting_of(len(rest))
        return rendering.joined(rendering.under(head, chunk), waiting), rest

    def _clip(self, head: str, matter: str, tail: str, cap: int) -> str:
        """-> a text CLIPPED under the cap, nothing kept: the head, the matter that fits, the tail
        and ONE fact at the foot saying how much was not shown -- the same text whatever the mode.
        What a view that keeps nothing (`shown`), and a text that cannot take the run's rest slot
        because a reading already waits there, come back as."""
        from .. import rendering
        fact = "a view cut under the cap: {n} characters not shown"
        room = cap - len(tail) - len(head) - len(fact) - 16
        chunk, rest = rendering.cut(matter, room)
        if not rest:
            return rendering.joined(rendering.under(head, matter), tail)
        said = fact.format(n=len(rest))
        foot = rendering.foot("", "", (said,))
        return rendering.joined(rendering.under(head, chunk), (tail + "\n" + foot.strip("\n")) if tail else foot)


    def shown(self, block: Block) -> str:
        """-> the block's TEXT for a VIEW that advances nothing -- the keyless look, `-peek`,
        an ask denied out of turn. Cut under the host's cap at the very seam every output
        uses; what is left is NOT kept, because a view writes no state: a fact at the foot
        says how much was not shown (`_clip`).

        documentary: one seam for every text the engine hands over (`rendering.cut`); an
        output and a view differ only in whether the rest waits at the run."""
        from .. import rendering
        matter, tail = rendering.parts(block)
        head = rendering.head(block)
        cap = self._cap()
        if cap <= 0:
            return rendering.joined(rendering.under(head, matter), tail)
        return self._clip(head, matter, tail, cap)

    def pending(self) -> bool:
        """-> whether a cut block still has matter waiting: the next bare call serves it
        BEFORE the flow advances."""
        slot = self._slot()
        return bool(slot and persistence.pending_of(slot).get("matter"))

    def drop_pending(self) -> str:
        """-> the closing of a cut block, the rest of its reading DROPPED on the caller's word:
        the rest is never served and the readings it staged stay unproven -- they were not
        delivered whole --; the trace says `chunk-dropped` with what was left, and the flow
        resumes where the block stood."""
        from .. import rendering
        slot = self._slot()
        held = persistence.pending_of(slot) if slot else {}
        persistence.set_pending(slot, {})
        self._trace("chunk-dropped", left=len(held.get("matter", "")))
        return rendering.joined(held.get("head", ""), held.get("tail", ""))

    def next_chunk(self) -> str:
        """-> the next chunk of a cut block, the state consumed as it goes: the last one
        carries the block's own closing back, so the flow resumes where it stood."""
        slot = self._slot()
        held = persistence.pending_of(slot) if slot else {}
        matter, tail, head = held.get("matter", ""), held.get("tail", ""), held.get("head", "")
        staged = list(held.get("staged", []))
        cap = self._cap()
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
