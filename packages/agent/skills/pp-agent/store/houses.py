"""The house and its agents: the instance a call serves, an agent by its path, the house's own refusals,
the provider it is wired with."""
from __future__ import annotations

import sys
from pathlib import Path

from model.policy import Asked
from model.refusal import RefusalLine
from model.words import HOUSE
from store.refusal import refuse


def bootstrap():
    """-> (`core`, `home`) of the skills' bootstrap `_core`: its folder is put on the path here, once, and
    nowhere else in `store`."""
    skills = str(Path(__file__).resolve().parents[2])
    if skills not in sys.path:
        sys.path.insert(0, skills)
    from _core import core, home                          # noqa: E402 -- the bootstrap
    return core, home


def house():
    """-> (the house's instance root, the conductor module) -- the bootstrap's one walk."""
    core, home = bootstrap()
    root = home(__file__)
    if root is None:
        refuse("not inside an installed instance -- no house to serve.")
    return root, core(__file__)


def agent_at(root: Path, path: str) -> Path:
    """-> where the agent `path` stands: `<house>/<path>/<instance dir>`, the instance
    directory named as the house's own. `.` is the HOUSE itself: its own instance."""
    if path == HOUSE:
        return root
    segments = path.split("/")
    return root.parent.joinpath(*segments) / root.name


def slugs_of(conductor, path: str) -> bool:
    """-> whether every segment of `path`, written with `/`, is a slug as the engine judges one."""
    return all(conductor.instance.valid_slug(one) for one in path.split("/"))


def agent_known(root: Path, conductor, path: str) -> Path:
    """-> where the agent `path` stands, an instance that must be there (`agent-unknown`)."""
    meta = agent_at(root, path)
    if not conductor.instance.is_instance(meta):
        refuse(f"agent-unknown -- no agent at `{path}` under {root.parent} (`./pp agent add {path}` creates it).")
    return meta


def agents_of(root: Path, conductor) -> list[tuple[str, Path]]:
    """-> (path, instance root) of every agent of the house: each instance under the house's
    workspace that borrows the machine (`instance.borrowers`), at any depth, by its path."""
    return [(one.parent.relative_to(root.parent).as_posix(), one)
            for one in conductor.instance.borrowers(root)]


def wired_of(conductor, root: Path) -> list[str]:
    """-> the providers the house is wired with, by their adapters' names."""
    return conductor.install.wired_providers(root.parent)


def engine_of(conductor, root: Path) -> Path:
    """-> the house's engine, the one the agents borrow."""
    return conductor.instance.engine_root(root) / "pp.py"


def documents_asked(root: Path, asked: Asked) -> str | None:
    """-> the root of documents `--documents` names, made absolute -- a relative path read from the
    house's directory --, None when the flag is absent. The engine judges the directory at `-new`."""
    given = asked.documents
    if given is None:
        return None
    path = Path(given).expanduser()
    return str((path if path.is_absolute() else root.parent / path).resolve())


def refusal_line() -> RefusalLine:
    """-> the form of the refusal line of the engine the house runs on, read in its messages
    (`conductor.core.messages`) -- never typed again here."""
    import importlib
    _, conductor = house()
    messages = importlib.import_module(f"{conductor.__name__}.core.messages")
    return RefusalLine(head=messages.REFUSED, separator=messages.SEPARATOR, voice=messages.console(""))
