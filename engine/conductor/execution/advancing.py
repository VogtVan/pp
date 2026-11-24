"""execution.advancing -- the TRANSACTION of a call that advances the run. A mixin of the facade: no
state of its own, it reads the facade's counters.

A call that advances the run -- an opening, a message, a value, a bare call, a door, a space closed,
a compaction declared -- restores the stack, plays the advance and renders a block. Everything the
advance writes of the SESSION'S STATE (the stack, what was served, the mounts, the exchange counter,
the segment map, the debt, the owed laws, the stop mark) goes through `persistence`, and under the
call's transaction (`persistence.begin`) it is STAGED: the slot is written once, when the call has
its block (`commit`), and not at all when a `Refusal` ends the call (`discard`) -- the slot stands
byte for byte as the call found it, so `nothing played` is true. One refusal is SETTLED: the run
stopped at the repair bound (`Refusal.settled`) -- the state it reports is the one the run reached,
and the call keeps its writes. One call holds TWO transactions: a compaction declared writes its
declaration, then its re-serve -- a script the re-serve launches reads the slot, and the slot must say
the declaration by then. The trace is not a state: an append-only journal, it keeps what the
refused call attempted, and the console's note of the refusal says how many of its lines were not
played (`unplayed`), so a reader that counts the trace (`_count_traced`) leaves them out."""
from __future__ import annotations

import contextlib
import functools

from ..core.errors import Refusal
from ..state import persistence


def advances(verb):
    """The decorator of a verb that ADVANCES the run: the slot resolved, the verb plays under the
    run's transaction -- `resume`, `forward`, `submit`, `play`, `close`; an opening (`start`,
    `reopen`) holds its own, around `_open`, once its key is settled, and `compacted` holds two, the
    declaration then the re-serve. A verb played inside another's transaction stages into it: the
    outer call owns the write."""
    @functools.wraps(verb)
    def played(self, *args, **kwargs):
        self._slot()
        with self._advancing():
            return verb(self, *args, **kwargs)
    return played


class Advancing:
    """The transaction of a call that advances the run -- a mixin of the facade."""

    @contextlib.contextmanager
    def _advancing(self):
        """The ONE site where a call's writes reach the slot: opened on the resolved slot, the
        state staged for the call's length; the call that ends with its block writes once, the
        call a refusal ends writes nothing -- but a SETTLED refusal (the run stopped at the repair
        bound), whose state the run did reach. No slot resolved, or a transaction already open on
        it in this process: nothing to hold here, the outer call owns the write."""
        slot = self._session
        if slot is None or not persistence.begin(slot):
            yield
            return
        self._traced_in_call = 0
        try:
            yield
        except Refusal as refusal:
            if refusal.settled:
                persistence.commit(slot)
            else:
                persistence.discard(slot)
                self._unplayed = self._traced_in_call
            raise
        except BaseException:
            persistence.discard(slot)
            raise
        persistence.commit(slot)
