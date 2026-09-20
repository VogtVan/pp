"""execution.boot -- the boot: the opening of a run, its dues and its standing signals, and the re-serve a declared compaction asks for. A mixin of the facade: no state of its own."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from ..packaging import compiling, events
from .. import reading
from ..core import navigation
from ..state import context, instance, log, persistence, settings
from ..core.errors import Refusal
from ..core.model import Block, Document, Instruction, Stack
from .revive import revive


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

    def start(self, path: Path) -> Block | None:
        """Opens a run on `path`, BESIDE whatever other conversations hold -- under
        its own short id, or fresh under ITS key when the conversation re-news (the
        discarded run's own trace says so). The root document's BODY comes with the first
        block -- the boot is the root CALL, served like any other."""
        self._stacked, self._fused, self._output_clock = [], 0, ""    # a fresh OUTPUT per call
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(), None
        self._segmap, self._remap = [], True
        if self._run:              # the conversation re-news ITS run: that slot, fresh
            self._discard(persistence.slot_of(self._launch.meta, self._run))
        self._run_id = self._run or self._mint()
        self._session = persistence.slot_of(self._launch.meta, self._run_id)
        os.environ[context.VARIABLE] = self._run_id   # the fresh run, named to what it launches
        self._served = {}
        self._proven = set()
        self._turns = 0
        self._log = log.fresh(self._session.parent)
        self._trace("new", run=self._run_id)
        document = reading.read(path)
        standing = self.member.meta / instance.SYS / "system.md"
        if standing.is_file():
            # the BUILD RECEIPT: the artifact must have been compiled by THIS
            # engine, from the inputs standing now -- a stale marble refuses at
            # the first boot instead of serving a truncated contract for days
            from ..core.version import VERSION
            receipt = compiling.receipts(self.member.meta).get("system.md") or {}
            if receipt.get("engine") != VERSION:
                raise Refusal("artifact-stale",
                              f"system.md was compiled by "
                              f"{receipt.get('engine') or 'an engine that left no receipt'} "
                              f"and the standing engine is {VERSION} -- "
                              "`doctor` (or `-build`) recompiles it")
            if receipt.get("inputs") != compiling.receipt_inputs(self.member.meta):
                raise Refusal("artifact-stale",
                              "system.md predates the standing vendor inputs -- "
                              "`doctor` (or `-build`) recompiles it")
            catalog = compiling.receipts(self.member.meta).get("tools.md") or {}
            if (catalog.get("catalog") != compiling.catalog_inputs(self.member.meta)
                    or str(catalog.get("switches", "")) != compiling.switch_state(self.member.meta)
                    or str(receipt.get("switches", "")) != compiling.switch_state(self.member.meta)):
                # the CATALOG's receipt: the instance's own inputs moved since the compile
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
        self._boot_payloads(path)
        stack = Stack(frames=[self._frame(document)])
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
        self._first_output = True      # the fresh run's first output says its key
        self._save(stack)              # the slot must stand before a latch comes with it...
        self._bare_checks()            # ...and the checks run BEFORE the advance: the
        block = self._advance(stack)   # boot's own crossings serve at the very first
        return block                   # the first block the fused boot reaches

    def _boot_payloads(self, path: Path) -> None:
        """The readings a boot owes, in their order: the standing rules when the host
        does not carry them in its own channel, the drift of a wired card, the root
        document's composed body. One composition, two callers -- the boot, and the
        re-serve a declared compaction asks for.

        documentary: with `PP_MARBLE` declared, the standing rules come with the host's own
        system channel and survive whatever it does to the conversation; without it
        they are matter of the block, and matter is what a compaction takes away."""
        standing = self.member.meta / instance.SYS / "system.md"
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

        documentary: four run counters go with the context and no others -- the
        proven readings (the agent holds none of them any more), the matter of a
        cut block (its served chunks are gone, the block starts whole), the
        standing drafts (they died with the context), and the codes-mode ledger
        (every law says its text again). What happened -- turns,
        latched signals, mounts, the stack itself -- happened."""
        slot = self._slot()
        self._proven = set()
        self._emitted_run = set()   # the codes-mode ledger goes with the context:
                                    # every law says its text again
        self._ephemerals = []
        persistence.set_pending(slot, {})
        self._first_output = True      # the key may have gone with the context
        self._boot_payloads(stack.frames[0].document.path)
        for frame in stack.frames[1:]:
            # every document still IN FORCE serves itself again -- the stack is what
            # governs the pending step, and its bodies were payloads like any other
            self._serve_document(frame.document.path, (), origin="body", by="the re-serve")
        for frame in stack.frames:
            self._serve_rows(frame.document)
            # the DECLARED payloads replay too: what a provider once rendered for
            # this document went with the context, exactly like a reading -- each token
            # once in the re-serve, a frame and a mount consuming it share one rendering
            self._declared_payloads(frame.document)
            token = self._cycle_token(frame.document)
            if token:
                # a lap in flight: the token is ASKED again and, the request being what
                # it is, renders the same element the lap opened on
                element, refused = self._cycle_element(frame.document)
                self.note(token, element or refused or "", "refused" if refused else "served",
                          "cycle", by=frame.document.name)
                self._payloads.append((token, element or refused or "nothing due -- the frame is leaving"))
        self._mount_bodies(self._mounted())
        self._mount_serves(self._mounted())
        for entry in self._mounted():
            document = self._mount_source(entry)
            if document is not None:
                self._declared_payloads(document)
        block = self._advance(stack)
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
        for check in contributions.composed(self.member.meta):
            if check["kind"] != "checks":
                continue
            predicate = str(check.get("predicate") or "record-crossing")
            judge = getattr(self, f"_predicate_{predicate.replace('-', '_')}", None)
            if judge is not None and judge(check):
                # the push is bare: a vector is a TYPED channel (families) and the
                # bus keeps no evidence -- the signal says the state, the repairing
                # call (`doctor`, the door) names the pieces
                self._signal(str(check["package"]), str(check["signal"]))

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

    def _predicate_card_drift(self, check: dict) -> bool:
        """The wired card at `home` no longer carries the canonical contract the
        DECLARING package ships at `record` -- the recall vehicle has no strong
        channel to certify itself, so the drift is judged byte for byte and said."""
        card = self.member.path / str(check.get("home", ""))
        if not card.is_file():
            return False
        canon = next((root / str(check.get("record", ""))
                      for root in instance.vendored(self.member.meta)
                      if root.name.split("@")[0] == str(check.get("package", ""))
                      and (root / str(check.get("record", ""))).is_file()), None)
        return bool(canon is not None
                    and card.read_text(encoding="utf-8") != canon.read_text(encoding="utf-8"))

    def _field_value(self, stem: str, field: str) -> str:
        """-> the value a `@Doc.field` reference names, as a guard and an exec argument
        read it: the field of `Doc.md` resolved in the instance; `SETTINGS` through the
        effort's presets, an absent key falling to its owner's default. Empty when
        nothing says it; a YAML boolean reads lowercase."""
        path = instance.resolve(self.member.meta, f"{stem}.md")
        front = reading.read(path).front if path.is_file() else {}
        if stem == "SETTINGS":
            # the profile's presets bind the guards exactly as they bind the typed
            # settings -- one resolution, wherever SETTINGS front matter is read
            front = settings.effective(front, self.member.meta)
        value = front.get(field, "")
        declared = ("true" if value else "false") if isinstance(value, bool) else str(value).strip()
        if not declared and stem == "SETTINGS":
            # the key left out: its owner says its default -- the system's seeds,
            # or the fragment of the package beyond
            declared = settings.default_of(self.member.meta, field)
        return declared

    def _due(self, instruction: Instruction) -> bool:
        """-> whether a guarded instruction plays THIS turn: the `@Doc.field` value is a
        SWITCH or a cadence. `true`/`false` is a switch -- it looks at NOW: true plays
        every turn from the very first, false never. An integer is a cadence -- it
        looks BACK: 0 (or nothing declared) never, n every n completed turns, and
        never before the first. An absent SETTINGS key falls to the engine default."""
        stem, field = instruction.guard.split(".", 1)
        declared = self._field_value(stem, field)
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
