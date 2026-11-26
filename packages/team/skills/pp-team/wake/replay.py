"""The `wake` domain, layer `replay`: the fold of the journal's events into the wake-ups' part of the state.

A definition belongs here when it folds an event into the wake-ups' part -- the intents and their launches, their ends,
failures and kills, the run each member holds, the flow read, the provider's limits, the halts, the context, the runs
that stand -- or when it is `WAKE_FOLDS`, the table that maps a kind of event to its fold. A fold is a function
`f(state, before, one)`: it takes one event of the journal and writes the keys of its part of the state, and nothing
else. `before` shows the parts that follow this one as they stood before the event -- at `team-started`, the season that
stood before it; the composer of `journal/replay.py` calls the folds, kind by kind, in the order of the domains. A fold
reads nothing but the state, `before` and the event, prints nothing and writes nothing to disk.

At `team-started`, `before` holds the season that stood before the event: the wake-ups' fold keeps a member's limit only
when the new season plays the same provider.

The end of a launch is folded once, by `launch_over`: `wake-ended`, `quota-reached` and `wake-failed` write alike the
tag that is over, the run that answered and the rank of the flow read, and their three folds call it with their body;
what each kind does beyond that stays in its own fold. The wake-ups' fold reads by its attributes -- its body, its
`at`, its `id` -- the event it folds, `team-started` and `resumed` included, and the events the mapping keeps (an
intent, a launch, the start). It reads by key the mapping it folds and its containers.

A fold reads the mapping it folds, not the typed state, so it calls no rule of `wake/rules.py`: two TWINS stand here,
`carrier_folded` and `closed_folded`, with the bodies `carrier_of` and `closed_before` had before those rules read the
typed state -- the carrier of a task, and whether a launch continued a closed task. They read by attribute the event
they are given and by key the mapping. `unpacked` (`journal/replay.py`) calls `carrier_folded` too.
"""
from __future__ import annotations

from season.replay import kept_folded
from task.replay import members_folded


def wake_wake_intent(state: dict, before: dict, one) -> None:
    """`wake-intent`."""
    state["intents"][one.body.tag] = one


def wake_wake_launched(state: dict, before: dict, one) -> None:
    """`wake-launched`."""
    state["launched"][one.body.tag] = one


def launch_over(state: dict, body, flowed: str | None = None):
    """The END of a launch, as `wake-ended`, `quota-reached` and `wake-failed` write it alike, read in the body of
    any of the three: its tag over; the run that answered, when the intent is known, the carrier's; the rank of the
    flow read kept for `flowed` -- by default that same run. -> the intent of the launch, None when none is known."""
    state["ended"].add(body.tag)
    intent = state["intents"].get(body.tag)
    if intent is not None and body.run:               # the run that answered is the carrier's
        state["runs"].setdefault(intent.body.agent, {})[carrier_folded(state, intent.body.task)] = body.run
    if flowed is None and intent is not None:
        flowed = body.run
    if flowed and body.flow is not None:              # the flow read up to there: never again
        state["flow"][str(flowed)] = int(body.flow)
    return intent


def wake_wake_ended(state: dict, before: dict, one) -> None:
    """`wake-ended`."""
    body = one.body
    intent = launch_over(state, body)
    state["ends"].append(one)
    agent = intent.body.agent if intent is not None else None
    if intent is not None:                            # an exchange played: the provider's limit is over
        state["quotas"].pop(agent, None)
    if intent is not None:                            # the context its exchange left, null unmeasured
        state["context"][agent] = body.context
    if intent is not None and body.run:
        pair = (agent, intent.body.task)
        if body.state == "standing" and not closed_folded(state, intent):   # the run waits for a
            state["standing"].add(pair)               # production: continued, nothing delivered to it until
        else:                                         # it parks (`continued_run`) -- parked, or standing
            state["standing"].discard(pair)           # after its ONE continuation on a closed task
    health = before["health"].get(agent) or {}
    if health.get("falls") and health.get("cause") != "silence":   # a fallen member answered: it repents, its
        for slot in [slot for slot in state["failures"] if slot[0] == agent]:   # failures afresh
            del state["failures"][slot]


def wake_wake_routed(state: dict, before: dict, one) -> None:
    """`wake-routed`, `wake-refused`: an act read at the flow: the rank reached."""
    body = one.body
    state["routed"][body.tag] = max(int(state["routed"].get(body.tag) or 0), int(body.line or 0))


def wake_team_started(state: dict, before: dict, one: dict) -> None:
    """`team-started`: a season: the old provider's limit kept, nobody held."""
    started = before["started"]                       # None before the first season
    state["quotas"] = {member: held for member, held in state["quotas"].items()
                       if kept_folded(started, member)["provider"] == kept_folded(one, member)["provider"]}
    state["halts"] = []                               # nobody held by its failures in a row


def wake_quota_reached(state: dict, before: dict, one) -> None:
    """`quota-reached`: the provider's limit: the member held, nothing failed; the run that met it stays the
    carrier's."""
    body = one.body
    intent = launch_over(state, body)
    if intent is not None:
        state["quotas"][intent.body.agent] = {"until": body.until, "said": body.said,
                                              "at": one.at, "task": intent.body.task, "tag": body.tag}


