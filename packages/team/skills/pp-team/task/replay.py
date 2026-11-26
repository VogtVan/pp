"""The `task` domain, layer `replay`: the fold of the journal's events into the task's part of the state.

A definition belongs here when it folds an event into the task's part -- the tasks and their messages, the debts, the
delegations and the terminals, what was delivered and returned, the owner's box -- or when it is `TASK_FOLDS`, the table
that maps a kind of event to its fold. A fold is a function `f(state, before, one)`: it takes one event of the journal
and writes the keys of its part of the state, and nothing else. `before` shows the parts that follow this one as they
stood before the event -- at `team-started`, the season that stood before it; the composer of `journal/replay.py` calls
the folds, kind by kind, in the order of the domains. A fold reads nothing but the state, `before` and the event, prints
nothing and writes nothing to disk.

The task's fold takes kinds of later domains, because what they change is the task's: `wake-intent`, `quota-reached` and
`wake-failed` for the messages a wake-up carried or failed to deliver (`delivered`, `terminals`), `wake-ended` for the
cost a wake-up adds to its task, and `ceremony-due` for who rang a ceremony at hand, which the task of that ceremony
keeps. A fold reads no domain that follows its own, so these kinds come to the task's fold instead. It keeps two
memories in the state while the journal is folded -- the intents by their tag, and who rang a ceremony at hand; the
composer takes them out before it returns the state, and no snapshot keeps them.

The task's fold reads every kind it folds by the attributes of its typed event -- its body, its `at`, its `id` --, the
kinds of other domains too (`wake-intent`, `wake-ended`, `quota-reached` and `wake-failed` of `wake`, `ceremony-due` of
`rhythm`), and so it reads an event the mapping keeps, such as an intent. It reads by key the mapping it folds, its
containers and the task being folded: it writes the task's dictionary as before, and the `Task` is born from it when
the state is composed.

A fold reads the mapping it folds, not the typed state, so it calls no rule. The rules of the task that a fold needs
have their TWINS here, each with the body its rule had before the rules read the typed state: `members_folded`
(`members_of`), `cited_folded` (`cited_of`), `task_folded` and `owes_folded` (`owes`). `task_folded` stays without
its rule: `task_of`, which no reader called, is gone since team 1.36.57. A twin reads by
attribute the event it is given and by key the mapping; `task_folded` reads by key what the composer gives it, a line
as it was read for a kind without a body, and `cited_folded` reads the `reply` of a post of before on its line. The
folds of `task`, `health` and `wake` and the composer of `journal/replay.py` call them; a twin calls only twins, and
`member_folded` comes from `season/replay.py`.

The reader of the journal (`read_on`, `journal/replay.py`) has two twins of its own here: `worded_folded` (`worded`), a
post in the words of its debt, and `opening_folded` (`opening_of`), the first `do` of a task. They read the context
the reader holds, which has the keys of a working state, and the post by attribute. `worded_folded` returns a
dictionary: the post's line when nothing is translated.
"""
from __future__ import annotations

from task.model import RETIRED_VERBS
from season.replay import member_folded, principal_folded


def task_wake_intent(state: dict, before: dict, one: dict) -> None:
    """`wake-intent`."""
    state["carried"][one.body.tag] = one
    state["delivered"].update(one.body.messages or [])


def task_post(state: dict, before: dict, one) -> None:
    """`post`."""
    body, key = one.body, one.id
    state["messages"][key] = one
    task = state["tasks"].get(body.task)
    if task is not None:
        task["messages"].append(key)
    verb, to = body.verb, body.to
    if verb == "do" and member_folded(state, to):
        if member_folded(state, body.sender):             # a delegation is the do itself
            state["delegations"].append({"id": key, "from": body.sender, "to": to, "task": body.task})
        state["terminals"].discard((to, body.task))   # a new round for that member
    if verb in ("do", "ask") and member_folded(state, to) and task is not None and task["state"] == "open":
        state["debts"][key] = None                    # one debt, open until its first answer
    cited = cited_folded(state, one)
    if cited is not None and owes_folded(state, cited) and state["messages"][cited].body.to == body.sender:
        state["debts"][cited] = key                   # the first answer settles it
        if state["messages"][cited].body.verb == "do":
            state["terminals"].add((body.sender, body.task))
        if verb == "stop" and task["state"] == "open":
            task["state"], task["ended"] = "stopped", one.at
    if body.suspected and cited is not None:          # answered in a suspected member's place: delivered
        state["delivered"].add(cited)
    if body.returned and body.by == "tick" and cited is not None:   # answered before any launch
        state["delivered"].add(cited)                  # delivered it: out of the member's inbox, and back to
        state["returned"].add(cited)                   # its author
        state["returned_to"][cited] = to
    if verb == "stop":                                # delivered at once -- but to a run STANDING on the task:
        state["stops"].setdefault(to, []).append(key)   # the head of one more launch
        if (to, body.task) not in before["standing"]:
            state["delivered"].add(key)
    elif principal_folded(state, to):                     # delivered at once: the principal's box reads it
        state["delivered"].add(key)


