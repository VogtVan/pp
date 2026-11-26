"""The `budget` domain, layer `replay`: the fold of the journal's events into the budget's part of the state.

A definition belongs here when it folds an event into the budget's part -- the cost of the season and the total of every
season, whether the budget is spent, the launches spent -- or when it is `BUDGET_FOLDS`, the table that maps a kind of
event to its fold. The cost a wake-up adds to its own task is the task's fold's. A fold is a function `f(state, before,
one)`: it takes one event of the journal and writes the keys of its part of the state, and nothing else. `before` shows
the parts that follow this one as they stood before the event -- at `team-started`, the season that stood before it; the
composer of `journal/replay.py` calls the folds, kind by kind, in the order of the domains. A fold reads nothing but the
state, `before` and the event, prints nothing and writes nothing to disk.

The budget's fold reads `launches-spent`, and `wakes-spent` through the same body, by the attributes of its body, and
so the kinds of other domains it takes: the cost of `wake-ended`, `quota-reached` and `wake-failed`, the task of
`resumed`. `team-started`, `budget-spent` and `budget-raised` come typed, and the fold reads nothing of them but
their kind.
"""
from __future__ import annotations


def charged(state: dict, before: dict, one: dict) -> None:
    """Adds the cost a wake-up's end carries to the team's season and to the team's total; the task of its intent
    takes it in the fold of `task`."""
    cost = one.body.cost
    if not isinstance(cost, (int, float)) or isinstance(cost, bool):
        return
    state["cost"] += float(cost)
    state["total"] = float(state.get("total") or 0.0) + float(cost)   # every season's, never counted afresh


def budget_team_started(state: dict, before: dict, one: dict) -> None:
    """`team-started`: a season: the counts afresh."""
    state["cost"], state["budget_spent"] = 0.0, False
    state["launches_spent"] = set()


def budget_budget_spent(state: dict, before: dict, one: dict) -> None:
    """`budget-spent`."""
    state["budget_spent"] = True


def budget_budget_raised(state: dict, before: dict, one: dict) -> None:
    """`budget-raised`: `team budget` raised a bound: spent no more."""
    state["budget_spent"] = False


def budget_launches_spent(state: dict, before: dict, one) -> None:
    """`launches-spent`, `wakes-spent`: `wakes-spent`: the kind of before (team 0.39.0), read by the same body."""
    state["launches_spent"].add(one.body.task)


def budget_resumed(state: dict, before: dict, one: dict) -> None:
    """`resumed`: `team resume`: the task's launches count afresh."""
    state["launches_spent"].discard(one.body.task)


# The fold of the part `budget` of the state: what ONE event writes in it -- the cost of the season and the team's
# total (`charged`), the budget spent and raised, the tasks whose launches are spent. `before` holds what a fold reads
# of a part that follows its own in the order of the domains, as it stood before the event.
BUDGET_FOLDS = {"team-started": budget_team_started, "wake-ended": charged,
              "quota-reached": charged, "wake-failed": charged,
              "budget-spent": budget_budget_spent, "budget-raised": budget_budget_raised,
              "launches-spent": budget_launches_spent, "wakes-spent": budget_launches_spent,
              "resumed": budget_resumed}
