"""The agents of a house as a call names them: the word that names one, the path it is."""
from __future__ import annotations

from model.refusal import Refusal
from model.words import USAGE, HOUSE


def agent_named(rest: list[str]) -> tuple[str, list[str]]:
    """-> (the agent's path, the rest): the first word of a call is the agent's path, never a flag -- the
    usage otherwise."""
    if not rest or rest[0].startswith("--"):
        raise Refusal(USAGE)
    return rest[0], rest[1:]


def agent_path(path: str, slugs: bool) -> str:
    """-> the path of an agent, as given: an agent IS its path, relative to the house's
    workspace, written with `/`, every segment a slug (`slugs`) -- anything else refuses
    `agent-path-invalid`. `.` is the HOUSE itself."""
    if path != HOUSE and (not path or not slugs):
        raise Refusal(f"agent-path-invalid -- `{path}`: an agent is its path under the house, slugs joined by `/` "
                      "(lowercase, digits and single dashes; no `..`, no leading `/`, no empty segment).")
    return path
