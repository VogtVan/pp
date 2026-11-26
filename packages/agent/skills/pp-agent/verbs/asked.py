"""What the verbs read of argv: the flags of a launch, the message, the agent and the key named."""
from __future__ import annotations

from pathlib import Path

from acts.refusal import ruled
from model.policy import Asked
from model.words import USAGE
from rules.houses import agent_named, agent_path
from store.houses import house, agent_at, agent_known, slugs_of
from store.refusal import refuse


def asked_of(rest: list[str]) -> Asked:
    """-> what the words of a call ask (`Asked.of`); what they cannot ask is refused in its own words."""
    return ruled(Asked.of, rest)


def named_agent(root: Path, conductor, rest: list[str]) -> tuple[str, Path, list[str]]:
    """-> (the agent's path, its instance root, the rest): the first word is the agent's
    path (`agent_named`, `agent_path`), where an instance must stand (`agent-unknown`)."""
    path, rest = ruled(agent_named, rest)
    ruled(agent_path, path, slugs_of(conductor, path))
    return path, agent_known(root, conductor, path), rest


def agent_of(root: Path, conductor, path: str) -> Path:
    """-> where the agent `path` stands (`agent_at`), its path judged first (`agent-path-invalid`)."""
    ruled(agent_path, path, slugs_of(conductor, path))
    return agent_at(root, path)


def json_flag(rest: list[str]) -> tuple[bool, list[str]]:
    """-> (whether `--json` was asked, the rest without it)."""
    return "--json" in rest, [one for one in rest if one != "--json"]


def message_of(asked: Asked) -> str | None:
    """-> the message to send: the text given, the file's content (`-` reads stdin), or
    None when none was given."""
    if asked.message is not None:
        return str(asked.message)
    if asked.message_file is None:
        return None
    if asked.message_file == "-":
        return house()[1].reading.piped().rstrip("\n")
    path = Path(asked.message_file)
    if not path.is_file():
        refuse(f"message-file-missing -- {path} is no file.")
    return path.read_text(encoding="utf-8").rstrip("\n")


def keyed(rest: list[str]) -> tuple[str, str, list[str]]:
    """-> (path, key, the rest) of `wait` and `result`: the agent's path then the run's key."""
    if len(rest) < 2 or rest[0].startswith("--") or rest[1].startswith("--"):
        refuse(USAGE)
    return rest[0], rest[1], rest[2:]


def last_of(rest: list[str]) -> tuple[str | None, int]:
    """-> (the agent named, or None; the count `--last n`, default 1)."""
    name, count = None, 1
    if rest and not rest[0].startswith("--"):
        name, rest = rest[0], rest[1:]
    if rest[:1] == ["--last"] and len(rest) == 2:
        try:
            count = int(rest[1])
        except ValueError:
            refuse(f"`{rest[1]}` is not a number.")
        if count < 1:
            refuse("`--last` wants at least 1.")
    elif rest:
        refuse(USAGE)
    return name, count
