"""What the readings show of the exchanges: a response as it was kept, a message as it was sent, a message with
the response that answers it."""
from __future__ import annotations

import json

from faces.text import harmless
from model.exchange import Message, Response
from model.text import first_line

NO_RESPONSE = "pp-agent: no response recorded yet."
NO_MESSAGE = "pp-agent: no message sent yet."


def response_lines(one: Response) -> list[str]:
    """-> a response as `responses` says it: a line with its hour, its agent, its run, its rank, the harness's
    exit code, its cost, its launches and its denials when it has any; then its text, harmless."""
    cost, launches = one.cost_usd, one.launches
    return [f"{one.at}  {one.agent} · run {one.run} · #{one.index} · rc {one.harness_rc}"
            + (f" · {cost:g} USD" if isinstance(cost, (int, float)) else "")
            + (f" · {launches} launch(es)" if isinstance(launches, int) else "")
            + (f" · denials {len(one.denials)}" if one.denials else ""),
            harmless(one.response) if one.response is not None else "(no response)"]


def message_lines(one: Message) -> list[str]:
    """-> a message as `messages` says it: a line with its hour, who sent it to whom, its run, the policy of its
    launch, its tag and its pid when it names them; then its text, harmless."""
    return [f"{one.at}  {one.sender} -> {one.to} · run {one.run} · policy {json.dumps(one.json()['policy'])}"
            + (f" · tag {one.tag}" if one.tag is not None else "")
            + (f" · pid {one.pid}" if one.pid is not None else ""),
            harmless(str(one.message))]


def exchange_object(name: str, key: str, number: int, message: Message, response: Response) -> dict:
    """-> one exchange as `exchanges --json` says it: the agent, the run, the rank of the message, its hour and
    its text, then what the `response` that answers it kept -- every field null for a message without one --,
    `conducted` false for an exchange the house did not conduct, the `words` and the `finals` as their line says
    them, the `overruns`."""
    return {"agent": name, "run": key, "index": number, "at": message.at,
            "message": message.message, "response": response.response,
            "cost_usd": response.cost_usd, "launches": response.launches,
            "error": response.error, "harness_rc": response.harness_rc,
            "conducted": message.conducted is not False,
            "words": response.json().get("words"),      # as the line says them, read or not
            "finals": response.json().get("finals"), "overruns": response.overruns,
            "model": response.model, "effort": response.effort}


def exchange_line(number: int, message: Message, response: Response | None) -> str:
    """-> one exchange as `exchanges` says it: the rank of the message, its hour, its first line, then the first
    line of the `response` that answers it with its cost, its launches and its overruns -- or that none came."""
    said = first_line(str(message.message))
    if response is None:
        return f"#{number}  {message.at}  {said} -> (no response)"
    cost, launches = response.cost_usd, response.launches
    return (f"#{number}  {message.at}  {said} -> "
            + (first_line(str(response.response)) if response.response is not None else "(no response)")
            + (f" · {cost:g} USD" if isinstance(cost, (int, float)) else "")
            + (f" · {launches} launch(es)" if isinstance(launches, int) else "")
            + (f" · {response.overruns} overrun(s)" if response.overruns else ""))
