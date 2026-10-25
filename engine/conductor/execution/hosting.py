"""execution.hosting -- the hosting: the mounted documents, their laws and tools in force. A mixin of the facade: no state of its own."""
from __future__ import annotations

from pathlib import Path
from ..packaging import compiling, events
from .. import reading
from ..core import language, navigation, tokens
from ..state import instance, persistence
from .revive import revive
from .. import rendering
from ..core.errors import Refusal
from ..core.model import Block, Constraint, Document, Frame, Stack, Tool


class Hosting:
    """The hosting: the mounted documents, their laws and tools in force -- a mixin of the facade."""

    def _mounted(self) -> list[dict]:
        """-> the run's standing mounts, straight from the slot -- the slot is their
        one home: a mount lives exactly as long as its exchange (the session cycle's
        rewind sweeps it; the lap of an iterated door keeps it), so nothing about it
        is worth keeping in memory."""
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
                              f"`{name}` -- no such document in a bundle this instance plays")
            path = root / where
        else:
            if not name or Path(name).is_absolute() or ".." in Path(name).parts:
                raise Refusal("mount-missing", f"`{name}` -- a mount names an address, "
                              "never an absolute path nor a `..`")
            path = self._resolve(name)
        if not path.is_file():
            raise Refusal("mount-missing", f"`{name}` -- no document answers that address")
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
                self._signal("engine", "mount-gone", evidence=f"{doc} -- gone")
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

    def _mount_laws(self) -> tuple[Constraint, ...]:
        """-> the constraints the mounts put in force, mount order -- hosted laws
        bind like any law on screen: rendered at every block, owed at every proof."""
        laws: list[Constraint] = []
        for entry in self._mounted():
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

    def _in_force(self, frame: Frame) -> tuple[Constraint, ...]:
        """-> the frame chain, the mounted laws and the laws a socket document left DUE,
        deduped by code (the chain wins) -- what the block shows and what the checkpoint
        owes."""
        held = {one.code for one in frame.constraints}
        extra: list[Constraint] = []
        for one in self._mount_laws() + self._owed_laws():
            if one.code not in held:
                held.add(one.code)
                extra.append(one)
        return frame.constraints + tuple(extra)

    def _tools_in_force(self, frame: Frame) -> tuple[Tool, ...]:
        """-> the frame chain's offer plus the mounted ones, deduped by name."""
        offered = {one.name for one in frame.tools}
        return frame.tools + tuple(one for one in self._mount_tools()
                                   if one.name not in offered)

    def mount(self, specs: list, lead: str = "", by_principal: bool = False,
              act: str = "mount") -> str:
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
        run -- or HELD for the principal's call when the agent mounts in a run its principal
        conducts (`by_principal`, the mark the console read; `act`, what the hold says).
        `lead` is what the mounting script printed before its directive: its answer, one
        output with the view in the LLM's mode, the tool's line alone when the view is held."""
        slot = self._slot()
        restored = persistence.restore(slot, revive) if slot else None
        if restored is None:
            raise Refusal("no-run", "no run is under way -- call `-new` first")
        stack = self._rebind(restored)
        frame = navigation.current(stack)
        held = {one.code for one in self._in_force(frame)}
        fresh: list[dict] = []
        for spec in specs:
            if not isinstance(spec, dict) or not str(spec.get("doc", "")).strip():
                raise Refusal("mount-invalid",
                              'a mount entry is {"doc": <path>[, "body", "constraints", '
                              '"tools": true|false]}')
            name = str(spec["doc"]).strip()
            path = self._mount_path(name)
            scope = str(spec.get("scope", "stacked")).strip() or "stacked"
            if scope not in ("stacked", "nested"):
                raise Refusal("mount-invalid",
                              f"`{scope}` -- a mount scope is `stacked` (one more "
                              "instruction of the current stretch) or `nested` (a "
                              "scope of its own, as a CALL)")
            entry = {"doc": name, "scope": scope, "body": self._body_asked(spec, name),
                     "constraints": bool(spec.get("constraints", True)),
                     "tools": bool(spec.get("tools", True))}
            if entry["constraints"]:
                for law in self._mount_force(reading.read(path))[0]:
                    if law.code in held:
                        raise Refusal("mount-collision",
                                      f"`{law.code}` ({name}) -- already in force here")
                    held.add(law.code)
            fresh.append(entry)
        # the entry: each document's `exec:` plays before it brings anything
        self._enter("mount", fresh, only=("exec",))
        # the READINGS are composed BEFORE anything is written: they are the half of
        # this call that refuses, and a refusal must leave the mount exactly where
        # it stood. Only the last act -- the pending block -- needs the state on disk,
        # because its laws are read back from the slot.
        self._mount_matter(stack, frame, fresh)
        self._trace("mounted", docs=[one["doc"] for one in fresh])
        persistence.set_mounted(slot, self._mounted() + fresh)
        # the standing block, as an OUTPUT: assembled with the mounted segments, its
        # offer map written (the `@n` addresses route), the pointer untouched -- the
        # crossing of a `§`, the hook and the checkpoint stay the next bare call's
        block = self._standing(stack)
        # documentary: the mount hands its text over like any output -- measured, cut at
        # the seam under the host's cap, the rest served on the next bare call; a bare
        # render here was the one output that could exceed the cap (le-mount-sous-le-cap)
        return self.delivered(block, by_principal, lead=lead, act=act)

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
                          f'`{name}` -- a `body` list holds selections, one at least: '
                          '["<start>..<end>", ...]')
        for one in asked:
            try:
                tokens.selector(one.strip())
            except Refusal as refusal:
                raise Refusal("mount-invalid",
                              str(refusal).split(" — ", 1)[-1] + f" -- `body` of `{name}`") from refusal
        return [one.strip() for one in asked]

    def _body_parts(self, entry: dict, path: Path) -> list[tuple]:
        """-> the readings an entry's body makes, (cut, title) each: the whole body under
        the document's title, or one reading per selection, titled `<title>[<selection>]`
        -- a selection reads the raw file, as a tagged serve token does."""
        asked = entry.get("body")
        if isinstance(asked, list):
            return [(tokens.selector(one), f"{reading.title(path)}[{one}]") for one in asked]
        return [((), reading.title(path))] if asked else []

    def _mount_matter(self, stack, frame: Frame, fresh: list[dict]) -> None:
        """The mount's MATTER, in the fusion's own grammar -- nothing parallel: a
        NESTED entry stacks a scope of its own (numbered heading, its tools, its body
        when asked for, its laws verbatim over the chain's codes -- a CALL's habit),
        a STACKED entry comes with the pending frame (its body an INFORMATION payload, its
        laws joining the pending CONSTRAINTS verbatim). Everything here reads from
        `fresh` and from the documents themselves: nothing consults the state, so the
        whole composition plays before the state is touched.

        documentary: this is where a mount refuses for real -- an unreadable document
        named by a row, an impossible range, a malformed `serve:`. Composing first is
        what makes the call atomic: the caller writes only once every reading has
        been served."""
        chain = [one.code for one in frame.constraints]
        self._stacked, self._fused, self._output_clock = [], 0, ""
        self._resolved = {}               # the payload memo lives one output
        self._emitted, self._seg_frame = set(chain), None
        self._segmap, self._remap = [], True
        trail = navigation.render(stack)
        # the mounted scope's heading extends the BARE path: ancestors only, the
        # active frame's pointer stripped -- a mount has no steps to point into
        bare = trail.rsplit("{", 1)[0].rstrip() if "{" in trail else trail
        for entry in (one for one in fresh if one["scope"] == "nested"):
            document = self._mount_source(entry)
            if document is None:
                continue
            name = reading.title(document.path)
            ordinal = len(self._segmap) + 1
            in_force = self._mount_force(document)
            laws = in_force[0] if entry["constraints"] else ()
            tools = in_force[1] if entry["tools"] else ()
            # the heading stays BARE: the assembler numbers every heading of a
            # multi-scope output, exactly as it numbers the frames' own -- and the
            # run and the hour sit on the output's own heading, above them all
            pieces = [f"{Block.MARK} {bare} ▸ {name}"]
            if tools:
                pieces += ["", f"{Block.MARK} TOOLS",
                           f"[{' '.join(one.name for one in tools)}]"]
            for cut, title in self._body_parts(entry, document.path):
                # the one reader decides whether a part enters: one already proven leaves
                # the segment its heading, its tools and its laws, and nothing more
                if cut and not self._clipped(document.path, cut, name, name, title):
                    said = self._payloads.pop()    # the line that says it sits under the heading
                    pieces += ["", f"{Block.MARK} INFORMATION — {said[0]}", said[1]]
                    continue
                admitted = self._admitted(document.path, cut,
                                          force=self._settings.body_serve == "always",
                                          title=title, origin="mount",
                                          by=Path(str(entry["doc"])).name,
                                          at=str(entry.get("socket") or ""))
                if admitted is not None and admitted[1]:
                    pieces += ["", f"{Block.MARK} INFORMATION — {title}", admitted[1]]
            if laws or chain:
                held = [one.code for one in laws if one.code in self._emitted_run]
                lines = [str(one) for one in laws if one.code not in self._emitted_run]
                if held or chain:
                    lines.append(f"[{' '.join(held + chain)}]")
                pieces += ["", f"{Block.MARK} CONSTRAINTS", *lines]
            self._stacked.append((navigation.position(frame), "\n".join(pieces), frame.document.name))
            self._segmap.append({
                "ordinal": ordinal, "frame": name, "stack": f"{bare} ▸ {name}",
                "tools": [one.name for one in tools],
                "constraints": [one.wire() for one in frame.constraints]
                               + [one.wire() for one in laws]})
            self._emitted.update(one.code for one in laws)
            if not self._settings.verbatim_constraints:
                self._emitted_run.update(one.code for one in laws)
        self._mount_readings([one for one in fresh if one["scope"] == "stacked"], fresh)

    def _mount_readings(self, stacked: list[dict], fresh: list[dict]) -> None:
        """Everything a mount SERVES, in the CALL's own order extended: the bodies, then
        the `serve:` rows, then the declared payloads. ONE composer for the two callers --
        the `mount` verb, whose nested entries carry their body under their own heading,
        and a socket's mounted contributor, whose every entry is stacked."""
        self._enter("mount", stacked, only=("body",))
        self._enter("mount", fresh, only=("rows", "overlay_rows", "payloads"))

    @staticmethod
    def holder_of(stack: Stack, frame: Frame) -> str:
        """-> the HOLDER a frame's initialize mounts name: its depth in the stack and its
        document -- what the pop releases, what the session cycle's rewind keeps."""
        return f"{stack.frames.index(frame)}:{frame.document.name}"

    def _release(self, holder: str) -> None:
        """A frame left: the mounts it held at its entry leave with it."""
        if self._dry or self._session is None:
            return
        standing = self._mounted()
        kept = [one for one in standing if one.get("held") != holder]
        if len(kept) != len(standing):
            self._trace("released", holder=holder,
                        docs=[one["doc"] for one in standing if one.get("held") == holder])
            persistence.set_mounted(self._session, kept)

    def _hold_laws(self, frame: Frame, names: list[str], holder: str) -> None:
        """The laws and the offer of a contributor CALLed at a frame's entry stay in force
        for the frame's life: a mount of its laws and tools alone -- no matter of its own,
        the CALL serves that once -- held by the frame and released with it."""
        if not names:
            return
        held = {one.code for one in self._in_force(frame)}
        fresh: list[dict] = []
        for name in names:
            path = self._mount_path(name)
            for law in self._mount_force(reading.read(path))[0]:
                if law.code in held:
                    raise Refusal("mount-collision",
                                  f"`{law.code}` ({name}) -- already in force here")
                held.add(law.code)
            fresh.append({"doc": name, "scope": "stacked", "body": False, "constraints": True,
                          "tools": True, "held": holder, "matter": False})
        if not self._dry and self._session is not None:
            self._trace("mounted", docs=[one["doc"] for one in fresh], held=holder)
            persistence.set_mounted(self._session, self._mounted() + fresh)

    def _mount_socket(self, frame: Frame, names: list[str], held_by: str = "") -> None:
        """The socket's MOUNTED contributors enter the view -- the mount's own matter,
        entered from the advance with the slot already open and never through the `mount`
        verb, which wants a run of its own and renders a block of its own. Every entry is
        stacked, its body ON: a document that declares `mount:` brings, it asks nothing.
        A contributor mounts AFRESH at every turn -- the session cycle's rewind, the one
        that opens an exchange, sweeps the previous one; the lap of an iterated door
        sweeps nothing -- so its codes never collide with themselves. A contributor of a
        frame's `initialize` socket is HELD by that frame (`held_by`): the rewind keeps it,
        the frame's pop releases it."""
        if not names:
            return
        held = {one.code for one in self._in_force(frame)}
        fresh: list[dict] = []
        for name in names:
            path = self._mount_path(name)
            for law in self._mount_force(reading.read(path))[0]:
                if law.code in held:
                    raise Refusal("mount-collision",
                                  f"`{law.code}` ({name}) -- already in force here")
                held.add(law.code)
            fresh.append({"doc": name, "scope": "stacked",
                          "body": True, "constraints": True, "tools": True,
                          **({"held": held_by} if held_by else {})})
        # the entry: each contributor's `exec:` plays before it brings anything -- the
        # work of a turn's beginning lives here, a contributor mounting afresh at every turn
        self._enter("mount", fresh, only=("exec",))
        # the readings are composed BEFORE the state moves, exactly as the verb does it:
        # a refusal here leaves the run's mounts where they stood
        self._mount_readings(fresh, fresh)
        if not self._dry and self._session is not None:
            self._trace("mounted", docs=[one["doc"] for one in fresh])
            persistence.set_mounted(self._session, self._mounted() + fresh)

    def _mount_bodies(self, entries: list[dict]) -> None:
        """The BODY of each mount that asked for one, as a payload, through the one
        reader: proven by its content, spared when unchanged, served again when it moved,
        forced under `proc_body_serve: always` like a CALLed body. The call calls it for
        its stacked entries alone -- a nested entry's body comes with its own heading; a
        re-serve calls it for every mount, the headings being gone with the agent's
        context."""
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

    def _serve_overlay_rows(self, host: Document) -> None:
        """The `serve:` rows the OVERLAYS of `host` add, served whole as the base
        enters -- the composer's rows, through the same reader as the base's own; a
        base without overlays, or overlays without rows, serve nothing."""
        for raw in self._overlay_rows(host.path):
            self._serve_line(raw, host.name, host.front)

    def _serve_line(self, raw: tuple[str, ...], host_name: str, host_front: dict | None = None) -> None:
        """ONE serve line, token by token, through the one reader -- the nature
        token declares, it never holds: every row serves. `host_front` is the front
        matter of the document that carries the row: its `material:` answers for a row
        that names none."""
        nature, mark, line = self._marked(raw)
        material = self._material_name(mark, host_front)
        for token in line:
            try:
                name, cut = reading.ranged(token)
                path = self._stale(name, material)
                if path is None:
                    # a GONE document degrades softly and says itself to the improve; a
                    # MALFORMED range refuses. The push latches the run at once
                    # (`_signal`), so it outlives a refusal that follows -- and that is
                    # right: an event happened, and an event does not un-happen.
                    self._signal("engine", "serve-stale",
                                 evidence=f"{name} -- gone")
                    self.note(token, "", "missing", "serve", by=host_name)
                    self._payloads.append(
                        (token, "(this section's document is gone)"))
                    continue
                if cut and not self._clipped(path, cut, host_name, name, token):
                    continue
                self._serve_document(path, cut, title=self._titled(token, path), origin="serve",
                                     by=host_name, nature=nature)
            except Refusal as refusal:
                # the refusal NAMES its row -- which document declared it, which
                # token could not be read: the agent repairs the row it wrote
                detail = str(refusal).split(" — ", 1)[-1]
                raise Refusal(refusal.code,
                              f"{detail} -- serve row `{token}` "
                              f"of {host_name}") from refusal
