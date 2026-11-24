"""The material of a run: its clone as `workdirs.jsonl` says it, and the push that sends its branch back."""
from __future__ import annotations

from dataclasses import dataclass, replace

from model.record import _read, _written

OPEN = ("at", "agent", "run", "repo", "path", "branch", "base", "state")   # the keys of the line a clone opens
SENT = ("pushed", "commits", "dirty")                                      # the keys a push adds to it


def _saying(keys: tuple[str, ...], *said: str) -> tuple[str, ...]:
    """-> the keys of a line that follows another and says `said`: `keys` in their order, then each of `said`
    they lacked."""
    return keys + tuple(key for key in said if key not in keys)


@dataclass(frozen=True)
class Push:
    """The push of a run's material after the harness: the `branch`, the `path` of the clone under the agent,
    whether the repository received it (`pushed`), the `commits` ahead of the base (None when the clone cannot
    count them), `dirty` for a clone with unstaged changes, the `reason` of a push that failed."""
    branch: str | None = None
    path: str | None = None
    pushed: bool = False
    commits: int | None = None
    dirty: bool = False
    reason: str | None = None


@dataclass(frozen=True)
class Workdir:
    """One line of `workdirs.jsonl`, the state of a run's material: the hour, the `agent`, the `run`, the
    `repo` cloned, the `path` of the clone under the agent, its `branch`, the `base` it is cut from
    (`<ref>@<sha>`), its `state` (`open`, `pushed`, `unpushed`, `pruned`); after a push, `pushed`, the `commits`
    ahead of the base, `dirty`, and the `reason` of a push that failed. `keys` are the keys its line carries, in
    their order -- the ones a clone opens with for a line composed, the line's own for a line read --, and
    `kept` what a line read carries beside the fields: a state that follows another (`sent`, `pruned`) carries
    the keys of the line it follows."""
    at: str | None = None
    agent: str | None = None
    run: str | None = None
    repo: str | None = None
    path: str | None = None
    branch: str | None = None
    base: str | None = None
    state: str | None = None
    pushed: bool | None = None
    commits: int | None = None
    dirty: bool | None = None
    reason: str | None = None
    keys: tuple[str, ...] = OPEN
    kept: tuple = ()

    @staticmethod
    def of(line: dict) -> "Workdir":
        """-> the material a line of `workdirs.jsonl` carries; a key it does not name is kept for `json()`."""
        return Workdir(**_read(Workdir, line))

    def json(self) -> dict:
        """-> the line `workdirs.jsonl` holds: its `keys` in their order, each with what its field says -- a line
        read alone, as it was."""
        return _written(self)

    def sent(self, at: str, push: Push) -> "Workdir":
        """-> the line a push writes after this one: its keys, the hour, the state `pushed` or `unpushed`, then
        `pushed`, `commits` and `dirty`; the `reason` last, for a push that failed alone."""
        keys = _saying(tuple(key for key in self.keys if key != "reason"), "at", "state", *SENT)
        return replace(self, at=at, state="pushed" if push.pushed else "unpushed", pushed=push.pushed,
                       commits=push.commits, dirty=push.dirty, reason=push.reason,
                       keys=keys + (("reason",) if push.reason is not None else ()))

    def pruned(self, at: str) -> "Workdir":
        """-> the line a prune writes after this one: every key it carries, the hour and the state `pruned`."""
        return replace(self, at=at, state="pruned", keys=_saying(self.keys, "at", "state"))
