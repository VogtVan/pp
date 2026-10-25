"""The SUPPORT module of the `steering` area's engine scenarios (tests/README.md, rule 10):
the keeper vendored in an instance -- its script, loaded or run in a subprocess -- and the
console of that instance. Loaded by `support(__file__, "steering")`; every scenario
installs its own house.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from tests.harness import load_script


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
