"""The `task` domain, layer `rules`: what the team's state says of its tasks, and what is written about them.

A definition belongs here when it computes its answer from the state and the values it is given: who owes what to whom,
a member's place in a task, the inbox of a member or of the owner, the acts read from a member's words and checked,
where each act goes, a post in the words of its debt (`worded`). It also holds the DECISIONS of the tasks, which compose
by `made` and `but` the bodies the journal's writer receives: what a resolution writes, `schedule-off` among them; what
a stop or a routed act writes; what `team post` writes, judged in two steps (`post_checked`, `post_decided`); what `team
inbox --seen` writes; what `team resume --task` writes, judged before and after the verb reads the budget
(`resume_checked`, `resume_decided`); the task and the post `team start` opens (`start_opened`); the tasks `team stop`
chooses (`stop_chosen`) and, once the verb has killed what it kills, what it writes of each (`stop_decided`). A decision
that refuses DECLINES by a code with its data, and the verb says the sentence; `principal_of`, which decisions call,
declines by a code too (`principal-unknown`); `named`, which reads the words of a flag, declines by the sentence the
refusal prints, and its verb refuses it. No rule here refuses. It also holds a question a task's rule asks of a later
domain's matter -- which recurrences are alive --, because a rule reads no domain that follows its own. It reads no
disk, no clock and no environment and prints nothing: the hour and what the verb read come to it as values, and what
needs the system belongs to `store` or to a verb.

It reads the typed state by its parts -- `state.task.tasks`, `state.task.messages`, `state.season.started` -- a task
by its fields and an event by `one.id` and `one.body`; a start or a task that may be missing is tested by `None`. What
it reads by key is a dictionary: the containers a part keeps (`debts`, `delegations`, `returned_to`), and the acts a
member sends, read on the JSON the member printed (`candidates_of`, `act_formed`, `routed`). `worded` returns a
dictionary in every case: the post's line when nothing is translated. `cited_of` reads the `reply` of a post written
before on its line, since no body names that key.
"""
from __future__ import annotations

import json

from house.model import Declined, decline
from house.rules import vector_formed
from declaration.model import NAME_CHARS
from season.model import CLOSED, ScheduleOff
from template.model import ALL
from task.model import (ACT_OPENED, ELEMENTS, RETIRED_VERBS, Done, InboxRead, InboxSeen, Post, Refused, Resumed,
                        Returned, Stopped, TaskBorn)
from season.rules import is_member, is_principal


def cited_of(state: dict, one: dict) -> int | None:
    """-> the id of the message a post ANSWERS, or None: a `re` cites it, a principal's `reply` too; in a journal
    written before team 0.33.0 a member's `reply` cites the ask it answered, and its `done` or `escalate` to the
    member that delegated answers that member's last `do` to it on the task."""
    body = one.body
    verb = body.verb
    if verb == "re":
        return body.re
    if verb == "reply":
        return one.line.get("reply")                  # the key of a reply of before: no body names it
    if verb in ("done", "escalate") and is_member(state, body.to):
        dos = [key for key, message in state.task.messages.items()
               if message.body.verb == "do" and message.body.sender == body.to
               and message.body.to == body.sender and message.body.task == body.task and key < one.id]
        return max(dos) if dos else None
    return None


def opening_of(state: dict, task: str) -> int | None:
    """-> the task's OPENING message: the first `do` its author posted to its member -- what the member that
    holds the task answers to close it. None when the journal holds none (a ceremony rung before team 0.33.0)."""
    held = state.task.tasks.get(task)
    if held is None:
        return None
    messages = state.task.messages
    return next((key for key in held.messages or []
                 if key in messages and messages[key].body.verb == "do"
                 and messages[key].body.sender == held.sender
                 and messages[key].body.to == held.to), None)


def owes(state: dict, key) -> bool:
    """-> whether the message's debt stands: a `do` or an `ask` delivered to a member, no answer of its yet."""
    return state.task.debts.get(key, "x") is None


def is_notice(state: dict, one: dict) -> bool:
    """-> whether a post is a NOTICE of the team to a principal: a `notice`, or an `escalate` to a principal in a journal
    written before team 0.36.0."""
    return one.body.verb == "notice" or (one.body.verb == "escalate" and not is_member(state, one.body.to))


