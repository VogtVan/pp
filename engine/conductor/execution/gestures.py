"""execution.gestures -- the public verbs of the run: play, resume, forward, submit, drain. A mixin of the facade: no state of its own."""
from __future__ import annotations

import json
from pathlib import Path
from ..packaging import events
from .. import reading
from ..core import deviation, language, navigation
from ..state import metrics, persistence
from .revive import revive
from ..core.errors import Refusal
from ..core.model import Block, Frame, Instruction


class Gesturing:
    """The public verbs of the run: play, resume, forward, submit, drain -- a mixin of the facade."""

    def play(self, name: str, route: dict | None = None,
             arguments: tuple = (), keyword: str = "CALL") -> Block | None:
        """Agent-opened proc: injects `CALL <name>.md` at the pending step of the
        CURRENT frame and advances -- the proc plays CONDUCTED, stacked over the turn.
        The caller checks the scope first (`peek`/`route`); this method trusts it.
        Routed (offered by a PAST segment of the current output), the door still
        stacks HERE -- the stack never runs backward -- but inherits the owning
        segment's snapshotted laws, and its entry heading says the route. `keyword`
        `OPEN` opens the proc as a SPACE (`open`)."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        stack = self._rebind(restored)
        frame = navigation.current(stack)
        if arguments:
            # a door opens on its own documents and reads nothing from the call: what
            # rode the call is said and traced, never refused (operator word 2026-10-16)
            self._trace("door-argument", name=name, arguments=list(arguments))
        injected = Instruction(keyword=keyword, argument=f"{name}.md", injected=True, site="door")
        if route is not None:
            injected.routed = tuple(route.get("constraints", ()))
            self._route_note = f"[{route.get('ordinal')}] {route.get('frame')}"
            self._trace("routed", name=name, segment=route.get("ordinal"),
                        frame=route.get("frame"))
        if keyword == language.OPEN:
            self._trace("opened", name=name)    # the space the agent opens: said once, by its name
        frame.procedure.instructions.insert(navigation.pointer(frame), injected)
        return self._advance(stack)

    def open(self, name: str, route: dict | None = None) -> Block | None:
        """`-open <name>`: the agent opens a SPACE -- the proc named enters at the pending step
        as an `OPEN` written there would, and becomes the root of the passages until `-close`.
        A document that cannot be a space refuses `open-unplayable`; the offer is the caller's
        to check, as for a door."""
        document = reading.read(self._resolve(f"{name}.md"))
        unplayable = reading.unopenable(document.front)
        if unplayable:
            raise Refusal("open-unplayable", f"`{name}` cannot be opened as a space: {unplayable}")
        return self.play(name, route, keyword=language.OPEN)

    def close(self) -> Block | None:
        """`-close`: the deepest SPACE leaves, with every frame stacked over it -- a step pending
        there is dropped, what was said stays said; what the space produced stays DUE at the next
        written PROVE below it, its own laws of production with it. Its caller takes up where it
        stood -- the step after its `OPEN`, or the step pending when `-open` opened it -- in the
        same passage, and the advance renders the next block. No space open: `space-none`."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        stack = self._rebind(restored)
        spaces = [at for at, one in enumerate(stack.frames) if navigation.space(one)]
        if not spaces:
            raise Refusal("space-none", "no space is open -- `-close` leaves the space an `OPEN` "
                                        "or `-open` opened")
        while len(stack.frames) > spaces[-1]:
            frame = navigation.current(stack)
            if self._indebted(stack, frame):
                self._owe(frame)         # its laws stay due beside its productions
            holder = self.holder_of(stack, frame)
            navigation.pop(stack)
            self._release(holder)
            if len(stack.frames) == spaces[-1]:
                navigation.give(frame.caller, navigation.upstream(frame))
                self._trace("closed", document=frame.document.name)
        self._save(stack)
        return self._advance(stack)

    def resume(self, path: Path) -> Block | None:
        """-> where the run stands; starts one if none is under way. NEVER mutates a
        pending instruction -- a status check, safe to call as many times as asked."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap = []          # a re-show: the standing addresses survive it
        slot = self._slot()
        if slot is not None and persistence.renewed(slot) is not None:
            return self.reopen(path)       # a run an upgrade renewed: reopened under its key
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return self.start(path)
        stack = self._rebind(restored)
        if persistence.compacted_of(slot):
            return self._reserved(stack)
        self._opening(stack)       # a parked run taken up bare: the next passage opens
        return self._advance(stack)

    def forward(self, given: str = "", by_principal: bool = False) -> Block | None:
        """The ONE advance call (`./pp <key> [value|-]`): binds `given` to a
        pending YIELD awaiting an answer, or carries the run on -- a reading's next
        chunk, the resume of a parked run -- when nothing awaits one. Advancing is the
        KEYED call: without a run it refuses, it never opens one. `by_principal` says the
        call carries the principal's mark -- the console read it; the facade reads no
        environment --: in a run its principal conducts, such a call is traced `advance`,
        and the agent's value call is the same judgment with its output HELD (`hold`)."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        stack = self._rebind(restored)
        if persistence.compacted_of(slot):
            # a declared compaction whose re-serve never reached the agent: the duty
            # comes with THIS output rather than expiring with the call that armed it
            block = self._reserved(stack)
        else:
            block = self.submit(given)
        if by_principal and self.principal():
            # the principal's call, once played: `-stats` counts what the principal served
            self._trace("advance", held=False, prompt=bool(given.strip()))
        return block

    def submit(self, answer: str) -> Block | None:
        """Binds the answer to the pending instruction, then carries on."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        stack = self._rebind(restored)
        mark = persistence.stopped_of(slot)
        if mark:
            # the run is STOPPED at the repair bound: text handed here is the principal's word,
            # a bare call its "go on" -- either takes the step up
            return self._taken_up(stack, mark, answer)
        frame = navigation.current(stack)
        if navigation.exhausted(frame):
            # the run is PARKED: the root of its passage is exhausted and waits for the
            # principal's message -- text handed here is that message, traced whatever the
            # tuning; the root rewinds and the passage opens on it (a bare call opens it too)
            if answer.strip():
                self._trace("prompt", text=answer)
            self._opening(stack)
            return self._advance(stack)
        instruction = navigation.peek(frame)
        if not (language.yields(instruction.keyword) and instruction.asked):
            # nothing awaits an answer: the batch resolved its response yields at render.
            # Text handed anyway is a stray production (bounced softly -- no repair): the
            # run waits for a production here, never for a message
            if answer.strip():
                self._trace("stray", instruction=str(instruction), asked=False)
                return self._advance(stack, "your production belongs in your words; the tool takes "
                                            "nothing back. Nothing was recorded.")
            return self._advance(stack)
        # the agent's side weighed at the source: what its production cost, in characters
        # and in estimated tokens -- the reader sums it apart from the blocks; the channel
        # says where the production goes, so the reader tells a value from a stray text
        channel = self._channel(stack, frame, instruction)
        self._trace("answer", instruction=str(instruction), given=answer, channel=channel,
                    weight={"chars": len(answer), "tokens": metrics.tokens(answer)})
        if (answer.strip() and instruction.keyword in language.FREE
                and channel == language.WORDS):
            # the soft catch: an over-eager hand-in is not a lie -- the block
            # answers, nothing is recorded, no repair is counted; the trace says it
            self._trace("stray", instruction=str(instruction), channel=channel)
            return self._advance(stack, "your production is not the tool's -- a response "
                                        "is said in your words, never handed. Nothing was recorded.")
        if not answer and instruction.keyword not in language.FREE:   # a FREE step's own text never
            return self._repair(stack, frame, instruction, deviation.empty_answer(instruction))
        mini = bool(instruction.refit)      # this answer is the mini-proof of a repair in place
        missed = self._check(stack, frame, instruction, answer)
        if missed:
            if self._inplace:
                # the cheap branch: the document STANDS -- the same checkpoint re-presents
                # with the fixes to play, nothing reopens; a fix costs nothing against the
                # bound, a mini-proof that misses its codes counts one
                instruction.refit, self._inplace = self._inplace, ()
                if mini:
                    anchor = instruction
                    if instruction.injected:
                        stable = [one for one in frame.procedure.instructions
                                  if not one.injected]
                        anchor = stable[-1] if stable else instruction
                    self._bound(stack, frame, anchor, missed)
                self._trace("repair-in-place", instruction=str(instruction),
                            codes=list(instruction.refit), counted=mini)
                self._save(stack)
                return self._advance(stack, missed)
            return self._repair(stack, frame, instruction, missed)
        if instruction.keyword == "PROVE":
            self._debt_paid(stack, frame)   # the checkpoint proven: this frame and its callees are paid
        elif instruction.keyword in language.YIELDING and not instruction.injected:
            self._produced(stack, frame)    # a production of the agent's: owed to the next written PROVE
        if (instruction.keyword in language.FREE and answer.strip()
                and self._form_of(stack, frame, instruction) in ("json", language.LIST)):
            # a validated json production IS data: parsed, it feeds a PICK's
            # options or a callee's seed -- the pipeline is the options source
            navigation.give(instruction, json.loads(answer))
        else:
            navigation.give(instruction, answer)
        if instruction.keyword == "FIELD":
            # the described door's field, accepted on its form: the frame holds what
            # remains due and opens on its head -- or leaves at once, nothing due
            self._open_field(stack, frame, json.loads(answer))
        sink = str(frame.document.front.get("sink", "")).strip()
        if sink and instruction.keyword in language.FREE and answer.strip():
            # the document's declared SINK: its production goes to a skill on stdin,
            # what the skill says to the bus is harvested, the rest is SAID back
            import time
            begun = time.perf_counter()
            said = events.sink(self.member.meta, sink, answer)
            self._trace("sink", skill=sink, said=len(said),   # named already -- the
                        ms=round((time.perf_counter() - begun) * 1000, 1))  # duration joins
            if said:
                text = "\n".join(said)
                self.note(f"sink {sink}", text, "served", "sink", with_=str(sink))
                self._payloads.append((f"sink {sink}", text))
        return self._advance(stack)

    def drain(self) -> tuple[tuple[str, str], ...]:
        """-> the documents served since the last block, and forgets them: they are delivered once."""
        served, self._payloads = tuple(self._payloads), []
        return served

    def _settled(self, frame: Frame, instruction: Instruction) -> str | None:
        """-> what the instruction already stands for, or None when it has work to do."""
        settler = getattr(self, f"_settled_{instruction.keyword.lower()}", None)
        return settler(frame, instruction) if settler else None
