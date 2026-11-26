"""The `journal` domain, layer `acts`: the state a face reads.

A definition belongs here when it chains the journal's reading with what other domains read now, for a face: the journal
replayed (`state_of`) and the launches nobody holds (`unproven`, `wake/acts.py`), given as `gone` in a second state,
never replayed nor packed (`faced`); the state it read is left as it was, and read by its parts. Only verbs and other
acts call it. It may use the lower layers of any domain.
"""
from __future__ import annotations

from pathlib import Path

from house.rules import journal_of
from wake.acts import unproven
from journal.store import state_of


def faced(root: Path, conductor, name: str) -> dict:
    """-> the state a FACE reads: the journal replayed, and `gone` -- the launches nobody holds (`unproven`), read
    now, never replayed nor packed. The faces say `running` of a PROVEN launch alone (`played`); the tick judges
    on the journal, and never reads `gone`."""
    state = state_of(journal_of(root, name))
    return state.but(gone=unproven(root, conductor, state) if state.season.started is not None else set())
