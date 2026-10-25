"""Support of the drawer `packaging`: what its scenarios share to install from a pattern's
demonstration -- the parts of a demonstrated package read from the pattern's folder, a SOURCE
reduced to the bench's engine, base and template with the packages and bases a demonstration
declares, an instance installed from it, a package unpinned as `remove` leaves it.
Never a scenario: the runner collects no file whose name opens on `_` (rule 10)."""
from __future__ import annotations

import shutil
from pathlib import Path

from conductor import discovery, install, instance
from tests.harness import PATTERNS

SPACES = ("system", "user", "seed")      # the folders of a package placed file by file


def parts(pattern: str, name: str) -> dict:
    """-> the parts of the package `name` the drawer's `pattern` demonstrates, each read under its
    package's name: `manifests/<name>.yaml`, `fragments/<name>.md`, `systems/<name>.<part>.md` (its
    `system/SYSTEM.<PART>.md`), `users/<name>/` and `seeds/<name>/` (its `user/` and `seed/`)."""
    home = PATTERNS / "packaging" / pattern
    found: dict = {"manifest": (home / "manifests" / f"{name}.yaml").read_text(encoding="utf-8")}
    fragment = home / "fragments" / f"{name}.md"
    if fragment.is_file():
        found["fragment"] = fragment.read_text(encoding="utf-8")
    systems = {f"SYSTEM.{path.name[len(name) + 1:-3].upper()}.md": path.read_text(encoding="utf-8")
               for path in sorted((home / "systems").glob(f"{name}.*.md"))}
    if systems:
        found["system"] = systems
    for space, folder in (("user", "users"), ("seed", "seeds")):
        files = home / folder / name
        if files.is_dir():
            found[space] = {path.name: path.read_text(encoding="utf-8")
                            for path in sorted(files.iterdir()) if path.is_file()}
    return found


def _place(home: Path, parts: dict) -> None:
    """One package or base written at `home` from its parts."""
    home.mkdir(parents=True)
    (home / "package.yaml").write_text(parts["manifest"], encoding="utf-8")
    for space in ("procs", "overlays"):
        for stem, text in parts.get(space, {}).items():
            (home / space).mkdir(exist_ok=True)
            (home / space / f"{stem}.md").write_text(text, encoding="utf-8")
    if parts.get("fragment") is not None:
        (home / "settings").mkdir()
        (home / "settings" / "SETTINGS.md").write_text(parts["fragment"], encoding="utf-8")
    for space in SPACES:
        for file, text in parts.get(space, {}).items():
            (home / space).mkdir(exist_ok=True)
            (home / space / file).write_text(text, encoding="utf-8")
    for skill, code in parts.get("skills", {}).items():
        folder = home / "skills" / skill
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: the {skill} skill\n"
                                         f"---\n\n{skill}\n", encoding="utf-8")
        (folder / f"{skill}.py").write_text(code, encoding="utf-8")


def source(bench, packages: dict[str, dict], bases: dict[str, dict] | None = None) -> Path:
    """-> the root of a source carrying the bench's engine, base and template, each package of
    `packages` under `packages/<name>/` and each base of `bases` under `bases/<name>/`, from their
    parts `{"manifest": text, "procs": {stem: text}, "overlays": {stem: text}, "fragment": text,
    "system": {file: text}, "user": {file: text}, "seed": {file: text}, "skills": {name: code}}`."""
    root = bench.temp() / "product"
    for part in ("engine", "bases", "template"):
        shutil.copytree(bench.source() / part, root / part,
                        ignore=shutil.ignore_patterns("__pycache__"))
    for folder, homes in (("packages", packages), ("bases", bases or {})):
        for name, one in homes.items():
            _place(root / folder / name, one)
    return root


def installed(bench, root: Path, name: str, packages: list[str], base: str | None = None):
    """-> `(made, member)`: an instance installed from the source `root` with `packages`, on the
    base `base` when one is named."""
    made = install.install(root / "engine" / "pp.py", bench.temp() / name / ".pp", packages, base=base)
    return made, discovery.instance_member(made / ".sys" / "engine" / "pp.py")


def unpin(made: Path, name: str) -> None:
    """The package unpinned AND gone from the vendor, as `remove` leaves it."""
    pins = instance.read(made)
    pins["packages"].pop(name, None)
    instance.write(made, pins)
    shutil.rmtree(made / ".sys" / "vendor" / f"{name}@0.0.1", ignore_errors=True)