def notice_about(state: dict, one: dict) -> str | None:
    """-> the member a notice concerns -- its `about`, or the member that wrote an `escalate` to a principal before team
    0.36.0 --; None for a guard's notice."""
    if one.body.verb == "notice":
        return one.body.about
    return one.body.sender if is_member(state, one.body.sender) else None


def principal_answered(state: dict) -> set:
    """-> the ids a principal's answer cites: its `re`, or its `reply` written before team 0.36.0."""
    return {cited_of(state, one) for one in state.task.messages.values()
            if one.body.verb in ("re", "reply") and is_principal(state, one.body.sender)} - {None}


def members_of(state: dict, task: str | None) -> list[str]:
    """-> the members a task concerns: the one that holds it, those a message on it was posted to, those woken
    on it."""
    held = state.task.tasks.get(task)
    found = [held.to if held is not None else None] + [one.body.to for one in state.task.messages.values()
                                                       if one.body.task == task]
    found += [one.body.agent for one in state.wake.intents.values() if one.body.task == task]
    return [one for one in dict.fromkeys(found) if is_member(state, one)]


def task_state(state: dict, task) -> str | None:
    """-> the state of the task -- `open`, `stopped`, `resolved` --, None for a task the state does not hold."""
    held = state.task.tasks.get(task)
    return held.state if held is not None else None


def inbox(state: dict, agent: str) -> list[dict]:
    """-> the messages to `agent` that no event delivered, on tasks not resolved, in order."""
    return [one for one in state.task.messages.values()
            if one.body.to == agent and one.id not in state.task.delivered
            and task_state(state, one.body.task) != "resolved"]


def is_open(state: dict, task) -> bool:
    return task_state(state, task) == "open"


def owed_by(state: dict, member: str) -> list[int]:
    """-> the debts the member owes, in order: each `do` or `ask` delivered to it on an open task that no
    answer of its settled yet."""
    return [key for key, one in sorted(state.task.messages.items())
            if one.body.to == member and owes(state, key) and key in state.task.delivered
            and is_open(state, one.body.task)]


def receives(state: dict, member: str) -> bool:
    """-> whether the member has something to receive: a message the ordinary rule would deliver it now;
    the members' `info`s alone are nothing to receive (`quiet`)."""
    return any(loud(state, box) for task, box in dues(state, member))


def principal_opening(state: dict, key: int) -> bool:
    """-> whether the debt is the opening a principal posted: never answered in its member's place."""
    message = state.task.messages.get(key)
    return (key == opening_of(state, message.body.task if message is not None else None)
            and not is_member(state, message.body.sender if message is not None else None))


def parent_of(state: dict, agent: str, task: str) -> str:
    """-> whom the agent reports to on this task: the one that delegated it, else the task's
    author (a principal)."""
    for one in reversed(state.task.delegations):
        if one["to"] == agent and one["task"] == task:
            return str(one["from"])
    held, started = state.task.tasks.get(task), state.season.started
    return str((held.sender if held is not None else None)
               or (started.body.owner if started is not None else None) or "")


def told_of(state: dict, member: str, task: str) -> str:
    """-> whom the team's NOTICE about the member on this task goes to -- a person with a box, never the team: the
    member that delegated the task to it, else the task's principal, the owner when the team itself wrote the task (a
    ceremony's)."""
    for one in reversed(state.task.delegations):
        if one["to"] == member and one["task"] == task:
            return str(one["from"])
    started, held = state.season.started, state.task.tasks.get(task)
    author = held.sender if held is not None else None
    team, owner = (started.team, started.body.owner) if started is not None else (None, None)
    return str(author if author and author != team else owner or "")


def is_root(state: dict, agent: str, task: str) -> bool:
    """-> whether the agent holds the task from a principal: its `done` resolves the task."""
    held = state.task.tasks.get(task)
    return held is not None and held.to == agent and not is_member(state, held.sender)


def edges_of(state: dict, task: str) -> set[tuple[str, str]]:
    """-> the (agent, the one it reports to) pairs that route on the task: the `reports:` edges,
    and on a ceremony task each participant reporting to the ceremony's facilitator."""
    started, held = state.season.started, state.task.tasks.get(task)
    reports, ceremonies = (started.body.reports, started.body.ceremonies) if started is not None else (None, None)
    pairs = {(child, str(one.get("to"))) for one in reports or [] for child in one.get("from") or []}
    ceremony = held.ceremony if held is not None else None
    for one in ceremonies or []:
        if ceremony is not None and one.get("name") == ceremony:
            pairs |= {(child, str(one.get("facilitator"))) for child in one.get("participants") or []}
    return pairs


