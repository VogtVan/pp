"""The SUPPORT module of the `steering` area's engine scenarios (tests/README.md, rule 10):
the keeper vendored in an instance -- its script, loaded or run in a subprocess --, the console
of that instance, and the keeper's steps read through the engine's store module. Loaded by `support(__file__, "steering")`; every scenario
installs its own house.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.harness import load_script

STEPS = ("steps", "labels", "counters")     # the keeper's records in the store


def keeper_script(meta: Path) -> Path:
    """-> the keeper's script in the instance's vendored steering bundle."""
    return next((meta / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"


def keeper_module(meta: Path):
    """-> the vendored keeper loaded as a module, for the writes a case makes in-process."""
    return load_script(keeper_script(meta))


def console(meta: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run([str(meta.parent / "pp"), *args], input=stdin, capture_output=True, text=True,
                          cwd=str(meta.parent))
    return done.stdout + done.stderr


def keeper(meta: Path, *args: str, stdin: str = "") -> str:
    done = subprocess.run([sys.executable, str(keeper_script(meta)), *args], input=stdin, capture_output=True,
                          text=True, cwd=str(meta.parent))
    return done.stdout + done.stderr


def steps(meta: Path) -> dict:
    """-> the steps of the instance's store, `{id: step}`, read in bounded pages."""
    return {one.key: one.body for one in _every(meta, "steps")}


def digest(meta: Path) -> str:
    """-> the sha256 of the keeper's records, ranks and dates included: to say they stood."""
    import hashlib
    import json
    shown = {name: [(one.seq, one.at, one.key, one.body) for one in _every(meta, name)] for name in STEPS}
    return hashlib.sha256(json.dumps(shown, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _every(meta: Path, name: str) -> list:
    from conductor import store
    found, cursor, kept = [], None, store.of(meta)
    while True:
        page = kept.read(name, order="asc", **({} if cursor is None else {"after": cursor}))
        found += page.rows
        if page.next is None:
            return found
        cursor = page.next["after"]
