"""execution.hosting -- the hosting: the mounted documents, their laws and tools in force. A mixin of the facade: no state of its own."""
from __future__ import annotations

from pathlib import Path
from ..packaging import compiling, events
from .. import reading
from ..core import language, messages, navigation, tokens
from ..state import instance, persistence
from .revive import revive
from .. import rendering
from ..core.errors import Refusal
from ..core.model import Constraint, Document, Frame, Instruction, Segment, Stack, Tool


class Hosting:
    """The hosting: the mounted documents, their laws and tools in force -- a mixin of the facade."""

    def _mounted(self) -> list[dict]:
        """-> the run's standing mounts, from the slot -- the slot is their one home: a
        mount lives exactly as long as its exchange (the session cycle's rewind sweeps it;
        the lap of an iterated door keeps it), so nothing about it is worth keeping in
        memory. Under a call's transaction the slot reads as the call has staged it: what
        a socket mounted earlier in the same advance is in the view, and leaves with the
        call if it refuses."""
        slot = self._session or self._slot()
        return persistence.mounted_of(slot) if slot else []

    def _mount_path(self, doc) -> Path:
        """-> the file a mount ADDRESS names -- the one reader of every mount, the verb's,
        an entry's, a socket's. Three forms: a bare NAME is the composition's base
        document of that name (a package's proc or ref, its overlays applying) or a
        skill's contract; a PATH (`plans/p/PLAN.md`) is the document at that place --
        the instance first, the repository last -- the form that names a document no
        name distinguishes; `<package>:<path>` is a file of that package's bundle
        as the instance plays it. An absolute path,
        a `..`, a package not in play or an address no file answers refuses
        `mount-missing`."""
        name = str(doc).strip()
        package, qualified, rest = name.partition(":")
        if qualified and package and "/" not in package:
            root = instance.bundle_of(self.member.meta, package)
            where = Path(rest.strip())
            if root is None or not rest.strip() or where.is_absolute() or ".." in where.parts:
                raise Refusal("mount-missing",
                              messages.refusal_mount_missing_2(name))
            path = root / where
        else:
            if not name or Path(name).is_absolute() or ".." in Path(name).parts:
                raise Refusal("mount-missing", messages.refusal_mount_missing_3(name))
            path = self._resolve(name)
        if not path.is_file():
            raise Refusal("mount-missing", messages.refusal_mount_missing(name))
        return path

    def _mount_source(self, entry: dict) -> Document | None:
        """-> the mounted document, re-read at each use: the view serves what the
        file SAYS NOW; one gone missing mid-run mounts nothing and SAYS so -- the
        engine's own `mount-gone`, a diagnostic of level note, once per address and
        per run, never from a view (`-peek`)."""
        doc = str(entry.get("doc", ""))
        try:
            return reading.read(self._mount_path(doc))
        except (Refusal, OSError):
            if not self._dry and not self._count_traced("mount-gone", "doc", doc):
                self._trace("mount-gone", doc=doc)
                self._signal("engine", "mount-gone", evidence=messages.gone(doc))
            return None

    def _mount_force(self, document: Document) -> tuple[tuple[Constraint, ...], tuple[Tool, ...]]:
        """-> the laws and the tools a mounted document puts in force: what a frame on it
        would -- its own sections, then the deltas of its overlays. The overlays answer a
        file NAME, so they apply to the BASE of that name alone: a document mounted by its
        path that only shares the name keeps its own sections. A delta that changes nothing refuses as it does for a frame. Its laws read their tags as a frame's do."""
        meta = self.member.meta
        hits = instance.chain(meta, document.path.name)
        if len(hits) > 1 and hits[-1].resolve() == document.path.resolve():
            return compiling.effective(meta, document)
        return compiling.resolved(meta, reading.constraints(document)), compiling.tools_of(document, meta)

    def _mount_laws(self, mounts: list[dict] | None = None) -> tuple[Constraint, ...]:
        """-> the constraints the mounts put in force, mount order -- hosted laws
        bind like any law on screen: rendered at every block, owed at every proof.
        `mounts` names the entries to read, the slot's by default."""
        laws: list[Constraint] = []
        for entry in self._mounted() if mounts is None else mounts:
            document = self._mount_source(entry) if entry.get("constraints", True) else None
            if document is not None:
                laws.extend(self._mount_force(document)[0])
        return tuple(laws)

    def _mount_tools(self) -> tuple[Tool, ...]:
        """-> the tools the mounts offer, mount order."""
        tools: list[Tool] = []
        for entry in self._mounted():
            document = self._mount_source(entry) if entry.get("tools", True) else None
            if document is not None:
                tools.extend(self._mount_force(document)[1])
        return tuple(tools)

    def _system_laws(self) -> tuple[Constraint, ...]:
        """-> the SYSTEM LAWS, read once per process (`compiling.system_laws`): the head of
        every frame's laws, whatever the stack, the space, the door, the mount or the repair."""
        known = getattr(self, "_system", None)
        if known is None:
            known = self._system = compiling.system_laws(self.member.meta)
        return known

    def _held_laws(self, frame: Frame) -> tuple[Constraint, ...]:
        """-> the laws the DOCUMENTS hold on `frame`: the frame chain, the mounted laws and the
        laws a socket document left DUE, deduped by code (the chain wins) -- what a segment's
        map snapshots for a routed door, and what the block renders under the system laws."""
        held = {one.code for one in self._system_laws()}
        kept: list[Constraint] = []
        for one in frame.constraints + self._mount_laws() + self._owed_laws():
            if one.code not in held:
                held.add(one.code)
                kept.append(one)
        return tuple(kept)

    def _in_force(self, frame: Frame) -> tuple[Constraint, ...]:
        """-> the laws in force on `frame`: the system laws first, then the documents' -- what
        the scope reads and what the checkpoint owes."""
        return self._system_laws() + self._held_laws(frame)

    def _scope(self, frame: Frame) -> tuple[frozenset, frozenset]:
        """-> the SCOPE of a block of `frame`: the codes of the laws in force for it, whatever their
        order -- and, under `tools_in_scope`, the names of its offers. Two blocks of one scope read
        in one segment; a scope that differs opens the next."""
        return (frozenset(one.code for one in self._in_force(frame)),
                frozenset(one.name for one in self._tools_in_force(frame))
                if self._settings.tools_in_scope else frozenset())

    def _tools_in_force(self, frame: Frame) -> tuple[Tool, ...]:
        """-> the frame chain's offer plus the mounted ones, deduped by name."""
        offered = {one.name for one in frame.tools}
        return frame.tools + tuple(one for one in self._mount_tools()
                                   if one.name not in offered)

    def mount(self, specs: list, lead: str = "", agents: bool = False,
              act: str = "mount", hold: bool = False) -> str:
        """The HOSTING call: documents of the composition, each named by its ADDRESS
        (`_mount_path`) and kept by it at the slot, enter the current view -- each one's `constraints:` in force at every block and proven at the
        checkpoints, its `tools:` offered, its body served when asked for -- until
        the exchange ends: the session cycle's rewind sweeps every mount -- the lap
        of an iterated door keeps them, a lap lives inside the exchange. The verb speaks
        DOCUMENTS alone; what to take from each is the CALLER's explicit say
        (`body` · `constraints` · `tools`, defaults constraints+tools). A `proc:`
        aboard a mounted document is ignored -- the flow stays the frames'.
        -> the text to print: the asked-for bodies, then the block that STANDS, re-shown
        in this richer context -- the step the last output asked for, at its position;
        a mount never advances the run: the pointer is where it was, the next bare call
        carries on from there. The view leaves through the seam of every block
        (`delivered`): cut under the host's cap like every output, the rest waiting at the
        run -- or HELD for the principal's call when the agent mounts (`agents`, what the console
        read on the call; `act`, what the hold says).
        `lead` is what the mounting script printed before its directive: its answer, one
        output with the view on the principal's call, the tool's line alone when the view is held.
        An address ALREADY mounted in the view is not mounted again: its laws and offers stand,
        the slot keeps its one entry; what this call asks
        of its matter (its body, its parts) is served in this output -- or said spared when it
        was already proven -- and nothing is served when nothing is asked, nor when the address was
        posed on an output that still waits open: its matter waits there. So a mount that
        names the chain already there plus a deeper document adds that document alone; a code
        a NEW document brings while another holds it refuses `mount-collision`.
        A document that IMPORTS (`imports:`) brings the documents it names before itself, each
        with its laws, its offer and its body, each entry naming its importer (`_imported`).
        An entry may name what it REPLACES (`"replaces": [<address>, ...]`): before anything
        enters, the entries of the passage at those addresses leave the slot -- their laws,
        offers and matter with them, so a law they carried no longer collides, and what they
        imported with them (`_leaving`); an address not in the view does nothing, an entry a
        frame holds is its frame's and stays, an imported entry is its importer's and stays.
        `hold`: the principal's call asks the output held OPEN (`PP_HOLD_OUTPUT`) -- and so does any
        mount played while an open output waits at the run: the mount is POSED -- its entries in the
        view, its matter waiting with that output in the order the mounts came -- and no block is
        rendered; the principal's bare call renders the exchange once, after the last mount
        (`_joined_open`, `_released_open`)."""
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", messages.refusal_no_run())
        stack = self._rebind(restored)
        frame = navigation.current(stack)
        named: set[str] = set()
        for spec in specs:
            replaces = spec.get("replaces", []) if isinstance(spec, dict) else []
            if not isinstance(replaces, list) or not all(
                    isinstance(one, str) and one.strip() for one in replaces):
                raise Refusal("mount-invalid", messages.refusal_mount_invalid_2())
            named.update(one.strip() for one in replaces)
        mounted = self._mounted()
        kept, gone = self._leaving(mounted, {one["doc"] for one in mounted if one["doc"] in named
                                             and not one.get("held") and not one.get("import")})
        held = ({one.code for one in self._system_laws()} | {one.code for one in frame.constraints}
                | {one.code for one in self._mount_laws(kept)} | {one.code for one in self._owed_laws()})
        standing = {one["doc"]: one for one in kept}
        taken = set(standing)
        fresh: list[dict] = []          # what enters the slot: the addresses not yet in the view
        again: list[dict] = []          # what is served again: the matter asked of an address in the view
        for spec in specs:
            if not isinstance(spec, dict) or not str(spec.get("doc", "")).strip():
                raise Refusal("mount-invalid",
                              messages.refusal_mount_invalid_3())
            name = str(spec["doc"]).strip()
            if "scope" in spec:
                raise Refusal("mount-invalid",
                              messages.refusal_mount_invalid_4(name))
            path = self._mount_path(name)
            entry = {"doc": name, "body": self._body_asked(spec, name),
                     "constraints": bool(spec.get("constraints", True)),
                     "tools": bool(spec.get("tools", True))}
            before = standing.get(name) or next((one for one in fresh if one["doc"] == name), None)
            if before is not None:
                if entry["body"]:      # its matter alone: its laws and its offers stand in the view
                    again.append({**entry, "constraints": False, "tools": False})
                continue
            own = instance.imports_of(self.member.meta, path)
            for one in self._imported(path, name, taken, own=own):
                self._collides(one["doc"], held)
                fresh.append(one)
            taken.add(name)
            if own:
                entry["imports"] = list(own)
            if entry["constraints"]:
                self._collides(name, held)
            fresh.append(entry)
        waiting = persistence.held_of(slot)
        if waiting.get("open"):
            # what a mount posed on the open output serves waits there, unread: naming it again
            # serves nothing more
            again = [one for one in again if one["doc"] not in waiting.get("posed", [])]
        # the entry: each document's `exec:` plays before it brings anything -- an address
        # served again enters nothing, so plays none
        self._enter("mount", fresh, only=("exec",))
        # the READINGS are composed BEFORE anything is written: they are the half of
        # this call that refuses, and a refusal must leave the mount exactly where
        # it stood. Only the last act -- the pending block -- needs the state on disk,
        # because its laws are read back from the slot.
        self._mount_matter(stack, frame, fresh + again, kept + fresh)
        if gone:
            self._trace("released", docs=[one["doc"] for one in gone], by="replaces")
        if fresh:
            self._trace("mounted", docs=[one["doc"] for one in fresh])
        if gone or fresh or kept != mounted:
            persistence.set_mounted(slot, kept + fresh)
        holds = hold and not agents
        if waiting.get("open") or (holds and not waiting):
            return self._joined_open(stack, frame, slot, waiting, lead, act, [one["doc"] for one in fresh])
        # the standing block, as an OUTPUT: assembled with what the mount serves, its
        # offer map written, the pointer untouched -- the
        # crossing of a `§`, the hook and the checkpoint stay the next bare call's
        block = self._standing(stack)
        if holds:
            # an output that closed already waits at the run: the view joins it as any held
            # view does -- its matter follows, the newest closing stands (`hold`)
            self._dry = False
            self.hold(block, act)
            said = messages.held(act, "mount", principal=True)
            return f"{lead}\n{said}" if lead else said
        # documentary: the mount hands its text over like any output -- measured, cut at
        # the seam under the host's cap, the rest served on the next bare call; a bare
        # render here was the one output that could exceed the cap (le-mount-sous-le-cap)
        return self.delivered(block, agents, lead=lead, act=act)

    @staticmethod
    def _body_asked(spec: dict, name: str):
        """-> what an entry asks of its document's body: True (whole), False (nothing), or
        the LIST of its selections, each one read by the model's grammar -- a badly
        written one refuses here, before anything is composed or written."""
        asked = spec.get("body", False)
        if not isinstance(asked, list):
            return bool(asked)
        if not asked or not all(isinstance(one, str) and one.strip() for one in asked):
            raise Refusal("mount-invalid",
                          messages.refusal_mount_invalid(name))
        for one in asked:
            try:
                tokens.selector(one.strip())
            except Refusal as refusal:
                raise Refusal("mount-invalid",
                              messages.refusal_row(refusal.detail, messages.row_body_of(name))) from refusal
        return [one.strip() for one in asked]

    def _body_parts(self, entry: dict, path: Path) -> list[tuple]:
        """-> the readings an entry's body makes, (cut, title) each: the whole body under
        the document's title, or one reading per selection, titled `<title>[<selection>]`
        -- a selection reads the raw file, as a tagged serve token does."""
        asked = entry.get("body")
        if isinstance(asked, list):
            return [(tokens.selector(one), f"{reading.title(path)}[{one}]") for one in asked]
        return [((), reading.title(path))] if asked else []

    def _mount_matter(self, stack, frame: Frame, fresh: list[dict], view: list[dict]) -> None:
        """The mount's MATTER: every entry comes with the pending frame and makes no segment --
        its body a reading of the block that stands, its laws joining that block's CONSTRAINTS,
        its offers its TOOLS. Everything here reads from `fresh` and from the documents
        themselves: nothing consults the state, so the whole composition plays before the state
        is touched -- `view` is the view as this call leaves it (the standing entries, then the
        entering ones), where a row's tree may be declared.

        documentary: this is where a mount refuses for real -- an unreadable document
        named by a row, an impossible range, a malformed `serve:`. Composing first is
        what makes the call atomic: the caller writes only once every reading has
        been served."""
        self._stacked, self._fused, self._output_clock = [], 0, ""
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_scope = {one.code for one in frame.constraints}, None
        self._segmap, self._remap = [], True
        self._mount_readings(fresh, view, stack)

    def _mount_readings(self, fresh: list[dict], view: list[dict] | None = None,
                        stack: Stack | None = None) -> None:
        """Everything a mount SERVES, in the CALL's own order extended: the bodies, in the order
        of the entries, then the `serve:` rows, then the declared payloads. ONE composer for the
        two callers -- the `mount` verb and a socket's mounted contributor. `view` and `stack`
        are where a row of these documents may find its tree declared (`_around_mount`)."""
        self._enter("mount", fresh, only=("body",))
        self._enter("mount", fresh, only=("rows", "overlay_rows", "payloads"), view=view, stack=stack)

    def _around_mount(self, host: Document, address: str, view: list[dict] | None = None,
                      stack: Stack | None = None) -> tuple[Document, ...]:
        """-> the documents a row of the MOUNTED document `host` looks a tree up in, nearest
        first: itself, then the documents mounted BEFORE it in the view, the last mounted
        first -- a plan's node after its phase after its plan: the chain a mount builds --,
        then the frames of the stack, nearest first. `view` is the view the entry stands in
        (the slot's when none is given); an entry whose document is gone declares nothing."""
        before: list[dict] = []
        for entry in self._mounted() if view is None else view:
            if str(entry.get("doc", "")) == address:
                break
            before.append(entry)
        found: list[Document] = [host]
        for entry in reversed(before):
            try:
                found.append(reading.read(self._mount_path(entry["doc"])))
            except (Refusal, OSError):
                continue
        return tuple(found) + self._around(None, stack)

    @staticmethod
    def holder_of(stack: Stack, frame: Frame) -> str:
        """-> the HOLDER a frame's initialize mounts name: its depth in the stack and its
        document -- what the pop releases, what the session cycle's rewind keeps."""
        return f"{stack.frames.index(frame)}:{frame.document.name}"

    def _release(self, holder: str) -> None:
        """A frame left: the mounts it held at its entry leave with it -- its imports and its
        contributors' (`_leaving`)."""
        if self._dry or self._session is None:
            return
        standing = self._mounted()
        kept, gone = self._leaving(standing, {one["doc"] for one in standing if one.get("held") == holder})
        if gone:
            self._trace("released", holder=holder, docs=[one["doc"] for one in gone])
        if kept != standing:
            persistence.set_mounted(self._session, kept)

    def _leaving(self, standing: list[dict], leaving: set[str]) -> tuple[list[dict], list[dict]]:
        """-> (kept, gone) when the entries at the addresses `leaving` leave the view: what an
        entry IMPORTED leaves with it, transitively -- unless a document still in the view
        imports it too: then it stays, naming that document as its importer and held as that
        one is, down the chain of what it imports. An entry a frame holds leaves only with its
        frame. So an imported entry always names an importer still in the view. The view's own
        record answers who imports what (`_importers`): no document is read."""
        gone: set[str] = set()
        keeper: dict[str, dict] = {}
        for _ in range(len(standing) + 1):        # bounded: an import graph has no cycle
            kept = [one for one in standing if one["doc"] not in gone]
            keeper = self._importers(kept) if leaving else {}
            now = {one["doc"] for one in standing
                   if (one["doc"] in leaving or (one.get("import") in gone and not one.get("held")))
                   and one["doc"] not in keeper}
            if now == gone:
                break
            gone = now
        kept = [one for one in standing if one["doc"] not in gone]
        moved = {one["doc"] for one in kept
                 if one["doc"] in keeper and (one["doc"] in leaving or one.get("import") in gone)}
        held_now = {one["doc"]: str(one.get("held") or "") for one in kept}

        def hold_of(doc: str, seen: tuple[str, ...] = ()) -> str:
            """-> the hold an entry keeps: its own, or -- when it moved to a keeper -- the keeper's."""
            if doc not in moved or doc in seen:
                return held_now.get(doc, "")
            return hold_of(keeper[doc]["doc"], seen + (doc,))

        kept = [{**{key: value for key, value in one.items() if key != "held"},
                 "import": keeper[one["doc"]]["doc"],
                 **({"held": hold_of(one["doc"])} if hold_of(one["doc"]) else {})}
                if one["doc"] in moved else one for one in kept]
        return kept, [one for one in standing if one["doc"] in gone]

    @staticmethod
    def _importers(entries: list[dict]) -> dict[str, dict]:
        """-> each address the entries import, as each one's `imports` recorded it at its entry, to
        the first entry that imports it, in the view's order."""
        found: dict[str, dict] = {}
        for entry in entries:
            for name in entry.get("imports") or ():
                found.setdefault(name, entry)
        return found

    def _importing(self, path: Path, address: str, standing: set[str], trail: tuple[str, ...] = (),
                   own: tuple[str, ...] | None = None,
                   met: list | None = None) -> list[tuple[str, str, tuple[str, ...]]]:
        """-> (address, importer, what it imports) for every document the document at `path`
        (`address`, importing `own` when the caller read it already) brings before itself: its
        imports and its overlays', in the order written, each preceded by its own -- depth first.
        Each imported document is judged by its own `when:`; an address in `standing` -- the
        view, and what enters before it -- enters once and brings nothing again, and `met`
        collects it with its importer. An address met again along its own chain refuses
        `import-cycle`; one no file answers, `mount-missing`."""
        trail = trail + (address,)
        found: list[tuple[str, str, tuple[str, ...]]] = []
        names = own if own is not None else instance.imports_of(self.member.meta, path)
        for name in names:
            if name in trail:
                raise Refusal("import-cycle", messages.refusal_import_cycle(" -> ".join(trail + (name,))))
            if name in standing:
                if met is not None:
                    met.append((name, address))
                continue
            guard = self._guard_of(name)
            if guard and not self._due(Instruction(keyword="CALL", argument=name,
                                                   injected=True, guard=guard)):
                continue
            standing.add(name)
            child = self._mount_path(name)
            theirs = instance.imports_of(self.member.meta, child)
            found += self._importing(child, name, standing, trail, theirs, met)
            found.append((name, address, theirs))
        return found

    def _imported(self, path: Path, address: str, standing: set[str], held_by: str = "",
                  own: tuple[str, ...] | None = None, met: list | None = None) -> list[dict]:
        """-> the entries of what the document at `path` imports (`_importing`): each with its
        body, its laws and its offer, naming its importer, held as its importer is, and
        recording what it imports in its turn (`imports`)."""
        return [{"doc": name, "body": True, "constraints": True, "tools": True, "import": importer,
                 **({"imports": list(theirs)} if theirs else {}), **({"held": held_by} if held_by else {})}
                for name, importer, theirs in self._importing(path, address, standing, own=own, met=met)]

    def _take_hold(self, met: list, holder: str) -> None:
        """The passage entries a frame's imports met in the view take the frame's hold: each
        names the importer it was met under, and what it imports in its turn follows it."""
        if self._dry or self._session is None or not met:
            return
        view = self._mounted()
        by_doc = {one["doc"]: one for one in view}
        queue, changed = list(met), False
        while queue:
            name, importer = queue.pop(0)
            entry = by_doc.get(name)
            if entry is None or entry.get("held"):
                continue
            entry["held"], entry["import"], changed = holder, importer, True
            queue += [(one, name) for one in entry.get("imports") or ()]
        if changed:
            persistence.set_mounted(self._session, view)

    def _collides(self, name: str, held: set[str]) -> None:
        """The laws `name` brings, judged against the codes `held`: a code already in force
        refuses `mount-collision`; the others join `held`."""
        for law in self._mount_force(reading.read(self._mount_path(name)))[0]:
            if law.code in held:
                raise Refusal("mount-collision", messages.refusal_mount_collision(law.code, name))
            held.add(law.code)

    def _hold_laws(self, frame: Frame, names: list[str], holder: str) -> None:
        """The laws and the offer of a contributor CALLed at a frame's entry stay in force
        for the frame's life: a mount of its laws and tools alone -- no matter of its own,
        the CALL serves that once -- held by the frame and released with it."""
        if not names:
            return
        held = {one.code for one in self._in_force(frame)}
        fresh: list[dict] = []
        for name in names:
            self._collides(name, held)
            fresh.append({"doc": name, "body": False, "constraints": True,
                          "tools": True, "held": holder, "matter": False})
        if not self._dry and self._session is not None:
            self._trace("mounted", docs=[one["doc"] for one in fresh], held=holder)
            persistence.set_mounted(self._session, self._mounted() + fresh)

    def _mount_socket(self, frame: Frame, names: list[str], held_by: str = "",
                      stack: Stack | None = None) -> None:
        """The socket's MOUNTED contributors enter the view -- the mount's own matter,
        entered from the advance with the slot already open and never through the `mount`
        verb, which wants a run of its own and renders a block of its own. Every entry
        comes with its body ON: a document that declares `mount:` brings, it asks nothing;
        what it imports enters before it (`_imported`). A name ALREADY in the view is not
        mounted again -- the rule the `mount` verb applies: its entry keeps its holder, its
        laws and offers stand, its matter is not served again and its `exec:` does not play;
        only the names absent from the view are judged against the laws in force and enter.
        So a socket played again within one exchange -- a repair replaying its document from
        the first step, a lap of an iterated door -- never collides with its own codes. A
        contributor comes back at every exchange: the session cycle's rewind, the one that
        opens an exchange, sweeps the previous one, and the socket mounts it afresh, traced
        `mounted` once per exchange. A contributor of a frame's `initialize` socket is HELD
        by that frame (`held_by`): the rewind keeps it, the frame's pop releases it."""
        taken = {one["doc"] for one in self._mounted()}
        fresh: list[dict] = []
        for name in names:
            if name in taken:
                continue
            path = self._mount_path(name)
            own = instance.imports_of(self.member.meta, path)
            fresh += self._imported(path, name, taken, held_by, own=own)
            taken.add(name)
            fresh.append({"doc": name,
                          "body": True, "constraints": True, "tools": True,
                          **({"imports": list(own)} if own else {}), **({"held": held_by} if held_by else {})})
        self._host(frame, fresh, stack)

    def _mount_imports(self, frame: Frame, holder: str, stack: Stack | None = None,
                       imported: tuple[str, ...] | None = None) -> None:
        """A proc's IMPORTS enter the view at its frame's entry -- its own `imports:` and its
        overlays' (`imported`, when the caller read them), transitively, each with its body, its
        laws and its offer, HELD by the frame for its life and naming the proc as their
        importer: the rewind keeps them, the frame's pop releases them. A passage entry they
        meet in the view takes the frame's hold (`_take_hold`)."""
        taken = {one["doc"] for one in self._mounted()}
        met: list = []
        self._host(frame, self._imported(frame.document.path, frame.document.path.name, taken, holder,
                                         own=imported, met=met), stack)
        self._take_hold(met, holder)

    def _host(self, frame: Frame, fresh: list[dict], stack: Stack | None = None) -> None:
        """The entries `fresh` enter the view from the advance: judged against the laws in
        force, each one's `exec:` played, their readings composed BEFORE the state moves --
        a refusal leaves the run's mounts where they stood --, then traced `mounted` and
        written to the slot."""
        if not fresh:
            return
        held = {one.code for one in self._in_force(frame)}
        for entry in fresh:
            self._collides(entry["doc"], held)
        # the entry: each document's `exec:` plays before it brings anything -- the work of a
        # turn's beginning lives here, a contributor mounting afresh at every exchange
        self._enter("mount", fresh, only=("exec",))
        self._mount_readings(fresh, self._mounted() + fresh, stack)
        if not self._dry and self._session is not None:
            self._trace("mounted", docs=[one["doc"] for one in fresh])
            persistence.set_mounted(self._session, self._mounted() + fresh)

    def _mount_bodies(self, entries: list[dict]) -> None:
        """The BODY of each mount that asked for one, as a payload, through the one
        reader: proven by its content, spared when unchanged, served again when it moved,
        forced under `proc_body_serve: always` like a CALLed body. The call calls it for
        the entries it brings, a re-serve for every mount."""
        for entry in entries:
            path = self._mount_path(entry["doc"])
            whole = entry.get("body") is True
            if whole and not reading.body_of(path.read_text(encoding="utf-8")).strip():
                continue
            for cut, title in self._body_parts(entry, path):
                if cut and not self._clipped(path, cut, Path(str(entry["doc"])).name,
                                             reading.title(path), title):
                    continue
                self._serve_document(path, cut, force=self._settings.body_serve == "always",
                                     title=title, origin="mount",
                                     by=Path(str(entry["doc"])).name,
                                     at=str(entry.get("socket") or ""))

    def _serve_overlay_rows(self, host: Document, around=None, callers=None) -> None:
        """The `serve:` rows the OVERLAYS of `host` add, served whole as the base
        enters -- the composer's rows, through the same reader as the base's own; a
        base without overlays, or overlays without rows, serve nothing."""
        for raw in self._overlay_rows(host.path):
            self._serve_line(raw, host, around, callers)

    def _serve_line(self, raw: tuple[str, ...], host: Document, around=None, callers=None) -> None:
        """ONE serve line, token by token, through the one reader -- the nature
        token declares, it never holds: every row serves. `host` is the document that
        carries the row: its `material:` answers for a row that names none, then the
        nearest of `callers` that says one (the frames a re-served frame was called
        through; a mounted document reads its own). `around` gives the documents the
        row's tree may be declared by, nearest first -- `host` alone when nothing is
        given."""
        host_name = host.name
        reading.materials(host)          # its own declaration, judged before a row reads
        nature, mark, line = self._marked(raw)
        material = self._material_name(mark, host.front, callers)
        for token in line:
            try:
                name, cut = reading.ranged(token)
                path, lacks, said = self._located(name, material, around if around is not None else (host,),
                                                  host=host.path)
                if path is None and lacks:
                    self._missing(token, material, lacks, said, host_name)   # a reading due, not served
                    continue
                if path is None:
                    # a GONE document degrades softly and says itself on the bus; a
                    # MALFORMED range refuses. The push latches the run at once
                    # (`_signal`), so it outlives a refusal that follows -- and that is
                    # right: an event happened, and an event does not un-happen.
                    self._signal("engine", "serve-stale",
                                 evidence=messages.gone(name))
                    self.note(token, "", "missing", "serve", by=host_name)
                    self._payloads.append(
                        (token, messages.SECTION_GONE))
                    continue
                if cut and not self._clipped(path, cut, host_name, name, token):
                    continue
                self._serve_document(path, cut, title=self._titled(token, path), origin="serve",
                                     by=host_name, nature=nature)
            except Refusal as refusal:
                # the refusal NAMES its row -- which document declared it, which
                # token could not be read: the agent repairs the row it wrote
                raise Refusal(refusal.code,
                              messages.refusal_row(refusal.detail, messages.row_token_of(token, host_name))) from refusal
