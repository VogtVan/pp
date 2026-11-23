"""task_stats -- what a task cost and took over all its seasons, as `team stats <name> --all --json` says it of each
task (its `by_task`): the costs in the three bases, the `do` and the `re`, the failed wake-ups, the elapsed time and the
effort, the largest share of the context its wake-ups left. Pure: no I/O, no Textual, nothing computed -- a number
the face leaves out stays None."""
from __future__ import annotations

from dataclasses import dataclass


def _number(value: object) -> float | int | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


@dataclass(frozen=True)
class TaskStats:
    """One task's line of `team stats`: `usd`, `launches`, `tokens` (its costs, `tokens_estimated` when a wake-up
    measured none), `do`, `re`, `failures`, `elapsed` and `effort` (seconds), `context_max` (a share of the window, 0
    to 1)."""
    usd: float | None = None
    launches: int | None = None
    tokens: int | None = None
    do: int | None = None
    re: int | None = None
    failures: int | None = None
    elapsed: int | None = None
    effort: int | None = None
    context_max: float | None = None
    tokens_estimated: bool = False

    @classmethod
    def read(cls, obj: dict) -> "TaskStats":
        cost, time = _dict(obj.get("cost")), _dict(obj.get("time"))
        return cls(_number(cost.get("usd")), _number(cost.get("launches")), _number(cost.get("tokens")),
                   _number(obj.get("do")), _number(obj.get("re")), _number(obj.get("failures")),
                   _number(time.get("elapsed")), _number(time.get("effort")), _number(obj.get("context_max")),
                   cost.get("tokens_estimated") is True)


def stats_of(found: dict | None) -> dict[str, TaskStats]:
    """-> each task's stats by its id, from what `team stats --all --json` printed: its `by_task`, one line per task
    over all its seasons."""
    lines = _dict(found).get("by_task")
    return {str(one["task"]): TaskStats.read(one) for one in (lines if isinstance(lines, list) else [])
            if isinstance(one, dict) and one.get("task")}
