"""The flow of an exchange: its sums by voice, in tokens, as a response's `flow` keeps them."""
from __future__ import annotations

from dataclasses import dataclass

from model.record import _read, _written, only_named


@dataclass(frozen=True)
class Sums:
    """The flow of ONE exchange summed by voice, in tokens, as a response's `flow` keeps it: what the prompts
    carry beside pp's output (`principal`), pp's output served (`conduction`), the calls of the agent's console
    and their results (`pp_input`, `pp_result`), the other tools' (`tool_input`, `tool_result`), the model's
    `words` and its `thinking`; the `calls` to the model; the `context` the last measured call sent it, named
    once a call was measured. `keys` and `kept` stand for sums read alone: what gives them back as they were."""
    principal: int = 0
    conduction: int = 0
    pp_input: int = 0
    pp_result: int = 0
    tool_input: int = 0
    tool_result: int = 0
    words: int = 0
    thinking: int = 0
    calls: int = 0
    context: int | None = only_named()
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(flow) -> "Sums | None":
        """-> the sums a response's `flow` carries, a key it does not name kept for `json()`; None when the
        line says no sums there."""
        return Sums(**_read(Sums, flow)) if isinstance(flow, dict) else None

    def json(self) -> dict:
        """-> the `flow` of a response: the sums read, as they were; the sums composed, every voice and the
        calls always, the `context` when a call was measured."""
        return _written(self)

    def voices(self) -> dict[str, int]:
        """-> its eight voices by their names, in the order a response writes them: a voice the line left
        unsaid, or said null, counts 0."""
        return {"principal": int(self.principal or 0), "conduction": int(self.conduction or 0),
                "pp_input": int(self.pp_input or 0), "pp_result": int(self.pp_result or 0),
                "tool_input": int(self.tool_input or 0), "tool_result": int(self.tool_result or 0),
                "words": int(self.words or 0), "thinking": int(self.thinking or 0)}

    def total(self) -> int:
        """-> the sum of its voices: the flow of the exchange, in tokens."""
        return sum(self.voices().values())

    def plus(self, other: "Sums") -> "Sums":
        """-> these sums and `other`'s, voice by voice, and their calls: the flow of both exchanges, composed
        -- no context, which is one call's."""
        mine, theirs = self.voices(), other.voices()
        return Sums(**{voice: said + theirs[voice] for voice, said in mine.items()},
                    calls=int(self.calls or 0) + int(other.calls or 0))
