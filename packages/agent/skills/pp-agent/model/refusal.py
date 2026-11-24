"""The refusals raised: what `model` and `rules` refuse, the exceptions an exchange raises, and the form of a
refusal line of the engine."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RefusalLine:
    """The form of the engine's refusal line, as its messages write it (`conductor.core.messages`, read by
    `store.houses.refusal_line`): its `head`, what opens the line before the code; the `separator` between its
    code and its detail; the console's `voice`, what opens every line of the console."""
    head: str
    separator: str
    voice: str

    @property
    def word(self) -> str:
        """-> the word a refusal line carries after the console's voice."""
        return self.head.removeprefix(self.voice).split()[0]


class Refusal(Exception):
    """What `model` and `rules` refuse: its text is what the caller that receives it says as it refuses."""


class VectorRefused(Exception):
    """A vector the launcher does not mount: its `cause` (a code), the `vector`, the `detail` -- said by the
    exchange under the ONE code a caller reads, `vector-refused`."""

    def __init__(self, cause: str, vector: str, detail: str) -> None:
        super().__init__(f"{cause} -- {detail}")
        self.cause, self.vector, self.detail = cause, vector, detail


class Unserved(Exception):
    """The first prompt of an exchange was not served: the bare call failed (`released`). Its text is the refusal
    the exchange says on stderr; `detail` is what the engine said, '' when it said nothing."""

    def __init__(self, said: str, detail: str) -> None:
        super().__init__(said)
        self.detail = detail


class WorkFailure(Exception):
    """A step of the material that refuses -- said by the caller once the wake lock is dealt with."""
