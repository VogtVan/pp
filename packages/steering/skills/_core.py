"""The bootstrap a package's skill uses to reach its instance and the engine's face.

It cannot itself be imported before it exists: that is why every package that
imports carries its own copy. One walk, and no dependency to reach it.

documentary: `home(start)` walks up from the CALLER's own file -- never from this
module's -- because a vendored file imported by name is shared across packages in
one process, and the first copy loaded would answer for every other. It returns
what it found, so a caller says its own refusal; `core(start)` reuses that same
walk and adds the engine to the path. Both take the caller's file for that reason.
"""
import sys
from pathlib import Path


def home(start=None):
    """-> the instance the CALLER belongs to, or None -- by walking up, never by env."""
    for parent in Path(start or __file__).resolve().parents:
        if (parent / ".sys" / "instance.yaml").is_file():
            return parent
    return None


def core(start=None):
    """-> the `conductor` module of the instance the CALLER is vendored in."""
    root = home(start)
    if root is None:
        raise SystemExit("not inside an installed instance -- no engine to import")
    sys.path.insert(0, str(root / ".sys" / "engine"))
    import conductor
    return conductor
