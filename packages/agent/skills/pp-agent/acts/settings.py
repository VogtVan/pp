"""What a birth writes through the engine's settings face: the profile, the cap of an output."""
from __future__ import annotations

from pathlib import Path

from model.words import PROFILES
from store.settings import known_setting

HARNESS_CAP = 200000            # `max_harness_tool_output` an agent is born with: one output of pp, one launch


def profiled(conductor, meta: Path, profile: str) -> str:
    """Writes the lines of `PROFILES[profile]` through the engine's settings face, one key per call,
    the file never opened here; a key the instance does not know -- a switch of a package the house
    does not pin, a key of a fragment it does not carry -- is left. -> what the birth says of it."""
    written, left = [], []
    for key, value in PROFILES[profile]:
        if known_setting(conductor, meta, key):
            conductor.settings.write(meta, key, value)
            written.append(f"{key} {value}")
        else:
            left.append(key)
    said = f"profile {profile}: {', '.join(written) or 'nothing written'}"
    return f"{said} (left, not pinned here: {', '.join(left)})" if left else said


def capped(conductor, meta: Path) -> str:
    """Sets the agent's `max_harness_tool_output` at the size of a prompt, through the engine's
    settings face (`settings.write`: one line of the agent's own settings, judged by the reading,
    the file never opened here): an output of pp reaches the harness whole, a boot in one launch.
    -> what the birth says of it."""
    conductor.settings.write(meta, "max_harness_tool_output", HARNESS_CAP)
    return f"max_harness_tool_output {HARNESS_CAP}"
