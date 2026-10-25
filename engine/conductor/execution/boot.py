"""execution.boot -- the boot: the opening of a run, its dues and its standing signals, and the re-serve a declared compaction asks for. A mixin of the facade: no state of its own."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from ..packaging import compiling, events
from .. import reading
from ..core import navigation, language
from ..state import context, instance, log, persistence, settings
from ..core.errors import Refusal
from ..core.model import Block, Document, Instruction, Stack
from .revive import revive


ENGINE_CHECKS = [    # the engine's OWN checks: its card, projected at the harness homes, drifts
    {"kind": "checks", "package": "engine", "signal": "card-drift", "predicate": "card-drift",
     "record": "refs/PP.md", "home": home, "door": "./pp doctor"}   # `door`: the way out
    for home in (".claude/skills/pp/SKILL.md", ".agents/skills/pp/SKILL.md")]   # a diagnostic names

class Booting:
    """The boot: the opening of a run, its dues and its standing signals, and the re-serve -- a mixin of the facade."""

    def boot(self, name: str) -> Path:
        """-> where the boot document lives: resolved through the instance (the vendored
        kit carries it), the member's own tree otherwise."""
        return instance.resolve(self.member.meta, name)

    def _discard(self, slot: Path) -> bool:
        """Drops ONE run -- its own trace says so. -> whether a run actually stood."""
        standing = persistence.trace_of(slot)
        if standing:
            log.record(slot.parent / standing, "reset")
        stood = slot.exists()
        persistence.forget(slot)
        return stood

    def start(self, path: Path, prompt: str = "") -> Block | None:
        """Opens a run on `path`, BESIDE whatever other conversations hold -- under
        its own short id, or fresh under ITS key when the conversation re-news (the
        discarded run's own trace says so). The root document's BODY comes with the first
        block -- the boot is the root CALL, served like any other. A `prompt` handed
        with the opening is the principal's message: traced `prompt` right after `new`,
        before the first block -- a line of the trace, what a base serves of it its own.
        The key is drawn here (`_mint`): its slot is RESERVED before anything is written, and
        an opening refused after that leaves no slot behind. A launcher may also name
        the run's DOOR (`PP_DOOR`, read here alone): the document is judged before anything
        is written (`door-unknown`) and opened as a CALL above the boot -- the first
        exchange carries it. `PP_CONDUCTED_BY_PRINCIPAL=true` (read here alone) opens a run
        its principal conducts (`_mode_asked`); `PP_WORKDIR` (read here alone) names the
        run's MATERIAL, the tree it works on, kept at the slot as `work`; `PP_DOCUMENTS`
        (read here alone) gives the run one more ROOT of documents (`_documents_asked`),
        bound before the door resolves and kept at the slot."""
        mode = self._mode_asked()
        work = os.environ.get(context.WORKDIR, "").strip()
        root = self._documents_asked()
        door = os.environ.get(context.DOOR, "").strip()
        instance.play_documents(self.member.meta, root)
        try:
            if door and not instance.resolve(self.member.meta, door).is_file():
                raise Refusal("door-unknown",
                              f"`{context.DOOR}={door}` names no document of this instance -- "
                              "the launcher's entry must resolve through its search paths")
        except Refusal:
            instance.play_documents(self.member.meta, "")
            raise
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        if self._run:              # the conversation re-news ITS run: that slot, fresh
            self._discard(persistence.slot_of(self._launch.meta, self._run))
            self._run_id = self._run
        else:
            self._run_id = self._mint()
        self._session = persistence.slot_of(self._launch.meta, self._run_id)
        try:
            return self._open(path, prompt, door, mode=mode, work=work, root=root)
        except Refusal:
            if persistence.reserved(self._session):    # a refused opening leaves no run behind
                self._session.unlink(missing_ok=True)
            instance.play_documents(self.member.meta, "")
            raise

    @staticmethod
    def _mode_asked() -> str:
        """-> the mode the launcher asks at `-new`: `principal` under
        `PP_CONDUCTED_BY_PRINCIPAL=true` (`context.by_principal`), "" (the LLM conducts)
        otherwise; an odd value refuses `conducted-by-invalid` before anything is written."""
        return persistence.PRINCIPAL if context.by_principal() else ""

    @staticmethod
    def _documents_asked() -> str:
        """-> the root of documents the launcher gives at `-new`: `PP_DOCUMENTS`, an absolute
        path to a directory, "" when absent or empty; anything else refuses
        `documents-unknown` before anything is written."""
        raw = os.environ.get(context.DOCUMENTS, "").strip()
        if not raw:
            return ""
        if not Path(raw).is_absolute() or not Path(raw).is_dir():
            raise Refusal("documents-unknown",
                          f"`{context.DOCUMENTS}={raw}` -- the root of documents is an absolute "
                          "path to a directory that exists")
        return str(Path(raw))

    def reopen(self, path: Path, given: str = "", verb: str = "") -> Block | None:
        """REOPENS the run an upgrade renewed, under ITS key, on `path` -- the boot served as
        at an opening. The mark the upgrade left in place of the slot says what crosses: the
        trace, continued (`reopened`); the exchanges completed, the boot set there (the
        context starts again at this exchange); the packages the run switched off. `given`
        is the text the call carried: the principal's message when the run waited for it
        (the mark's `awaits`: a message), traced `prompt`; a production or a value handed to a
        run that waited for one, or a `verb` the call named, is NOT played -- the first block
        says so."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        slot = self._slot()
        mark = persistence.renewed(slot) if slot is not None else None
        if mark is None:
            raise Refusal("no-run", "no renewed run under this key -- call `-new` first")
        self._run_id = persistence.run_id_of(slot)
        message = (given if mark.get("awaits") == persistence.MESSAGE and given.strip() and not verb
                   else "")
        unplayed = verb or ("" if message else given.strip())
        return self._open(path, message, renewed=mark, unplayed=unplayed,
                          mode=str(mark.get(persistence.MODE, "")),
                          work=str((mark.get(persistence.MATERIAL) or {}).get("path", "")),
                          root=str(mark.get(persistence.DOCUMENTS) or ""))

    def _open(self, path: Path, prompt: str, door: str = "",
              renewed: dict | None = None, unplayed: str = "", mode: str = "",
              work: str = "", root: str = "") -> Block | None:
        """The opening proper, under the key `start` settled and reserved -- or the key a
        renewal mark holds (`renewed`), whose trace continues and whose exchanges count on.
        A `door` is the launcher's named entry: a CALL injected at the floor's pending step,
        so the door's frame opens above the boot and plays in the first exchange. `unplayed`
        is what a reopening call carried and did not play: the first block says it. `mode`
        is the run's conduction mode, written to its slot before the first block renders;
        `work` the launcher's material, written beside it and named `work` by the rows;
        `root` the launcher's root of documents, written beside it -- already bound."""
        os.environ[context.VARIABLE] = self._run_id   # the fresh run, named to what it launches
        self._served = {}
        self._proven = set()
        self._turns = int(renewed.get("turns", 0)) if renewed else 0
        if renewed is None or not self._log:
            self._log = log.fresh(self._session.parent, self._run_id)
        if renewed is None:
            self._trace("new", run=self._run_id, **({persistence.MODE: mode} if mode else {}),
                        **({persistence.MATERIAL: {"name": "work", "path": work}} if work else {}),
                        **({persistence.DOCUMENTS: root} if root else {}))
        else:
            moved = renewed.get(persistence.RENEWED) or {}
            self._trace("reopened", run=self._run_id,
                        **{"from": moved.get("from") or {}, "to": moved.get("to") or {}})
        if prompt.strip():
            self._trace("prompt", text=prompt)
        document = reading.read(path)
        if reading.nexts(document):
            # a successor enters the CALLER's frame: the floor has none to inject into
            raise Refusal("next-floor",
                          f"{document.name} declares `next:` and is the floor -- a "
                          "transition needs a caller; CALL it from a root document")
        marble = compiling.marble_of(mode)          # the standing orders of the run's mode
        standing = self.member.meta / instance.SYS / marble
        if standing.is_file():
            # the BUILD RECEIPT: the artifact must have been compiled by THIS
            # engine, from the inputs standing now -- a stale marble refuses at
            # the first boot instead of serving a truncated contract for days
            from ..core.version import VERSION
            receipt = compiling.receipts(self.member.meta).get(marble) or {}
            if receipt.get("engine") != VERSION:
                raise Refusal("artifact-stale",
                              f"{marble} was compiled by "
                              f"{receipt.get('engine') or 'an engine that left no receipt'} "
                              f"and the standing engine is {VERSION} -- "
                              "`doctor` (or `-build`) recompiles it")
            if receipt.get("inputs") != compiling.receipt_inputs(self.member.meta):
                raise Refusal("artifact-stale",
                              f"{marble} predates the standing vendor inputs -- "
                              "`doctor` (or `-build`) recompiles it")
            held = compiling.receipts(self.member.meta)
            inputs = compiling.catalog_inputs(self.member.meta)
            switches = compiling.switch_state(self.member.meta)
            if (any((held.get(name) or {}).get("catalog") != inputs
                    or str((held.get(name) or {}).get("switches", "")) != switches
                    for name in compiling.CATALOGS)
                    or str(receipt.get("switches", "")) != switches):
                # the receipts of the two READINGS: the instance's own inputs moved since the compile
                # (a format declared, a proc dropped, a tool offered), or a package SWITCH
                # moved at SETTINGS -- the boot recompiles before it serves, so the catalog
                # and the marble it hands over are the ones that play; a composition that
                # no longer holds refuses here, by name, instead of booting on a dead name
                # (le-recu-du-catalogue)
                compiling.build_tools(self.member.meta)
                compiling.render_registry(self.member.meta)   # validates; writes nothing
                compiling.build_system(self.member.meta)
        if os.environ.get("PP_MARBLE") and not standing.is_file():
            # the sentinel is a RECEIPT, not a switch: it certifies that the marble
            # channel carries the compiled contract -- with nothing compiled to
            # carry, it lies, and a lying receipt refuses rather than boots blind
            raise Refusal("marble-missing",
                          "PP_MARBLE is declared but no compiled contract exists "
                          f"at {standing} -- run `-build` (or drop the sentinel)")
        self._boot_payloads(path, mode)
        # the floor enters as a CALL does, less its `exec:` (no CALL enters it): the rows
        # its overlays add and its declared payloads, after its body
        self._enter("floor", [path], only=("overlay_rows", "payloads"))
        stack = Stack(frames=[self._frame(document)])
        self._initialize(stack, stack.frames[0])   # the floor's own entry socket, once
        token = self._cycle_token(document)
        if token:
            # an iterated door as the FLOOR: its token asked before its first step --
            # an element opens the first lap; nothing due, the run completes at once
            element, refused = self._cycle_element(document)
            if element:
                self._trace("lap", document=document.name)
                self._lap_payloads(document, element)
            else:
                self.note(token, refused or "", "refused" if refused else "served", "cycle",
                          by=document.name)
                self._payloads.append((token, refused or "nothing due -- the run completes"))
                for one in stack.frames[0].procedure.instructions:
                    navigation.give(one, "off")
        if door:
            # the launcher's door: a CALL above the boot, exactly as `play()` injects one
            frame = stack.frames[0]
            injected = Instruction(keyword="CALL", argument=door, injected=True, site="door")
            frame.procedure.instructions.insert(navigation.pointer(frame), injected)
            self._trace("door", document=door)
        self._first_output = True      # the fresh run's first output says its key
        self._save(stack)              # the slot must stand before a latch comes with it...
        if mode:
            persistence.set_mode(self._session, mode)   # the blocks render by the mode
        if work:
            persistence.set_material(self._session, {"name": "work", "path": work})
        if root:
            persistence.set_documents(self._session, root)
        if renewed is not None:
            persistence.set_boot(self._session, self._turns)   # the context starts again HERE
        self._bare_checks()            # ...and the checks run BEFORE the advance: the
        wrong = ""                     # boot's own crossings serve at the very first
        if unplayed:
            wrong = f"run {self._run_id} was renewed by an upgrade and reopens here, on its boot"
        block = self._advance(stack, wrong)
        return block                   # the first block the fused boot reaches

    def _boot_payloads(self, path: Path, mode: str = "") -> None:
        """The readings a boot owes, in their order: the standing rules of the run's
        `mode` when the host does not carry them in its own channel, the drift of a wired
        card, the root document's composed body. One composition, two callers -- the
        boot, and the re-serve a declared compaction asks for.

        documentary: with `PP_MARBLE` declared, the standing rules come with the host's own
        system channel and survive whatever it does to the conversation; without it
        they are matter of the block, and matter is what a compaction takes away."""
        standing = self.member.meta / instance.SYS / compiling.marble_of(mode)
        if not os.environ.get("PP_MARBLE") and standing.is_file():
            text = standing.read_text(encoding="utf-8").strip()
            self.note("standing orders", text, "served", "marble", by="BOOT", package="engine")
            self._serve_payload("standing orders", text)
        body = self._composed_body(path)
        if body:
            self.note(reading.title(path), body, "served", "body", by="BOOT",
                      package=self.note_package(path))
            self._serve_payload(reading.title(path), body)

    def compacted(self) -> Block | None:
        """The COMPACTION verb: the agent DECLARES that its host summarized the
        session, and the run serves itself back. pp never detects a compaction --
        it cannot see the host's message -- so the declaration is taken at face
        value, and the duty it opens stands until an output carries it.
        -> the re-served block."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None   # every law said VERBATIM again
        self._segmap, self._remap = [], True
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        stack = self._rebind(restored)
        persistence.set_compacted(slot, True)
        persistence.set_boot(slot, self._turns)   # the context starts again HERE
        self._trace("compacted")
        self._reserving = True         # what the re-serve serves COMES BACK: the ledger
        try:                           # says so, and the state returns to normal after
            return self._reserved(stack)
        finally:
            self._reserving = False

    def _reserved(self, stack: Stack) -> Block | None:
        """The RE-SERVE: what the run had served comes back. The counters that make a
        reading serve once are cleared, the boot's readings and the mounted documents
        are pushed again, and the pending block renders with every law verbatim. The
        declaration is consumed HERE, and only here -- an output that never reached
        the agent leaves it armed for the next call.

        documentary: three run counters go with the context and no others -- the
        proven readings (the agent holds none of them any more), the matter of a
        cut block (its served chunks are gone, the block starts whole), and the
        codes-mode ledger (every law says its text again). What happened -- turns,
        latched signals, mounts, the stack itself -- happened."""
        slot = self._slot()
        self._proven = set()
        self._emitted_run = set()   # the codes-mode ledger goes with the context:
                                    # every law says its text again
        persistence.set_pending(slot, {})
        self._first_output = True      # the key may have gone with the context
        self._boot_payloads(stack.frames[0].document.path, persistence.mode_of(slot))
        # every document still IN FORCE serves itself again -- the stack is what governs
        # the pending step, and its bodies were payloads like any other
        self._enter("reserve", stack.frames[1:], only=("body",))
        for frame in stack.frames:
            # its `serve:` sections at the pace its SERVEs played them, its overlays' rows,
            # and its declared payloads -- what a provider once rendered went with the
            # context; each token once in the re-serve, a frame and a mount sharing it
            self._enter("reserve", [frame], only=("rows_played", "overlay_rows", "payloads"))
            token = self._cycle_token(frame.document)
            if token:
                # a lap in flight: the token is ASKED again and, the request being what
                # it is, renders the same element the lap opened on
                element, refused = self._cycle_element(frame.document)
                self.note(token, element or refused or "", "refused" if refused else "served",
                          "cycle", by=frame.document.name)
                self._payloads.append((token, element or refused or "nothing due -- the frame is leaving"))
            if frame.caller is not None:
                self._input(frame.document, frame.procedure, frame.seed)   # what it received
            if frame.cycle == language.FIELD and frame.field:
                # a described door mid-lap: the head is what the lap opened on -- served
                # again from the frame, which held it through the compaction
                self.note("field", frame.field[0], "served", "cycle", by=frame.document.name)
                self._payloads.append(("field", frame.field[0]))
        standing = [one for one in self._mounted()
                    if one.get("matter", True) and self._mount_source(one) is not None]
        self._enter("reserve-mount", standing)   # a laws-only hold has no matter to re-serve
        # a parked run re-serves the closing that parked it: the passage ended once
        block = (self._standing(stack) if navigation.exhausted(navigation.current(stack))
                 else self._advance(stack))
        persistence.set_compacted(slot, False)
        return block

    def _serve_payload(self, subject: str, text: str) -> None:
        """Appends one payload of the boot. The serve budget does NOT count these:
        it models the HARNESS's inline limit for the serve mechanism (a served
        chunk plus the block around it) -- the boot arrives in pieces anyway,
        outside that mechanism, and is never braked by it (operator word,
        2026-08-23)."""
        self._payloads.append((subject, text))

    def _bare_checks(self) -> None:
        """The boot's predicates -- every one DECLARED: each `checks:` entry of the
        composition names a signal and the generic predicate that judges it, and
        the engine plays the predicate with the entry's own fields. The engine
        knows HOW to judge (a record crossed, a fingerprint worn, a home idle, a
        card drifted); WHAT is watched -- the signal, the document, the record --
        is the declaring package's, never coded here."""
        from ..packaging import contributions
        declared = [one for one in contributions.composed(self.member.meta) if one["kind"] == "checks"]
        for check in ENGINE_CHECKS + declared:
            predicate = str(check.get("predicate") or "record-crossing")
            judge = getattr(self, f"_predicate_{predicate.replace('-', '_')}", None)
            found = judge(check) if judge is not None else False
            if found:
                # the push is bare: a vector is a TYPED channel (families) and the
                # bus keeps no evidence -- the signal says the state, the repairing
                # call (`doctor`, the door) names the pieces. The FACT a predicate
                # renders and the check's own `door` travel to the diagnostic alone
                self._signal(str(check["package"]), str(check["signal"]),
                             evidence=found if isinstance(found, str) else "",
                             way=str(check.get("door") or ""))

    def _predicate_record_crossing(self, check: dict) -> bool:
        """A work is due: the anchored day crossed the record since its last entry."""
        from ..state import cadences
        return cadences.crossing_due(self.member.meta, str(check.get("anchor", "")),
                                     str(check.get("record", "")))

    def _predicate_fingerprint(self, check: dict) -> bool:
        """The declared document still wears the fingerprint the install stamped:
        its bytes hash to the instance's `member_seed` -- the member is bare."""
        declared = (instance.read(self.member.meta)
                    if instance.is_instance(self.member.meta) else {})
        seed = str(declared.get("member_seed", ""))
        home = self.member.meta / str(check.get("home", ""))
        return bool(seed and home.is_file()
                    and hashlib.sha256(home.read_bytes()).hexdigest() == seed)

    def _predicate_home_idle(self, check: dict) -> bool:
        """The harness homes hold skills and no instance document adopts any
        (`+name` in a `tools:` block) -- the stock sleeps."""
        homes = [self.member.path / home for home in instance.HARNESS_HOMES]
        stocked = any(any(one.is_dir() for one in home.iterdir())
                      for home in homes if home.is_dir())
        if not stocked:
            return False
        spots = (list(self.member.meta.glob("*.md"))
                 + list((self.member.meta / "procs").glob("*.md")))
        for doc in spots:
            block = str(reading.read(doc).front.get("tools", ""))
            if any(line.strip().startswith("+") for line in block.splitlines()):
                return False
        return True

    def _predicate_card_drift(self, check: dict) -> str | bool:
        """The wired card at `home` no longer carries the canonical contract the
        DECLARING package ships at `record` -- the recall vehicle has no strong
        channel to certify itself, so the drift is judged byte for byte and said.
        -> the FACT (`<home> differs from the contract`) when it drifts, False otherwise."""
        card = self.member.path / str(check.get("home", ""))
        if not card.is_file():
            return False
        if str(check.get("package", "")) == "engine":
            # the engine's own card lives beside the running engine, never under vendor, and
            # a harness receives it followed by the engine's SYSTEM.CONDUCT.md: one
            # composition, the install's
            from ..packaging import install
            own = self._script.parent / str(check.get("record", ""))
            contract = install.card_of(self._script.parent) if own.is_file() else None
        else:
            canon = next((root / str(check.get("record", ""))
                          for root in instance.vendored(self.member.meta)
                          if root.name.split("@")[0] == str(check.get("package", ""))
                          and (root / str(check.get("record", ""))).is_file()), None)
            contract = canon.read_text(encoding="utf-8") if canon is not None else None
        if contract is None or card.read_text(encoding="utf-8") == contract:
            return False
        return f"{check.get('home', '')} differs from the contract"

    def _due(self, instruction: Instruction) -> bool:
        """-> whether a guarded instruction plays THIS turn: the `@Doc.field` value is a
        SWITCH or a cadence. `true`/`false` is a switch -- it looks at NOW: true plays
        every turn from the very first, false never. An integer is a cadence -- it
        looks BACK: 0 (or nothing declared) never, n every n completed turns, and
        never before the first. An absent SETTINGS key falls to the engine default."""
        stem, field = instruction.guard.split(".", 1)
        declared = settings.field_value(self.member.meta, stem, field)
        if not declared:
            return False
        if declared.lower() in ("true", "false"):
            return declared.lower() == "true"
        try:
            cadence = int(declared)
        except ValueError:
            raise Refusal("guard-invalid",
                          f"`^ @{instruction.guard}` -- `{declared}` is not a whole number")
        if cadence < 0:
            raise Refusal("guard-invalid",
                          f"`^ @{instruction.guard}` -- a cadence below 0 means nothing")
        return cadence > 0 and self._turns >= 1 and self._turns % cadence == 0
