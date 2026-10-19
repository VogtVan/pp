"""execution.entry -- the ENTRY of a document: ONE table says what each path a document
enters by applies of its front matter, ONE function applies it. A mixin of the facade: no
state of its own.

The paths, and what each one applies:

- `floor`      the root document `-new` opens -- no CALL enters it, so its `exec:` never plays;
               its body comes with the standing rules (`_boot_payloads`)
- `call`       a `CALL X.md` a `proc:` writes
- `door`       a skill the agent opens (`-s NAME`) -- an injected CALL
- `successor`  the document a `next:` leaves to -- a sibling CALL in the caller's frame
- `socket`     a document `attach:` CALLs at its HOOK
- `cadence`    a cadence due at its socket
- `lap`        a new lap of an iterated or described door -- no body: the door's was proven
- `mount`      a mounted document, by the verb or at its socket (`mount:`) -- its body through
               the mount's own parts (selections, nested headings), all its `serve:` rows
- `reserve`    a frame still in force at `-compacted` -- no `exec:`, a re-serve is no entry;
               its `serve:` sections at the pace its SERVEs played them
- `reserve-mount` a standing mount at `-compacted` -- all its rows again

The steps, in the order an entry applies them:

- `exec`          the document's `exec:` -- before anything it brings
- `body`          its composed body
- `rows`          all its `serve:` sections
- `rows_played`   the `serve:` sections its frame's SERVEs already played
- `overlay_rows`  the `serve:` rows its overlays add
- `payloads`      its declared `payloads:`

And the proof of the document's OWN laws of production when its frame leaves:

- `proof`  owed at the frame's exit (the floor's at its frontier, a lap's at each lap)
- `defer`  carried to the next checkpoint -- a socket or a cadence document leaves its
           laws DUE at the run until the turn's proof names them, no step of its own
"""
from __future__ import annotations

from pathlib import Path

from ..core.model import Constraint, Frame
from ..packaging import compiling
from ..core import document as documents
from ..state import persistence

STEPS = ("exec", "body", "rows", "rows_played", "overlay_rows", "payloads")

_CALLED = frozenset({"exec", "body", "overlay_rows", "payloads", "proof"})
_CONTRIBUTORS = frozenset({"socket", "cadence", "mount"})   # the sites a contributor enters by
ENTRIES: dict[str, frozenset[str]] = {
    "floor": frozenset({"body", "overlay_rows", "payloads", "proof"}),
    "call": _CALLED,
    "door": _CALLED,
    "successor": _CALLED,
    "socket": frozenset({"exec", "body", "overlay_rows", "payloads", "defer"}),
    "cadence": frozenset({"exec", "body", "overlay_rows", "payloads", "defer"}),
    "lap": frozenset({"exec", "payloads", "proof"}),
    "mount": frozenset({"exec", "body", "rows", "overlay_rows", "payloads"}),
    "reserve": frozenset({"body", "rows_played", "overlay_rows", "payloads"}),
    "reserve-mount": frozenset({"body", "rows", "overlay_rows", "payloads"}),
}

# the site an `exec:` line names at the trace: the entry it plays at
_EXEC_SITE = {"call": "call", "door": "call", "successor": "call", "socket": "call",
              "cadence": "call", "lap": "lap", "mount": "mount"}


def site_of(frame: Frame) -> str:
    """-> the path `frame` entered by: `floor` for a frame no CALL opened, the path its
    CALL carries otherwise -- a CALL a `proc:` writes carries none, it is a `call`."""
    if frame.caller is None:
        return "floor"
    return frame.caller.site or "call"


