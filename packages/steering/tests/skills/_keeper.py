"""The SUPPORT module of the steering keeper's scenarios (tests/README.md, rule 10): a case
judged as a whole, the record and the settings of an instance, the vendored script played in
process or as the console plays it, the frozen clock, and the readers of what the keeper
renders as data (`list --json`, `show --json`), the keeper's records read
through the engine's store module. A scenario compares the fields these readers
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
STEPS, LABELS, COUNTERS = "steps", "labels", "counters"     # the keeper's records in the store
STAMPS = ("at", "touched", "closed", "archived", "recalled")


def kept(root: Path):
    """-> the instance's store, through the engine's own module: the bench never opens the base."""
    from conductor import store
    return store.of(root)


def every(root: Path, name: str, **query) -> list:
    """-> every entry of a record of the store, in rank order, read in bounded pages."""
    found, cursor, base = [], None, kept(root)
    while True:
        page = base.read(name, order="asc", **query, **({} if cursor is None else {"after": cursor}))
        found += page.rows
        if page.next is None:
            return found
        cursor = page.next["after"]


def record(root: Path) -> dict:
    """-> the keeper's three records as one value, `{counters, steps, labels}`."""
    counter = kept(root).get(COUNTERS, "s")
    return {"counters": {"s": counter.body["value"] if counter else 0},
            "steps": {one.key: one.body for one in every(root, STEPS)},
            "labels": {one.key: one.body for one in every(root, LABELS)}}


def entries(root: Path) -> dict:
    """-> each step's entry as the store holds it, `{id: (seq, at, body)}`: what a write moved."""
    return {one.key: (one.seq, one.at, one.body) for one in every(root, STEPS)}


def digest(root: Path) -> str:
    """-> the sha256 of the keeper's records with their ranks and dates, to say they stood."""
    shown = {name: [(one.seq, one.at, one.key, one.body) for one in every(root, name)]
             for name in (STEPS, LABELS, COUNTERS)}
    return hashlib.sha256(json.dumps(shown, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def last_write(step: dict) -> str:
    """-> the time a keeper would have written a step last: the latest of its stamps -- None, the
    store's now, for a body that carries none."""
    return max((step[one] for one in STAMPS if step.get(one)), default=None)


def lay(root: Path, steps: dict, labels: dict | None = None, counter: int | None = None) -> None:
    """Lays steps (and labels, the counter) BY HAND in the store, as the keeper would have written
    them -- each step at the time of its last stamp; the operator's forge of a case."""
    with kept(root).transaction() as session:
        for sid, step in steps.items():
            session.put(STEPS, sid, step, at=last_write(step))
        for name, held in (labels or {}).items():
            session.put(LABELS, name, held)
        if counter is not None:
            session.put(COUNTERS, "s", {"value": counter})


def filled(root: Path, count: int, at: str, start: int = 1) -> int:
    """A SYNTHETIC book: `count` ARCHIVED done steps of the member added in one call
    (`store.extend`), ids from `start` -- the large record a read is measured on."""
    member = root.resolve().parent.name
    body = lambda n: {"name": f"un-pas-archive-{n}", "at": at, "work": f"le travail archive {n} " * 4,
                      "comment": "", "status": "done", "reason": "", "labels": ["le-lot-archive"], "key": None,
                      "touched": at, "closed": at, "archived": at, "recalled": None}
    return len(kept(root).extend(STEPS, ({"key": f"{member}.s.{n}", "body": body(n), "at": at}
                                         for n in range(start, start + count))))


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
    counter = kept(keeper.home()).get(COUNTERS, "s").body["value"]
    return f"{keeper.home().resolve().parent.name}.s.{counter}"


LARGE = 100_000      # the archived steps of the large book


def large_book(bench, name: str, now: str, archived_at: str):
    """-> (the instance, its player under the clock `now`, its member) of a LARGE book: `LARGE`
    archived done steps (`filled`) and 60 active open ones born and touched at `now`, ids after them."""
    import os
    made = bench.env(name, ("steering",), pin=False).made
    run = player(script_of(made), made.parent)
    filled(made, LARGE, archived_at, start=1)
    member = made.resolve().parent.name
    lay(made, {f"{member}.s.{LARGE + n}": {"name": f"un-pas-actif-{n}", "at": now, "work": f"le travail actif {n}",
                                           "comment": "", "status": "open", "reason": "", "labels": [], "key": None,
                                           "touched": now, "closed": None, "archived": None, "recalled": None}
                for n in range(1, 61)}, counter=LARGE + 60)
    return made, (lambda *args: run(*args, env={**os.environ, CLOCK: now})), member
