"""The agents of a house: the word that names one in a call, the path it is, its git identity."""
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


def identity_of(name: str, slug: str) -> dict:
    """-> the git identity of the exchange, in the harness's environment: the agent's path,
    its address at the house (`rep1/ag1` -> `rep1.ag1@<slug>`)."""
    email = f"{name.replace('/', '.')}@{slug or 'house'}"
    return {"GIT_AUTHOR_NAME": name, "GIT_AUTHOR_EMAIL": email,
            "GIT_COMMITTER_NAME": name, "GIT_COMMITTER_EMAIL": email}