class Entering:
    """The entry: the table read, the steps applied -- a mixin of the facade."""

    def _enter(self, site: str, targets: list, only: tuple = (), by: str = "") -> None:
        """Applies to every target what the table gives `site`, step by step in the order
        of `STEPS` -- all the targets through one step before the next, the way a mount of
        several documents composes its matter. `only` narrows the steps to those an entry
        applies at this moment (a CALL brings its body in one output and opens its frame in
        the next). A target is a Frame (`reserve`), a mount entry dict (`mount`,
        `reserve-mount`) or a Path."""
        given = ENTRIES[site]
        # a CONTRIBUTOR that declares `payloads:` (plan fixes1): its body is the brief of the
        # section its tokens render -- served WITH that section, before it, and not at all
        # when nothing rendered: a brief without its matter instructs nothing. The hold lives
        # on the conductor: an entry narrowed to its body and the one narrowed to its payloads
        # may be two calls
        with_section: set[str] = self.__dict__.setdefault("_bodies_with_section", set())

        def body(target, path, entry) -> None:
            if entry is not None:
                self._mount_bodies([entry])
            else:
                self._serve_document(
                    path, (), force=(site != "reserve" and self._settings.body_serve == "always"),
                    origin="body", by=by or ("the re-serve" if site == "reserve" else ""))

        for step in STEPS:
            if step not in given or (only and step not in only):
                continue
            for target in targets:
                path, document, frame, entry = self._entry_target(target)
                if step == "exec":
                    self._run_exec(path, _EXEC_SITE[site])
                elif step == "body":
                    if (site in _CONTRIBUTORS and "payloads" in given
                            and str(document.front.get("payloads", "")).strip()):
                        with_section.add(str(path))
                    else:
                        body(target, path, entry)
                elif step == "rows":
                    for raw in documents.serve_lines(document):
                        self._serve_line(raw, document.name, document.front)
                elif step == "rows_played":
                    for raw in self._rows_played(frame):
                        self._serve_line(raw, document.name, document.front)
                elif step == "overlay_rows":
                    self._serve_overlay_rows(document)
                elif step == "payloads":
                    at = len(self._payloads)
                    rendered = self._declared_payloads(document)
                    if str(path) in with_section and rendered:
                        with_section.discard(str(path))
                        before = len(self._payloads)
                        body(target, path, entry)            # the brief, then the section it explains
                        brought = self._payloads[before:]
                        del self._payloads[before:]
                        self._payloads[at:at] = brought

    def _entry_target(self, target) -> tuple:
        """-> (path, document, frame, mount entry) of one target the table applies to."""
        from .. import reading
        if isinstance(target, Frame):
            return target.document.path, target.document, target, None
        if isinstance(target, dict):
            path = self._mount_path(target["doc"])
            return path, reading.read(path), None, target
        path = Path(target)
        return path, reading.read(path), None, None

    @staticmethod
    def _rows_played(frame: Frame) -> list:
        """-> the `serve:` lines of the sections the frame's bare SERVEs have played or
        begun -- the pace a CALL keeps, which a re-serve keeps too."""
        sections = documents.serve_sections(frame.document)
        played = sum(1 for one in frame.procedure.instructions
                     if one.keyword == "SERVE" and not one.argument
                     and (one.done or one.slot))
        return [line for section in sections[:played] for line in section]

    # --- the proof a socket document defers ------------------------------------------

    def _defers(self, frame: Frame) -> bool:
        """-> whether `frame` carries its laws' proof to the next checkpoint instead of
        proving at its exit -- the table's `defer`."""
        return "defer" in ENTRIES[site_of(frame)]

    def _owe(self, frame: Frame) -> None:
        """The frame LEAVES with productions its own laws have not proven: those laws stay
        due at the run -- the slot is their home, as it is the mounts' -- until the next
        checkpoint names them; a law already due is not due twice."""
        laws, _ = compiling.effective(self.member.meta, frame.document)
        own = [one for one in laws if one.section == "production"]
        slot = self._session or self._slot()
        if not own or slot is None or self._dry:
            return
        held = persistence.owed_of(slot)
        codes = {Constraint.parse(line).code for line in held}
        persistence.set_owed(slot, held + [one.wire() for one in own if one.code not in codes])
        self._trace("owed", document=frame.document.name, codes=[one.code for one in own])

    def _owed_laws(self) -> tuple[Constraint, ...]:
        """-> the laws a socket document left due, in the order they were left."""
        slot = self._session or self._slot()
        return tuple(Constraint.parse(line) for line in persistence.owed_of(slot)) if slot else ()

    def _settle_owed(self) -> None:
        """A checkpoint was proven: what was due is paid."""
        slot = self._session or self._slot()
        if slot is not None and not self._dry and persistence.owed_of(slot):
            persistence.set_owed(slot, [])
