"""_common.house -- a house read from its files alone, without its engine: its version, its source,
its instances, its plan roots, its teams."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .refusal import Refused

INSTANCE = ".pp"                                    # the instance directory of the house and of each agent
MANIFEST = Path(".sys") / "instance.yaml"           # marks a directory as an instance
ENGINE = Path(".sys") / "engine"                    # the machine's engine, under the house's instance alone
VERSION = Path("conductor") / "core" / "version.py"  # where an engine says its version
PRUNED = {".git", ".sys", "node_modules", ".venv", "__pycache__", "_templates"}
SAID = re.compile(r'^VERSION\s*=\s*["\']([^"\']+)["\']', re.M)


@dataclass
class House:
    """One house: its root, its instance, the version of its engine, the source it was installed
    from, its instances (the house's first, then each agent's), its plan roots, its teams."""
    root: Path
    meta: Path
    version: str | None
    source: str
    instances: list[Path] = field(default_factory=list)
    plans: list[Path] = field(default_factory=list)
    teams: list[Path] = field(default_factory=list)


def version_of(engine: Path) -> str | None:
    """-> the version an engine directory says (`conductor/core/version.py`), None without one."""
    path = engine / VERSION
    if not path.is_file():
        return None
    found = SAID.search(path.read_text(encoding="utf-8"))
    return found.group(1) if found else None


def source_version(source: Path) -> str | None:
    """-> the version of a product checkout, None when it carries no engine."""
    return version_of(source / "engine")


def read(root: Path) -> House:
    """-> the house at `root`. Refuses `house-missing` when `root` carries no instance with its own
    engine -- an agent's instance borrows its house's, and is migrated with it."""
    root = Path(root).expanduser().resolve()
    meta = root / INSTANCE
    if not (meta / MANIFEST).is_file() or not (meta / ENGINE).is_dir():
        raise Refused("house-missing", f"{root} carries no house: no {INSTANCE}/{MANIFEST.as_posix()} "
                                       f"with its engine")
    declared = yaml.safe_load((meta / MANIFEST).read_text(encoding="utf-8")) or {}
    found = House(root=root, meta=meta, version=version_of(meta / ENGINE),
                  source=str(declared.get("source") or ""))
    found.instances = instances(root)
    found.teams = sorted(team.parent for team in (root / "teams").glob("*/TEAM.md"))
    found.plans = [one / "plans" for one in found.instances + found.teams if (one / "plans").is_dir()]
    return found


def instances(root: Path) -> list[Path]:
    """-> every instance under the house, its own first: each `.pp` that carries a manifest, the
    walk pruned of what never holds one."""
    found = []
    for here, directories, _ in os.walk(root):
        if INSTANCE in directories and (Path(here) / INSTANCE / MANIFEST).is_file():
            found.append(Path(here) / INSTANCE)
        directories[:] = sorted(name for name in directories if name not in PRUNED and name != INSTANCE)
    own = root / INSTANCE
    return [own] + sorted(one for one in found if one != own)