def next_task(state: dict) -> str:
    return f"T{len(state.task.tasks) + 1}"


def candidates_of(text: str) -> list[tuple[list | None, str]]:
    """-> the CANDIDATES a `words` carries, in their order: each JSON value found in its text -- the text alone,
    a sentence around it, a ``` block, several values -- that is an object, or a list of objects, with a key of
    a form (`do`, `ask`, `re`, `info`) at its first level, as `(elements, "")`; and each object opened on such a key
    that does not read as JSON, as `(None, why)`. Anything else is SAID: prose, a table, a JSON value without
    the key of a form, a verb of an answer before team 0.33.0 (`done`, `reply`, `escalate`) -- nothing of it
    is a candidate. A value read is never searched inside: what it holds is its own."""
    decoder, found, spans, at = json.JSONDecoder(), [], [], 0
    while True:
        starts = [one for one in (text.find("{", at), text.find("[", at)) if one >= 0]
        if not starts:
            break
        start = min(starts)
        try:
            value, end = decoder.raw_decode(text, start)
        except ValueError:
            at = start + 1
            continue
        if not isinstance(value, (dict, list)):
            at = start + 1
            continue
        spans.append((start, end))
        elements = [value] if isinstance(value, dict) else value
        if elements and all(isinstance(one, dict) for one in elements) and any(
                form in one for one in elements for form in ELEMENTS):
            found.append((start, elements, ""))
        at = end
    for opened in ACT_OPENED.finditer(text):
        if not any(start <= opened.start() < end for start, end in spans):
            found.append((opened.start(), None, f"`{text[opened.start():opened.start() + 40]}` is no JSON value: "
                                                "an act is one JSON object, or a list of them, written whole"))
    return [(elements, why) for _, elements, why in sorted(found, key=lambda one: one[0])]


def act_formed(elements: list) -> None:
    """Judges the FORM of a candidate before its sense: every element an object of ONE form, no key beyond
    that form's, its values of their kind -- `do` an object of member -> work or a list of members, `ask` and
    `info` an object of `to` and `text` or a text, `re` the id of a message and a text. A fault raises `Refused`
    with its reason."""
    for one in elements:
        if not isinstance(one, dict):
            raise Refused(f"{json.dumps(one)[:40]} is not an object: each element of an act is one object")
        forms = [form for form in ELEMENTS if form in one]
        if len(forms) != 1:
            raise Refused(f"an element carries {' and '.join(forms) or 'none'} of the forms do, ask, re, info: "
                          "it carries exactly one")
        form = forms[0]
        extra = sorted(set(one) - ELEMENTS[form])
        if extra:
            raise Refused(f"the key `{extra[0]}` does not belong to the form `{form}`, whose keys are "
                          + ", ".join(f"`{key}`" for key in sorted(ELEMENTS[form])))
        said = one[form]
        if form == "do" and not (
                (isinstance(said, dict) and said and all(isinstance(key, str) and (isinstance(work, str) or (
                    isinstance(work, dict) and isinstance(work.get("text"), str) and not set(work) - {"text", "vector"}))
                                                         for key, work in said.items()))
                or (isinstance(said, list) and said and all(isinstance(name, str) for name in said))):
            raise Refused(f"do {json.dumps(said)[:40]}: the form is {{\"<member>\": \"<the work>\"}}, "
                          "{\"<member>\": {\"text\": \"<the work>\", \"vector\": \"<family>:<id>\"}} or a list of members")
        if form == "do" and isinstance(said, dict):
            for work in said.values():
                if isinstance(work, dict) and "vector" in work and not vector_formed(work["vector"]):
                    raise Refused(f"vector-invalid -- do {json.dumps(work['vector'])[:40]}: a vector is "
                                  "`<family>:<id>`")
        if form == "ask" and not (isinstance(said, str) or (
                isinstance(said, dict) and not set(said) - {"to", "text"}
                and all(isinstance(value, str) for value in said.values()))):
            raise Refused(f"ask {json.dumps(said)[:40]}: the form is {{\"to\": \"<member>\", \"text\": \"...\"}}")
        if form == "info" and not (isinstance(said, str) or (
                isinstance(said, dict) and not set(said) - {"to", "text"}
                and all(isinstance(value, str) for value in said.values()))):
            raise Refused(f"info {json.dumps(said)[:40]}: the form is {{\"to\": \"<member or principal>\", \"text\": \"...\"}}")
        if form == "re" and (cited_id(said) is None or not isinstance(one.get("text", ""), str)):
            raise Refused(f"re {json.dumps(said)[:40]}: the form is {{\"re\": <the message number>, \"text\": \"...\"}}")


