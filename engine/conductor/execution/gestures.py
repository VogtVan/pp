"""execution.gestures -- the public verbs of the run: play, resume, forward, submit, drain. A mixin of the facade: no state of its own."""
from __future__ import annotations

import json
from pathlib import Path
from ..packaging import events
from .. import reading
from ..core import language, messages, navigation
from ..state import metrics, persistence
from .advancing import advances
from .revive import revive
from ..core.errors import Refusal
from ..core.model import Block, Frame, Instruction


class Gesturing:
    """The public verbs of the run: play, resume, forward, submit, drain -- a mixin of the facade."""

    @advances
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
        self._emitted, self._seg_scope = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
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
        else:
            # a door opened from a step said on `terminal` stands for its production: the step's
            # print is due no more -- the door's exit gives the step what the door produced; the
            # trace says the debt lifted by its own event, never as a production missed
            due = persistence.prints_of(slot)
            kept = [one for one in due if one.get("stack") != navigation.render(stack)]
            if len(kept) != len(due):
                persistence.set_prints(slot, kept)
                for one in due:
                    if one not in kept:
                        self._trace("print-by-door", instruction=one["instruction"],
                                    document=one["document"], door=name)
        frame.procedure.instructions.insert(navigation.pointer(frame), injected)
        return self._advance(stack)

    def open(self, name: str, route: dict | None = None) -> Block | None:
        """`-open <name>`: the agent opens a SPACE -- the proc named enters at the pending step
        as an `OPEN` written there would, and becomes the root of the passages until `-close`.
        A document that cannot be a space refuses `open-unplayable`; a space the stack holds
        open already refuses `space-open`, judged on the run's stack alone; the offer is the
        caller's to check, as for a door."""
        document = reading.read(self._resolve(f"{name}.md"))
        unplayable = reading.unopenable(document.front)
        if unplayable:
            raise Refusal("open-unplayable", messages.refusal_open_unplayable(name, unplayable))
        opened = self.spaces_open()
        if name in opened:
            raise Refusal("space-open", messages.refusal_space_open(name, ' ▸ '.join(opened)))
        return self.play(name, route, keyword=language.OPEN)

    def spaces_open(self) -> list[str]:
        """-> the names of the SPACES the run's stack holds open, from the outermost to the deepest
        (the last one the root); [] without a run. Reads the slot, moves nothing."""
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return []
        stack = self._rebind(restored)
        return [one.document.name for one in stack.frames if navigation.space(one)]

    @advances
    def close(self) -> Block | None:
        """`-close`: the deepest SPACE leaves, with every frame stacked over it -- a step pending
        there is dropped, what was said stays said; what the space produced stays DUE at the next
        written PROVE below it, its own laws of production with it. Its caller takes up where it
        stood -- the step after its `OPEN`, or the step pending when `-open` opened it -- in the
        same passage, and the advance renders the next block. No space open: `space-none`."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
        stack = self._rebind(restored)
        spaces = [at for at, one in enumerate(stack.frames) if navigation.space(one)]
        if not spaces:
            raise Refusal("space-none", messages.refusal_space_none())
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

    @advances
    def resume(self, path: Path) -> Block | None:
        """-> where the run stands; starts one if none is under way. NEVER mutates a
        pending instruction -- a status check, safe to call as many times as asked."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = set(), None
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

    @advances
    def forward(self, given: str = "", principal: bool = False) -> Block | None:
        """The ONE advance call (`./pp <key> [value|-]`): binds `given` to a
        pending YIELD awaiting an answer, or carries the run on -- a reading's next
        chunk, the resume of a parked run -- when nothing awaits one. Advancing is the
        KEYED call: without a run it refuses, it never opens one. `principal` says the
        call is the principal's -- the console read it (`context.agents`); the facade reads no
        environment --: such a call is traced `advance`, and the agent's value call is the same
        judgment with its output HELD (`hold`)."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
        stack = self._rebind(restored)
        if persistence.compacted_of(slot):
            # a declared compaction whose re-serve never reached the agent: the duty
            # comes with THIS output rather than expiring with the call that armed it
            block = self._reserved(stack)
        else:
            block = self.submit(given)
        if principal:
            # the principal's call, once played: `-stats` counts what the principal served
            self._trace("advance", held=False, prompt=bool(given.strip()))
        return block

    @advances
    def opens(self, given: str = "") -> str:
        """The principal's MESSAGE under an output it holds open (`PP_HOLD_OUTPUT`, read by the
        console): the call opens the exchange and renders no block -- the mounts the principal
        plays next pose its context, and its bare call plays the exchange and renders it once
        (`release`). A PARKED run: the message is traced `prompt` and the root of the passage
        rewinds (`_opening`); the stack advances no further. A run STOPPED at the repair bound:
        the word waits with the hold and takes the step up at the release. A run that STANDS on a
        step: nothing moves, an output waits open for the mounts. An exchange an earlier call
        opened and never served: nothing more is opened. An output that closed already waits at the
        run: nothing is opened -- the mounts join that output and the bare call serves it.
        -> what the call prints: the output's heading, then the line of its act."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = set(), None
        self._segmap = []                 # nothing is rendered: the standing addresses stay
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
        stack = self._rebind(restored)
        waiting = persistence.held_of(slot)
        if waiting:
            if waiting.get("open"):
                self._trace("held", act="value", open=True)
            self._say_open(stack, "standing" if waiting.get("open") else "waiting")
        elif persistence.stopped_of(slot):
            self._held_open(stack, "value", word=given)
        elif navigation.exhausted(navigation.current(stack)):
            if given.strip():
                self._prints_lifted(slot)
                self._trace("prompt", text=given)
            self._opening(stack)
            self._held_open(stack, "value")
        else:
            self._held_open(stack, "value", advance=False)
        return self._said_open

    @advances
    def submit(self, answer: str) -> Block | None:
        """Binds the answer to the pending instruction, then carries on."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
        stack = self._rebind(restored)
        mark = persistence.stopped_of(slot)
        if mark:
            # the run is STOPPED at the repair bound: text handed here is the principal's word,
            # a bare call its "go on" -- either takes the step up
            return self._taken_up(stack, mark, answer)
        frame = navigation.current(stack)
        if navigation.exhausted(frame) and answer.strip():
            self._prints_lifted(slot)
        prints = persistence.prints_of(slot)
        if prints:
            # a print misses: no value is judged and no bare call moves the run while a production
            # said on `terminal` is due -- the block that stands answers, the documents due named;
            # no repair is counted, the trace says it
            due = [one["document"] for one in prints]
            self._trace("stray", instruction=prints[0]["instruction"], due=due, handed=bool(answer.strip()))
            return self._caught_back(stack, messages.prints_due(due))
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
                return self._advance(stack, messages.stray_production())
            return self._advance(stack)
        # the agent's side weighed at the source: what its production cost, in characters
        # and in estimated tokens -- the reader sums it apart from the blocks; the channel
        # says where the production goes, so the reader tells a value from a stray text
        channel = self._channel(stack, frame, instruction)
        self._trace("answer", instruction=str(instruction), given=answer, channel=channel,
                    weight={"chars": len(answer), "tokens": metrics.tokens(answer)})
        if (answer.strip() and instruction.keyword in language.FREE
                and channel == language.TERMINAL):
            # the soft catch: the step that pends is the LAST message of its output (a run its
            # principal conducts) -- a text handed for it is no value: the block answers, nothing
            # is recorded, no repair is counted; the trace says it
            self._trace("stray", instruction=str(instruction), channel=channel)
            return self._advance(stack, messages.soft_catch(frame.document.name))
        if not answer and instruction.keyword not in language.FREE:   # a FREE step's own text never
            return self._repair(stack, frame, instruction, messages.empty_answer(instruction))
        mini = bool(instruction.refit)      # this answer is the mini-proof of a repair in place
        missed = self._check(stack, frame, instruction, answer)
        if missed:
            if self._reask:
                # a proof that breaks its form or its coverage: the same checkpoint asks it
                # again, the document STANDS -- the try counts against the bound
                self._reask = False
                anchor = instruction
                if instruction.injected:
                    stable = [one for one in frame.procedure.instructions if not one.injected]
                    anchor = stable[-1] if stable else instruction
                self._bound(stack, frame, anchor, missed)
                self._trace("repair-in-place", instruction=str(instruction),
                            codes=list(instruction.refit), counted=True, reask=True)
                self._save(stack)
                self._asked_again = True
                try:
                    return self._replayed(stack, missed)
                finally:
                    self._asked_again = False
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
                return self._replayed(stack, missed)
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

    def _prints_lifted(self, slot) -> None:
        """The principal's message is never handed back: on a parked run it opens the passage, and
        the prints the passage over left due are lifted without a capture -- `print-waived`, one
        per entry."""
        for one in persistence.prints_of(slot):
            self._trace("print-waived", instruction=one["instruction"], document=one["document"],
                        refused=one.get("refused", 0))
        persistence.set_prints(slot, [])

    @advances
    def printed(self, document: str, text: str) -> tuple[str, Block | None]:
        """The PRINT call (`./pp <key> -print <DOCUMENT> -`, the production piped) -> (what the
        call answers, its block): a line of `messages.PRINTED` by its name and no block -- `waived` when
        the bound lifted the print without a capture; `moved` and the
        block the run moved to; `caught` and the block that stands with its deviation (`caught`
        says so to the console). A production said to the principal is HANDED here: it answers the first print
        due of the document named, the trace keeps it as it was handed (`answer`, channel
        `terminal`), and its entry leaves the run's state. A print is judged on the FORM of its
        step as a value is: empty or misformed, it is refused and stays due, and the bound of the
        repairs lifts its debt without a capture (`print-waived`). What the call answers is read on what is
        left: other prints due, or a value the output still awaits -- `more`; the last message
        alone -- `last`; an output that had closed on its prints -- the run moves on, and the
        next block leaves by the seam of a value."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
        stack = self._rebind(restored)
        due = persistence.prints_of(slot)
        at = next((n for n, one in enumerate(due) if one["document"] == document), None)
        if at is None:
            # no print: nothing of that document is due -- the block that stands answers
            self._trace("stray", document=document, due=[one["document"] for one in due])
            return "caught", self._caught_back(stack, messages.print_stray(document))
        entry = due[at]
        missed = self._formed(entry["form"], text) if text.strip() else messages.empty_print(document)
        if missed:
            # a print that breaks its form is refused at the return of the call: its entry stays
            # due and counts the refusal, no document replays; at the bound the debt is lifted
            # without a capture, and the run goes on
            entry["refused"] = int(entry.get("refused", 0)) + 1
            if entry["refused"] < self._settings.repairs_allowed:
                persistence.set_prints(slot, due)
                self._trace("repair-in-place", instruction=entry["instruction"], document=document,
                            counted=True, reask=True, refused=entry["refused"])
                return "caught", self._caught_back(stack, missed)
            self._trace("print-waived", instruction=entry["instruction"], document=document,
                        refused=entry["refused"])
            del due[at]
            persistence.set_prints(slot, due)
            said, block = self._after_print(stack, entry, due)
            return ("waived", None) if block is None else (said, block)   # nothing kept: its own line
        else:
            self._trace("answer", instruction=entry["instruction"], document=document, given=text,
                        channel=language.TERMINAL,
                        weight={"chars": len(text), "tokens": metrics.tokens(text)})
        del due[at]
        persistence.set_prints(slot, due)
        return self._after_print(stack, entry, due)

    def _caught_back(self, stack, wrong: str) -> Block:
        """-> the block that STANDS, its DEVIATION saying what the call missed: a catch plays
        nothing and counts no repair -- the view of the run where it is (`caught` says so to the
        console, which hands it over as a view)."""
        from dataclasses import replace
        self._dry = True
        try:
            block = self._standing(stack)
        finally:
            self._dry = False
        self._caught = True
        return replace(block, deviation=wrong)

    def caught(self) -> bool:
        """-> whether the call under way was caught: its block is a view, nothing moved."""
        return self._caught

    def _after_print(self, stack, entry: dict, due: list) -> tuple[str, Block | None]:
        """-> what a print call answers once its entry has left. The step the output closed on,
        when the print was its own, is answered by it; the run moves on at the last print of an
        output that awaits nothing else -- no value, no last message, no output held or cut."""
        frame = navigation.current(stack)
        parked = navigation.exhausted(frame)
        pending = None if parked else navigation.peek(frame)
        if (pending is not None and pending.asked and pending.keyword in language.FREE
                and entry.get("stack") == navigation.render(stack)):
            navigation.give(pending, "")
            if not pending.injected:
                self._produced(stack, frame)
            self._save(stack)
            pending = None
        if due:
            self._print_next = messages.next_print(due[0]["document"])
            return "more", None
        if parked or self.held() or self.pending():
            return "last", None
        if pending is not None and language.yields(pending.keyword) and pending.asked:
            channel = self._channel(stack, frame, pending)
            valued = language.valued(channel)
            self._print_next = (messages.next_value(frame.document.name, self._run_id or "",
                                                    channel == language.TOOL_HEREDOC) if valued else "")
            return ("more" if valued else "last"), None
        return "moved", self._advance(stack)

    def print_due(self) -> str:
        """-> the call due after the print this call answered `more`: the next print, or the value a
        step awaits (`messages.next_print`, `next_value`); "" for any other call."""
        return getattr(self, "_print_next", "")

    def prints_due(self) -> list[str]:
        """-> the documents of the prints due at the run, in the order their steps were said; []
        without a run. Reads the slot, moves nothing."""
        slot = self._slot()
        return [one["document"] for one in persistence.prints_of(slot)] if slot else []

    def drain(self) -> tuple[tuple[str, str], ...]:
        """-> the documents served since the last block, and forgets them: they are delivered once."""
        served, self._payloads = tuple(self._payloads), []
        return served

    def _settled(self, frame: Frame, instruction: Instruction) -> str | None:
        """-> what the instruction already stands for, or None when it has work to do."""
        settler = getattr(self, f"_settled_{instruction.keyword.lower()}", None)
        return settler(frame, instruction) if settler else None
