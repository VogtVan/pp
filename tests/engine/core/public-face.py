"""Scenario `public-face` -- the engine's ONE public face (plan pp_core, phase
la-decoupe-du-moteur; `record` joined at pp-split / la-face-paresseuse):
- `__all__` names the whole API, `dir()` renders it, and every name resolves
- `record` is on the face: the write regime a package's script imports
- a name off the API refuses by AttributeError, and the face brings PyYAML with it
"""
from __future__ import annotations

import conductor


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    # --- every declared name resolves, and dir() renders the API
    unresolved = [name for name in conductor.__all__ if not hasattr(conductor, name)]
    if not unresolved and set(conductor.__all__) <= set(dir(conductor)):
        held("the API is whole", f"{len(conductor.__all__)} names declared, each one resolves")
    else:
        failures.append(f"  ✗ API whole                  unresolved={unresolved}")

    # --- `record` is reachable by its name on the face
    if ("record" in conductor.__all__
            and hasattr(conductor.record, "held") and hasattr(conductor.record, "replace")):
        held("record is on the face", "the write regime a package's script imports: held, replace")
    else:
        failures.append("  ✗ record on the face         absent from the API")

    # --- a name off the API refuses, and the engine's dependency travels with the face
    try:
        conductor.nothing_of_the_sort
        off = "reached"
    except AttributeError:
        off = "refused"
    import sys
    if off == "refused" and "yaml" in sys.modules:
        held("the face is closed and whole", "an unknown name refuses; importing it brings the engine, PyYAML included")
    else:
        failures.append(f"  ✗ face closed                {off}, yaml loaded={'yaml' in sys.modules}")
    return 0
