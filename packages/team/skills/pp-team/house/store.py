"""The `house` domain, layer `store`: where the house meets the system.

A definition belongs here when it reaches outside the values it is given: it finds the house and the engine, loads an
engine module, reads the clock, the environment or the process space it runs in, or ends the call with a refusal. It
also holds the tools of the whole skill that reach the disk or the process space: whether a launch was born in another
process space (`foreign`), a file written whole by a rename (`placed`), and the lines of a record read (`lines_of`) --
the journal's or any other's --, so that a store of any domain reads them from `house`, which comes first. A store reads
and gives back what it read; it judges nothing, and leaves the judgement to a rule. This module also holds `ENTRY`, the
path of the skill's entry script: code moved out of the entry reads it where it once read `__file__`.
"""
from __future__ import annotations

import json
import os
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

from house.model import NOW, USAGE

ENTRY = str(Path(__file__).resolve().parents[1] / "pp-team.py")   # the entry's path: what `__file__` read in the bodies moved here (C13)


def refuse(said: str) -> None:
    sys.stderr.write(f"pp-team: {said}\n")
    raise SystemExit(2)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# --- the house -----------------------------------------------------------------------------

def house():
    """-> (the house's instance root, the conductor module) -- the bootstrap's one walk."""
    sys.path.insert(0, str(Path(ENTRY).resolve().parents[1]))
    from _core import core, home                          # noqa: E402 -- the bootstrap
    root = home(ENTRY)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(ENTRY)


def machine_house() -> tuple[Path, object]:
    """-> (the HOUSE's instance root, the conductor module): the machine the skill lives in (`_machine()`),
    whatever instance calls it -- an agent that borrows the machine reads its house's teams, never its own
    instance alone. The one resolution the verbs that address the house from an agent share."""
    sys.path.insert(0, str(Path(ENTRY).resolve().parents[1]))
    from _core import _machine, core                      # noqa: E402 -- the bootstrap
    root = _machine(ENTRY)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(ENTRY)


def caller() -> Path | None:
    """-> the instance the call serves (`home()`: the one `PP_HOME` names when it borrows the machine)."""
    sys.path.insert(0, str(Path(ENTRY).resolve().parents[1]))
    from _core import home                                # noqa: E402 -- the bootstrap
    found = home(ENTRY)
    return found.resolve() if found is not None else None


def locks(conductor):
    """-> the engine's `state.lock` module: the tick lock, and the launchers' files it tests."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.lock")


def tracing(conductor):
    """-> the engine's `state.log` module: the one reader of a trace (`tail`, `follow`,
    `step_of`, `said`), shared with `pp-agent`."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.state.log")


def house_console(root: Path, conductor) -> Path:
    """-> the house's console by its absolute path (`pp`, `pp.cmd` on Windows): what an agent
    calls to read what the head of its message names."""
    import importlib
    return importlib.import_module(f"{conductor.__name__}.packaging.adapters").console_of(root.parent)


def owner_of(root: Path, conductor) -> str:
    """-> the team's OWNER: the house's slug."""
    return str(conductor.instance.slug(root))


def launch_of(conductor, meta: Path, run: str) -> Path:
    """-> the launcher's file of an agent's run, `session-<run>.wake.lock` beside its slot --
    the `agent` package's published contract: held while a wake-up plays."""
    return conductor.persistence.slot_of(meta, run).with_name(f"session-{run}.wake.lock")


def space_now() -> str | None:
    """-> the process SPACE this process plays in, as the kernel names it (`pid:[4026531836]`: its pid namespace,
    Linux); None where the system names none. A pid means something inside its space alone: a launcher detached
    from a sandbox is born in the sandbox's space, where the tick that launched it plays too, and ends with it."""
    try:
        return os.readlink("/proc/self/ns/pid")
    except OSError:
        return None


def engine_of(root: Path, conductor) -> Path:
    """-> the engine the house's console runs: the one a tick names in `--on-end`."""
    return conductor.instance.engine_root(root) / "pp.py"


def named_team(conductor, rest: list[str]) -> tuple[str, list[str]]:
    """-> (the team's name, the rest): the first word names the team, a slug."""
    if not rest or rest[0].startswith("--"):
        refuse(USAGE)
    name = rest[0]
    if not conductor.instance.valid_slug(name):
        refuse(f"team-invalid -- `{name}`: a team's name is lowercase, digits and single dashes.")
    return name, rest[1:]


def tick_now() -> datetime:
    """-> the tick's wall clock, LOCAL and naive: `PP_NOW` (ISO) when the variable is set --
    the bench, a try --, else the house's local time (the one the timer and the relaunch entry play under)."""
    given = os.environ.get(NOW, "").strip()
    if not given:
        return datetime.now()
    try:
        return datetime.fromisoformat(given)
    except ValueError:
        refuse(f"now-invalid -- `{NOW}={given}` is no ISO date-time.")


def foreign(space: str | None) -> bool:
    """-> whether a launch was born in ANOTHER process space than the one that reads it: its `wake-launched`
    kept a `space` -- the one given --, this process names its own, and they differ. Its pid then names nobody here
    -- never killed by it --, and its death with a free wake lock is its space's end, the house's failure, never the
    member's."""
    born, here = space, space_now()
    return bool(born) and bool(here) and born != here


def placed(target: Path, data: bytes) -> None:
    """Writes `target` whole: a temporary beside it, then one rename."""
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}-{secrets.token_hex(3)}")
    temporary.write_bytes(data)
    os.replace(temporary, target)


def lines_of(path: Path) -> list[dict]:
    """-> the record's lines, oldest first. A LAST line that does not parse is a writer still
    writing it and is skipped; one anywhere else is a hand in the file and refuses."""
    if not path.is_file():
        return []
    raw = path.read_text(encoding="utf-8").splitlines()
    found = []
    for number, line in enumerate(raw, 1):
        if not line.strip():
            continue
        try:
            found.append(json.loads(line))
        except ValueError:
            if number == len(raw):
                continue
            refuse(f"line {number} of {path.name} is not a record -- this script is the "
                   "only writer, the file is not for hand edits.")
    return found