def wake_wake_halted(state: dict, before: dict, one) -> None:
    """`wake-halted`: the same failure in a row: launched there no more."""
    state["halts"].append(one)


def wake_wake_failed(state: dict, before: dict, one) -> None:
    """`wake-failed`: a launch that failed: its run stays the carrier's, the flow of the run it launched is read."""
    body = one.body
    launched = state["launched"].get(body.tag)
    intent = launch_over(state, body, (launched.body.run if launched is not None else None) or body.run)
    state["fails"].append(one)
    if body.house:                                    # the house refused the launch: the member did nothing
        state["house"].add(body.tag)
    if intent is not None:
        slot = (intent.body.agent, intent.body.task)
        if body.reason != "launch-missing" and not body.house:   # the agent's retries count what it did
            state["failures"][slot] = state["failures"].get(slot, 0) + 1
        if (body.state == "standing" and not body.final
                and not closed_folded(state, intent)):    # the run stands: relaunched
            state["standing"].add(slot)
        elif body.state is not None or body.final:    # parked, or its retries spent
            state["standing"].discard(slot)
        if body.final and (state["tasks"].get(intent.body.task) or {}).get("state") != "stopped":
            state["fell"].add(slot)                   # its terminal is the failure's


def wake_wake_killed(state: dict, before: dict, one) -> None:
    """`wake-killed`."""
    body = one.body
    state["ended"].add(body.tag)
    state["killed"].add(body.tag)
    state["kills"].add((body.agent, body.task))


def wake_run_reset(state: dict, before: dict, one) -> None:
    """`run-reset`: `team reset` forgot one run of the member."""
    body = one.body
    held = state["runs"].get(body.member) or {}
    forgot = [carrier for carrier, run in held.items() if run == body.run]
    for carrier in forgot:
        del held[carrier]
    for pair in [pair for pair in state["standing"]   # the pairs of the run forgotten
                 if pair[0] == body.member and carrier_folded(state, pair[1]) in forgot]:
        state["standing"].discard(pair)
    state["reset"][body.member] = one.id


def wake_quota_lifted(state: dict, before: dict, one) -> None:
    """`quota-lifted`: `team resume --quota`: the owner lifts the provider's limit."""
    for member in one.body.members or []:
        state["quotas"].pop(member, None)


def wake_run_renewed(state: dict, before: dict, one) -> None:
    """`run-renewed`: the run detached from its carrier: a new one opens there."""
    body = one.body
    held = state["runs"].get(body.member) or {}
    carrier = body.recurrence or carrier_folded(state, body.task)
    if held.get(carrier) == body.run:
        del held[carrier]


def wake_resumed(state: dict, before: dict, one: dict) -> None:
    """`resumed`: `team resume` took the task back: its failures afresh."""
    resumed = one.body.task
    for slot in [slot for slot in state["failures"] if slot[1] == resumed]:
        del state["failures"][slot]
    for slot in [slot for slot in state["fell"] if slot[1] == resumed]:
        state["fell"].discard(slot)
    for member in members_folded(state, resumed):     # a limit without an hour: lifted by the owner
        if member in state["quotas"] and state["quotas"][member].get("until") is None:
            del state["quotas"][member]
    state["halts"] = [held for held in state["halts"] if held.body.task != resumed]


def carrier_folded(state: dict, task: str | None) -> str | None:
    """-> the CARRIER of a task as a fold reads it, on the mapping it folds: the twin of `carrier_of`, which reads the
    typed state -- an occurrence's recurrence, a ring's ceremony, any other task itself."""
    held = (state.get("tasks") or {}).get(task) or {}
    return held.get("recurrence") or held.get("ceremony") or task


def closed_folded(state: dict, intent: dict) -> bool:
    """-> whether a launch was a CONTINUATION ON A CLOSED TASK, as a fold reads it, on the mapping it folds: the twin
    of `closed_before`, which reads the typed state -- its intent written after the `done` of its task."""
    done = state["done"].get(intent.body.task)
    return done is not None and int(intent.id or 0) > int(done.id or 0)


# The fold of the part `wake` of the state: what ONE event writes in it -- the intents, launches, routes, ends,
# failures and kills of the wake-ups, the runs each member holds by carrier, the flows read, the quotas and the halts.
# `before` holds what this fold reads of a part that follows its own in the order of the domains, as it stood before
# the event: the `started` a new season replaces (the providers of the quotas), the `health` of a member whose end
# makes it repent.
WAKE_FOLDS = {"wake-intent": wake_wake_intent, "wake-launched": wake_wake_launched, "wake-ended": wake_wake_ended,
            "wake-routed": wake_wake_routed, "wake-refused": wake_wake_routed, "team-started": wake_team_started,
            "quota-reached": wake_quota_reached, "wake-halted": wake_wake_halted, "wake-failed": wake_wake_failed,
            "wake-killed": wake_wake_killed, "run-reset": wake_run_reset, "quota-lifted": wake_quota_lifted,
            "run-renewed": wake_run_renewed, "resumed": wake_resumed}
