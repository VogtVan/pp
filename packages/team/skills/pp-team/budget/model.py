"""The `budget` domain, layer `model`: what a team's budget is, held as plain values.

A definition belongs here when it is data about what a team may spend and does nothing -- the flags of the verb that
raises the budget, or a type that carries a budget. Nothing here reads the disk, the clock or the environment.

It also holds the budget's part of the team's state -- a frozen class, a field per key of the state its fold writes,
each typed by what it holds -- and the bodies of the budget's three kinds of event: `BudgetRaised`, `BudgetSpent` and
`LaunchesSpent`, in the tuple `BUDGET_BODIES` that `journal/model.py` reads to decode the journal.

A body reads what an old journal wrote under the names of today: `BudgetRaised` reads the key `wakes` as `launches`;
`LaunchesSpent` also reads the kind `wakes-spent`, and its key `wakes` as `launches`. The line itself is never
rewritten.
"""
from __future__ import annotations

from dataclasses import dataclass

from house.model import Body, Part

BUDGET_FLAGS = {"launches": True, "as": True, "no-tick": False}


@dataclass(frozen=True, eq=False)
class BudgetRaised(Body):
    """`budget-raised`: `team budget` raised a bound -- the season's budget in USD, its launches; `launches` reads the
    key `wakes` of a journal of team 0.39.0."""
    KIND = "budget-raised"
    by: str | None = None
    budget: float | None = None
    launches: int | None = None

    @classmethod
    def of(cls, line: dict) -> "BudgetRaised":
        return super().of({**line, "launches": line["launches"] if "launches" in line else line.get("wakes")})


@dataclass(frozen=True, eq=False)
class BudgetSpent(Body):
    """`budget-spent`: the tick found the budget spent -- what was spent against the bound, in USD or, `unit`, in
    launches."""
    KIND = "budget-spent"
    spent: int | float | None = None
    budget: int | float | None = None
    unit: str | None = None


@dataclass(frozen=True, eq=False)
class LaunchesSpent(Body):
    """`launches-spent`: a task's launches are spent -- read from `wakes-spent` too, the kind of team 0.39.0, whose
    bound is the key `wakes`."""
    KIND = "launches-spent"
    KINDS = ("launches-spent", "wakes-spent")
    task: str | None = None
    spent: int | None = None
    launches: int | None = None

    @classmethod
    def of(cls, line: dict) -> "LaunchesSpent":
        return super().of({**line, "launches": line["launches"] if "launches" in line else line.get("wakes")})


BUDGET_BODIES: tuple = (BudgetRaised, BudgetSpent, LaunchesSpent)   # the bodies of this domain's kinds:
#                                                                    `journal/model.py` reads them


@dataclass(frozen=True, eq=False)
class BudgetPart(Part):
    """The part `budget` of the team's state -- the budget: the cost of the season and the team's total, the budget
    spent, the tasks whose launches are spent."""
    cost: float
    total: float
    budget_spent: bool
    launches_spent: set