def resolution(state: dict, task: str, result) -> list:
    """-> what closes a task the root answered: `done` with the result, a `returned` for every post to an agent
    left undelivered on it, `schedule-off` when no task stays open, no ceremony is declared and no recurrence lives."""
    events: list = [Done.made(task=task, result=result)]
    for one in state.task.messages.values():
        if one.body.task == task and one.id not in state.task.delivered:
            events.append(Returned.made(message=one.id, to=one.body.sender))
    others_open = [one for one in state.task.tasks.values() if one.id != task and one.state == "open"]
    started = state.season.started
    if (not others_open and not ((started.body.ceremonies if started is not None else None) or [])
            and not live_recurrences(state) and state.season.schedule):
        events.append(ScheduleOff.made())
    return events


def cited_id(said) -> int | None:
    """-> the id a `re` names -- `12` or `"#12"` --, None for any other value."""
    if isinstance(said, bool):
        return None
    if isinstance(said, int):
        return said
    text = str(said).strip().lstrip("#")
    return int(text) if text.isdigit() else None


def routed(state: dict, intent: dict, elements: list[dict], settled: set | None = None,
           closed: set | None = None) -> list:
    """-> the events an ACT writes: its ELEMENTS as posts, in their order -- a `do` to each member named that
    reports to the acting one, an `ask` to any member of the team or
    to a principal, an answer `{"re": <id>}` to the author of the message it cites, on that message's task,
    an `info` to any member or principal (the parent on the task when it names nobody): no debt, off
    every edge (row 114). The first answer to a `do` or an `ask` settles its debt; a later one is posted `info:
    true`. The ROOT's answer to its task's opening resolves the task (`resolution`). Refused, nothing written: a
    member nobody declared, a `do` off the edges, a `re` citing a message never delivered to the member or
    citing an `info`. `settled` and `closed` carry what the acts said before it in the
    same `words` settled and closed."""
    agent, task = intent.body.agent, intent.body.task
    events: list = []
    held = state.task.tasks.get(task)
    edges = edges_of(state, task)
    settled = set() if settled is None else settled
    closed = set() if closed is None else closed
    for one in elements:
        form = next(form for form in ELEMENTS if form in one)
        if form == "do":
            asked = one["do"]
            pairs = list(asked.items()) if isinstance(asked, dict) else [(name, (held.text if held is not None else None)
                                                                                 or "")
                                                                          for name in (asked or [])]
            for target, work in pairs:
                if not is_member(state, target):
                    raise Refused(f"do names `{target}`, a member nobody declared")
                if (target, agent) not in edges:
                    raise Refused(f"do names `{target}`, off the edges: `{target}` does not report to `{agent}`")
                text, vector = (work.get("text"), work.get("vector")) if isinstance(work, dict) else (work, None)
                events.append(Post.made(task=task, sender=agent, to=target, verb="do", text=str(text),
                                        **({"vector": vector} if vector else {})))
        elif form == "ask":
            asked = one["ask"] if isinstance(one["ask"], dict) else {"text": one["ask"]}
            target = asked.get("to") or parent_of(state, agent, task)
            if not is_member(state, target) and not is_principal(state, target):
                raise Refused(f"ask names `{target}`, a member nobody declared")
            events.append(Post.made(task=task, sender=agent, to=target, verb="ask", text=str(asked.get("text") or "")))
        elif form == "info":
            said = one["info"] if isinstance(one["info"], dict) else {"text": one["info"]}
            target = said.get("to") or parent_of(state, agent, task)
            if not is_member(state, target) and not is_principal(state, target):
                raise Refused(f"info names `{target}`, a member nobody declared")
            events.append(Post.made(task=task, sender=agent, to=target, verb="info", text=str(said.get("text") or "")))
        else:
            cited = cited_id(one["re"])
            answered = state.task.messages.get(cited) if cited is not None else None
            if answered is None or answered.body.to != agent or cited not in state.task.delivered:
                raise Refused(f"re #{str(one['re']).lstrip('#')}: no message #{str(one['re']).lstrip('#')} "
                              f"was delivered to `{agent}`")
            if answered.body.verb == "info":
                raise Refused(f"re #{cited} answers an info: an info owes nothing, nobody answers it")
            on = answered.body.task
            due = owes(state, cited) and cited not in settled and on not in closed
            post = Post.made(task=on, sender=agent, to=answered.body.sender, verb="re", re=cited,
                             text=str(one.get("text") or ""))
            if not due:
                post = post.but(info=True)
            events.append(post)
            if due:
                settled.add(cited)
                if cited == opening_of(state, on) and is_root(state, agent, on):
                    closed.add(on)
                    events += resolution(state, on, post.text)
    return events


