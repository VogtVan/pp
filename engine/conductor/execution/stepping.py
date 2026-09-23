"""execution.stepping -- the step: the advance over the stack, the executors of SERVE, HOOK and CALL, the repair. A mixin of the facade: no state of its own."""
from __future__ import annotations

import re

from pathlib import Path
from ..packaging import compiling, events, topology
from .. import reading
from ..core import deviation, language, navigation
from ..state import instance, persistence
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
        closed the output (a delivered frontier, a stretch closed at its cap or at a
        `§`, a finished conduction). A VIEW renders this one: nothing is played, so
        the screen never reaches a step the run has not, and what it offers is what
        the router accepts.

        documentary: the flow moves on a keyed call alone. Reading the state is the
        only way to show what holds -- playing the flow forward on a throwaway copy
        shows what would come NEXT, which is a different question."""
        frame = navigation.current(stack)
        pending = None if navigation.exhausted(frame) else navigation.peek(frame)
        if pending is not None and pending.asked:
            return self._offered_as_mapped(self._block(stack, frame, pending))
        at = navigation.pointer(frame) - 1
        closed = frame.procedure.instructions[at] if at >= 0 else None
        if closed is not None and closed.keyword == language.FINAL:
            return self._offered_as_mapped(
                self._block(stack, frame, closed, order=language.FINAL))
        asked = self._asked_position(frame) if pending is not None else None
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
        if pending is not None:
            return self._offered_as_mapped(
                self._block(stack, frame, pending, order=language.CONTINUE))
        floor = stack.frames[0]
        return self._offered_as_mapped(
            self._block(stack, floor, floor.procedure.instructions[-1], order=language.END))

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
                if self._exit_due(frame):
                    # the exit checkpoint: a frame proves what it produced BEFORE it
                    # leaves -- its laws, inherited ones included, are still on screen
                    frame.procedure.instructions.append(
                        Instruction(keyword="PROVE", argument="", injected=True))
                    self._save(stack)
                    continue
                if frame.cycle is True:          # a session document replays: the rewind
                    navigation.rewind(frame)      # happens at the RESUME of the next
                    if not self._dry and self._session is not None:
                        # a mount lives ONE exchange: the rewind that opens the next
                        # one sweeps the hosted documents -- no stale law survives
                        persistence.set_mounted(self._session, [])
                    self._save(stack)             # exchange -- a fresh block follows in
                    continue                      # this same invocation, never a silence
                if frame.cycle == language.FIELD:
                    # a DESCRIBED door: the lap that closes drops the head it served --
                    # the field IS what remains due, no cursor beside it; a head left
                    # opens the next lap on a rewind that keeps the mounts
                    if frame.field:
                        frame.field.pop(0)
                    if frame.field:
                        navigation.rewind(frame)
                        self._trace("lap", document=frame.document.name)
                        self._run_exec(frame.document.path, "lap")
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
                        self._run_exec(frame.document.path, "lap")
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
                if frame.caller is None:         # the floor frame -- nothing called it
                    break
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
                # CALL resolves: the callee's last production flows out -- every
                # output is the next instruction's input, across the frame boundary
                navigation.pop(stack)
                self._save(stack)
                continue
            instruction = navigation.peek(frame)
            if instruction.guard and not self._due(instruction):
                navigation.give(instruction, "off")   # resolves without playing: 0 serve
                self._save(stack)
                continue
            if instruction.keyword == "FINAL":
                if self._exit_due(frame, at_frontier=True):
                    # the proof GATES the frontier: nothing leaves unproven -- the
                    # checkpoint slides in front of the delivery, laws on screen
                    frame.procedure.instructions.insert(
                        frame.procedure.instructions.index(instruction),
                        Instruction(keyword="PROVE", argument="", injected=True))
                    self._save(stack)
                    continue
                # the declared frontier: the exchange closes HERE -- the order block
                # comes with the very response that resolved the step before it, and its
                # delivery order empties the turn's drawer of drafts
                navigation.give(instruction, "")
                self._turns += 1
                block = self._block(stack, frame, instruction, wrong, order=language.FINAL)
                self._ephemerals = []   # delivered: a fresh turn owes a fresh drawer
                self._save(stack)
                return block
            if instruction.barrier and self._fused:
                # the `§` section break: fusion never crosses it -- the output closes
                # here and the marked step opens the next call, WHATEVER its keyword.
                # The anchor decides, never the type: the read sits ABOVE the yielding
                # guard, and above `_settled` too -- a HOOK settles by INJECTING its
                # contributors, and a step that has not opened must inject nothing.
                return self._block(stack, frame, instruction, wrong,
                                   order=language.CONTINUE)
            if instruction.keyword != "NEXT":
                # a NEXT step's OPTIONS are the successors its document declares, set at
                # its injection: the pipeline is the options source everywhere else
                instruction.taken = navigation.upstream(frame)
            settled = self._settled(frame, instruction)
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
                    return self._block(stack, frame, instruction, wrong,
                                       order=language.CONTINUE)
                self._fused += 1
                room = cap == 0 or self._fused < cap
                # a cycling frame's last step closes the LAP: with no checkpoint coming
                # to capture the output, the lap's end is the batch's end -- else the
                # rewind would batch the same lap again, without end
                lap_end = (frame.cycle and navigation.position(frame) == len(frame.procedure)
                           and not self._exit_coming(frame, instruction))
                if instruction.keyword in language.FREE and not consumed and room and not lap_end:
                    # an unchecked production with ROOM behind it: nothing for
                    # the tool to judge or capture -- resolved at render, the flow
                    # carries on in the same output (the batch)
                    drafted = self._channel(stack, frame, instruction) == "ephemeral"
                    self._stacked.append(
                        (navigation.position(frame),
                         rendering.render(self._block(stack, frame, instruction, "",
                                                      segment=True))))    # a DEVIATION never arrives on a segment: it
                    # comes with the output's closing block, REPAIR heading included
                    if drafted:
                        self._draft(frame)   # a draft stands: the FINAL owes it
                    self._trace("batched", instruction=str(instruction))
                    navigation.give(instruction, "")
                    self._save(stack)
                    continue
                instruction.asked = True    # its answer (or bare close) comes with the call
                block = self._block(stack, frame, instruction, wrong)
                closing = self._closing(frame, instruction)
                if (closing is not None and instruction.keyword in language.FREE
                        and not consumed
                        # a due checkpoint BREAKS the adjacency: the step renders
                        # alone, the proof gates the frontier on the next advance
                        and not self._exit_coming(frame, instruction)):
                    # the declared frontier sits right after this chat step: the block
                    # IS the whole story -- the FINAL resolves with it, and the turn's
                    # drawer empties (an adjacent draft joins the delivery it comes with)
                    navigation.give(instruction, "")
                    navigation.give(closing, "")
                    self._turns += 1
                    self._ephemerals = []
                self._save(stack)
                return block
            navigation.give(instruction, settled) if settled is not None else self._execute(stack, frame, instruction)
            self._save(stack)
        # the run is over: the LAST block is a block like the others -- the floor's
        # constraints are on screen at the very moment the agent decides what comes next.
        floor = stack.frames[0]
        last = floor.procedure.instructions[-1]
        return self._block(stack, floor, last, order=language.END)

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
            _, name, cut, token = entry
            path = self._stale(name)
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
            self._serve_document(path, cut, title=token, origin="serve",
                                 by=frame.document.name, nature=entry[0])
            # served now, or proven before by a section, a SERVE <doc>, a mount:
            # either way the entry is done and the next one follows
            instruction.slot += 1
        if instruction.slot >= len(plan):
            # the SERVE keeps the proofs it gave: a repair that reopens the frame
            # hands them back, so the reading re-serves
            navigation.give(instruction, [self._reading(path, cut)[1]
                                          for kind, *rest in plan if kind == "doc"
                                          for name, cut, _token in (rest,)
                                          if (path := self._stale(name)) is not None])

    def _run_hook(self, stack: Stack, frame: Frame, instruction: Instruction) -> None:
        """A HOOK is a named socket, and its contributors reach it by one of TWO verbs of
        their own front matter: `attach: <name>` is CALLed there, `mount: <name>` is
        MOUNTED there -- it enters the view, laws and matter, and asks the agent nothing.
        Both verbs make ONE list, ordered together: the requires topology of their homes
        and, within one, the name -- then the ORDER PREFERENCES each contributor declares
        for this socket (`order:` in its front matter, `instance.ordering`). A contributor
        carries its own guard (`when: @Doc.field` in its front matter): a called one hands
        it to the injected CALL, a mounted one is judged by the same predicate before it
        enters -- the socket knows neither key. Nothing declared = a strict no-op."""
        from ..packaging import contributions
        # what the proc WRITES is `<proc>.<hook>`; what contributors address is the socket's
        # ADDRESS -- the package that opens it qualifies what it wrote
        socket = contributions.address(contributions.owner_of(frame.document.path),
                                       instruction.argument)
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
                                         guard=guard, socket=True))
        for name in due:
            offset += 1
            frame.procedure.instructions.insert(
                at + offset, Instruction(keyword="CALL", argument=name, injected=True,
                                         socket=True))
        self._mount_socket(frame, mounting)
        navigation.give(instruction, contributors + due)

    def _cadences_due(self, socket: str) -> list[str]:
        """-> the documents the CADENCES declared at `socket` play NOW -- each one
        due by the crossing predicate (its anchored day crossed its record, its
        `since` record moved), after the socket's contributors. A `play` that
        resolves to no document is said to the trace and skipped: a cadence never
        breaks the boot."""
        from ..packaging import contributions
        from ..state import cadences
        found = []
        for one in contributions.composed(self.member.meta):
            if one["kind"] != "cadences" or str(one.get("at", "")) != socket:
                continue
            if not cadences.crossing_due(self.member.meta, str(one.get("anchor", "")),
                                         str(one.get("record", "")), one.get("since")):
                continue
            play = str(one["play"])
            if not self._resolve(play).is_file():
                self._trace("cadence-unplayable", cadence=str(one.get("name")), play=play)
                continue
            found.append(play)
        return found

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

    def _declared_payloads(self, document: Document) -> None:
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
        delivered is spared by its content -- a changed rendering enters whole."""
        from ..packaging import contributions
        import hashlib
        import time
        tokens = str(document.front.get("payloads", "")).split()
        for token in tokens:
            known = self._resolved.get(token)
            if known is not None:
                for one in known:
                    self.note(token, "", "spared", "payload", by=document.name,
                              with_=one["with"], package=one["package"], spared=one["chars"])
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
                elif out.strip():
                    text = out.strip()
                    digest = hashlib.sha256(text.encode()).hexdigest()[:12]
                    tag = f"payload:{self._turns}:{token}:{said}:{digest}"
                    if tag in self._proven:
                        self.note(token, "", "spared", "payload", by=document.name,
                                  with_=said, package=package, spared=len(text))
                    else:
                        self.note(token, text, "served", "payload", by=document.name,
                                  with_=said, package=package)
                        self._payloads.append((token, text))
                        self._prove_payload(tag)
                else:
                    continue
                rendered.append({"with": said, "package": package, "chars": len(text)})
            self._resolved[token] = rendered

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
        self._declared_payloads(document)
        self.note(self._cycle_title(document), element, "served", "cycle", by=document.name)
        self._payloads.append((self._cycle_title(document), element))

    def _cycle_title(self, document: Document) -> str:
        """-> the title an iterated door's element is served under: its token for a
        provided door, `field` for a described one -- the word of the key, as `proof`
        is the checkpoint's."""
        token = self._cycle_token(document)
        return token if token else "field"

    def _field_brief(self, document: Document) -> str:
        """-> the described door's prose, its `@Doc.field` references resolved as an
        exec's arguments are (`_field_value`); an empty value refuses
        `field-argument-empty` -- a brief that names nothing describes nothing."""
        prose = reading.fields(document)

        def resolve(match: re.Match) -> str:
            stem, field = match.group(1), match.group(2)
            value = self._field_value(stem, field)
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
            value = self._field_value(stem, field)
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
        reopening purges it; the `socket` mark carried, so a contributor's successor
        owes no exit checkpoint of its own; no guard, judged at the first entry."""
        caller = stack.frames[-2]
        at = caller.procedure.instructions.index(frame.caller)
        caller.procedure.instructions.insert(
            at + 1, Instruction(keyword="CALL", argument=successor, injected=True,
                                socket=frame.caller.socket))

    def _open_field(self, stack: Stack, frame: Frame, elements: list) -> None:
        """The field RENDERED and accepted: the frame holds what remains due and the door
        opens on its head -- the first lap, its element under `field`. An empty array is
        nothing due: no lap opens, the line under `field` says it, and the door leaves
        like any callee -- the run completes when it is the floor."""
        frame.field = [str(one) for one in elements]
        if frame.field:
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
            navigation.pop(stack)
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
        value = self._field_value(match.group(1), match.group(2))
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
        if instruction.slot == 0:
            # the entry: what the document declares under `exec:` plays first, before
            # its body and before anything the frame serves
            self._run_exec(path, "call")
            # `proc_body_serve: always` forces the body back at every CALL; `once`
            # leaves the common rule to play -- a body proven in the run comes with no more
            self._serve_document(path, (), force=self._settings.body_serve == "always",
                                 origin="body", by=frame.document.name)
            # the readings its overlays ADD come with the body, at the entry -- the
            # base's own sections keep their SERVE pace
            self._serve_overlay_rows(document)
            instruction.slot = 1
            return
        if token:
            # the first lap opens: the element under its token, after the declared payloads
            self._trace("lap", document=document.name)
            self._lap_payloads(document, element)
        else:
            self._declared_payloads(document)
        laws, tools = compiling.effective(self.member.meta, document)
        seed = navigation.upstream(frame) if str(document.front.get("input", "")).strip() else None
        snapshot = (tuple(Constraint.parse(line) for line in instruction.routed)
                    if instruction.routed else None)   # a routed door inherits the
        # owning segment's snapshotted laws, never the pending frame's chain
        offered = {one.name for one in frame.tools}   # a name is offered ONCE at a step:
        callee = Frame(document=document, procedure=reading.playable(document),   # the callee
                       constraints=(snapshot if snapshot is not None
                                    else frame.constraints) + laws,   # re-declaring an
                       tools=frame.tools + tuple(one for one in tools  # inherited tool
                                                 if one.name not in offered),   # adds nothing
                       caller=instruction, cycle=reading.cycles(document), seed=seed,
                       routed=snapshot)
        navigation.push(stack, callee)

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
        deviation.register(anchor, self._settings.repairs_allowed)
        # the reopened frame re-serves NOTHING: a reading proven in the run stays
        # proven across the repair -- the agent re-reads its own context, never a
        # second copy (operator word 2026-09-05; measured at 33 % of a campaign)
        navigation.reopen(frame)
        self._save(stack)
        return self._advance(stack, wrong)
