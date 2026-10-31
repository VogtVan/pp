"""execution.blocks -- the assembly of a block: what it carries, its closing, its next call -- the process; the text is rendering's. A mixin of the facade: no state of its own."""
from __future__ import annotations

from datetime import datetime, timezone
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

    def _closing(self, stack: Stack, frame: Frame, instruction: Instruction) -> bool:
        """-> whether `instruction` is the LAST step of the root of the passage: its own
        block then carries the end of the passage (the fused closing: 0 extra call) -- the
        step done, the run parks."""
        return (frame.procedure.instructions[-1] is instruction
                and self._completes(stack, frame))

    def _channel(self, stack: Stack, frame: Frame, instruction: Instruction) -> str:
        """-> where this yield's production goes -- DERIVED, never declared: a proof, a
        field, a choice and a consumed production go to the tool, by the call the closing
        shows; an unconsumed production is said to the principal at its own step, in the
        agent's words, whatever stands ahead: the end of the passage delivers nothing."""
        if instruction.keyword not in language.FREE:
            return language.TOOL
        consumed, _ = self._consumer(stack, frame, instruction)
        return language.TOOL if consumed else language.WORDS

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
        out = [text for _, text, *_ in self._stacked]
        ends: dict[int, int] = {}       # opener index -> last position of its stretch
        at = None
        for k, (pos, text, *_) in enumerate(self._stacked):
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
               at: int | None = None, repairing: bool = False) -> Block:
        """-> the block, assembled with the output's stacked segments and written to the
        offer map. `at` names the step position the heading stands for when a block
        RE-SHOWS an earlier step of the frame (a mount, a view after a `§`): the map
        keeps that position, so the next view finds the same ask. `repairing` says a
        segment belongs to an output a repair opened: its own heading says `REPAIR n`."""
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
            output = instance.declared(self.member.meta, frame.document.path, "output") or output
            if self._elects(stack, frame, instruction):
                output = language.LIST
        if not order and language.yields(instruction.keyword):
            if output not in compiling.format_enumeration(self.member.meta):
                raise Refusal("format-unknown",
                              f"`output: {output}` ({frame.document.name}) -- not in "
                              "the enumeration; declare it in a `formats:` first")
        channel = self._receiving()
        awaited, form = self._awaited(stack, frame, instruction, order, channel)
        wait = awaited == language.MESSAGE_DUE
        label, next_call, fact = (("", "", "") if segment
                                  else self.closing(awaited, channel,
                                                    template=self._template(self._command(), form) if form else "",
                                                    message=self._message_call()))
        merged = (self._seg_frame is frame and bool(self._stacked or segment))
        repair = (max((one.repairs for one in frame.procedure.instructions), default=0)
                  if wrong or (repairing and not merged) else 0)
        # a closing STEP whose heading is elided (merged, no REPAIR) extends the
        # last stretch: its position closes the range; an order block never does
        extends = merged and not order and not repair and not segment
        if instruction.keyword == "FIELD" and not order:
            # the described door's brief: the prose, served under `field` and promoted
            # as the step's own context -- resolved at every render, a view carries it
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
        if not order and instruction.keyword == "WORK" and frame is self._root(stack):
            # the WORK of the ROOT of the passage: its context is the principal's last
            # message -- said as a fixed section at every passage, never the message
            self.note(language.ASK, language.ASK_TEXT, "served", "ask", by=frame.document.name)
            payloads = payloads + ((language.ASK, language.ASK_TEXT),)
        # the closing dresses for what it carries: an order block owes no step --
        # with a reading aboard it keeps its heading alone (the laws arm on the
        # output that carries the ask); with only segments behind, the signal and
        # its command ARE the block; alone, or repairing, it keeps its habit. Behind a
        # segment whose frame has left the stack, the closing names the frame that
        # stands, its laws and its offers: the last heading read is where the run is
        plain = bool(order) and not wrong and bool(payloads or self._stacked)
        moved = (plain and bool(self._stacked) and self._seg_frame is not None
                 and not any(one is self._seg_frame for one in stack.frames))
        bare = plain and not payloads and not moved
        merged = merged or bare
        opener = f"{Block.MARK} "
        own_heading = (not merged) or bool(repair)
        seg_heads = sum(1 for _, text, *_ in self._stacked if text.startswith(opener))
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
        # the engine's own diagnostics due: formed at the signal, rendered by THIS block
        # and marked rendered on its trace line -- a segment takes them, the next finds none
        due = self._due_diagnostics()
        block = Block(
            document=frame.document.name,
            instruction=instruction,
            command=("" if order in (language.CONTINUE, language.AWAIT)
                     else (order or ("INFER" if instruction.keyword in ("PROVE", "FIELD")
                                     else "PICK next" if instruction.keyword == "NEXT"
                                     else str(instruction).strip()))),
            position=navigation.position(frame),
            total=len(frame.procedure),
            options=() if order else tuple(instruction.options),
            constraints=() if plain and not moved else self._in_force(frame),
            tools=() if plain and not moved else self._tools_in_force(frame),
            payloads=payloads,
            output="" if order else output,
            channel=channel,
            next_call=next_call,
            label=label,
            fact=fact,
            stack=navigation.render(stack),
            root=self._root(stack).document.name if stack.frames else "",
            deviation=wrong,
            diagnostics=tuple(text for _, text in due),
            repair=repair,
            wait=wait,
            stacked=stacked,
            merged=merged,
            coded=coded,
            gaps=self._closing_gaps(not segment),
            idle=self._closing_idle(not segment),
            ordinal=ordinal,
            judged=(tuple(one.code for one in self._in_force(frame)
                          if one.section == "production")
                    if instruction.keyword == "PROVE" and order != language.AWAIT else ()),
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
        self._trace("block", stack=block.stack, root=block.root, command=block.command, wait=block.wait,
                    weight={part: weighed[part] for part in (*metrics.PARTS, "total", "tokens")},
                    **({"payloads": served_parts} if served_parts else {}),
                    **({"served": ledger} if ledger else {}),
                    **({"deviation": wrong} if wrong else {}),
                    **({"diagnostics": [key for key, _ in due]} if due else {}))
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

    def _closing_idle(self, closes: bool) -> tuple:
        """-> the lines of the written PROVEs this call resolved with nothing to ask, taken
        by the block that CLOSES the output -- said once, under that closing."""
        if not closes or not getattr(self, "_idle", None):
            return ()
        taken, self._idle = tuple(self._idle), []
        return taken

    def _closing_gaps(self, closes: bool) -> tuple:
        """-> the gaps this call's proof declared, taken by the block that CLOSES the
        output (the one carrying the closing) -- said once, under that closing."""
        if not closes or not self._gaps:
            return ()
        taken, self._gaps = tuple(self._gaps), []
        return taken

    def _command(self) -> str:
        """-> the keyed call of this run: the conversation's key comes with EVERY command pp hands
        out, first -- the agent copies verbatim, and only ever talks to its own run."""
        command = self.member.command()
        return f"{command} {self._run_id}" if self._run_id else command

    def _message_call(self) -> str:
        """-> the call that carries the principal's message at a parked run: the bare keyed call,
        or, under the base's convenience key `capture_prompt` (read by name as a `@SETTINGS.<key>`
        guard would), the call that asks for the message itself -- the message reaches the run
        either way, the key only shapes the closing."""
        if self._settings.of_package("capture_prompt", False):
            return f"{self._command()} <the principal's next message>"
        return self._command()

    def _awaited(self, stack: Stack, frame: Frame, instruction: Instruction,
                 order: str, channel: str) -> tuple[str, str]:
        """-> (what the stack AWAITS after this block, the FORM due when a value is): a message at an
        AWAIT order and at the fused end of the passage -- by the tool alone: at the prompt the last
        free step of the root stays PENDING, never fused with the end (`stepping`), so a response is
        awaited there; a response at a CONTINUE order and at a free step nothing consumes; a value --
        its form -- at a checkpoint, a field, a choice and a production a consumer takes."""
        if order == language.AWAIT:
            return language.MESSAGE_DUE, ""
        if order:
            return language.RESPONSE_DUE, ""
        if instruction.keyword in ("PROVE", "FIELD"):
            # the INSTRUCTION line names the laws the proof may judge; the closing shows the
            # call to type, the form due standing where the production goes
            return language.VALUE_DUE, language.output_of(instruction.keyword)
        if instruction.keyword not in language.FREE:
            return language.VALUE_DUE, "options"
        consumed, _ = self._consumer(stack, frame, instruction)
        if consumed:
            return language.VALUE_DUE, self._form_of(stack, frame, instruction)
        if channel == language.TOOL and self._closing(stack, frame, instruction):
            # the fused end of the passage: the run parks with this block
            return language.MESSAGE_DUE, ""
        return language.RESPONSE_DUE, ""

    def closing(self, awaited: str, channel: str, template: str = "", message: str = "",
                left: int = 0, more: int = 0) -> tuple[str, str, str]:
        """-> (label, call, fact): the FOOT of an output, deduced from what the stack AWAITS after
        it (`language.AWAITED`) and the CHANNEL the output reaches the agent by (`language.TOOL`,
        the result of its own call; `language.PROMPT`, the prompt of a launch) -- the one site of
        the engine that decides a closing; the mode of conduction chooses the channel
        (`_receiving`), never the foot.
        - a value due: `CONTINUE` and the call's `template`, on both channels;
        - a response due (a free step the agent says, then the run moves on): `CONTINUE` and the
          bare call by the tool; nothing at the prompt -- the step ends when the agent decides;
        - a message due (the root exhausted): `AWAIT` and the call that carries the `message` by
          the tool; nothing at the prompt;
        - a reading that continues (a chunk before the last): `CONTINUE` and the bare call by the
          tool, `MORE` and no call at the prompt; the fact says what remains -- `left` characters
          in `more` chunk(s) -- on both channels.
        A label empty says the output owes no closing; a fact empty says none."""
        if awaited == language.VALUE_DUE:
            return language.CONTINUE, template, ""
        if awaited == language.READING_ON:
            fact = f"a reading continues: {left} characters in {more} more chunk(s)"
            if channel == language.PROMPT:
                return language.MORE, "", fact
            return language.CONTINUE, self._command(), fact
        if channel == language.PROMPT:
            return "", "", ""
        if awaited == language.MESSAGE_DUE:
            return language.AWAIT, message or self._command(), ""
        return language.CONTINUE, self._command(), ""

    def _template(self, command: str, form: str) -> str:
        """-> the call the closing shows for a production of `form`: on the call for an
        inline form -- `options` one token, any other quoted --, piped by a heredoc
        otherwise; the form's name stands where the production goes."""
        mode = compiling.format_enumeration(self.member.meta).get(form, ("stdin",))[0]
        if mode == "inline":
            return f"{command} <{form}>" if form == "options" else f'{command} "<{form}>"'
        return f"{command} - <<'EOF'\n<{form}>\nEOF"


def _opened_at(log_name: str) -> datetime | None:
    """-> when the run opened, read from its trace's name (`session-<UTC>.jsonl`, stamped
    at -new); None when no run stands."""
    raw = log_name[len("session-"):].split(".")[0].rstrip("Z") if log_name.startswith("session-") else ""
    try:
        return datetime.strptime(raw[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
