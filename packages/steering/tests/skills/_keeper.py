"""The SUPPORT module of the steering keeper's scenarios (tests/README.md, rule 10): a case
judged as a whole, the record and the settings of an instance, the vendored script played in
process or as the console plays it, the frozen clock, and the readers of what the keeper
renders as data (`list --json`, `show --json`). A scenario compares the fields these readers
return, never a rendered sentence. Loaded by `support(__file__, "keeper")`.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CLOCK = "PP_NOW"      # the variable the keeper reads its instant from


# --- a case ------------------------------------------------------------------------------
class Checks:
    """The checks of one case: each failed one is kept with what it says."""

    def __init__(self) -> None:
        self.missed: list[str] = []

    def __call__(self, ok: object, why: str) -> bool:
        if not ok:
            self.missed.append(why)
        return bool(ok)


@contextlib.contextmanager
def case(bench, label: str, detail: str):
    """One case: `held(label, detail)` when every check passed, else one ✗ naming what
    missed -- an exception raised inside the case is one of them, and the cases after it
    still play."""
    checks = Checks()
    try:
        yield checks
    except (Exception, SystemExit) as error:                               # noqa: BLE001
        checks.missed.append(f"raised {type(error).__name__}: {error}")
    if checks.missed:
        bench.failures.append(f"  ✗ {label}  {' · '.join(checks.missed)}")
    else:
        bench.held(label, detail)


def refused(bench, played: subprocess.CompletedProcess, code: str) -> bool:
    """A refusal of the script played in a subprocess: exit 2 with `code` on stderr."""
    bench.refusals += 1
    if played.returncode == 2 and code in played.stderr:
        bench.held(code, "refused by the script")
        return True
    bench.failures.append(f"  ✗ {code:<28}exit {played.returncode} -- {played.stderr.strip()[:80]}")
    return False


# --- an instance -------------------------------------------------------------------------
def spool(root: Path) -> Path:
    """-> the keeper's record of an instance."""
    return root / ".sys" / "records" / "steps.json"


def record(root: Path) -> dict:
    return json.loads(spool(root).read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    """-> the sha256 of a file, to say it stood byte for byte."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def short(sid: str) -> str:
    """-> `s.<n>`: the short form the keeper renders for a step of the instance's member."""
    return "s." + sid.rsplit(".", 1)[1]


def whole(root: Path, said: str) -> str:
    """-> the whole id of the instance's member for a short one."""
    return f"{root.resolve().parent.name}.{said}" if said.startswith("s.") else said


def set_to(root: Path, key: str, value: int) -> None:
    """The operator's edit of one setting line of `SETTINGS.md`."""
    settings = root / "SETTINGS.md"
    settings.write_text(re.sub(rf"^{key}:.*$", f"{key}: {value}", settings.read_text(encoding="utf-8"),
                               flags=re.M), encoding="utf-8")


def script_of(root: Path) -> Path:
    """-> the VENDORED keeper of an instance: it reaches the engine through its bootstrap."""
    return next((root / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"


def player(script: Path, cwd: Path):
    """-> `play(*args, stdin="", cwd_=None, env=None)`: the script in a subprocess, as the
    console runs it."""
    def play(*args: str, stdin: str = "", cwd_: Path | None = None,
             env: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(script), *args], input=stdin, capture_output=True,
                              text=True, cwd=str(cwd_ or cwd), env=env)
    return play


@contextlib.contextmanager
def frozen(instant: str):
    """The keeper's clock set to `instant` (ISO) for the block, restored after."""
    kept = os.environ.get(CLOCK)
    os.environ[CLOCK] = instant
    try:
        yield
    finally:
        if kept is None:
            os.environ.pop(CLOCK, None)
        else:
            os.environ[CLOCK] = kept


# --- the readers -------------------------------------------------------------------------
def said(keeper, *argv: str) -> str:
    """-> what the in-process keeper prints for `argv`; its exit code must be 0."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = keeper.main(list(argv))
    if code != 0:
        raise AssertionError(f"{' '.join(argv)} -> rc {code}")
    return out.getvalue()


def listed(keeper, *flags: str) -> list[dict]:
    """-> the steps `list --json` returns, each with its `id`."""
    return json.loads(said(keeper, "list", "--json", *flags))


def shown(keeper, sid: str) -> dict:
    """-> the step `show --json` returns, with its `id`."""
    return json.loads(said(keeper, "show", sid, "--json"))


def minted(keeper, *argv: str) -> str:
    """-> the id of the step `add` mints: the newest id of the record after the call."""
    said(keeper, "add", *argv)
    root = keeper.home()
    return max(record(root)["steps"], key=lambda sid: int(sid.rsplit(".", 1)[1]))