def named(conductor, asked: dict) -> dict:
    """-> the `name` field a task is born with: `{"name": <text>}` under `--name`, `{}` without --
    a task born without a name writes the fields it always wrote. A name is what a user types: free
    text on ONE line, its spaces at the edges dropped, 1 to `NAME_CHARS` characters, every one
    printable -- a line break or a control character would split the task's line in `status`, `log`
    and `watch`. `name-invalid` otherwise."""
    given = asked.get("name")
    if given is None:
        return {}
    text = given.strip()
    if not text or len(text) > NAME_CHARS or not text.isprintable():
        shown_name = " ".join(given.split())[:40]
        decline(f"name-invalid -- `--name {shown_name}`: a task's name is one line of 1 to {NAME_CHARS} printable "
               "characters.")
    return {"name": text}


def live_recurrences(state: dict) -> list[dict]:
    """-> the recurrences of the team not stopped, in the order they were posted -- a suspended one among them."""
    return [one for one in state.rhythm.recurrences.values() if one.stopped is None]


def dues(state: dict, agent: str) -> list[tuple[str, list[dict]]]:
    """-> what a launch of the agent would deliver, task by task in the tasks' order: (task, its inbox
    on that task) for each task that has some -- a stopped task has none to deliver, its stop delivered
    at once, unless a run of the agent STANDS on it, (agent, task): then its stop alone, the head of one more launch
    (the run parks there)."""
    waiting = inbox(state, agent)
    found = []
    for task, held in state.task.tasks.items():
        if held.state == "resolved":
            continue
        box = [one for one in waiting if one.body.task == task]
        if held.state == "stopped":
            box = [one for one in box if one.body.verb == "stop" and (agent, task) in state.wake.standing]
        if box:
            found.append((task, box))
    return found


def quiet(state: dict, one: dict) -> bool:
    """-> whether a message launches nobody: a MEMBER's `info` -- it waits in its recipient's box and rides the head of
    its next launch, whatever its cause; an `info` of a principal or of the team is due as any message (row 114)."""
    return one.body.verb == "info" and is_member(state, one.body.sender)


def loud(state: dict, box: list[dict]) -> list[dict]:
    """-> the messages of a box that make their recipient due: every one but the members' `info`s (`quiet`)."""
    return [one for one in box if not quiet(state, one)]


def principal_of(state: dict, owner: str, asked: str | None) -> str:
    """-> who posts: the mandator `--as` names (declared under `principals:`) or the owner; else
    `Declined("principal-unknown", asked, allowed)`, the name asked and the principals allowed."""
    if asked is None:
        return owner
    started = state.season.started
    allowed = [owner] + list((started.body.principals if started is not None else None) or [])
    if asked not in allowed:
        raise Declined("principal-unknown", asked, allowed)
    return asked


def holders(state: dict, task: dict) -> list[str]:
    """-> the agents holding the task: its agent unless it is terminal on it, then every delegate
    on it without a terminal, in the order of their delegations."""
    found = [] if (task.to, task.id) in state.task.terminals else [str(task.to)]
    for one in state.task.delegations:
        if one["task"] == task.id and (one["to"], task.id) not in state.task.terminals and one["to"] not in found:
            found.append(str(one["to"]))
    return found