def task_task(state: dict, before: dict, one) -> None:
    """`task`."""
    body = one.body
    state["tasks"][body.task] = {"id": body.task, "from": body.sender, "to": body.to,
                                 "text": body.text, "state": "open", "messages": [],
                                 "ceremony": body.ceremony, "period": body.period,
                                 "name": body.name, "at": one.at, "ended": None,
                                 "recurrence": body.recurrence, "context": body.context,
                                 "vectors": list(body.vectors or [])}
    if body.ceremony and state["rung_by"].get((body.ceremony, body.period)):
        state["tasks"][body.task]["by"] = state["rung_by"][(body.ceremony, body.period)]


def task_stopped(state: dict, before: dict, one) -> None:
    """`stopped`."""
    task = state["tasks"].get(one.body.task)
    if task is not None and task["state"] == "open":
        task["state"], task["ended"] = "stopped", one.at


def task_quota_reached(state: dict, before: dict, one: dict) -> None:
    """`quota-reached`."""
    charged_task(state, before, one)
    intent = state["carried"].get(one.body.tag)
    if intent is not None:
        state["delivered"].difference_update(intent.body.messages or [])   # read at its next launch


def task_wake_failed(state: dict, before: dict, one: dict) -> None:
    """`wake-failed`."""
    charged_task(state, before, one)
    intent = state["carried"].get(one.body.tag)
    if intent is not None:
        slot = (intent.body.agent, intent.body.task)
        if one.body.final and (state["tasks"].get(intent.body.task) or {}).get("state") != "stopped":
            state["terminals"].add(slot)              # its terminal is the failure's
        for mid in intent.body.messages or []:        # a retry sends them again; a final failure keeps them
            if one.body.final:
                state["delivered"].add(mid)
            else:
                state["delivered"].discard(mid)


def task_terminal(state: dict, before: dict, one) -> None:
    """`terminal`."""
    state["terminals"].add((one.body.agent, one.body.task))


def task_done(state: dict, before: dict, one) -> None:
    """`done`."""
    resolved = one.body.task
    state["done"][resolved] = one
    task = state["tasks"].get(resolved)
    if task is not None:
        task["state"], task["ended"] = "resolved", one.at
        state["terminals"].add((task["to"], resolved))
    for key, settled in list(state["debts"].items()):
        message = state["messages"].get(key)
        if settled is None and message is not None and message.body.task == resolved:
            state["debts"][key] = "closed"            # the root's answer settles every debt of the task


def task_returned(state: dict, before: dict, one) -> None:
    """`returned`."""
    body = one.body
    state["returned"].add(body.message)
    state["returned_to"][body.message] = body.to
    state["delivered"].add(body.message)


def task_ceremony_due(state: dict, before: dict, one: dict) -> None:
    """`ceremony-due`."""
    body = one.body
    if body.by:                                       # a ring at hand: its task, written next, keeps who rang
        state["rung_by"][(body.ceremony, body.period)] = body.by


def task_deferred(state: dict, before: dict, one) -> None:
    """`deferred`."""
    state["deferred"].append(one)


def task_inbox_seen(state: dict, before: dict, one) -> None:
    """`inbox-seen`."""
    state["seen"] = int(one.body.upto or 0)


def task_inbox_read(state: dict, before: dict, one) -> None:
    """`inbox-read`: one message marked read by the owner (team 1.12.1)."""
    state["read"].add(int(one.body.message or 0))


def task_resumed(state: dict, before: dict, one) -> None:
    """`resumed`: `team resume` took the task back."""
    resumed = one.body.task
    task = state["tasks"].get(resumed)
    if task is not None and task["state"] == "stopped":
        task["state"], task["ended"] = "open", None
    state["resumed"][resumed] = one.id
    for slot in [slot for slot in before["fell"] if slot[1] == resumed]:
        state["terminals"].discard(slot)


def charged_task(state: dict, before: dict, one: dict) -> None:
    """Adds the cost a wake-up's end carries to the task of its intent (`cost` of the task, kept with the task through
    every season and every snapshot)."""
    cost = one.body.cost
    if not isinstance(cost, (int, float)) or isinstance(cost, bool):
        return
    intent = state["carried"].get(one.body.tag)
    task = state["tasks"].get(intent.body.task if intent is not None else None)
    if task is not None:
        task["cost"] = float(task.get("cost") or 0.0) + float(cost)


