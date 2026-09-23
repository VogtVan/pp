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

    def play(self, name: str, route: dict | None = None) -> Block | None:
        """Agent-opened proc: injects `CALL <name>.md` at the pending step of the
        CURRENT frame and advances -- the proc plays CONDUCTED, stacked over the turn.
        The caller checks the scope first (`peek`/`route`); this method trusts it.
        Routed (offered by a PAST segment of the current output), the door still
        stacks HERE -- the stack never runs backward -- but inherits the owning
        segment's snapshotted laws, and its entry heading says the route."""
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
        injected = Instruction(keyword="CALL", argument=f"{name}.md", injected=True)
        if route is not None:
            injected.routed = tuple(route.get("constraints", ()))
            self._route_note = f"[{route.get('ordinal')}] {route.get('frame')}"
            self._trace("routed", name=name, segment=route.get("ordinal"),
                        frame=route.get("frame"))
        frame.procedure.instructions.insert(navigation.pointer(frame), injected)
        return self._advance(stack)

    def resume(self, path: Path) -> Block | None:
        """-> where the run stands; starts one if none is under way. NEVER mutates a
        pending instruction -- a status check, safe to call as many times as asked."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap = []          # a re-show: the standing addresses survive it
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            return self.start(path)
        stack = self._rebind(restored)
        if persistence.compacted_of(slot):
            return self._reserved(stack)
        return self._advance(stack)

    def forward(self, given: str = "") -> Block | None:
        """The ONE advance call (`./pp <key> [value|-]`): binds `given` to a
        pending YIELD awaiting an answer, or carries the run on -- a reading's next
        chunk, the after-FINAL resume -- when nothing awaits one. Advancing is the
        KEYED call: without a run it refuses, it never opens one."""
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
            return self._reserved(stack)
        frame = navigation.current(stack)
        pending = (navigation.peek(frame)
                   if not navigation.exhausted(frame) else None)
        return self.submit(given)

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
        frame = navigation.current(stack)
        if navigation.exhausted(frame):
            if not frame.cycle:
                if answer.strip():
                    raise Refusal("run-complete",
                                  "the run is over -- there is nothing to answer")
                return None   # a bare advance on a finished run: complete, not a lie
            # a cycling floor at its frontier: the rewind happens in the advance --
            # text handed here is the operator's message (captured) or a stray
            if answer.strip():
                if self._settings.capture_prompt:
                    self._trace("prompt", text=answer)
                    return self._advance(stack)
                return self._advance(stack, "your production belongs in the CHAT -- "
                                            "say it there and call back with the key "
                                            "alone; the tool takes nothing back. "
                                            "Nothing was recorded.")
            return self._advance(stack)
        instruction = navigation.peek(frame)
        if not (language.yields(instruction.keyword) and instruction.asked):
            # nothing awaits an answer: the batch resolved its chat yields at render.
            # Text handed anyway: the operator's message under capture (traced), a
            # stray production otherwise (bounced softly -- no repair)
            if answer.strip():
                if self._settings.capture_prompt:
                    self._trace("prompt", text=answer)
                    return self._advance(stack)
                return self._advance(stack, "your production belongs in the CHAT -- "
                                            "say it there and call back with the key "
                                            "alone; the tool takes nothing back. "
                                            "Nothing was recorded.")
            return self._advance(stack)
        # the agent's side weighed at the source: what its production cost, in characters
        # and in estimated tokens -- the reader sums it apart from the blocks
        self._trace("answer", instruction=str(instruction), given=answer,
                    weight={"chars": len(answer), "tokens": metrics.tokens(answer)})
        if (answer.strip() and instruction.keyword in language.FREE
                and self._channel(stack, frame, instruction) in ("chat", "ephemeral")):
            # the soft catch: an over-eager hand-in is not a lie -- the block
            # answers, nothing is recorded, no repair is counted
            return self._advance(stack, "your production is not the tool's -- a draft "
                                        "waits for the FINAL delivery, a chat one is "
                                        "said there; call back with the key alone. "
                                        "Nothing was recorded.")
        if not answer and instruction.keyword not in language.FREE:   # a FREE step's own text never
            return self._repair(stack, frame, instruction, deviation.empty_answer(instruction))
        missed = self._check(stack, frame, instruction, answer)
        if missed:
            if self._inplace:
                # the cheap branch: the bound counts, the document STANDS -- the same
                # checkpoint re-presents with the fixes to play, nothing reopens
                instruction.refit, self._inplace = self._inplace, ()
                anchor = instruction
                if instruction.injected:
                    stable = [one for one in frame.procedure.instructions
                              if not one.injected]
                    anchor = stable[-1] if stable else instruction
                deviation.register(anchor, self._settings.repairs_allowed)
                self._trace("repair-in-place", instruction=str(instruction),
                            codes=list(instruction.refit))
                self._save(stack)
                return self._advance(stack, missed)
            return self._repair(stack, frame, instruction, missed)
        if (instruction.keyword in language.FREE and answer.strip()
                and self._output_of(frame) == "json"):
            # a validated json production IS data: parsed, it feeds a PICK's
            # options or a callee's seed -- the pipeline is the options source
            navigation.give(instruction, json.loads(answer))
        else:
            if (instruction.keyword in language.FREE and not answer.strip()
                    and self._channel(stack, frame, instruction) == "ephemeral"):
                self._draft(frame)   # a mid-turn draft closed bare: the FINAL owes it
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
