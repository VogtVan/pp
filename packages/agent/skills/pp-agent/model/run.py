"""A run as the house reads it: the session it lives in and the name it was given, at the house's records; the mark
its launcher wrote into its wake lock; an event of its trace."""
from __future__ import annotations

from dataclasses import dataclass

from model.record import _read, _written


@dataclass(frozen=True)
class Mark:
    """The mark a launcher wrote into the wake lock of a run, as a later call reads it: the `responses` the run
    had when its launch began (None for a mark that awaits no launch's outcome, or for none), and whether the
    wake-up that wrote it was `interrupted`."""
    responses: int | None = None
    interrupted: bool = False

    @staticmethod
    def of(read) -> "Mark":
        """-> the mark a wake lock file carries; the mark of nothing for a file that carries no object."""
        if not isinstance(read, dict):
            return Mark()
        launched = read.get("responses")
        return Mark(responses=launched if isinstance(launched, int) else None,
                    interrupted=read.get("interrupted") is True)


@dataclass(frozen=True)
class Traced:
    """One event of a run's trace, as far as the house reads it: its `kind`; of a `block`, the `stack` it stands
    on, the `command` that rendered it, whether it holds a `wait`, and the `spaces` it says -- the engine's own
    object, given whole to the faces --; of a `cut` or a `chunk`, the characters `left`; of a `refusal`, its
    `detail`; of an `answer`, the `channel` it was said on, the `document` a print call named and the text
    `given`, as the trace holds it."""
    kind: str | None = None
    stack: str = ""
    command: str = ""
    wait: bool = False
    left: int | None = None
    spaces: dict | None = None
    detail: str = ""
    channel: str = ""
    document: str = ""
    given: str | None = None

    @staticmethod
    def of(event: dict) -> "Traced":
        """-> the event a line of the trace carries; a key it does not say reads empty."""
        spaces, given = event.get("spaces"), event.get("given")
        return Traced(kind=event.get("kind"), stack=str(event.get("stack", "")),
                      command=str(event.get("command", "")), wait=bool(event.get("wait")), left=event.get("left"),
                      spaces=spaces if isinstance(spaces, dict) else None, detail=event.get("detail", ""),
                      channel=str(event.get("channel", "")), document=str(event.get("document", "")),
                      given=given if isinstance(given, str) else None)


@dataclass(frozen=True)
class Session:
    """One line of `sessions.jsonl`: the hour, the `agent`, the `run`, the `provider` of the session (null for a
    caller's command) and the `session` the harness named. `keys` and `kept` stand for a line read alone: what
    gives it back as it was."""
    at: str | None = None
    agent: str | None = None
    run: str | None = None
    provider: str | None = None
    session: str | None = None
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(line: dict) -> "Session":
        """-> the session a line of `sessions.jsonl` carries; a key it does not name is kept for `json()`."""
        return Session(**_read(Session, line))

    def json(self) -> dict:
        """-> the line `sessions.jsonl` holds: the one read, as it was; the one composed, its five keys always."""
        return _written(self)


@dataclass(frozen=True)
class Naming:
    """One line of `names.jsonl`: the hour, the `agent`, the `run` and the `name` it was given. `keys` and `kept`
    stand for a line read alone: what gives it back as it was."""
    at: str | None = None
    agent: str | None = None
    run: str | None = None
    name: str | None = None
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(line: dict) -> "Naming":
        """-> the naming a line of `names.jsonl` carries; a key it does not name is kept for `json()`."""
        return Naming(**_read(Naming, line))

    def json(self) -> dict:
        """-> the line `names.jsonl` holds: the one read, as it was; the one composed, its four keys always."""
        return _written(self)