def stopping(state: dict, task: dict, sender: str, text: str, to: list[str]) -> list:
    """-> the events that stop a task: `stopped {task, by}` -- the task stops whatever holds it --,
    then a `stop` post to each agent named (none when nobody holds the task), then a `returned`
    for every post left undelivered on the task, to its author."""
    events: list = [Stopped.made(task=task.id, by=sender)]
    events += [Post.made(task=task.id, sender=sender, to=one, verb="stop", text=text) for one in to]
    for mid in task.messages:
        one = state.task.messages[mid]
        if mid not in state.task.delivered:
            events.append(Returned.made(message=mid, to=one.body.sender))
    return events


def start_opened(state: dict, owner: str, target: str, naming: dict, text: str | None) -> list:
    """-> what `team start --message` opens once `team-started` is composed: `task {task, from, to, name?, text}`, then
    its `post {do}` from the owner to `target` -- the task numbered on the state under the lock (`next_task`), `naming`
    its name or {}; [] without a message."""
    if text is None:
        return []
    task = next_task(state)
    return [TaskBorn.made(task=task, sender=owner, to=target, **naming, text=text),
            Post.made(task=task, sender=owner, to=target, verb="do", text=text)]


def stop_chosen(state: dict, task_id: str | None) -> list:
    """-> the tasks `team stop` stops, in their order: the task `--task` names, else every open task of the team;
    refused by its code `task-unknown` (the id asked), `task-closed` (the task, closed already)."""
    if task_id is None:
        return [one for one in state.task.tasks.values() if one.state == "open"]
    task = state.task.tasks.get(task_id)
    if task is None:
        raise Declined("task-unknown", task_id)
    if task.state in CLOSED:
        raise Declined("task-closed", task)
    return [task]


def stop_decided(state: dict, chosen: list, killed: list, owner: str) -> list:
    """-> what the stop of the tasks `chosen` writes, task by task in their order: the `wake-killed` its kill wrote
    (`killed`, one list per task, empty without `--kill`), then what `stopping` writes -- the owner stops it, its
    holders told."""
    made: list = []
    for task, ended in zip(chosen, killed):
        made += ended
        made += stopping(state, task, owner, "", holders(state, task))
    return made


def owner_box(state: dict, owner: str) -> list[dict]:
    """-> the posts to the owner and the posts returned to them, in the journal's order."""
    return [one for one in state.task.messages.values()
            if one.body.to == owner or state.task.returned_to.get(one.id) == owner]


def answer_of_debt(state: dict, key: int) -> int | None:
    """-> the id of the answer that settled the debt of the message `key`, None while it stands or when the task's close
    settled it."""
    settled = state.task.debts.get(key)
    return settled if isinstance(settled, int) and not isinstance(settled, bool) else None


def waiting(state: dict) -> dict:
    """-> what waits for the owner: the QUESTIONS -- an agent's `ask` to them on an open task no answer of theirs
    cites --; the NOTICES of the team to them, each in the words of the debt (`worded`) with `awaits` -- a notice about
    a member on an open task no answer cites, which holds that member's wait and stays until the answer --, the others
    since the cursor `inbox-seen`; the INFOS sent to them since the cursor, which hold nobody, in id order -- among
    them an `ask` no answer cites whose task is resolved or stopped: nobody can answer it any more --; the tasks
    resolved and the posts returned to them since the cursor -- an info, a notice that holds nobody, a task resolved
    (by its id) or a post returned the owner marked read one by one (`inbox-read`) leaves too."""
    started = state.season.started
    owner = str((started.body.owner if started is not None else None) or "")
    answered = principal_answered(state)
    to_owner = [one for one in state.task.messages.values() if one.body.to == owner]
    asked = [one for one in to_owner if one.body.verb == "ask" and one.id not in answered]
    questions = [one for one in asked if is_open(state, one.body.task)]

    def unread(mid: int) -> bool:
        return mid > state.task.seen and mid not in state.task.read

    infos = sorted((one for one in to_owner if unread(one.id) and (one.body.verb == "info" or (
        one in asked and not is_open(state, one.body.task)))), key=lambda one: one.id)
    notices = []
    for one in to_owner:
        if not is_notice(state, one):
            continue
        awaits = (notice_about(state, one) is not None and one.id not in answered
                  and is_open(state, one.body.task) and one.body.cause != "silence")   # a silence holds nobody
        if awaits or unread(one.id):
            notices.append({**worded(state, one), "awaits": awaits})
    done = [one for one in state.task.done.values() if unread(int(one.id or 0))]
    returned = [mid for mid, to in state.task.returned_to.items() if to == owner and unread(mid)]
    return {"questions": questions, "notices": notices, "infos": infos, "done": done, "returned": returned}



