"""What a run costs: its budget under a cap, and the sums of its records."""
from __future__ import annotations

from dataclasses import dataclass


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
