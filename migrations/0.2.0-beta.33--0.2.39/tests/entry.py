"""Scenario `entry` -- the entry `migrate.py` of the migration 0.2.0-beta.33 -> 0.2.39, played as a
user plays it, in its own process, on throwaway houses:
- a house that does not stand at 0.2.0-beta.33 refuses `house-version`, rc 2, nothing written
- a source that does not stand at 0.2.39 refuses `source-version`, rc 2, nothing written
- a pp living in the house refuses `house-busy`, rc 2, nothing written
- `--dry-run` on a house at the starting version: rc 0, nothing written, no backup, no journal
- what stays the user's after a migration: `next` read in the packages of `instance.yaml` (a slug
  that holds the word pins nothing), the house read by the frame's grammar, `--from <source>` first;
  a dry run (`--dry`, the parser's abbreviation, included) says none of it
"""
from __future__ import annotations

import hashlib
import importlib.util
import subprocess
import sys
from pathlib import Path

from tests.harness import SOURCE, support
from conductor.state import lock

old = support(__file__, "old_form")
sys.path.insert(0, str(old.MIGRATION.parent))
from _common import refusal   # noqa: E402 -- `_common` lives beside the migrations
ENTRY = old.MIGRATION / "migrate.py"
FROM = "0.2.0-beta.33"
VERSION = Path("conductor") / "core" / "version.py"


def fingerprint(root: Path) -> str:
    """-> one digest of the house and of what stands beside it: every path, every content."""
    digest = hashlib.sha256()
    for path in sorted(root.parent.rglob("*")):
        digest.update(path.relative_to(root.parent).as_posix().encode())
        if path.is_file() and not path.is_symlink():
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def migrate(root: Path, source: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ENTRY), str(root), "--from", str(source), *extra],
                          capture_output=True, text=True, stdin=subprocess.DEVNULL)


def code_of(done: subprocess.CompletedProcess) -> str | None:
    return refusal.code_of(done.stderr)


def entry():
    """-> the module `migrate.py`, loaded by its path: its entry plays only as `__main__`."""
    spec = importlib.util.spec_from_file_location("migrate_entry", ENTRY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def at_version(path: Path, version: str) -> None:
    """The engine at `path` says `version`: what a house or a source at another version carries."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'VERSION = "{version}"\n', encoding="utf-8")


def refuses(bench, code: str, root: Path, source: Path) -> None:
    before = fingerprint(root)
    done = migrate(root, source)
    if done.returncode == 2 and code_of(done) == code and fingerprint(root) == before:
        bench.held(code, "rc 2, nothing written")
    else:
        bench.failures.append(f"  ✗ {code:<28}rc {done.returncode} code {code_of(done)!r} -- {done.stderr.strip()[-300:]}")


def scenario(bench) -> int:
    env = bench.env("house", packages=old.PACKAGES, at=bench.temp() / "arrived")
    refuses(bench, "house-version", env.root, SOURCE)

    env = bench.env("house", packages=old.PACKAGES, at=bench.temp() / "starting")
    root = env.root
    at_version(env.made / ".sys" / "engine" / VERSION, FROM)
    other = bench.temp() / "other-source"
    at_version(other / "engine" / VERSION, "0.0.0")
    refuses(bench, "source-version", root, other)

    lease = lock.try_(lock.maintenance_of(env.made), shared=True)        # a pp living in the house
    try:
        refuses(bench, "house-busy", root, SOURCE)
    finally:
        lock.release(lease)

    before = fingerprint(root)
    done = migrate(root, SOURCE, "--dry-run")
    beside = sorted(root.parent.glob(f"{root.name}.pre-*"))
    if done.returncode == 0 and fingerprint(root) == before and not beside:
        bench.held("dry-run", "rc 0, nothing written, no backup, no journal")
    else:
        bench.failures.append(f"  ✗ dry-run                     rc {done.returncode} beside {beside} "
                              f"-- {done.stderr.strip()[-300:]}")

    # what stays the user's: `next` read in the pinned packages, the house by the frame's grammar
    import yaml
    module = entry()
    manifest = env.made / ".sys" / "instance.yaml"
    declared = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    declared["slug"] = "next-door"                        # the word, and no package next
    manifest.write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")
    first = module.said(["--from", str(SOURCE), str(root)])
    declared["packages"]["next"] = "0.1.2"
    manifest.write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")
    second = module.said([str(root), "--from", str(SOURCE)])
    if (first[0] == root and module.NEXT in first[1] and second[0] == root
            and module.NEXT not in second[1]):
        bench.held("next", "read in the pinned packages, the house read whatever the order of the arguments")
    else:
        bench.failures.append(f"  ✗ next                        {first} then {second}")
    declared["packages"].pop("next")
    manifest.write_text(yaml.safe_dump(declared, sort_keys=False), encoding="utf-8")
    dry = module.said([str(root), "--from", str(SOURCE), "--dry"])     # the parser's abbreviation of --dry-run
    if dry == (root, []):
        bench.held("dry-silent", "a dry run, abbreviated or not, says nothing of what stays the user's")
    else:
        bench.failures.append(f"  ✗ dry-silent                  {dry}")
    return 0
