"""execution.blocks -- the assembly of a block: what it carries, its closing, its next call -- the process; the text is rendering's. A mixin of the facade: no state of its own."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from ..packaging import compiling, contributions
from .. import reading
from ..core import deviation, language, navigation
from ..state import instance, metrics
from .. import rendering
from ..core.errors import Refusal
from ..core.model import Block, Frame, Instruction, Stack


def clock() -> datetime:
    """The engine's clock, aware -- the bench replaces it to render a known hour."""
    return datetime.now(timezone.utc)


class Assembling:
    """The assembly of a block: what it carries, its closing, its next call -- the process; the text is rendering's -- a mixin of the facade."""

    def _closing(self, frame: Frame, instruction: Instruction) -> Instruction | None:
        """-> the FINAL adjacent AFTER `instruction`, when the proc declares one there --
        the frontier an INFER's own block carries (the fused closing: 0 extra call)."""
        at = frame.procedure.instructions.index(instruction)
        following = frame.procedure.instructions[at + 1:at + 2]
        if following and following[0].keyword == "FINAL":
            return following[0]
        return None

    def _channel(self, stack: Stack, frame: Frame, instruction: Instruction) -> str:
        """-> where this yield's production goes -- DERIVED, never declared: a
        consumed production travels by its format's mode (tool, tool (heredoc));
        a PICK comes with the command (tool); a PROVE pipes its proof (heredoc). An
        unconsumed production is a DRAFT before the turn's frontier (ephemeral --
        the FINAL delivers it), except the one adjacent TO the frontier while no
        draft stands, and any production of a run with no frontier ahead: those
        speak chat, directly."""
        if instruction.keyword in ("PROVE", "FIELD"):
            return "tool (heredoc)"
        if instruction.keyword not in language.FREE:
            return "tool"
        consumed, _ = self._consumer(stack, frame, instruction)
        if consumed:
            mode = compiling.format_enumeration(self.member.meta).get(
                self._output_of(frame), ("stdin",))[0]
            return "tool" if mode == "inline" else "tool (heredoc)"
        if not self._frontier_ahead(stack):
            return "chat"
        if self._closing(frame, instruction) is not None and not self._ephemerals:
            return "chat"
        return "ephemeral"

    def _frontier_ahead(self, stack: Stack) -> bool:
        """-> whether a FINAL still stands between here and the run's end: in the
        remaining DECLARED flow of any frame in flight -- CALLs resolved statically
        (their callees' declared flows too, the parse is memoized), a cycling frame
        scanned whole: its rewind will replay it."""
        seen: set[Path] = set()

        def carried(name: str) -> bool:
            path = instance.resolve(self.member.meta, name)
            if path in seen or not path.is_file():
                return False
            seen.add(path)
            return holds_final(reading.playable(reading.read(path)).instructions)

        def holds_final(steps) -> bool:
            for one in steps:
                if one.keyword == "FINAL":
                    return True
                if one.keyword == "CALL" and carried(one.argument):
                    return True
                if one.keyword == "HOOK" and any(
                        carried(name) for name in
                        instance.attached(self.member.meta, one.argument)):
                    return True
            return False

        for frame in stack.frames:
            steps = frame.procedure.instructions
            start = 0 if frame.cycle else navigation.pointer(frame)
            if holds_final(steps[start:]):
                return True
        return False

    def _assemble(self, closing: int | None, numbered: bool = False) -> tuple[str, ...]:
        """-> the batched segments, each stretch opener's heading widened to its
        range `{i-j/m}` when the B-merge ran past it -- only the assembler knows,
        at the closing, how far a stretch went. `closing` is the closing block's
        own step when that block extends the LAST stretch (heading elided).
        `numbered`: a MULTI-heading output numbers its headings `[n]` -- the
        address a `-s` call routes by."""
        # a stacked segment whose text OPENS on the mark carries its own heading; a
        # merged one opens on the blank line of its first section, or on its step
        opener = f"{Block.MARK} "
        out = [text for _, text in self._stacked]
        ends: dict[int, int] = {}       # opener index -> last position of its stretch
        at = None
        for k, (pos, text) in enumerate(self._stacked):
            if text.startswith(opener):
                at = k
            if at is not None:
                ends[at] = pos
        if closing is not None and at is not None:
            ends[at] = closing
        for k, j in ends.items():
            i = self._stacked[k][0]
            if j > i:
                heading, sep, rest = out[k].partition("\n")
                spot = heading.find(f"{{{i}/")
                close = heading.find("}", spot)
                total = heading[spot + len(f"{{{i}/"):close]
                # an injected checkpoint may have grown the frame SINCE the opener
                # rendered: the range's total follows, never trails
                grown = max(int(total), j) if total.isdigit() else total
                out[k] = heading[:spot] + f"{{{i}-{j}/{grown}}}" + heading[close + 1:] + sep + rest
        if numbered:
            seen = 0
            for k, text in enumerate(out):
                if text.startswith(opener):
                    seen += 1
                    out[k] = f"{opener}[{seen}] " + text[len(opener):]
        return tuple(out)

    def _block(self, stack: Stack, frame: Frame, instruction: Instruction,
               wrong: str = "", order: str = "", segment: bool = False,
               at: int | None = None) -> Block:
        """-> the block, assembled with the output's stacked segments and written to the
        offer map. `at` names the step position the heading stands for when a block
        RE-SHOWS an earlier step of the frame (a mount, a view after a `§`): the map
        keeps that position, so the next view finds the same ask."""
        if not order and language.needs_options(instruction.keyword):
            if not isinstance(instruction.taken, list) or not instruction.taken:
                raise Refusal("options-empty", f"`{instruction}` has nothing to choose from")
            # the guard of what no capture judged -- a list arrived by a callee's seed,
            # a slot written before the form was judged: refused by name, the element
            # said, never handed to the renderer
            wrong_form = language.scalars_form(instruction.taken, "OPTIONS", empty_ok=False)
            if wrong_form:
                raise Refusal("options-invalid", f"`{instruction}` -- {wrong_form}")
        output = language.output_of(instruction.keyword)
        if instruction.keyword in language.FREE:
            output = str(frame.document.front.get("output", output)).strip() or output
        if not order and language.yields(instruction.keyword):
            if output not in compiling.format_enumeration(self.member.meta):
                raise Refusal("format-unknown",
                              f"`output: {output}` ({frame.document.name}) -- not in "
                              "the enumeration; declare it in a `formats:` first")
        next_call, wait = (("", False) if segment
                           else self._next_call(stack, frame, instruction, order))
        merged = (self._seg_frame is frame and bool(self._stacked or segment))
        repair = (max((one.repairs for one in frame.procedure.instructions), default=0)
                  if wrong else 0)
        # a closing STEP whose heading is elided (merged, no REPAIR) extends the
        # last stretch: its position closes the range; an order block never does
        extends = merged and not order and not repair and not segment
        if instruction.keyword == "FIELD" and not order:
            # the described door's brief: the prose, served under `field` and promoted
            # as the step's own context -- resolved at every render, a `-peek` shows it
            brief = self._field_brief(frame.document)
            self.note("field", brief, "served", "cycle", by=frame.document.name)
            self._payloads.append(("field", brief))
        if instruction.keyword == "NEXT" and not order:
            # the leaving document's brief: the `choose:` prose, served under `next`
            # and promoted as the step's own context -- resolved at every render
            brief = self._next_brief(frame.document)
            self.note("next", brief, "served", "next", by=frame.document.name)
            self._payloads.append(("next", brief))
        payloads = self._own_last(frame)
        # the closing dresses for what it carries: an order block owes no step --
        # with a reading aboard it keeps its heading alone (the laws arm on the
        # output that carries the ask); with only segments behind, the signal and
        # its command ARE the block; alone, or repairing, it keeps its habit
        plain = bool(order) and not wrong and bool(payloads or self._stacked)
        bare = plain and not payloads
        merged = merged or bare
        opener = f"{Block.MARK} "
        own_heading = (not merged) or bool(repair)
        seg_heads = sum(1 for _, text in self._stacked if text.startswith(opener))
        numbered = not segment and (seg_heads + (1 if own_heading else 0)) >= 2
        if not self._output_clock:
            # the hour belongs to the OUTPUT: read once, at its first block, and carried
            # to the block that writes the output's heading
            self._output_clock = self._clock_mark()
        first_output = getattr(self, "_first_output", False)
        if first_output and not segment:
            self._first_output = False
        stacked = () if segment else self._assemble(
            navigation.position(frame) if extends else None, numbered)
        if not segment:
            self._stacked = []
        if own_heading and not self._dry:
            # the output's OFFER MAP grows one entry per heading: the scope kept
            # per segment, addressable once the segment's frame moves on -- what
            # `route()` consults, one list at a time, never their union
            self._segmap.append({
                "ordinal": len(self._segmap) + 1,
                "frame": frame.document.name,
                "stack": navigation.render(stack),
                "at": navigation.position(frame) if at is None else at,
                "tools": [one.name for one in self._tools_in_force(frame)],
                "constraints": [one.wire() for one in self._in_force(frame)]})
        ordinal = len(self._segmap) if (numbered and own_heading) else 0
        routed_note, self._route_note = self._route_note, ""
        foresee = ""
        if wait:
            anchor = (instruction if instruction.keyword == "FINAL"
                      else self._closing(frame, instruction))
            if anchor is not None and self._owes_proof(frame, anchor):
                foresee = "the turn closes on its proof"
            elif (anchor is not None and self._armed(frame)
                  and not self._production_in_force(frame)):
                foresee = "no law of production in force: no proof owed"
        # documentary: a law's text renders ONCE -- per OUTPUT under verbatim, per RUN
        # under codes mode -- and every later emission is its code; the LEDGER, never
        # the setting, decides what the reader sees twice
        coded = tuple(one.code for one in self._in_force(frame)
                      if one.code in self._emitted or one.code in self._emitted_run)
        self._emitted.update(one.code for one in self._in_force(frame))
        if not self._settings.verbatim_constraints:
            self._emitted_run.update(one.code for one in self._in_force(frame))
        self._seg_frame = frame
        channel = ("" if order or not language.yields(instruction.keyword)
                   else self._channel(stack, frame, instruction))
        drafts = tuple(self._ephemerals) if wait else ()
        if wait and channel == "ephemeral" and (not drafts or drafts[-1] != frame.document.name):
            # the step the frontier resolves with is a draft too: its document closes the list
            drafts += (frame.document.name,)
        block = Block(
            document=frame.document.name,
            instruction=instruction,
            command=("" if order in (language.CONTINUE, language.FINAL, language.END)
                     else (order or ("INFER" if instruction.keyword in ("PROVE", "FIELD")
                                     else "PICK next" if instruction.keyword == "NEXT"
                                     else str(instruction).strip()))),
            position=navigation.position(frame),
            total=len(frame.procedure),
            options=() if order else tuple(instruction.options),
            constraints=() if plain else self._in_force(frame),
            tools=() if plain else self._tools_in_force(frame),
            payloads=payloads,
            output="" if order else output,
            channel=channel,
            next_call=next_call,
            stack=navigation.render(stack),
            deviation=wrong,
            repair=repair,
            wait=wait,
            stacked=stacked,
            merged=merged,
            coded=coded,
            foresee=foresee,
            drafts=drafts,
            ordinal=ordinal,
            judged=(tuple(one.code for one in self._in_force(frame)
                          if one.section == "production")
                    if instruction.keyword == "PROVE" else ()),
            switches=self._switch_state(),
            clock=self._output_clock,
            fusion=first_output and self._settings.fusion != 1,
            segment=segment,
            run_key=self._say_key(),
            routed=routed_note,
            verbatim_constraints=self._settings.verbatim_constraints,
            context=("" if order else "field" if instruction.keyword == "FIELD"
                     else "next" if instruction.keyword == "NEXT"
                     else reading.title(frame.document.path)),
            end=language.END_TEXT if order == language.END else "",
        )
        weighed = metrics.weigh(block, rendering.render(block))
        self._served = metrics.accumulate(self._served, weighed)
        self._save(stack)
        # the weight rides the trace line: what this block cost, part by part -- the
        # reader (state/traces.py) sums it per exchange, the engine never reads it back
        served_parts: dict[str, list[int]] = {}
        for subject, text_ in block.payloads:     # the itemization the measure needs:
            chars, approx = len(text_), metrics.tokens(text_)   # each payload SUBJECT
            held_ = served_parts.setdefault(subject, [0, 0])    # with its own mass --
            held_[0] += chars; held_[1] += approx  # two providers of one token add up
        ledger, self._ledger = self._own_last_ledger(frame), []
        self._trace("block", stack=block.stack, command=block.command, wait=block.wait,
                    weight={part: weighed[part] for part in (*metrics.PARTS, "total", "tokens")},
                    **({"payloads": served_parts} if served_parts else {}),
                    **({"served": ledger} if ledger else {}),
                    **({"deviation": wrong} if wrong else {}))
        return block

    def _own_last_ledger(self, frame: Frame) -> list:
        """-> the LEDGER in the order the block carries: the current frame's own document
        moves last, exactly as its payloads do (`_own_last`), so the journal reads as the
        block reads -- and a subject served twice keeps its two lines."""
        own = reading.title(frame.document.path)
        return ([one for one in self._ledger if one.get("subject") != own]
                + [one for one in self._ledger if one.get("subject") == own])

    def _switch_state(self) -> tuple:
        """-> one (package, state) pair per pin beyond the base, in the REQUIRES topology
        -- dependencies first, so a cause is read before what it took out. The state is
        empty where the package plays, its own name where a switch took it out, the
        dependency's name where its requirement did: the line the output's heading
        carries, read from the ONE place the switches live."""
        meta = self.member.meta
        base = instance.base_of(meta)
        try:
            beyond = [root.name.split("@")[0]
                      for root in instance.vendored(meta, switched=False)]
            off = instance.switched_off(meta)
        except Refusal:
            return ()        # an instance that does not read: the block says nothing of it
        return tuple((name, off.get(name, "")) for name in beyond if name != base)

    def _clock_mark(self) -> str:
        """-> `HH:MM:SS · +H:MM:SS`: the local time of this output and the time elapsed
        since the run opened (its trace is stamped at -new) -- the agent's only notion
        of the hour along a session. Said once per output, on its first heading."""
        now = clock()
        mark = now.astimezone().strftime("%H:%M:%S")
        opened = _opened_at(self._log or "")
        if opened is None:
            return mark
        seconds = max(0, int((now - opened).total_seconds()))
        return f"{mark} · +{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"

    def _say_key(self) -> str:
        """-> the run's key, said on EVERY output's heading: the closing sits outside a
        harness preview, the heading inside -- whatever output the agent is looking at,
        the key it must copy is under its eyes, without opening the persisted file."""
        return self._run_id or ""

    def _own_last(self, frame: Frame) -> tuple[tuple[str, str], ...]:
        """-> what was served, the CURRENT frame's own document moved last -- the material
        an INFER's order draws from sits closest to it, not buried under earlier reading."""
        own = reading.title(frame.document.path)
        served = self.drain()
        return tuple([p for p in served if p[0] != own] + [p for p in served if p[0] == own])

    def _next_call(self, stack: Stack, frame: Frame, instruction: Instruction,
                   order: str) -> tuple[str, bool]:
        command = self.member.command()
        if self._run_id:
            # the conversation's key comes with EVERY command pp hands out, first --
            # the agent copies verbatim, and only ever talks to its own run
            command = f"{command} {self._run_id}"
        if order == language.END:
            return "", False
        if order == language.FINAL:
            if self._settings.capture_prompt:
                # the capture comes with the after-FINAL resume -- the one call that
                # carries the operator's message; fusion is none of its business
                return f"{command} <the operator's next message>", True
            return command, True
        if order:      # CONTINUE -- the keyed call is enough to keep receiving the reading
            return command, False
        if instruction.keyword == "PROVE":
            # the INSTRUCTION line names the laws the proof may judge; the hint keeps
            # what is its own -- the way back, on its OWN line: the command is copied
            # verbatim, a hint beside it was copied with it (le-hint-a-part)
            return f"{command} -\n   (your proof on stdin -- heredoc)", False
        if instruction.keyword == "FIELD":
            # the described door's step: the field on stdin, a JSON array -- the brief
            # above says what the array holds, the form says its shape
            return f"{command} -\n   (your field on stdin -- heredoc: a JSON array)", False
        if instruction.keyword not in language.FREE:
            return f"{command} <your-choice>", False
        consumed, _ = self._consumer(stack, frame, instruction)
        if consumed:
            name = self._output_of(frame)
            mode = compiling.format_enumeration(self.member.meta).get(name, ("stdin",))[0]
            if mode == "inline":
                return f"{command} <output>", False
            return f"{command} -   (your <output> on stdin -- heredoc)", False
        if self._closing(frame, instruction) is not None:
            # the fused frontier: the FINAL resolves with this block -- the call is
            # owed only once the operator replies (and carries their message when
            # the capture is on)
            if self._settings.capture_prompt:
                return f"{command} <the operator's next message>", True
            return command, True
        return command, False  # pp never needs the agent's own output back -- it


def _opened_at(log_name: str) -> datetime | None:
    """-> when the run opened, read from its trace's name (`session-<UTC>.jsonl`, stamped
    at -new); None when no run stands."""
    raw = log_name[len("session-"):].split(".")[0].rstrip("Z") if log_name.startswith("session-") else ""
    try:
        return datetime.strptime(raw[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