def members_folded(state: dict, task: str | None) -> list[str]:
    """-> the members a task concerns, as a fold reads it, on the mapping it folds: the twin of `members_of` -- the
    one that holds it, those a message on it was posted to, those woken on it."""
    held = state["tasks"].get(task) or {}
    found = [held.get("to")] + [one.body.to for one in state["messages"].values() if one.body.task == task]
    found += [one.body.agent for one in state["intents"].values() if one.body.task == task]
    return [one for one in dict.fromkeys(found) if member_folded(state, one)]


def cited_folded(state: dict, one: dict) -> int | None:
    """-> the id of the message a post ANSWERS, or None, as a fold reads it, on the mapping it folds: the twin of
    `cited_of` -- a `re` cites it, a principal's `reply` too, and in a journal of before team 0.33.0 a member's
    `reply`, `done` or `escalate`."""
    body = one.body
    verb = body.verb
    if verb == "re":
        return body.re
    if verb == "reply":
        return one.line.get("reply")                  # the key of a reply of before: no body names it
    if verb in ("done", "escalate") and member_folded(state, body.to):
        dos = [key for key, message in state["messages"].items()
               if message.body.verb == "do" and message.body.sender == body.to
               and message.body.to == body.sender and message.body.task == body.task and key < one.id]
        return max(dos) if dos else None
    return None


def task_folded(state: dict, one: dict) -> str | None:
    """-> the task an event belongs to, as a fold reads it, on the mapping it folds -- the task it names, or the task
    of the intent its `tag` names."""
    if one.get("task"):
        return one["task"]
    intent = state["intents"].get(one.get("tag")) if one.get("tag") else None
    return intent.body.task if intent is not None else None


def owes_folded(state: dict, key) -> bool:
    """-> whether the message's debt stands, as a fold reads it, on the mapping it folds: the twin of `owes`."""
    return state["debts"].get(key, "x") is None


def opening_folded(state: dict, task: str) -> int | None:
    """-> the task's OPENING message, as the reader of the journal reads it, on the mapping it holds: the twin of
    `opening_of` -- the first `do` its author posted to its member, None when the journal holds none."""
    held = state["tasks"].get(task) or {}
    return next((key for key in held.get("messages") or []
                 if key in state["messages"] and state["messages"][key].body.verb == "do"
                 and state["messages"][key].body.sender == held.get("from")
                 and state["messages"][key].body.to == held.get("to")), None)


def worded_folded(state: dict, one) -> dict:
    """-> a post as the faces say it, in the words of the debt, as the reader of the journal reads it, on the mapping it
    holds: the twin of `worded` -- a member's `done`, `reply` or `escalate` to a member, and a principal's `reply`,
    written before team 0.36.0, said `re` to the message it answers with `was` its verb; an `escalate` to a principal
    said as the team's `notice`, `about` the member that wrote it; a `note` written before team 0.47.0 said `info`; any
    other post as its line says it."""
    body, line = one.body, one.line
    verb = body.verb
    if verb == "note":                                           # the principal's note until team 0.47.0: an info
        return {**{key: value for key, value in line.items() if key != "verb"}, "verb": "info", "was": verb}
    if verb not in RETIRED_VERBS:
        return line
    rest = {key: value for key, value in line.items() if key not in ("verb", "reply")}
    if verb == "escalate" and not member_folded(state, body.to):
        about = body.sender if member_folded(state, body.sender) else None
        started = state["started"]
        return {**rest, "verb": "notice", "from": (started.team if started is not None else None) or one.team,
                **({"about": about} if about else {}), "was": verb}
    cited = cited_folded(state, one)
    if cited is None and verb == "done":
        cited = opening_folded(state, body.task)
    return {**rest, "verb": "re", "re": cited, "was": verb}


# The fold of the part `task` of the state: what ONE event writes in it -- the tasks, their messages and debts, the
# delegations and terminals, what was delivered and returned, the owner's box; from the ends of a launch, the messages
# its intent carried and the cost it adds to its task. Its memories: `carried`, the intents by tag, and `rung_by`, who
# rang a ceremony at hand -- never packed. `before` holds what this fold reads of a part that follows its own in the
# order of the domains (`standing`, `fell`), as it stood before the event.
TASK_FOLDS = {"wake-intent": task_wake_intent, "wake-ended": charged_task, "post": task_post, "task": task_task,
            "stopped": task_stopped, "quota-reached": task_quota_reached, "wake-failed": task_wake_failed,
            "terminal": task_terminal, "done": task_done, "returned": task_returned,
            "ceremony-due": task_ceremony_due, "deferred": task_deferred, "inbox-seen": task_inbox_seen,
            "inbox-read": task_inbox_read, "resumed": task_resumed}
