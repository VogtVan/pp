"""What a run costs and what its context weighs: its budget under a cap, the sums of its records, what its
provider's adapter declares, and its context as the flow of its responses says it."""
from __future__ import annotations

from dataclasses import dataclass, field

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


@dataclass(frozen=True)
class Budget:
    """The budget of a run under a cap: the `cap`, what the run `spent`, what is `left` -- below 0 when the last
    launch went past the cap."""
    cap: float = 0.0
    spent: float = 0.0
    left: float = 0.0

    def json(self) -> dict:
        """-> the budget as the faces and the flow's events say it: `cap`, `spent`, `left`."""
        return {"cap": self.cap, "spent": self.spent, "left": self.left}


@dataclass(frozen=True)
class Cumuls:
    """What the records say of a run, summed: its `responses`, their cost (None when none says one), their
    `launches`, their `overruns` -- the last messages over `ANSWER_BOUND` --, the first message and its hour, the
    hour of the last line of either record."""
    responses: int = 0
    cost_usd: float | None = None
    launches: int = 0
    overruns: int = 0
    first_message: str | None = None
    first_at: str | None = None
    last_at: str | None = None

    def json(self) -> dict:
        """-> the sums as `status --json` says them, in that order."""
        return {"responses": self.responses, "cost_usd": self.cost_usd, "launches": self.launches,
                "first_message": self.first_message, "first_at": self.first_at, "last_at": self.last_at}


@dataclass(frozen=True)
class Declared:
    """What a provider's adapter declares for the context of its runs: the `windows` of the models it names
    (pairs of a model and its window), the `default` window of a model it does not name (None without one), and
    the constants of the estimate -- its `base`, the `ratio` the flow weighs, the part of the thought `kept`."""
    windows: tuple = ()
    default: int | None = None
    base: float = 0
    ratio: float = 1.0
    kept: float = 1.0


@dataclass(frozen=True)
class Scale:
    """What the context of ONE run is judged with: the `window` of its model (None for a caller's command), its
    adapter's `base`, `ratio` and `kept`, and the tokens of the `marble` its launches carry."""
    window: int | None = None
    base: float = 0
    ratio: float = 1.0
    kept: float = 1.0
    marble: int = 0


@dataclass(frozen=True)
class Measure:
    """The context the last call measured by its provider sent the model: its `tokens`, and the `index` of the
    response it closed."""
    tokens: int = 0
    index: int | None = None

    def json(self) -> dict:
        return {"tokens": self.tokens, "index": self.index}


@dataclass(frozen=True)
class Share:
    """pp's part of a run's context: its `tokens`, the `marble`'s within them, its `share` of the context (None
    when it is `over`, past the context), and what the engine `served` beside (None when it counts none)."""
    tokens: int = 0
    marble: int = 0
    share: float | None = None
    over: bool = False
    served: int | None = None

    def json(self) -> dict:
        return {"tokens": self.tokens, "marble": self.marble, "share": self.share, "over": self.over,
                "served": self.served}


@dataclass(frozen=True)
class Context:
    """The context of a run, as the flow of its responses says it: the `flow` of those responses summed, voice
    by voice and their calls, and the `total` of its voices; the `tokens` of the context now; what was `measured`
    last (None when no call was); `estimated`, whether anything was added to a measure; the `window` of the run's
    model and the part of it `used`; `pp`'s part; the `reread` and the response the count starts `since` (None
    without a compaction)."""
    flow: Sums = field(default_factory=Sums)
    total: int = 0
    tokens: int = 0
    measured: Measure | None = None
    estimated: bool = False
    window: int | None = None
    used: float | None = None
    pp: Share = field(default_factory=Share)
    reread: int = 0
    since: int | None = None

    def json(self) -> dict:
        """-> the context as `stats --json` says it, in that order: the voices of the flow and their total
        under `flow`, its calls under `calls`."""
        return {"flow": {**self.flow.voices(), "total": self.total},
                "tokens": self.tokens,
                "measured": self.measured.json() if self.measured is not None else None,
                "estimated": self.estimated, "window": self.window, "used": self.used, "pp": self.pp.json(),
                "calls": self.flow.calls, "reread": self.reread, "since": self.since}


@dataclass(frozen=True)
class Spread:
    """How far estimates stand from what was measured: the `median`, the 10th and the 90th percentile of their
    absolute relative gaps -- None each without a gap."""
    median: float | None = None
    p10: float | None = None
    p90: float | None = None

    def json(self) -> dict:
        return {"median": self.median, "p10": self.p10, "p90": self.p90}


@dataclass(frozen=True)
class Gauged:
    """A run its provider's store measured, as the fit reads it: the context its `first` call sent the model
    and its `last`, the `flow` its responses sum and the `thinking` within it."""
    first: int
    last: int
    flow: int
    thinking: int


@dataclass(frozen=True)
class Fit:
    """The constants of the estimate that fit a provider's measured runs best: the `base`, the `ratio` the flow
    weighs, the part of the thought `kept`, and the gap they leave to the runs' last call -- its `median` and
    its `p90`."""
    base: int
    ratio: float
    kept: float
    median: float | None
    p90: float | None

    def json(self) -> dict:
        """-> the fit as `calibrate --json` says it: the three constants under the names an adapter declares
        them by, then the `gap`."""
        return {"CONTEXT_BASE": self.base, "FLOW_RATIO": self.ratio, "THINKING_KEPT": self.kept,
                "gap": {"median": self.median, "p90": self.p90}}