def post_checked(state: dict, owner: str, asked_as: str | None, to: str | None) -> tuple[str, list[str]]:
    """-> who posts and the season's members, once the team is known to take a post: refused by its code
    `team-not-started`, `team-deleting`, `season-stopped`, then `participant-unknown` (the member `--to` names);
    who posts is the owner or the principal `--as` names (`principal_of`, which refuses by its own text)."""
    started = state.season.started
    if started is None:
        raise Declined("team-not-started")
    if state.season.deleting:
        raise Declined("team-deleting")
    if state.season.stopped:
        raise Declined("season-stopped")
    agents = list(started.body.agents or {})
    sender = principal_of(state, owner, asked_as)
    if to is not None and to not in agents:
        raise Declined("participant-unknown", to)
    return sender, agents


def post_decided(state: dict, sender: str, agents: list[str], to: str | None, task_id: str | None, text: str | None,
                 ask: bool, stop: bool, reply: str | None, naming: dict, vectors: list[str], limit: int | None) -> list:
    """-> what `team post` writes once the team takes it (`post_checked`): without a task, a new task and its `do`;
    on a task, a stop (`stopping`), an answer to the post `reply` cites, an `ask`, or a note. Refused by its code:
    `task-unknown` (the task asked), `task-closed` (the task, its state), `message-unknown` (the post cited, the
    task)."""
    if task_id is None:
        target = to or str(state.season.started.body.root)
        task = next_task(state)
        return [TaskBorn.made(task=task, sender=sender, to=target, **naming, text=text,
                              **({"vectors": vectors} if vectors else {}),
                              **({"context": limit} if limit is not None else {})),
                Post.made(task=task, sender=sender, to=target, verb="do", text=text)]
    task = state.task.tasks.get(task_id)
    if task is None:
        raise Declined("task-unknown", task_id)
    if task.state in CLOSED:
        raise Declined("task-closed", task.id, task.state)
    verb, cited = ("ask" if ask else "info"), None   # a note informs; `--ask` asks, an answer due
    target = to or task.to
    if stop:
        return stopping(state, task, sender, text if text is not None else "", [target] if to else holders(state, task))
    if reply is not None:
        try:
            cited = int(reply.lstrip("#"))
        except ValueError:
            cited = -1
        answered = state.task.messages.get(cited)
        if answered is None or answered.body.task != task.id:
            raise Declined("message-unknown", reply, task.id)
        verb = "re"
        if to is None and answered.body.sender in agents:
            target = str(answered.body.sender)
        elif to is None and answered.body.about in agents:
            target = str(answered.body.about)
    one = Post.made(task=task.id, sender=sender, to=target, verb=verb, text=text if text is not None else "")
    return [one.but(re=cited)] if cited is not None else [one]


