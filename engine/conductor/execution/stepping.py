"""execution.stepping -- the step: the advance over the stack, the executors of SERVE, HOOK and CALL, the repair. A mixin of the facade: no state of its own."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone

from pathlib import Path
from ..packaging import compiling, events, topology
from .. import reading
from ..core import deviation, language, navigation
from ..state import instance, persistence, settings
from .. import rendering
from ..core.errors import Refusal
from ..core.model import Block, Constraint, Document, Frame, Instruction, Stack, Tool


FIELD_REFERENCE = re.compile(r"@([A-Za-z][A-Za-z0-9_-]*)\.([a-z_][a-z0-9_]*)")
# a `@Doc.field` in a described door's prose: the same shape a guard or an exec
# argument writes, resolved by the same reader

class Stepping:
    """The step: the advance over the stack, the executors of SERVE, HOOK and CALL, the repair -- a mixin of the facade."""

    def _standing(self, stack: Stack) -> Block | None:
        """-> the block that STANDS: the one the last output left, read back from the
        run's own state -- the step whose answer is awaited, or the order block that
        closed the output (the end of a passage, a stretch closed at its cap or at a
        `§`). A VIEW renders this one: nothing is played, so
        the screen never reaches a step the run has not, and what it offers is what
        the router accepts.

        documentary: the flow moves on a keyed call alone. Reading the state is the
        only way to show what holds -- playing the flow forward on a throwaway copy
        shows what would come NEXT, which is a different question."""
        frame = navigation.current(stack)
        if navigation.exhausted(frame):
            # the run is PARKED: the root of its passage is done -- the view renders the
            # closing that parked it, never the passage the next message would open
            return self._offered_as_mapped(
                self._block(stack, frame, frame.procedure.instructions[-1], order=language.AWAIT))
        pending = navigation.peek(frame)
        if pending.asked:
            block = self._offered_as_mapped(self._block(stack, frame, pending))
            mark = persistence.stopped_of(self._session) if self._session is not None else {}
            if mark:
                # the run is STOPPED at the repair bound: the step stands, the agent owes it
                # nothing -- the view says the fact and no closing
                from dataclasses import replace
                block = replace(block, label="", next_call="",
                                fact=f"stopped at the repair bound: `{mark.get('instruction', '')}` "
                                     f"missed {mark.get('repairs', 0)} times")
            return block
        asked = self._asked_position(frame)
        if asked is not None:
            # the output closed on an ORDER block carrying no step of its own -- the
            # fusion cap cut the stretch right after a batched step. What the output
            # ASKED for is that step, and the agent still owes it: the view re-shows
            # IT, at ITS position, never the tail the cap left behind.
            from dataclasses import replace
            step = frame.procedure.instructions[asked - 1]
            return self._offered_as_mapped(
                replace(self._block(stack, frame, step, at=asked), position=asked,
                        stack=navigation.render(stack, asked)))
        return self._offered_as_mapped(
            self._block(stack, frame, pending, order=language.CONTINUE))

    def _root(self, stack: Stack) -> Frame:
        """-> the ROOT of the passage: the deepest frame of the CHAIN -- the deepest SPACE (a
        frame an `OPEN` opened, wherever its step stands) or the floor, and, above it, every
        callee opened by the LAST step of the frame below, so that its exhaustion exhausts the
        whole chain -- that YIELDS a step to the agent; the chain's base when no frame of it
        yields. The root is what the principal's messages feed (the kit's TURN under BOOT and
        MEMBER, or the space opened over it): exhausted, it parks the run instead of leaving,
        and the next message rewinds it. A door routed over a pending step, a callee with steps
        behind its CALL, a consumer of HOOKs alone opened last: never the root. The ONE site of
        the rule: every reader asks it here."""
        base = max((at for at, one in enumerate(stack.frames) if navigation.space(one)), default=0)
        chain = [stack.frames[base]]
        for above in stack.frames[base + 1:]:
            if (above.caller is None or above.caller.injected
                    or chain[-1].procedure.instructions[-1] is not above.caller):
                break                 # a door, a contributor: opened by an injected CALL, never the root
            chain.append(above)
        yielding = [one for one in chain
                    if any(language.yields(step.keyword) for step in one.procedure.instructions)]
        return (yielding or chain)[-1]

    def _completes(self, stack: Stack, frame: Frame) -> bool:
        """-> whether `frame` is the root of the passage: its exhaustion ends the passage."""
        return frame is self._root(stack)

    def _passage_end(self, stack: Stack, frame: Frame) -> None:
        """The ONE site where a passage ends: the root is exhausted, the exchange is counted
        (the cadences, the payload tags and the context read the count), the mounts of the
        passage are swept -- a mount a frame holds from its entry lives as long as the frame
        -- and the run is PARKED on its exhausted root: it waits for the principal's message,
        which rewinds the root (`_opening`)."""
        self._turns += 1
        self._sweep()

    def _sweep(self) -> None:
        """The mounts of the passage leave; a mount a frame holds from its entry stays."""
        if not self._dry and self._session is not None:
            persistence.set_mounted(self._session,
                                    [one for one in self._mounted() if one.get("held")])

    def _parked(self, stack: Stack, frame: Frame, wrong: str) -> Block:
        """-> the closing that parks the run: the passage ended, the order block AWAIT -- it
        delivers nothing, every production was said at its own step."""
        self._passage_end(stack, frame)
        block = self._block(stack, frame, frame.procedure.instructions[-1], wrong,
                            order=language.AWAIT)
        self._save(stack)
        return block

    def _opening(self, stack: Stack) -> None:
        """A PARKED run taken up -- the principal's message, or a bare call: the root of the
        passage rewinds and the advance opens the passage on its first step. Nothing is
        counted nor swept here: the end of the passage did both."""
        frame = navigation.current(stack)
        if navigation.exhausted(frame):
            navigation.rewind(frame)
            self._save(stack)

    def _asked_position(self, frame: Frame) -> int | None:
        """-> the position the standing OUTPUT asked for, when that output closed on an
        order block with no step of its own: the last heading's own position, held at
        the segment map, whenever it names an EARLIER step of THIS frame.

        documentary: an output renders a STRETCH -- its opening heading and the lines of
        the steps it batched; the block it closes on may carry none of them. Reading the
        pointer alone shows that tail, an ask the agent never received."""
        segments = persistence.segments_of(self._session) if self._session else []
        if not segments:
            return None
        last = segments[-1]
        at = last.get("at")
        if not isinstance(at, int) or last.get("frame") != frame.document.name:
            return None
        return at if 0 < at < navigation.position(frame) else None

    def _offered_as_mapped(self, block: Block) -> Block:
        """-> the block with the OFFER MAP's own list: what the output offered is what
        the view shows, so the screen never carries a name the router would refuse.
        The block's frame is read back from the documents, which may have changed under
        the run; the map is the output's, and the output is what stands."""
        from dataclasses import replace
        segments = persistence.segments_of(self._session) if self._session else []
        if not segments:
            return block
        named = list(segments[-1].get("tools", []))
        held = {one.name: one for one in block.tools}
        return replace(block, tools=tuple(held.get(name, Tool(name, "")) for name in named))

    def _advance(self, stack: Stack, wrong: str = "") -> Block | None:
        """-> the next block, or None once the WHOLE STACK is exhausted. `wrong` is a
        reopening deviation: it comes with the first block this advance renders."""
        while True:
            frame = navigation.current(stack)
            if (frame.cycle == language.FIELD and frame.field is None
                    and not any(one.keyword == "FIELD" for one in frame.procedure.instructions)):
                # a DESCRIBED door whose field is not rendered yet: its FIELD step stands
                # first -- injected here, lazily, so a reopening (a repair purges what is
                # injected) finds it again; the door's prose is the step's brief
                frame.procedure.instructions.insert(
                    0, Instruction(keyword="FIELD", argument="", injected=True))
                self._save(stack)
            if navigation.exhausted(frame):
                if frame.cycle == language.FIELD:
                    # a DESCRIBED door: the lap that closes drops the head it served --
                    # the field IS what remains due, no cursor beside it; a head left
                    # opens the next lap on a rewind that keeps the mounts
                    if frame.field:
                        frame.field.pop(0)
                    if frame.field:
                        navigation.rewind(frame)
                        self._trace("lap", document=frame.document.name)
                        self._enter("lap", [frame.document.path], only=("exec",))
                        self._lap_payloads(frame.document, frame.field[0])
                        self._save(stack)
                        continue
                    self._trace("cycle-done", document=frame.document.name)
                elif frame.cycle:                # an ITERATED door: its token is asked
                    element, refused = self._cycle_element(frame.document)
                    if element:
                        # an element due: the lap opens on a rewind that KEEPS the
                        # mounts -- a lap lives inside the exchange, the sweep is the
                        # session cycle's alone
                        navigation.rewind(frame)
                        self._trace("lap", document=frame.document.name)
                        self._enter("lap", [frame.document.path], only=("exec",))
                        self._lap_payloads(frame.document, element)
                        self._save(stack)
                        continue
                    # nothing due, or a provider down: the door leaves like any callee,
                    # its last production to the caller, the refusal said on the block
                    self._trace("cycle-done", document=frame.document.name,
                                **({"refused": refused} if refused else {}))
                    if refused:
                        self.note(str(frame.cycle), refused, "refused", "cycle",
                                  by=frame.document.name)
                        self._payloads.append((str(frame.cycle), refused))
                if self._completes(stack, frame):
                    last = frame.procedure.instructions[-1]
                    if last.injected and last.site == "door":
                        # a door opened on the PARKED run has left: the passage ended before
                        # it, the run stays parked -- nothing counted; what the door mounted
                        # at its sockets leaves with it
                        self._sweep()
                        block = self._block(stack, frame, last, wrong, order=language.AWAIT)
                        self._save(stack)
                        return block
                    # the ROOT of the passage is exhausted -- nothing pends below it: the
                    # passage ends HERE and the run parks. In a run its principal conducts,
                    # the last FREE step batched is handed back first: the end comes at the
                    # principal's next call, the step resolved
                    held_back = self._held_back(stack, frame, wrong)
                    if held_back is not None:
                        return held_back
                    return self._parked(stack, frame, wrong)
                if self._defers(frame) and self._indebted(stack, frame):
                    # a socket document leaves in debt: its own laws stay DUE at the run,
                    # the next written PROVE names them
                    self._owe(frame)
                if reading.nexts(frame.document):
                    # the document LEAVES to a successor: decided now -- alone, by its
                    # skill, or by the agent at a NEXT step that stands first -- and
                    # injected as a SIBLING CALL in the caller's frame, right after the
                    # CALL that is resolving: the successor is born of the root's laws,
                    # never of this frame's, and the stack never grows by the transition
                    successor = self._successor(stack, frame)
                    if successor is None:
                        continue
                    self._inject_successor(stack, frame, successor)
                navigation.give(frame.caller, navigation.upstream(frame))
                if frame.caller.site == "door":
                    # a door routed from a FREE step takes that step with it: its
                    # production IS the step's result -- one production, never two
                    below = stack.frames[-2]
                    at = below.procedure.instructions.index(frame.caller)
                    after = below.procedure.instructions[at + 1:at + 2]
                    if after and after[0].keyword in language.FREE and not after[0].done:
                        navigation.give(after[0], navigation.upstream(frame))
                        self._produced(stack, below)
                        self._trace("consumed-by-door", document=below.document.name,
                                    instruction=str(after[0]), door=frame.document.name)
                # CALL resolves: the callee's last production flows out -- every
                # output is the next instruction's input, across the frame boundary
                holder = self.holder_of(stack, frame)
                navigation.pop(stack)
                self._release(holder)
                self._save(stack)
                continue
            instruction = navigation.peek(frame)
            if instruction.guard and not self._due(instruction):
                navigation.give(instruction, "off")   # resolves without playing: 0 serve
                self._save(stack)
                continue
            if instruction.keyword == "PROVE" and not self._due_proof(stack, frame):
                # a written PROVE with nothing to ask -- no law of production in force, or
                # nothing produced since the last PROVE played: it resolves on a line, as a
                # guard not due does; the next block carries the line
                said = ("nothing due: no law of production in force"
                        if not self._production_in_force(frame) else
                        "nothing due since the last proof")
                navigation.give(instruction, "off")
                self._idle.append(f"{frame.document.name}: PROVE -- {said}")
                self._trace("prove-idle", document=frame.document.name, said=said)
                self._save(stack)
                continue
            if instruction.barrier and self._fused:
                # the `§` section break: fusion never crosses it -- the output closes
                # here and the marked step opens the next call, WHATEVER its keyword.
                # The anchor decides, never the type: the read sits ABOVE the yielding
                # guard, and above `_settled` too -- a HOOK settles by INJECTING its
                # contributors, and a step that has not opened must inject nothing. The trace
                # says the cut once, with the step that opens the next call.
                self._trace("section", instruction=str(instruction))
                return (self._held_back(stack, frame, wrong)
                        or self._block(stack, frame, instruction, wrong, order=language.CONTINUE))
            if instruction.keyword == "HOOK" and not self._prove_ahead(frame, instruction):
                # the output is about to leave the last FREE step it batched: a HOOK (injecting
                # its contributors behind it, or not) -- in a run its principal conducts that
                # step stays PENDING instead, the output closes on it. A written
                # PROVE ahead, with nothing the agent plays before it, keeps the step batched:
                # the proof is asked in the same output, as the LLM's mode asks it (one launch)
                held_back = self._held_back(stack, frame, wrong)
                if held_back is not None:
                    return held_back
            if instruction.keyword != "NEXT":
                # a NEXT step's OPTIONS are the successors its document declares, set at
                # its injection: the pipeline is the options source everywhere else
                instruction.taken = navigation.upstream(frame)
            settled = self._settled(frame, instruction)
            if (settled is None and instruction.keyword == "PROVE" and self._stacked
                    and any(name != frame.document.name for _, _, name in self._stacked)):
                # a checkpoint never fuses under a `=> words` of ANOTHER segment: the
                # output closes on the words it asks for, the proof opens the next call --
                # a command at the foot of a massive output is played before the words
                # above it (begin, 2026-10-16); within one frame (a lap: its line, then its
                # proof) the fusion stays
                return (self._held_back(stack, frame, wrong)
                        or self._block(stack, frame, instruction, wrong, order=language.CONTINUE))
            if settled is None and language.yields(instruction.keyword):
                consumed, needs = ((self._consumer(stack, frame, instruction), )[0]
                                   if instruction.keyword in language.FREE else (False, ""))
                if (consumed and needs and "any" not in (needs, self._output_of(frame))
                        and self._output_of(frame) != needs):
                    raise Refusal("format-mismatch",
                                  f"{frame.document.name} produces "
                                  f"`{self._output_of(frame)}` -- the adjacent CALL "
                                  f"needs `{needs}`")
                cap = self._fusion_cap(frame)
                if cap and self._fused >= cap:
                    return (self._held_back(stack, frame, wrong)
                            or self._block(stack, frame, instruction, wrong, order=language.CONTINUE))
                self._fused += 1
                room = cap == 0 or self._fused < cap
                # a cycling frame's last step closes the LAP: with no checkpoint coming
                # to capture the output, the lap's end is the batch's end -- else the
                # rewind would batch the same lap again, without end
                lap_end = (frame.cycle and navigation.position(frame) == len(frame.procedure)
                           and not self._prove_coming(frame, instruction))
                if instruction.keyword in language.FREE and not consumed and room and not lap_end:
                    # an unchecked production with ROOM behind it: nothing for
                    # the tool to judge or capture -- resolved at render, the flow
                    # carries on in the same output (the batch)
                    self._stacked.append(
                        (navigation.position(frame),
                         rendering.render(self._block(stack, frame, instruction, "",
                                                      segment=True, repairing=bool(wrong))),
                         frame.document.name))    # a DEVIATION never arrives on a segment: it
                    # comes with the output's closing block, REPAIR heading included
                    self._trace("batched", instruction=str(instruction))
                    navigation.give(instruction, "")
                    self._produced(stack, frame)
                    # the last FREE step batched, with the segment that carries it: what the
                    # output's close hands back to the agent in a run its principal conducts
                    self._batched_free = (frame, instruction, self._stacked[-1])
                    self._save(stack)
                    continue
                instruction.asked = True    # its answer (or bare close) comes with the call
                block = self._block(stack, frame, instruction, wrong)
                if (self._closing(stack, frame, instruction) and instruction.keyword in language.FREE
                        and not consumed
                        # a written PROVE BREAKS the adjacency: the step renders
                        # alone, the proof is asked on the next advance
                        and not self._prove_coming(frame, instruction)
                        # a run its principal conducts: the step stays PENDING, its term is
                        # the principal's call -- the end of the passage comes with that call
                        and not self.principal()):
                    # this response step is the LAST of the root: the block IS the whole
                    # story -- the step done, the passage ends with it, the run parks
                    navigation.give(instruction, "")
                    self._produced(stack, frame)
                    self._passage_end(stack, frame)
                self._save(stack)
                return block
            navigation.give(instruction, settled) if settled is not None else self._execute(stack, frame, instruction)
            self._save(stack)

    def _hook_injects(self, frame: Frame, instruction: Instruction) -> bool:
        """-> whether the HOOK would inject a step behind the one before it: a contributor
        attached at its socket, or a cadence due -- read as `_run_hook` reads them, nothing
        played. A socket with mounts alone, or nothing, injects no step."""
        from ..packaging import contributions
        socket = contributions.address(contributions.owner_of(frame.document.path),
                                       instruction.argument, instance.base_of(self.member.meta))
        return (bool(list(instance.attached(self.member.meta, socket)))
                or bool(self._cadences_due(socket, claim=False)))

    def _held_back(self, stack: Stack, frame: Frame, wrong: str) -> Block | None:
        """-> the bare CONTINUE block closing the output on the last FREE step it batched, that
        step back to PENDING (`asked`, not done), in a run its principal conducts; None where
        there is nothing to hand back. A `=> words` production is the agent's words and its
        term is the principal's call: whatever the agent plays meanwhile -- a mount, a gesture, a
        door -- acts on THAT step, and the principal's bare call resolves it (`submit("")`) and
        goes on in the same call, through the `§` the next document opens on. The steps batched
        before it in the output stay batched; a step of another frame is never handed back."""
        kept = getattr(self, "_batched_free", None)
        if kept is None or not self.principal():
            return None
        held_frame, held, entry = kept
        if held_frame is not frame or not self._stacked or self._stacked[-1] is not entry:
            return None
        self._batched_free = None
        held.done, held.given, held.asked = False, None, True
        self._trace("pending", instruction=str(held))
        block = self._block(stack, frame, held, wrong, order=language.CONTINUE)
        self._save(stack)
        return block

    def _run_open(self, stack: Stack, frame: Frame, instruction: Instruction) -> None:
        """An OPEN enters its document exactly as a CALL does -- one entry; what makes the frame
        a SPACE is its caller's keyword, read by `_root`."""
        self._run_call(stack, frame, instruction)

    def _execute(self, stack: Stack, frame: Frame, instruction: Instruction) -> None:
        handler = getattr(self, f"_run_{instruction.keyword.lower()}", None)
        if handler is None:
            raise Refusal("keyword-not-executable", f"`{instruction.keyword}` has no handler")
        handler(stack, frame, instruction)

    def _run_serve(self, stack: Stack, frame: Frame, instruction: Instruction) -> None:
        """The TOOL reads a whole SECTION -- every line, one document after another,
        by the one reader, ALL of them in this output. A document already proven in
        this run renders nothing and is never served twice, whatever vehicle brought
        it; what the output cannot hold is the CUT's business, not the reading's."""
        lines = self._section(frame, instruction)
        try:
            plan = self._serve_plan(lines)
        except Refusal as refusal:
            # the refusal NAMES the document whose row could not be read
            detail = str(refusal).split(" — ", 1)[-1]
            raise Refusal(refusal.code,
                          f"{detail} -- serve row of {frame.document.name}") from refusal
        while instruction.slot < len(plan):
            entry = plan[instruction.slot]
            _, name, cut, token, mark = entry
            material = self._material_name(mark, frame.document.front, stack)
            path = self._stale(name, material)
            if path is None:
                # the document is gone: the reading continues without it -- the
                # signal keeps the section honest, the note keeps the agent oriented
                self._signal("engine", "serve-stale",
                             evidence=f"{name} -- gone")
                self.note(token, "", "missing", "serve", by=frame.document.name)
                self._payloads.append(
                    (token, "(this section's document is gone)"))
                instruction.slot += 1
                continue
            if cut and not self._clipped(path, cut, frame.document.name, name, token):
                instruction.slot += 1
                continue
            self._serve_document(path, cut, title=self._titled(token, path), origin="serve",
                                 by=frame.document.name, nature=entry[0])
            # served now, or proven before by a section, a SERVE <doc>, a mount:
            # either way the entry is done and the next one follows
            instruction.slot += 1
        if instruction.slot >= len(plan):
            # the SERVE keeps the proofs it gave: a repair that reopens the frame
            # hands them back, so the reading re-serves
            navigation.give(instruction, [self._reading(path, cut)[1]
                                          for kind, *rest in plan if kind == "doc"
                                          for name, cut, _token, mark in (rest,)
                                          if (path := self._stale(
                                              name, self._material_name(mark, frame.document.front, stack))) is not None])

    def _run_hook(self, stack: Stack, frame: Frame, instruction: Instruction) -> None:
        """A HOOK is a named socket, and its contributors reach it by one of TWO verbs of
        their own front matter: `attach: <name>` is CALLed there, `mount: <name>` is
        MOUNTED there -- it enters the view, laws and matter, and asks the agent nothing.
        Both verbs make ONE list, ordered together: the requires topology of their homes
        and, within one, the name -- then the ORDER PREFERENCES each contributor declares
        for this socket (`order:` in its front matter, `instance.ordering`). A contributor
        carries its own guard (`when: @Doc.field` in its front matter): a called one hands
        it to the injected CALL, a mounted one is judged by the same predicate before it
        enters -- the socket knows neither key. The HOOKING document mounts too: the names
        its `mounts:` table (and its overlays') gives this socket follow the contributors,
        each judged by its own guard, through the same `_mount_socket`. Nothing declared =
        a strict no-op."""
        from ..packaging import contributions
        # what the proc WRITES is `<proc>.<hook>`; what contributors address is the socket's
        # ADDRESS -- the package that opens it qualifies what it wrote
        socket = contributions.address(contributions.owner_of(frame.document.path),
                                       instruction.argument, instance.base_of(self.member.meta))
        attached = list(instance.attached(self.member.meta, socket))
        hosted = list(instance.mounting(self.member.meta, socket))
        due = self._cadences_due(socket)
        # the derived order and the preferences decide when a contributor plays
        contributors = instance.ordering(self.member.meta, socket, attached + hosted)
        at = frame.procedure.instructions.index(instruction)
        offset, mounting = 0, []
        for name in contributors:
            guard = self._guard_of(name)
            if name in hosted:
                if not guard or self._due(Instruction(keyword="CALL", argument=name,
                                                      injected=True, guard=guard)):
                    mounting.append(name)
                continue
            offset += 1
            frame.procedure.instructions.insert(
                at + offset, Instruction(keyword="CALL", argument=name, injected=True,
                                         guard=guard, site="socket"))
        for name in self._hosted_by(frame, instruction.argument):
            guard = self._guard_of(name)
            if name not in mounting and (not guard or self._due(
                    Instruction(keyword="CALL", argument=name, injected=True, guard=guard))):
                mounting.append(name)
        for name in due:
            offset += 1
            frame.procedure.instructions.insert(
                at + offset, Instruction(keyword="CALL", argument=name, injected=True,
                                         site="cadence"))
        self._mount_socket(frame, mounting)
        navigation.give(instruction, contributors + due)

    def _initialize(self, stack: Stack, frame: Frame) -> None:
        """The IMPLICIT socket of a frame's entry, `<proc>.initialize`, played ONCE before its
        first step -- the same two verbs as a HOOK, the same order, the same guards: an
        `attach:` is CALLed there (site `initialize`: its body served, no proof of its own)
        and its laws and offer then HELD for the frame's life; a `mount:` enters the view
        held the same way; a cadence due there is CALLed as at any socket. What a frame
        holds, the session cycle's rewind keeps and the frame's pop releases: a contributor
        plays once per entry, never per lap."""
        from ..packaging import contributions
        socket = contributions.address(contributions.owner_of(frame.document.path),
                                       contributions.initialize_of(frame.document.path),
                                       instance.base_of(self.member.meta))
        attached = list(instance.attached(self.member.meta, socket))
        hosted = list(instance.mounting(self.member.meta, socket))
        due = self._cadences_due(socket)
        contributors = instance.ordering(self.member.meta, socket, attached + hosted)
        if not contributors and not due:
            return
        holder = self.holder_of(stack, frame)
        offset, mounting, called = 0, [], []
        for name in contributors:
            guard = self._guard_of(name)
            if name in hosted:
                if not guard or self._due(Instruction(keyword="CALL", argument=name,
                                                      injected=True, guard=guard)):
                    mounting.append(name)
                continue
            frame.procedure.instructions.insert(
                offset, Instruction(keyword="CALL", argument=name, injected=True,
                                    guard=guard, site="initialize"))
            offset += 1
            if not guard or self._due(Instruction(keyword="CALL", argument=name,
                                                  injected=True, guard=guard)):
                called.append(name)
        for name in due:
            frame.procedure.instructions.insert(
                offset, Instruction(keyword="CALL", argument=name, injected=True, site="cadence"))
            offset += 1
        self._trace("initialize", document=frame.document.name, socket=socket,
                    contributors=contributors + due)
        self._mount_socket(frame, mounting, held_by=holder)
        self._hold_laws(frame, called, holder)

    def _hosted_by(self, frame: Frame, hook: str) -> list[str]:
        """-> the names the hooking document mounts at `hook` itself: its `mounts:` table,
        then -- when it is the base of its name -- each overlay's, in application order,
        each name once. An overlay adds, it never removes."""
        document = frame.document
        found: list[str] = []
        layers = [document]
        if instance.resolve(self.member.meta, document.path.name).resolve() == document.path.resolve():
            layers += [reading.read(one) for one in
                       instance.overlays_of(self.member.meta, document.path.name)]
        for layer in layers:
            for name in reading.mounts(layer).get(hook, ()):
                if name not in found:
                    found.append(name)
        return found

    def _cadences_due(self, socket: str, claim: bool = True) -> list[str]:
        """-> the documents the CADENCES declared at `socket` play NOW -- each one
        due by the crossing predicate (its anchored day crossed its record, its
        `since` record moved), after the socket's contributors, and CLAIMED by this
        run for its period: a period another living run holds plays nothing here and
        says so in the trace (`cadence-claimed`) -- what is due once is played once. A
        `play` that resolves to no document is said to the trace and skipped: a
        cadence never breaks the boot. `claim=False` READS what is due and claims
        nothing (`_hook_injects`): the claim is the HOOK's own, when it plays."""
        from ..packaging import contributions
        from ..state import cadences
        found = []
        for one in contributions.composed(self.member.meta):
            if one["kind"] != "cadences" or str(one.get("at", "")) != socket:
                continue
            anchor = str(one.get("anchor", ""))
            if not cadences.crossing_due(self.member.meta, anchor,
                                         str(one.get("record", "")), one.get("since")):
                continue
            play = str(one["play"])
            if not self._resolve(play).is_file():
                self._trace("cadence-unplayable", cadence=str(one.get("name")), play=play)
                continue
            name, period = str(one.get("name")), cadences.boundary_of(self.member.meta, anchor)
            if claim and period is not None and not cadences.claim(self.member.meta, name, period.isoformat(),
                                                                    self._run_id, self._claimant_alive):
                self._trace("cadence-claimed", cadence=name, period=period.isoformat(),
                            run=cadences.holder_of(self.member.meta, name, period.isoformat()))
                continue
            found.append(play)
        return found

    def _claimant_alive(self, run: str) -> bool:
        """-> whether a claimant run still holds what it claimed: its saved state stands --
        one rule for every run, whoever launched it. A run that died during its exchange
        keeps the period until it is forgotten: one period lost at most. A renewal mark is
        no saved state: the run an upgrade renewed claims again when it reopens."""
        slot = persistence.slot_of(self.member.meta, run)
        return slot.exists() and persistence.renewed(slot) is None

    def _guard_of(self, name: str) -> str:
        """-> the guard a contributor declares for itself -- `when: @Doc.field` in its
        front matter, the grammar of an instruction's `^ @Doc.field` -- or "" when
        it plays unconditionally."""
        path = self._resolve(name)
        if not path.is_file():
            return ""
        declared = str(reading.read(path).front.get("when", "")).strip()
        if not declared:
            return ""
        if not declared.startswith("@") or "." not in declared:
            raise Refusal("guard-invalid",
                          f"`when: {declared}` on {name} -- a guard is `@Doc.field`")
        return declared[1:]

    def _declared_payloads(self, document: Document) -> int:
        """The PAYLOADS a document declares (`payloads: <tokens>` in its front
        matter): for each token, every document that PROVIDES it (`provides:` and
        `with:` in its own front matter) names a skill the engine runs, its output
        rendered as the `INFORMATION -- <token>` section of the block, providers in
        the requires topology. An empty output renders nothing; a skill that refuses
        is SAID in the section and the turn goes on -- a broken package never stops
        the conduction.

        A token enters an output ONCE: its providers run for the first consumer, and a
        second consumer in the same output runs none and receives nothing, the ledger
        saying `spared` with the mass avoided. Across the outputs of one exchange the
        providers run again, and a rendering identical to one the exchange already
        delivered is spared by its content -- a changed rendering enters whole.
        -> how many sections this entry rendered -- served, refused, or SPARED because the
        exchange delivered the same rendering already (the matter stands in the agent's
        context): what a contributor's body waits for."""
        from ..packaging import contributions
        import hashlib
        import time
        tokens = str(document.front.get("payloads", "")).split()
        appended = 0
        for token in tokens:
            known = self._resolved.get(token)
            if known is not None:
                for one in known:
                    self.note(token, "", "spared", "payload", by=document.name,
                              with_=one["with"], package=one["package"], spared=one["chars"])
                    appended += 1
                continue
            rendered: list[dict] = []
            for provider in contributions.providers(self.member.meta, token):
                begun = time.perf_counter()
                rc, out, err = contributions.run_skill(
                    self.member.meta, str(provider["skill"]), list(provider.get("args") or []))
                # the engine-run skill leaves its named line -- the effort of a
                # provider is attributable, like an agent gesture (la-mesure-de-l-effort)
                self._trace("provider", name=str(provider["skill"]), token=token,
                            package=str(provider.get("package") or ""), rc=rc,
                            ms=round((time.perf_counter() - begun) * 1000, 1))
                said = str(provider["skill"])
                package = str(provider.get("package") or "")
                if rc != 0:
                    text = f"{provider['skill']} refused ({rc}): {err.strip()[-300:]}"
                    self.note(token, text, "refused", "payload", by=document.name,
                              with_=said, package=package)
                    self._payloads.append((token, text))
                    appended += 1
                elif out.strip():
                    text = out.strip()
                    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
                    tag = f"payload:{self._turns}:{token}:{said}:{digest}"
                    if tag in self._proven:
                        self.note(token, "", "spared", "payload", by=document.name,
                                  with_=said, package=package, spared=len(text))
                        appended += 1
                    else:
                        self.note(token, text, "served", "payload", by=document.name,
                                  with_=said, package=package)
                        self._payloads.append((token, text))
                        self._prove_payload(tag)
                        appended += 1
                else:
                    continue
                rendered.append({"with": said, "package": package, "chars": len(text)})
            self._resolved[token] = rendered
        return appended

    def _prove_payload(self, tag: str) -> None:
        """A rendering the exchange delivered is proven by its content, for this exchange
        alone: the tags of earlier exchanges leave the proofs as a new one enters, and the
        tag is staged like a reading -- an output cut under the cap proves it at its last
        chunk."""
        current = f"payload:{self._turns}:"
        self._proven.difference_update({one for one in self._proven
                                        if one.startswith("payload:")
                                        and not one.startswith(current)})
        self._proven.add(tag)
        self._staged.append(tag)

    def _cycle_token(self, document: Document) -> str | None:
        """-> the token an ITERATED door declares (`cycle: <token>`), None for the session
        cycle or no cycle at all."""
        cycle = reading.cycles(document)
        return cycle if isinstance(cycle, str) and cycle != language.FIELD else None

    def _cycle_element(self, document: Document) -> tuple[str, str]:
        """The ITERATOR of an iterated door, asked: the token's providers render the
        element that remains DUE -- a REQUEST, never a cursor: two calls in a row
        render the same element, the engine keeps no count, and it is the accepted
        production (a sink, a keyless verb) that moves it. -> (the element, the refusal
        said): a token no document provides refuses `cycle-unprovided` at once; a provider
        that refuses ends the cycle, its refusal carried -- a door never turns on a
        breakdown."""
        from ..packaging import contributions
        import time
        token = str(reading.cycles(document))
        providers = contributions.providers(self.member.meta, token)
        if not providers:
            raise Refusal("cycle-unprovided",
                          f"{document.name}: `cycle: {token}` -- no document of the "
                          f"composition provides `{token}`")
        parts: list[str] = []
        for provider in providers:
            begun = time.perf_counter()
            rc, out, err = contributions.run_skill(
                self.member.meta, str(provider["skill"]), list(provider.get("args") or []))
            self._trace("provider", name=str(provider["skill"]), token=token,
                        package=str(provider.get("package") or ""), rc=rc,
                        ms=round((time.perf_counter() - begun) * 1000, 1))
            if rc != 0:
                return "", f"{provider['skill']} refused ({rc}): {err.strip()[-300:]}"
            if out.strip():
                parts.append(out.strip())
        return "\n".join(parts), ""

    def _lap_payloads(self, document: Document, element: str) -> None:
        """What a LAP renders at its first block: every `payloads:` of the document
        re-resolved -- a lap is an ENTRY, its output a new one, its providers run again,
        a rendering the exchange already delivered spared by its content -- then the
        token's element under the token's own title."""
        self._enter("lap", [document.path], only=("payloads",))
        self.note(self._cycle_title(document), element, "served", "cycle", by=document.name)
        self._payloads.append((self._cycle_title(document), element))

    def _input(self, document: Document, procedure, seed) -> None:
        """The production a consumer RECEIVES, served once at the entry of its frame under
        `input`, as it was given -- a JSON value rendered as JSON. A consumer whose first
        producing step is a PICK sees it as its OPTIONS and is served nothing more."""
        if seed is None or seed == "":
            return
        first = next((one for one in procedure.instructions
                      if one.keyword in language.FREE or language.needs_options(one.keyword)), None)
        if first is not None and first.keyword == "PICK":
            return
        text = seed if isinstance(seed, str) else json.dumps(seed, ensure_ascii=False, indent=2)
        self.note("input", text, "served", "input", by=document.name)
        self._payloads.append(("input", text))

    def _cycle_title(self, document: Document) -> str:
        """-> the title an iterated door's element is served under: its token for a
        provided door, `field` for a described one -- the word of the key, as `proof`
        is the checkpoint's."""
        token = self._cycle_token(document)
        return token if token else "field"

    def _field_brief(self, document: Document) -> str:
        """-> the described door's prose, its `@Doc.field` references resolved as an
        exec's arguments are (`settings.field_value`); an empty value refuses
        `field-argument-empty` -- a brief that names nothing describes nothing."""
        prose = reading.fields(document)

        def resolve(match: re.Match) -> str:
            stem, field = match.group(1), match.group(2)
            value = settings.field_value(self.member.meta, stem, field)
            if not value:
                raise Refusal("field-argument-empty",
                              f"{document.name}: `@{stem}.{field}` in `field:` resolves to "
                              "nothing -- a reference of the brief names a value")
            return value
        return FIELD_REFERENCE.sub(resolve, prose)

    def _next_brief(self, document: Document) -> str:
        """-> the prose that decides the successor (`choose:`), its `@Doc.field`
        references resolved as a described door's are; an empty value refuses
        `choose-argument-empty`."""
        prose = reading.chooses(document)

        def resolve(match: re.Match) -> str:
            stem, field = match.group(1), match.group(2)
            value = settings.field_value(self.member.meta, stem, field)
            if not value:
                raise Refusal("choose-argument-empty",
                              f"{document.name}: `@{stem}.{field}` in `choose:` resolves to "
                              "nothing -- a reference of the brief names a value")
            return value
        return FIELD_REFERENCE.sub(resolve, prose)

    def _successor(self, stack: Stack, frame: Frame) -> str | None:
        """-> the document `frame` leaves to, decided NOW at its exit: the one name of
        `next:` (`alone`); the name the owner's skill prints under `decide:` (`skill` --
        a name outside `next:` refuses `next-foreign`, a non-zero exit `next-refused`);
        the name the agent elected at the NEXT step (`agent`). None when the NEXT step is
        not answered yet: it is injected in the frame's tail and stands first."""
        from ..packaging import contributions
        names = list(reading.nexts(frame.document))
        document = frame.document
        if len(names) == 1:
            self._trace("next", document=document.name, successor=names[0], by="alone")
            return names[0]
        words = list(reading.decides(document))
        if words:
            owner = contributions.owner_of(document.path)
            skill, rest = ((words[0], words[1:]) if owner is None
                           else (f"{topology.SKILL_LEAD}{owner}", words))
            given = [self._exec_argument(one, document.path) for one in rest]
            rc, out, err = contributions.run_skill(self.member.meta, skill, given)
            if rc != 0:
                raise Refusal("next-refused",
                              f"`{skill} {' '.join(rest)}` at {document.name} refused ({rc}): "
                              f"{(err.strip() or out.strip())[-300:]}")
            said = out.strip()
            if said not in names:
                raise Refusal("next-foreign",
                              f"`{skill} {' '.join(rest)}` at {document.name} said `{said}` -- "
                              f"not a successor of its `next:` ({', '.join(names)})")
            self._trace("next", document=document.name, successor=said, by="skill")
            return said
        chosen = next((one for one in frame.procedure.instructions
                       if one.keyword == "NEXT" and one.done), None)
        if chosen is None:
            step = Instruction(keyword="NEXT", argument="", injected=True)
            step.taken = names
            frame.procedure.instructions.append(step)
            self._save(stack)
            return None
        self._trace("next", document=document.name, successor=str(chosen.given), by="agent")
        return str(chosen.given)

    def _inject_successor(self, stack: Stack, frame: Frame, successor: str) -> None:
        """The successor enters the CALLER's frame as a sibling CALL, right after the
        CALL that opened `frame` -- the gesture of a HOOK: injected, so a rewind or a
        reopening purges it; a socket or a cadence document's successor keeps its path, so
        its own laws are deferred to the turn's checkpoint too; no guard, judged at the
        first entry."""
        caller = stack.frames[-2]
        at = caller.procedure.instructions.index(frame.caller)
        path = frame.caller.site if frame.caller.site in ("socket", "cadence") else "successor"
        caller.procedure.instructions.insert(
            at + 1, Instruction(keyword="CALL", argument=successor, injected=True, site=path))

    def _open_field(self, stack: Stack, frame: Frame, elements: list) -> None:
        """The field RENDERED and accepted: the frame holds what remains due and the door
        opens on its head -- the first lap, its element under `field`. An empty array is
        nothing due: no lap opens, the line under `field` says it, and the door leaves
        like any callee -- the run completes when it is the floor."""
        frame.field = [str(one) for one in elements]
        if frame.field:
            # the FIELD step, played once, leaves the procedure: the laps count their own
            # steps alone, the first as the others (`{1/1}`, never `{2/2}`)
            frame.procedure.instructions = [one for one in frame.procedure.instructions
                                            if one.keyword != "FIELD"]
            self._trace("lap", document=frame.document.name)
            self._lap_payloads(frame.document, frame.field[0])
            return
        if frame.caller is None:
            said = "nothing due -- the run completes"
            for one in frame.procedure.instructions:
                if not one.done:
                    navigation.give(one, "off")
        else:
            said = "nothing due -- nothing opens"
            navigation.give(frame.caller, "")
            holder = self.holder_of(stack, frame)
            navigation.pop(stack)
            self._release(holder)
        self.note("field", said, "served", "cycle", by=frame.document.name)
        self._payloads.append(("field", said))
        self._trace("cycle-done", document=frame.document.name)

    def _exec_declarants(self, path: Path) -> list[tuple[Path, str, str, list[str]]]:
        """-> (file, skill, verb, arguments) for every `exec:` the document at `path`
        carries -- its own file and, when `path` IS the resolved base, each overlay of
        its name -- in the order they play (`instance.exec_order`). A package's file
        never names the skill: it is the `pp-<package>` of the file's owner; a file of
        the instance names one of the instance's own skills first."""
        from ..packaging import contributions
        files = [path]
        if instance.resolve(self.member.meta, path.name) == path:
            files += instance.overlays_of(self.member.meta, path.name)
        declared = {one: str(reading.read(one).front.get("exec") or "").split()
                    for one in files}
        found = []
        for one in instance.exec_order(self.member.meta, [f for f in files if declared[f]]):
            words = declared[one]
            owner = contributions.owner_of(one)
            skill, rest = (words[0], words[1:]) if owner is None else (f"{topology.SKILL_LEAD}{owner}", words)
            found.append((one, skill, rest[0] if rest else "", rest[1:]))
        return found

    def _exec_argument(self, word: str, path: Path) -> str:
        """-> an exec argument as the skill receives it: a word as it is, a `@Doc.field`
        by the value a guard would read -- and never empty."""
        match = topology.TAG.fullmatch(word)
        if match is None:
            return word
        value = settings.field_value(self.member.meta, match.group(1), match.group(2))
        if not value:
            raise Refusal("exec-argument-empty",
                          f"`{word}` at {path.name} -- no `{match.group(2)}:` on "
                          f"{match.group(1)}.md and no default: an exec argument is never "
                          "passed empty")
        return value

    def _run_exec(self, path: Path, site: str) -> None:
        """The document ACTS at its entry: every `exec:` it carries plays its owner's
        skill NOW -- before the body and any service -- once per entry (a CALL, a mount,
        a lap), never on a view, a chunk, a re-serve or a repair. A non-zero exit refuses
        `exec-refused` and the entry does not happen. What the skill says to the bus is
        harvested, a `::mount` refuses `exec-mount`, the rest of its output is dropped:
        an exec prepares, it serves nothing."""
        if self._dry:
            return
        from ..packaging import contributions
        import time
        for file, skill, verb, args in self._exec_declarants(path):
            given = ([verb] if verb else []) + [self._exec_argument(one, path) for one in args]
            begun = time.perf_counter()
            rc, out, err = contributions.run_skill(self.member.meta, skill, given)
            self._trace("exec", skill=skill, verb=verb, document=reading.title(path),
                        package=contributions.owner_of(file) or "instance", site=site, rc=rc,
                        ms=round((time.perf_counter() - begun) * 1000, 1))
            if rc != 0:
                raise Refusal("exec-refused",
                              f"`{skill} {verb}` at {path.name} ({site}) refused ({rc}): "
                              f"{(err.strip() or out.strip())[-300:]}")
            rest = events.harvest(self.member.meta, out)
            if any(line.startswith("::mount ") for line in rest):
                raise Refusal("exec-mount",
                              f"`{skill} {verb}` at {path.name} printed a `::mount` -- an "
                              "exec prepares, it mounts nothing")

    def _run_call(self, stack: Stack, frame: Frame, instruction: Instruction) -> None:
        """A CALL is a SERVE that also executes: the callee's BODY comes with the block first,
        read by the one reader exactly like a SERVE -- proven by its composition,
        silent once proven -- and only once it is delivered whole (or stands proven
        already) does the frame open. Constraints and tools ACCUMULATE from there
        on, never lighten. An ITERATED door asks its token BEFORE its body: nothing
        due, no lap opens -- neither body nor step -- and the line under the token
        says it; the CALL resolves in place."""
        path = self._resolve(instruction.argument)
        document = reading.read(path)
        token = self._cycle_token(document)
        if token:
            element, refused = self._cycle_element(document)
            if not element:
                self.note(token, refused or "", "refused" if refused else "served", "cycle",
                          by=document.name)
                self._payloads.append((token, refused or "nothing due -- nothing opens"))
                self._trace("cycle-done", document=document.name,
                            **({"refused": refused} if refused else {}))
                navigation.give(instruction, "")
                return
        site = instruction.site or "call"
        if instruction.slot == 0:
            # the entry ARRIVES: its `exec:`, its body (`proc_body_serve: always` forces it
            # back at every CALL), the rows its overlays add -- the base's own sections keep
            # their SERVE pace; the frame opens at the next step, once the body is delivered
            self._enter(site, [path], only=("exec", "body", "overlay_rows"),
                        by=frame.document.name)
            instruction.slot = 1
            return
        if token:
            # the first lap opens: the element under its token, after the declared payloads
            self._trace("lap", document=document.name)
            self._lap_payloads(document, element)
        else:
            self._enter(site, [path], only=("payloads",))
        laws, tools = compiling.effective(self.member.meta, document)
        seed = (navigation.upstream(frame) if instance.declared(self.member.meta, path, "input")
                else None)
        snapshot = (tuple(Constraint.parse(line) for line in instruction.routed)
                    if instruction.routed else None)   # a routed door inherits the
        # owning segment's snapshotted laws, never the pending frame's chain
        offered = {one.name for one in frame.tools}   # a name is offered ONCE at a step:
        procedure = reading.playable(document)
        self._input(document, procedure, seed)
        callee = Frame(document=document, procedure=procedure,   # the callee
                       constraints=(snapshot if snapshot is not None
                                    else frame.constraints) + laws,   # re-declaring an
                       tools=frame.tools + tuple(one for one in tools  # inherited tool
                                                 if one.name not in offered),   # adds nothing
                       caller=instruction, cycle=reading.cycles(document), seed=seed,
                       routed=snapshot)
        navigation.push(stack, callee)
        self._initialize(stack, callee)   # the callee's own entry socket, once

    def _bound(self, stack: Stack, frame: Frame, anchor: Instruction, wrong: str) -> None:
        """Counts the deviation on `anchor`; at the bound the run STOPS on its step: the mark
        written at the slot (the document, the step, the count, the miss), the stack saved as it
        stands -- neither reopened nor rewound --, the fact traced; then the refusal, which is the
        agent's answer. The principal's word takes the step up (`_taken_up`)."""
        try:
            deviation.register(anchor, self._settings.repairs_allowed)
        except Refusal as refusal:
            if refusal.code != "repair-exhausted":
                raise
            repairs = self._settings.repairs_allowed
            if not self._dry and self._session is not None:
                persistence.set_stopped(self._session, {
                    "document": frame.document.name, "instruction": str(anchor), "repairs": repairs,
                    "miss": wrong, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
                self._save(stack)
            self._trace("stopped", document=frame.document.name, instruction=str(anchor),
                        repairs=repairs)
            raise

    def _taken_up(self, stack: Stack, mark: dict, word: str) -> Block | None:
        """A run STOPPED at the repair bound, taken up -- by the principal's word, or by a bare
        call: the mark leaves, the counts of the document re-arm, the document reopens on the
        miss the bound saw (the repair the bound denied, played now), the word served as a
        reading. Nothing is counted nor swept: the passage goes on."""
        frame = navigation.current(stack)
        for one in frame.procedure.instructions:
            one.repairs = 0
        if not self._dry and self._session is not None:
            persistence.set_stopped(self._session, {})
        self._trace("taken-up", document=frame.document.name, instruction=str(mark.get("instruction", "")),
                    word=bool(word.strip()))
        if word.strip():
            self._trace("prompt", text=word)
            self.note(language.WORD, word, "served", "prompt", by=frame.document.name)
            self._payloads.append((language.WORD, word))
        navigation.reopen(frame)
        self._save(stack)
        return self._advance(stack, str(mark.get("miss", "")))

    def _repair(self, stack: Stack, frame: Frame, instruction: Instruction, wrong: str) -> Block:
        """A deviation reopens the WHOLE document: the pointer returns to the first
        instruction, chained steps replay, and the reopened cession carries the miss.
        The repair counts survive the reopening -- the bound still hands back."""
        self._trace("repair", document=frame.document.name, instruction=str(instruction))
        if self._count_traced("repair", "document", frame.document.name) >= 2:
            self._signal("engine", "repaired", evidence=frame.document.name)
        anchor = instruction
        if instruction.injected:
            # an injected checkpoint is PURGED by the reopening -- its count would
            # restart at zero; a stable instruction carries the bound instead
            stable = [one for one in frame.procedure.instructions if not one.injected]
            anchor = stable[-1] if stable else instruction
        self._bound(stack, frame, anchor, wrong)
        # the reopened frame re-serves NOTHING: a reading proven in the run stays
        # proven across the repair -- the agent re-reads its own context, never a
        # second copy (operator word 2026-09-05; measured at 33 % of a campaign)
        navigation.reopen(frame)
        self._save(stack)
        return self._advance(stack, wrong)
