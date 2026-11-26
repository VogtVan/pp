"""What the context of a run weighs: what its provider's adapter declares, what it is judged with, what a call
measured, pp's part, the context as the flow of its responses says it, and the fit of the estimate."""
from __future__ import annotations

from dataclasses import dataclass, field

from model.flow import Sums


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