def inbox_seen_decided(state: dict, one_id: int | None, upto: int) -> list:
    """-> what `team inbox --seen` writes: under `--id`, `inbox-read` of that message; else the owner's cursor
    `inbox-seen` up to `upto`, the last event of the journal, when it moves. Refused by its code:
    `team-not-started`, `inbox-question` (a question or a notice that awaits its answer), `inbox-id-unknown` (no
    such message in the inbox) -- each with the id asked."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if one_id is not None:
        waits = waiting(state)
        if one_id in [one.id for one in waits["questions"]] + [
                one["id"] for one in waits["notices"] if one["awaits"]]:
            raise Declined("inbox-question", one_id)
        held = ([one["id"] for one in waits["notices"]] + [one.id for one in waits["infos"]] + waits["returned"]
                + [int(one.id or 0) for one in waits["done"]])
        if one_id not in held:
            raise Declined("inbox-id-unknown", one_id)
        return [InboxRead.made(message=one_id)]
    return [InboxSeen.made(upto=upto)] if upto > state.task.seen else []


def resume_checked(state: dict, owner: str, asked_as: str | None, to: str | None, task_id: str) -> tuple:
    """-> who resumes, the season's members and the task `team resume --task` takes back, before its budget is read:
    refused by its code `team-not-started`, `team-deleting`, `season-stopped`, `member-unknown` (the member `--to`
    names, the season's members), `task-unknown` (the task asked), `task-resolved` (the task); who resumes is the
    owner or the principal `--as` names (`principal_of`)."""
    if state.season.started is None:
        raise Declined("team-not-started")
    if state.season.deleting:
        raise Declined("team-deleting")
    if state.season.stopped:
        raise Declined("season-stopped")
    sender = principal_of(state, owner, asked_as)
    season = list((state.season.started.body.agents or {}))
    if to is not None and to != ALL and to not in season:
        raise Declined("member-unknown", to, season)
    task = state.task.tasks.get(task_id)
    if task is None:
        raise Declined("task-unknown", task_id)
    if task.state == "resolved":
        raise Declined("task-resolved", task.id)
    return sender, season, task


def resume_decided(state: dict, sender: str, season: list[str], task, to: str | None, text: str, spent: str) -> list:
    """-> what `team resume --task` writes once `resume_checked` took the task and the budget was read (`spent`, what
    the team spent past its bound, '' when nothing): `resumed {task, by, from}` -- the causes that held the task --
    then an `info` to each member it revives, or to the member `--to` names, or to every one under `all`. Refused
    by its code: `budget-spent` (what was spent), `task-not-blocked` (the task)."""
    if spent:
        raise Declined("budget-spent", spent)
    fell = [agent for agent, one in sorted(state.wake.fell) if one == task.id]
    causes = ((["stopped"] if task.state == "stopped" else []) + (["failed"] if fell else [])
              + (["launches-spent"] if task.id in state.budget.launches_spent else []))
    halted = [one.body.agent for one in state.wake.halts if one.body.task == task.id]
    limited = [member for member in members_of(state, task.id)
               if member in state.wake.quotas and state.wake.quotas[member].get("until") is None]
    causes += (["halted"] if halted else []) + (["quota"] if limited else [])
    if not causes:
        raise Declined("task-not-blocked", task.id)
    revived = holders(state, task) if task.state == "stopped" else []
    revived += fell + halted + limited
    if task.id in state.budget.launches_spent:
        revived += [agent for agent in (state.season.started.body.agents or {})
                    if any(one.body.task == task.id for one in inbox(state, agent))]
    if to is not None:                                # the resume aimed: the member named, or every one
        revived = season if to == ALL else [to]
    return ([Resumed.made(task=task.id, by=sender, sender=causes)]
            + [Post.made(task=task.id, sender=sender, to=one, verb="info", text=text) for one in dict.fromkeys(revived)])


def worded(state: dict, one: dict) -> dict:
    """-> a post as the faces say it, in the words of the debt: a member's `done`, `reply` or `escalate` to a member,
    and a principal's `reply`, written before team 0.36.0, said `re` to the message it answers (`cited_of`; a `done` to a
    principal answers the task's opening) with `was` its verb; an `escalate` to a principal said as the team's `notice`,
    `about` the member that wrote it; a `note` written before team 0.47.0 said `info`; any other post as its line says it."""
    body, line = one.body, one.line
    verb = body.verb
    if verb == "note":                                           # the principal's note until team 0.47.0: an info
        return {**{key: value for key, value in line.items() if key != "verb"}, "verb": "info", "was": verb}
    if verb not in RETIRED_VERBS:
        return line
    rest = {key: value for key, value in line.items() if key not in ("verb", "reply")}
    if verb == "escalate" and not is_member(state, body.to):
        about = body.sender if is_member(state, body.sender) else None
        started = state.season.started
        return {**rest, "verb": "notice", "from": (started.team if started is not None else None) or one.team,
                **({"about": about} if about else {}), "was": verb}
    cited = cited_of(state, one)
    if cited is None and verb == "done":
        cited = opening_of(state, body.task)
    return {**rest, "verb": "re", "re": cited, "was": verb}
