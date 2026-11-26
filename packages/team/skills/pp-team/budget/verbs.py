"""The `budget` domain, layer `verbs`: the command line of the verb that raises a team's budget.

A definition belongs here when it plays that verb: it reads its arguments, raises the team's bounds without a start,
ticks unless told not to, and refuses with the usage. The first decision of `budget/rules.py` judges who raises and
the amount; the verb then reads what the season launched, hands it to the second, writes the event it composes, and
says the sentence of each code declined. A verb is where the skill meets its caller: it may print, end the call and
use every other layer.
"""
from __future__ import annotations

from house.model import USAGE, Declined
from house.rules import journal_of, team_doc
from house.store import house, named_team, owner_of, refuse
from house.verbs import flags, retired_flags
from budget.model import BUDGET_FLAGS
from task.faces import principal_unknown
from budget.rules import budget_asked, budget_raised
from budget.acts import launched_since_start
from net.acts import netted
from journal.store import state_of, written
from tick.acts import ticked


def budget_verb(rest: list[str]) -> int:
    """`team budget <name> [<usd>] [--launches <n>] [--as <principal>] [--no-tick]`: RAISES the team's bounds
    without a start -- `budget` in dollars, `budget-launches` in launches --, judged under the journal's lock
    before anything is written: each above what the team spent since its last start (`budget-invalid`).
    Then `budget-raised {budget, launches, by}`: the replay takes the new limits and lifts `budget-spent`;
    the members keep their runs. Then the relaunch entry laid again, and a tick unless `--no-tick`."""
    root, conductor = house()
    name, rest = named_team(conductor, rest)
    usd = None
    if rest and not rest[0].startswith("--"):
        usd, rest = rest[0], rest[1:]
    retired_flags(rest)
    asked = flags(rest, BUDGET_FLAGS)
    if usd is None and asked["launches"] is None:
        refuse(USAGE)
    try:
        money = None if usd is None else float(usd)
        wakes = None if asked["launches"] is None else int(asked["launches"])
    except ValueError:
        refuse(f"budget-invalid -- `{usd if asked['launches'] is None else asked['launches']}`: dollars are a number, "
               "launches a whole number.")
    if not team_doc(root, name).is_file():
        refuse(f"team-unknown -- no {team_doc(root, name)}: the owner declares the team there.")
    owner = owner_of(root, conductor)
    journal = journal_of(root, name)

    def judge(state: dict, events: list[dict]) -> list[dict]:
        try:
            sender = budget_asked(state, owner, asked["as"], money)
            return budget_raised(sender, money, wakes, launched_since_start(root, state))
        except Declined as declined:
            code, *data = declined.args
            if code == "team-not-started":
                refuse(f"team-not-started -- {name} was never started.")
            if code == "principal-unknown":
                refuse(principal_unknown(*data))
            if code == "budget-invalid":
                unit, asked_for, held = data
                if unit == "usd":
                    refuse(f"budget-invalid -- {name}: {asked_for:g} USD is not above the {held:g} USD spent since "
                           "the start.")
                refuse(f"budget-invalid -- {name}: {asked_for} launches is not above the {held} launched since the "
                       "start.")
            raise ValueError(f"no sentence for the refusal `{code}`")

    made = written(conductor, root, journal, name, judge)[0]
    said = " · ".join(one for one in (f"budget {made.body.budget:g} USD" if "budget" in made.line else "",
                                      f"budget-launches {made.body.launches}" if "launches" in made.line else "")
                      if one)
    print(f"pp-team: {name} · raised #{made.id} · {said}")
    state = state_of(journal)
    if any(one.state == "open" for one in state.task.tasks.values()):
        netted(root, conductor, name, state)       # a task open: the net laid again when gone
    if not asked["no-tick"]:
        ticked(root, conductor, name)
    return 0
