"""execution.revive -- the facade's reader of a SAVED frame, handed to persistence:
what a data module cannot read itself (the document, its declared procedure, its
laws and tools, its cycle). One function, its own module: every mixin that restores
a run imports it here, the facade never below."""
from __future__ import annotations

from pathlib import Path

from ..packaging import compiling
from .. import reading


def revive(meta: Path, path: Path) -> tuple:
    """The facade's reader of a SAVED frame -- what persistence cannot read itself:
    the document, its declared procedure, its own laws and tools, its cycle. A data
    module imports no process module: the reading and the compiling stay here."""
    document = reading.read(path)
    laws, tools = compiling.effective(meta, document)
    return document, reading.playable(document), laws, tools, reading.cycles(document)
