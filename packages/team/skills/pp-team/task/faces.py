"""The `task` domain, layer `faces`: how a task and its messages are put into words.

A definition belongs here when it turns the state of a task into what a member or the owner reads -- a count of
messages, the owner's inbox as a line or as a JSON object, the sentence of a principal unknown (`principal_unknown`),
which every verb or act that calls `principal_of` says for its code -- and gives it back without printing it. A post in
the words of its debt, which a rule writes into the messages it composes, is a rule (`worded`, `task/rules.py`).
"""
from __future__ import annotations

from task.rules import waiting



def counted(messages: list[dict]) -> str:
    """-> `do 1, note 2`: the messages by verb, in the order the verbs appear."""
    seen: dict[str, int] = {}
    for one in messages:
        seen[one.get("verb", "?")] = seen.get(one.get("verb", "?"), 0) + 1
    return ", ".join(f"{verb} {count}" for verb, count in seen.items())


def inbox_line(name: str, state: dict) -> str:
    """-> `review: T1 done · 1 question waiting for you · 2 notices · 1 info · 1 post returned`, or '' when
    nothing waits for the owner."""
    waits = waiting(state)
    parts = [f"{one.body.task} done" for one in waits["done"]]
    asks, told = len(waits["questions"]), len(waits["notices"])
    if asks:
        parts.append(f"{asks} question{'s' if asks > 1 else ''} waiting for you")
    if told:
        parts.append(f"{told} notice{'s' if told > 1 else ''}")
    if waits["infos"]:
        parts.append(f"{len(waits['infos'])} info{'s' if len(waits['infos']) > 1 else ''}")
    if waits["returned"]:
        parts.append(f"{len(waits['returned'])} post{'s' if len(waits['returned']) > 1 else ''} returned")
    return f"{name}: " + " · ".join(parts) if parts else ""


def inbox_object(name: str, state: dict) -> dict | None:
    """-> what waits for the owner in one team, to READ: the questions, the notices, the infos and the posts returned
    with their texts, the tasks resolved by task and id, each with the `at` of its event -- None when nothing waits.
    `waiting()` decides. Each info says `closed`: true for an ask whose task is resolved or stopped, false for an
    info."""
    waits = waiting(state)
    if not (waits["questions"] or waits["notices"] or waits["infos"] or waits["done"] or waits["returned"]):
        return None

    def post(one: dict) -> dict:
        return {"id": one.id, "verb": one.body.verb, "from": one.body.sender, "task": one.body.task,
                "text": one.body.text, "at": one.at}

    return {"team": name, "questions": [post(one) for one in waits["questions"]],
            "notices": [{"id": one["id"], "from": one.get("from"), "about": one.get("about"), "task": one.get("task"),
                         "text": one.get("text"), "awaits": one["awaits"], "at": one.get("at")}
                        for one in waits["notices"]],
            "infos": [{"id": one.id, "from": one.body.sender, "task": one.body.task, "text": one.body.text,
                       "closed": one.body.verb == "ask", "at": one.at} for one in waits["infos"]],
            "done": [{"task": one.body.task, "id": one.id, "at": one.at} for one in waits["done"]],
            "returned": [post(state.task.messages[mid]) for mid in waits["returned"] if mid in state.task.messages]}



def principal_unknown(asked: str, allowed: list[str]) -> str:
    """-> the sentence of `principal-unknown`: the name `--as` gave, and the principals the team allows."""
    return (f"principal-unknown -- `--as {asked}`: the principals are {', '.join(allowed)} (the owner, then "
            "`principals:` of TEAM.md).")
