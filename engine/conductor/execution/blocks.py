"""execution.blocks -- the assembly of a block: what it carries, its closing, its next call -- the process; the text is rendering's. A mixin of the facade: no state of its own."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from ..packaging import compiling, contributions
from .. import reading
from ..core import language, messages, navigation
from ..state import instance, metrics, persistence
from .. import rendering
from ..core.errors import Refusal
from ..core.model import Block, Frame, Instruction, Segment, Stack


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

    def _handed(self, stack: Stack, frame: Frame, instruction: Instruction) -> str:
        """-> the FORM of the value this yield hands to pp, "" when it hands none: the proof of a
        checkpoint, the field of a described door, the options of a choice, the form a consumer
        takes -- an unconsumed production is no value."""
        if instruction.keyword in ("PROVE", "FIELD"):
            return language.output_of(instruction.keyword)
        if instruction.keyword not in language.FREE:
            return "options"
        consumed, _ = self._consumer(stack, frame, instruction)
        return self._form_of(stack, frame, instruction) if consumed else ""

    def _channel(self, stack: Stack, frame: Frame, instruction: Instruction) -> str:
        """-> where this yield's production goes -- DERIVED, never declared: a value is handed to
        pp, on the call or piped by a heredoc as the MODE of its form says (`language.handed`), the
        one site that reads a form's mode for a channel; an unconsumed production is said to the
        principal at its own step, whatever stands ahead: the end of the passage delivers nothing.
        Never `response`: the last message of an output is decided where the output closes
        (`responding`)."""
        form = self._handed(stack, frame, instruction)
        if not form:
            return language.TERMINAL
        return language.handed(compiling.format_enumeration(self.member.meta).get(form, ("stdin",))[0])

    def responding(self, arrival: str, awaited: str, channel: str, said_last: bool) -> str:
        """-> how the output a block CLOSES asks its LAST message (`language.STEP`, `language.ADDED`,
        "" for none) -- the ONE site that decides the channel `response`. An output asks its last
        message when it reaches the agent by the prompt, or by the tool on a message due (the end
        of the passage); every other output -- a step the bare call follows, a value due in a tool
        result -- asks none, and its lines keep their channel. `channel` is the closing block's own
        step's ("" when it renders no step), `said_last` whether the last segment stacked is a said
        step still at hand:
        - its last step SAYS a production: that step goes `=> response` (`STEP`);
        - its last step hands a VALUE to pp: the line of the form `empty` is ADDED behind it;
        - it renders no step at all: by the tool (the bare AWAIT) the line is ADDED; at the prompt
          nothing -- a root at its end asks nothing, and a line there would ask for a message."""
        return ""   # trial of the principal (2026-11-21): no step goes `=> response`, no `empty` line is added

    @staticmethod
    def _print_of(block: Block) -> dict:
        """-> the entry of a step said on `terminal`: what its print call answers, and the line
        a later output says again while it is due."""
        return {"document": block.document, "keyword": block.instruction.keyword, "form": block.output,
                "instruction": str(block.instruction), "line": rendering.line_of(block),
                "stack": block.stack, "refused": 0}

    def _pose(self, closing: Block, due: list, order: bool, shown: str) -> None:
        """The output closes: every step it said on `terminal` is DUE from here to its print call --
        the steps stacked, then the closing block's own when it says one, once per step (`shown`
        says where that step stands: a gesture that shows a step again poses nothing). The trace
        says `print-due` for each; a view poses nothing."""
        said, self._owing = list(self._owing), []
        if self._dry or self._session is None:
            return
        fresh = [self._print_of(one) for one in said]
        if (not order and closing.instruction.keyword in language.FREE
                and closing.channel == language.TERMINAL
                and not any(one.get("stack") == shown for one in due)):
            fresh.append({**self._print_of(closing), "stack": shown})
        if not fresh:
            return
        persistence.set_prints(self._session, due + fresh)
        for one in fresh:
            self._trace("print-due", instruction=one["instruction"], document=one["document"])

    def _last_said(self) -> tuple | None:
        """-> the last step this call said -- (frame, instruction, block) -- while its block
        is still the LAST of the last segment stacked; None once another block or nothing
        stands there."""
        kept = getattr(self, "_said_free", None)
        if kept is None or not self._stacked or self._stacked[-1].blocks[-1] is not kept[2]:
            return None
        return kept

    def _stack(self, frame: Frame, block: Block) -> None:
        """A block rendered to be STACKED joins the output being built: under the segment above
        it when that one takes it in, else as the opener of a segment of its own."""
        last = self._stacked[-1] if self._stacked else None
        if not block.headed and last is not None:
            self._stacked[-1] = replace(last, blocks=last.blocks + (block,))
        else:
            self._stacked.append(Segment(position=block.position, document=frame.document.name,
                                         blocks=(block,)))

    def _added(self, block: Block) -> tuple[str, str]:
        """-> (what the output reads with `block`, what it read before it): for a block rendered
        to be stacked, its segment with and without it; for the block that closes the output,
        the whole output and the segments stacked before it, as they were weighed -- the number
        and the range a heading takes where the output closes weigh with that block."""
        def stood(one: Segment) -> str:
            return rendering.segment(replace(one, ordinal=0, reach=0))
        if not block.segment:
            return rendering.render(block), "".join(stood(one) for one in block.stacked)
        last = self._stacked[-1] if self._stacked else None
        if not block.headed and last is not None:
            return stood(replace(last, blocks=last.blocks + (block,))), stood(last)
        return rendering.segment(Segment(blocks=(block,))), ""

    def _assemble(self, closing: int | None, numbered: bool = False) -> tuple[Segment, ...]:
        """-> the segments the output stacked, as the block that closes it carries them: each
        live one with the REACH of its stretch -- the last step merged under its opener, the
        closing block's own (`closing`) when that block extends the LAST stretch -- and, in a
        MULTI-heading output (`numbered`), each headed one with its number `[n]`, the address
        a `-s` call routes by. Data for the renderer: no text is written here."""
        out, seen = [], 0
        for rank, one in enumerate(self._stacked):
            reach = one.stretch
            if closing is not None and rank == len(self._stacked) - 1:
                reach = closing
            seen += 1 if one.headed else 0
            out.append(replace(one, reach=reach, ordinal=seen if numbered and one.headed else 0))
        return tuple(out)

    def _block(self, stack: Stack, frame: Frame, instruction: Instruction,
               wrong: str = "", order: str = "", segment: bool = False,
               at: int | None = None, repairing: bool = False,
               passage: tuple | None = None) -> Block:
        """-> the block, assembled with the output's stacked segments and written to the
        offer map. `at` names the step position the heading stands for when a block
        RE-SHOWS an earlier step of the frame (a mount, a view after a `§`): the map
        keeps that position, so the next view finds the same ask. `repairing` says a
        segment belongs to an output a repair opened: its own heading says `REPAIR n`.
        `passage` is the scope the passage played under, read before its mounts were swept:
        the block that parks the run is judged under it."""
        if not order and language.needs_options(instruction.keyword):
            if not isinstance(instruction.taken, list) or not instruction.taken:
                raise Refusal("options-empty", messages.refusal_options_empty(instruction))
            # the guard of what no capture judged -- a list arrived by a callee's seed,
            # a slot written before the form was judged: refused by name, the element
            # said, never handed to the renderer
            wrong_form = language.scalars_form(instruction.taken, language.OPTIONS, empty_ok=False)
            if wrong_form:
                raise Refusal("options-invalid", messages.refusal_options_invalid(instruction, wrong_form))
        output = language.output_of(instruction.keyword)
        if instruction.keyword in language.FREE:
            output = instance.declared(self.member.meta, frame.document.path, "output") or output
            if self._elects(stack, frame, instruction):
                output = language.LIST
        if not order and language.yields(instruction.keyword):
            if output not in compiling.format_enumeration(self.member.meta):
                raise Refusal("format-unknown",
                              messages.refusal_format_unknown(output, frame.document.name))
        arrival = self._receiving()
        awaited = self._awaited(stack, frame, instruction, order, arrival)
        wait = awaited == language.MESSAGE_DUE
        label, next_call, fact = (("", "", "") if segment
                                  else self.closing(awaited, arrival, message=self._message_call()))
        channel = ("" if order or not language.yields(instruction.keyword)
                   else self._channel(stack, frame, instruction))
        response = ""
        prints: list = []
        said_there = False
        if not segment:
            # the output closes HERE: how it asks its last message is decided now, with the channel
            # it arrives by and what the stack awaits -- its last said step goes `=> response`, on
            # this block's own line or on the last segment stacked, rendered again. An order block
            # that closes a stretch takes no step back: the steps said stay on `terminal`, due
            last = None if channel else self._last_said()
            if last is not None and order == language.CONTINUE and not last[1].asked:
                last = None
            response = self.responding(arrival, awaited, channel, last is not None)
            if response == language.STEP and channel:
                channel = language.RESPONSE
            elif response == language.STEP:
                held = self._stacked[-1]
                self._stacked[-1] = replace(held, blocks=held.blocks[:-1]
                                            + (replace(last[2], channel=language.RESPONSE),))
                self._owing = [one for one in self._owing if one is not last[2]]   # the last message is never due
            prints = persistence.prints_of(self._session) if self._session else []
            waiting = persistence.held_of(self._session) if self._session and not self._dry else {}
            said_there = bool(waiting) and not waiting.get("open")   # a closed output waits at the run: this
            # block joins it, and the lines of the steps due stand there already
        shown = navigation.render(stack, at)      # where the step this block shows stands: its own, or the
        # earlier one a view or a gesture shows again
        # the SCOPE makes the segment: a block whose scope is the last segment's joins it,
        # whatever its frame -- a step said, the step, the proof or the order block that
        # closes the output; any other scope opens a segment. The block that parks the run
        # joins the segment of the passage's steps under the scope they were said under: the
        # sweep of the passage's mounts opens no segment
        scope = self._scope(frame)
        merged = bool(self._stacked) and self._seg_scope in (scope, passage)
        repair = (max((one.repairs for one in frame.procedure.instructions), default=0)
                  if (wrong and not self._asked_again) or (repairing and not merged) else 0)
        # a closing STEP whose heading is elided (merged, no REPAIR) extends the last
        # stretch when it is a step of the frame that opened it: its position closes the
        # range; a step of another frame is said by its line, an order block never extends
        opener = self._stacked[-1].blocks[0] if self._stacked else None
        extends = (merged and not order and not repair and not segment and opener is not None
                   and Segment.trail(opener.stack) == Segment.trail(navigation.render(stack)))
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
        proper, self._proper = tuple(subject for subject, _ in payloads if subject in self._proper), set()
        if not order and instruction.keyword == "WORK" and frame is self._root(stack):
            # the WORK of the ROOT of the passage: its context is the principal's last
            # message -- said as a fixed section at every passage, never the message
            self.note(language.ASK, messages.ASK_TEXT, "served", "ask", by=frame.document.name)
            payloads = payloads + ((language.ASK, messages.ASK_TEXT),)
        # the closing dresses for what it carries: an order block owes no step --
        # behind a segment of its scope it joins it, the signal and its command the
        # block, a reading it brings among the segment's; behind a segment of another
        # scope it names the frame that stands, its laws and its offers: the last
        # heading read is where the run is; with a reading aboard and no segment behind
        # it keeps its heading alone (the laws arm on the output that carries the ask);
        # alone, or repairing, it keeps its habit
        plain = bool(order) and not wrong and bool(payloads or self._stacked)
        moved = plain and bool(self._stacked) and not merged
        own_heading = (not merged) or bool(repair)
        seg_heads = sum(1 for one in self._stacked if one.headed)
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
                "constraints": [one.wire() for one in self._held_laws(frame)]})
        elif not self._dry and self._segmap and not (plain and not moved):
            # a step joins the segment: its entry of the map offers what the step offers too,
            # and names the last step the output asked, with its frame
            entry = self._segmap[-1]
            entry["tools"] = list(dict.fromkeys(
                [*entry.get("tools", []), *(one.name for one in self._tools_in_force(frame))]))
            if not order:
                entry.update({"frame": frame.document.name, "stack": navigation.render(stack),
                              "at": navigation.position(frame) if at is None else at})
        ordinal = len(self._segmap) if (numbered and own_heading) else 0
        routed_note, self._route_note = self._route_note, ""
        # documentary: a law's text renders ONCE -- per OUTPUT under verbatim, per RUN
        # under codes mode -- and every later emission is its code; the LEDGER, never
        # the setting, decides what the reader sees twice. A law enters the ledger by the
        # block whose CONSTRAINTS section says it: an order block that carries readings
        # without its laws, and a block merged under the segment above, say none. A SYSTEM
        # law is never a code: its whole text heads the first CONSTRAINTS section of the
        # output, whatever the setting, and no later segment of it says the law again
        in_force = self._held_laws(frame)
        coded = tuple(one.code for one in in_force
                      if one.code in self._emitted or one.code in self._emitted_run)
        says = not (plain and not moved) and not merged
        system = self._system_laws()
        heads = says and not any(one.code in self._emitted for one in system)
        if says:
            self._emitted.update(one.code for one in in_force + system)
            if not self._settings.verbatim_constraints:
                self._emitted_run.update(one.code for one in in_force)
        if own_heading:
            self._seg_scope = scope
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
            constraints=() if plain and not moved else in_force,
            system=system if heads else (),
            tools=() if plain and not moved else self._tools_in_force(frame),
            payloads=payloads,
            output="" if order else output,
            channel=channel,
            owed=() if said_there else tuple(one["line"] for one in prints   # but this block's own step, said once
                                             if order or one.get("stack") != shown),
            response=response,
            next_call=next_call,
            label=label,
            fact=fact,
            stack=navigation.render(stack),
            root=self._root(stack).document.name if stack.frames else "",
            deviation=wrong,
            diagnostics=tuple(text for _, text in due),
            repair=repair,
            replay=self._replaying,
            wait=wait,
            stacked=stacked,
            merged=merged,
            coded=coded,
            gaps=self._closing_gaps(not segment),
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
            proper=proper,
        )
        if not segment:
            self._pose(block, prints, bool(order), shown)
        weighed = metrics.weigh(block, *self._added(block))
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
        event = dict(stack=block.stack, root=block.root, command=block.command, wait=block.wait,
                     spaces=self._spaces(stack, frame),
                     weight={part: weighed[part] for part in (*metrics.PARTS, "total", "tokens")},
                     **({"payloads": served_parts} if served_parts else {}),
                     **({"served": ledger} if ledger else {}),
                     **({"deviation": wrong} if wrong else {}),
                     **({"diagnostics": [key for key, _ in due]} if due else {}))
        self._trace("block", **event)
        return block

    def _spaces(self, stack: Stack, frame: Frame) -> dict:
        """-> what the block says of the SPACES: `open`, the names of the frames that are spaces, from the
        outermost to the deepest (the last one the root); `openable`, among the names the output's segments
        OFFER (`_segmap[*].tools`, the frame's own offer when no segment stands yet), those that resolve to a proc
        `-open` would let open (`reading.unopenable`) and that no frame holds open already, each ONCE as
        `{name, segment: null}`: a name resolves one document whatever the segment offers it, so `-open <name>`
        opens it bare, at the pending step. Nothing out of the offer: a proc of the catalogue the output does not
        offer is never named."""
        opened = [one.document.name for one in stack.frames if navigation.space(one)]
        offers: dict[str, list[int]] = {}
        segments = [one for one in self._segmap if one.get("tools")]
        if segments:
            for one in segments:
                for name in one["tools"]:
                    offers.setdefault(name, []).append(int(one["ordinal"]))
        else:
            for one in self._tools_in_force(frame):
                offers.setdefault(one.name, []).append(0)
        openable = []
        for name in offers:
            if name in opened:
                continue
            try:
                front = reading.read(self._resolve(f"{name}.md")).front
            except (Refusal, OSError):
                continue
            if reading.unopenable(front):
                continue
            openable.append({"name": name, "segment": None})
        return {"open": opened, "openable": openable}

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
                 order: str, channel: str) -> str:
        """-> what the stack AWAITS after this block: a message at an AWAIT order and at the fused end
        of the passage -- by the tool alone: at the prompt the last free step of the root stays
        PENDING, never fused with the end (`stepping`), so a response is awaited there; a response at
        a CONTINUE order and at a free step nothing consumes; a value at a checkpoint, a field, a
        choice and a production a consumer takes."""
        if order == language.AWAIT:
            return language.MESSAGE_DUE
        if order:
            return language.RESPONSE_DUE
        if self._handed(stack, frame, instruction):
            return language.VALUE_DUE
        if channel == language.TOOL and self._closing(stack, frame, instruction):
            # the fused end of the passage: the run parks with this block
            return language.MESSAGE_DUE
        return language.RESPONSE_DUE

    def closing(self, awaited: str, channel: str, message: str = "",
                left: int = 0, more: int = 0) -> tuple[str, str, str]:
        """-> (label, call, fact): the FOOT of an output, deduced from what the stack AWAITS after
        it (`language.AWAITED`) and the CHANNEL the output reaches the agent by (`language.TOOL`,
        the result of its own call; `language.PROMPT`, the prompt of a launch) -- the one site of
        the engine that decides a closing; the call chooses the channel -- the prompt of a launch
        (`_receiving`), the tool for a view or an inline answer --, never the foot.
        - a value due: nothing, on both channels -- the step's line names the channel the value is
          handed by, and no foot repeats its call;
        - a response due (a free step the agent says, then the run moves on): `CONTINUE` and the
          bare call by the tool; nothing at the prompt -- the step ends when the agent decides;
        - a message due (the root exhausted): `AWAIT` on both channels -- the passage is over --,
          over the call that carries the `message` by the tool, over no call at the prompt, where
          the launcher carries it;
        - a reading that continues (a chunk before the last): `CONTINUE` and the bare call by the
          tool, `MORE` and no call at the prompt; the fact says what remains -- `left` characters
          in `more` chunk(s) -- on both channels.
        A label empty says the output owes no closing; a fact empty says none."""
        if awaited == language.VALUE_DUE:
            return "", "", ""
        if awaited == language.READING_ON:
            fact = messages.reading_continues(left, more)
            if channel == language.PROMPT:
                return language.MORE, "", fact
            return language.CONTINUE, self._command(), fact
        if channel == language.PROMPT:
            return (language.AWAIT, "", "") if awaited == language.MESSAGE_DUE else ("", "", "")
        if awaited == language.MESSAGE_DUE:
            return language.AWAIT, message or self._command(), ""
        return language.CONTINUE, self._command(), ""


def _opened_at(log_name: str) -> datetime | None:
    """-> when the run opened, read from its trace's name (`session-<UTC>.jsonl`, stamped
    at -new); None when no run stands."""
    raw = log_name[len("session-"):].split(".")[0].rstrip("Z") if log_name.startswith("session-") else ""
    try:
        return datetime.strptime(raw[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
