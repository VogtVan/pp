"""The switches of a run's packages, `--package <name>=on|off`: the ones a launch asks, the waiting list they
start, the line an opening carries."""
from __future__ import annotations

from model.policy import Asked
from model.refusal import Refusal


def asked_switches(asked: Asked, where: str, base: str, pinned: set[str]) -> list[tuple[str, bool, str]]:
    """-> the `--package <name>=on|off` of a launch as (name, on, value), judged before anything is opened
    or written, against the packages the agent's instance at `where` pins (`pinned`, beyond its `base`):
    `package-invalid` (not the form), `package-base` (the instance's base), `package-unpinned` (a name it does
    not pin, switched on). A name it does not pin, switched off, asks nothing -- it plays nowhere already --
    and is left out."""
    found = []
    for value in asked.package or []:
        name, _, state = str(value).partition("=")
        if not name or state not in ("on", "off"):
            raise Refusal(f"package-invalid -- `--package {value}`: the form is <name>=on or <name>=off.")
        if name == base:
            raise Refusal(f"package-base -- `{name}` is the instance's base: it always plays.")
        if name not in pinned:
            if state == "off":
                continue
            raise Refusal(f"package-unpinned -- `{name}` is not pinned by {where}: the packages it pins are "
                          f"{', '.join(sorted(pinned)) or 'none'}.")
        found.append((name, state == "on", str(value)))
    return found


def seeded(switches: list, held: dict) -> dict:
    """-> the waiting list a launch's `--package` starts with, `{name: (on, value)}`: each switch the run's own
    switches (`held`) do not hold already -- at an opening, every one --, in the order given, the last word on
    a name winning. At an opening the list rides `PP_PACKAGES` on the `-new` (`packages_line`); at a resume
    `replayer` plays it: either way the word is WRITTEN at the run, over the agent's SETTINGS."""
    waiting: dict = {}
    for name, on, value in switches:
        waiting.pop(name, None)
        if held.get(name) != ("on" if on else "off"):
            waiting[name] = (on, value)
    return waiting


def packages_line(waiting: dict) -> str | None:
    """-> what an opening carries as `PP_PACKAGES`: every switch of the waiting list, `<name>=on|off` joined by
    commas, in the order they came; None when nothing waits."""
    if not waiting:
        return None
    return ",".join(f"{name}={'on' if on else 'off'}" for name, (on, _) in waiting.items())
