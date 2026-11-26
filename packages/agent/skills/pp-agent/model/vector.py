"""The vectors of a run: the set it keeps at the house's records, and what the launcher plays for each."""
from __future__ import annotations

from dataclasses import dataclass

from model.record import _read, _written


@dataclass(frozen=True)
class Mount:
    """What the launcher plays for ONE vector of a run: the `vector` as it was given (`<family>:<id>`), the
    `script` its family's manifest names as its verifier, and the `ident` that script mounts."""
    vector: str = ""
    script: str = ""
    ident: str = ""


@dataclass(frozen=True)
class Keeping:
    """One line of `vectors.jsonl`: the hour, the `agent`, the `run` and the `vectors` it keeps from then on, in
    the order they came (empty for a set emptied). `keys` and `kept` stand for a line read alone: what gives it
    back as it was."""
    at: str | None = None
    agent: str | None = None
    run: str | None = None
    vectors: list | None = None
    keys: tuple[str, ...] | None = None
    kept: tuple = ()

    @staticmethod
    def of(line: dict) -> "Keeping":
        """-> the keeping a line of `vectors.jsonl` carries; a key it does not name is kept for `json()`."""
        return Keeping(**_read(Keeping, line))

    def json(self) -> dict:
        """-> the line `vectors.jsonl` holds: the one read, as it was; the one composed, its four keys always."""
        return _written(self)
