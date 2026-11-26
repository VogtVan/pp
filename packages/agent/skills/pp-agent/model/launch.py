"""What the adapter read of a launch that answered, and the provider's stop it read in its output."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Stop:
    """A provider's stop, as the adapter read it in a launch's output: its `kind` (`quota`, a usage limit), the
    hour it lasts `until` (None when the provider names none) and what the provider `said`."""
    kind: str = "quota"
    until: str | None = None
    said: str = ""

    @staticmethod
    def of(answer) -> "Stop | None":
        """-> the stop an adapter's answer says under `stop`; None when it says none, or says it in another shape
        than a quota's: the kind `quota`, what the provider said, an hour or none."""
        stop = answer.get("stop") if isinstance(answer, dict) else None
        if not (isinstance(stop, dict) and stop.get("kind") == "quota" and isinstance(stop.get("said"), str)
                and (stop.get("until") is None or isinstance(stop.get("until"), str))):
            return None
        return Stop(kind="quota", until=stop.get("until"), said=stop["said"])


@dataclass(frozen=True)
class Launch:
    """What the adapter read of ONE launch that answered: the `session` the harness lives in, its `cost_usd` as
    the adapter counts it, the `denials` in the order they came, the `error` the harness said, and the provider's
    `stop` when the adapter read one."""
    session: str | None = None
    cost_usd: float | None = None
    denials: tuple = ()
    error: str | None = None
    stop: Stop | None = None

    @staticmethod
    def of(answer: dict, stop: Stop | None = None) -> "Launch":
        """-> the launch the engine's face read (`adapters.answer`: its four keys, the session owed), the
        provider's `stop` beside."""
        return Launch(session=answer["session"], cost_usd=answer.get("cost_usd"),
                      denials=tuple(answer.get("denials") or ()), error=answer.get("error"), stop=stop)
