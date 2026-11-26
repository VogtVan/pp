"""The `wake` domain, layer `faces`: how a wake-up is put into words.

A definition belongs here when it turns the state into what a woken member or a user reads -- the message a member
receives, the history of a task in a reopened run, a text clipped, the face of a member's run or of its quota -- and
gives it back without printing it. It reads no clock: the face of a quota receives the hour as `now`, read by the act
that asks for the face (`status_object`, `status/acts.py`).
"""
from __future__ import annotations

from datetime import datetime

from wake.model import ANSWERED_FOR, HANDED_BACK, HANDED_BACK_VECTOR, HISTORY_CHARS, OWED
from task.rules import cited_of, opening_of, owes
from wake.rules import carrier_of, quota_of


def clipped(text) -> str:
    """-> a message's text as a history line carries it: HISTORY_CHARS at most."""
    text = str(text or "")
    return text if len(text) <= HISTORY_CHARS else text[:HISTORY_CHARS - 1] + "…"


def history_of(state: dict, agent: str, task: str) -> str:
    """-> what a NEW run must be told of a task the member already worked: the messages
    delivered to the member on the task, then the posts its answers made there, one line each,
    under `[history of <task> for <agent>]` -- or '' when the member has no past on the task.
    The texts are clipped; `team responses` reads the answers whole."""
    told = [f"#{one.id} {one.body.verb} from {one.body.sender}: {clipped(one.body.text)}".rstrip()
            for one in state.task.messages.values()
            if one.body.to == agent and one.body.task == task and one.id in state.task.delivered]
    said = [f"#{one.id} {one.body.verb} to {one.body.to}: {clipped(one.body.text)}".rstrip()
            for one in state.task.messages.values() if one.body.sender == agent and one.body.task == task]
    if not told and not said:
        return ""
    return f"[history of {task} for {agent}]\n" + "\n".join(told + said)


def histories_of(state: dict, member: str, task: str) -> str:
    """-> what a NEW run of a member must be told: the history of the open tasks of the task's CARRIER -- the
    task alone, or the open occurrences of a recurrence, the open rings of a ceremony --, in the tasks' order;
    '' when the member has no past there."""
    carrier = carrier_of(state, task)
    return "\n\n".join(one for one in (history_of(state, member, other) for other, held in state.task.tasks.items()
                                       if held.state == "open" and carrier_of(state, other) == carrier) if one)


def message_of(state: dict, agent: str, one: dict) -> str:
    """-> a message as a wake-up's head shows it: `#163 DO from supervisor on T8 -- you owe an answer`, the
    kind in capitals and the id an answer cites (`RE #175`); the debt said while it stands -- and, for the
    opening of a task the member holds, that its answer closes the task --; the text indented under it. A `re` the
    tick wrote in a member's place (`by: tick`) hands the message it cites back to its author. A first line says that
    the team wrote the answer, why (`ANSWERED_FOR`: the member never received the message under `returned`, was
    given it and did not answer under `suspected`; under neither field the launch that carried the message failed --
    dead after it carried it, or refused before it reached the member), that the message is closed and how to send
    it again. Then comes the tick's text, then the message cited -- its number, its
    vector when it carries one, its whole text (`HANDED_BACK`, `HANDED_BACK_VECTOR`) --, composed from the journal's
    message: nothing is copied into the `re`."""
    cited = cited_of(state, one)
    post = one.body
    head = (f"#{one.id} {str(post.verb or '').upper()}" + (f" #{cited}" if cited is not None else "")
            + f" from {post.sender} on {post.task}")
    if owes(state, one.id) and post.to == agent:
        head += f" -- {OWED}"
        if one.id == opening_of(state, post.task):
            head += f", and your answer to it closes {post.task}"
    text = str(post.text or "")
    said, back = [], []
    message = state.task.messages.get(cited) if post.by == "tick" and post.verb == "re" else None
    if message is not None:
        how = "returned" if post.returned else "suspected" if post.suspected else "failed"
        said = [ANSWERED_FOR[how].format(member=post.sender, id=cited)]
        vector = message.body.vector
        back = [HANDED_BACK_VECTOR.format(id=cited, vector=vector) if vector else HANDED_BACK.format(id=cited),
                *(f"  {line}" for line in str(message.body.text or "").splitlines())]
    return head + "".join(f"\n  {line}" for line in [*said, *text.splitlines(), *back])


def quota_face(state: dict, member: str, now: datetime) -> dict | None:
    """-> `{until, said, at}` of the provider's limit that holds the member at the hour `now`, None when none holds
    it."""
    held = quota_of(state, member, now)
    return None if held is None else {key: held.get(key) for key in ("until", "said", "at")}


def run_face(state: dict, member: str, key: str) -> dict:
    """-> `{how, since, context}` of ONE run of the member, read from that run's launches alone -- its
    intents, `wake-launched`, ends, failures and kills --, never from the replay's `standing`: `running`
    while a launch of the run has no end, `since` its intent's hour -- `gone` when nobody holds that launch
    (`faced`) --; otherwise the state its last end said,
    `standing` or `parked`, `ended` when that end says neither (killed, a final failure, the house's
    refusal), `since` that end's hour (null for a kill, whose hour the state does not keep); `context` the
    one of the run's last `wake-ended` that carries one, null without."""
    ends = {str(one.body.tag): one for one in [*state.wake.ends, *state.wake.fails]}

    def run_at(tag: str, intent: dict) -> str | None:
        launch, end = state.wake.launched.get(tag), ends.get(tag)
        return ((launch.body.run if launch is not None else None) or intent.body.run
                or (end.body.run if end is not None else None))

    launches = sorted(((str(tag), one) for tag, one in state.wake.intents.items()
                       if one.body.agent == member and run_at(str(tag), one) == key),
                      key=lambda entry: int(entry[1].id or 0))   # filtered, then sorted: the same order
    held = dict(launches)
    context = next((one.body.context for one in reversed(state.wake.ends)
                    if one.body.context is not None and str(one.body.tag) in held), None)
    running = [(tag, one) for tag, one in launches if tag not in state.wake.ended]
    if running:
        gone = state.wake.gone or ()
        return {"how": "gone" if all(tag in gone for tag, _ in running) else "running",
                "since": running[-1][1].at, "context": context}
    if not launches:
        return {"how": None, "since": None, "context": context}
    tag = launches[-1][0]
    end = ends.get(tag)
    if tag in state.wake.killed or end is None:
        return {"how": "ended", "since": None, "context": context}
    said = end.body.state                               # `final` and `house`: a `wake-failed`'s, read on the line
    how = (said if said in ("standing", "parked") and not end.line.get("final") and not end.line.get("house")
           else "ended")
    return {"how": how, "since": end.at, "context": context}
