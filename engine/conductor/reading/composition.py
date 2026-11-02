"""reading.composition -- a document COMPOSED through its overlays: the base, then
each overlay's body, one hash over the whole. The mixin of the facade that holds
it: the member's search paths are its only state."""
from __future__ import annotations

import hashlib
from pathlib import Path

from ..core import document
from ..state import instance
from .tokens import served


class Composing:
    """The composition of a document with its overlays -- a mixin of the facade."""

    def _overlay_bodies(self, path: Path) -> list[str]:
        """The ONE source of hosted prose (there is no second composer): the overlay
        bodies `path` gains, in application order -- the deeper packages first, the
        USER's last: the prose arrives exactly as its law applies. An overlay served
        by itself gains nothing -- only the resolved BASE composes."""
        if instance.resolve(self.member.meta, path.name) != path:
            return []
        bodies = []
        for overlay in instance.overlays_of(self.member.meta, path.name):
            try:
                body = document.body_of(overlay.read_text(encoding="utf-8")).strip()
            except OSError:
                continue
            if body.strip():
                bodies.append(body)
        return bodies

    def _overlay_rows(self, path: Path) -> tuple[tuple[str, ...], ...]:
        """The ONE source of hosted readings, beside the prose: the `serve:` lines
        the overlays of `path` ADD, in application order -- the deeper packages
        first, the USER's last -- served whole when the base enters. A `+` heading a
        line is stripped, a `-` refuses (`overlay-serve-removal`); no overlay, or no
        line: nothing -- the base's own sections keep their pace."""
        if instance.resolve(self.member.meta, path.name) != path:
            return ()
        rows: list[tuple[str, ...]] = []
        for overlay in instance.overlays_of(self.member.meta, path.name):
            rows.extend(document.overlay_serve_lines(document.read(overlay)))
        return tuple(rows)

    def _composed(self, path: Path) -> tuple[str, str]:
        """-> (the served text, its hash) THROUGH the composition: the base document,
        then each overlay's body -- and the hash taken over the COMPOSITION: two readings differ exactly when
        what is served differs. No overlay body: byte-identical to the file."""
        text, digest = served(path)
        bodies = self._overlay_bodies(path)
        if not bodies:
            return text, digest
        composed = "\n\n".join([text.strip()] + bodies) + "\n"
        return composed, hashlib.sha256(composed.encode()).hexdigest()[:6]

    def _composed_body(self, path: Path) -> str:
        """The BODY cut of the same composition: the document's own body, then the
        overlay bodies -- one source, two cuts, never a second composer."""
        own = document.body_of(path.read_text(encoding="utf-8")).strip()
        bodies = self._overlay_bodies(path)
        return "\n\n".join(([own] if own else []) + bodies)
