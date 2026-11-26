"""The bootstrap a package's skill uses to reach its instance and the engine's face.

It cannot itself be imported before it exists: that is why every package that
imports carries its own copy. One walk, and no dependency to reach it.

A script's file lives in the vendor of a MACHINE: the instance found by walking up
from it. That machine may be BORROWED by an instance below it, which carries no
engine of its own; the engine that launches a script for such an instance names it
in the child's environment, `PP_HOME`. The instance a script serves is therefore
the one `PP_HOME` names when that instance borrows the machine the script lives in,
the machine's own otherwise -- so a neighbour's script, launched by another
instance's, keeps its own home.

documentary: `home(start)` walks up from the CALLER's own file -- never from this
module's -- because a vendored file imported by name is shared across packages in
one process, and the first copy loaded would answer for every other. It returns
what it found, so a caller says its own refusal; `core(start)` takes the machine
that same walk finds and adds its engine to the path. Both take the caller's file
for that reason.
"""
import os
import sys
from pathlib import Path


def _machine(start=None):
    """-> the instance the CALLER's file lives in -- the machine it belongs to -- or None."""
    for parent in Path(start or __file__).resolve().parents:
        if (parent / ".sys" / "instance.yaml").is_file():
            return parent
    return None


def _borrows(meta, machine):
    """-> whether `meta` is an instance without an engine whose nearest machine above is
    `machine`."""
    if not (meta / ".sys" / "instance.yaml").is_file() or (meta / ".sys" / "engine").is_dir():
        return False
    for ancestor in meta.parent.parents:
        candidate = ancestor / meta.name
        if (candidate / ".sys" / "engine").is_dir():
            return candidate.resolve() == machine.resolve()
    return False


def home(start=None):
    """-> the instance the CALLER serves, or None: the one `PP_HOME` names when it borrows
    the machine the caller's file lives in; that machine otherwise."""
    machine = _machine(start)
    named = os.environ.get("PP_HOME", "").strip()
    if machine is not None and named and _borrows(Path(named).resolve(), machine):
        return Path(named).resolve()
    return machine


def core(start=None):
    """-> the `conductor` module of the machine the CALLER's file lives in."""
    machine = _machine(start)
    if machine is None:
        raise SystemExit("not inside an installed instance -- no engine to import")
    sys.path.insert(0, str(machine / ".sys" / "engine"))
    import conductor
    return conductor
