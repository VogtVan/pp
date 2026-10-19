"""The SUPPORT module of the steering keeper's scenarios (tests/README.md, rule 10): a case
judged as a whole, the record and the settings of an instance, the vendored script played as
the console plays it, and the READERS of what the keeper renders -- the front (its header,
its rows cell by cell, the ⏸ line, the 💤 footer), the ledger (a block per thread, a line
per step) and the line `move` prints. A scenario compares the parts these readers return,
never a rendered sentence. Loaded by `support(__file__, "keeper")`.
"""
from __future__ import annotations

import contextlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

# The front's table header, cell by cell.
HEADER = ["initiative", "note", "progress", "age", "next action(s)"]


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
def record(root: Path) -> dict:
    return json.loads((root / ".sys" / "records" / "threads.json").read_text(encoding="utf-8"))


def graves(root: Path) -> list[dict]:
    path = root / ".sys" / "records" / "threads-closed.jsonl"
    return [json.loads(one) for one in path.read_text(encoding="utf-8").splitlines() if one.strip()]


def tid_of(root: Path, name: str) -> str:
    """-> the id of the open thread wearing `name`."""
    return next(tid for tid, one in record(root)["threads"].items() if one["name"] == name)


def set_to(root: Path, key: str, value: int) -> None:
    """The operator's edit of one setting line of `SETTINGS.md`."""
    settings = root / "SETTINGS.md"
    settings.write_text(re.sub(rf"^{key}:.*$", f"{key}: {value}", settings.read_text(encoding="utf-8"),
                               flags=re.M), encoding="utf-8")


def script_of(root: Path) -> Path:
    """-> the VENDORED keeper of an instance: it reaches the engine through its bootstrap."""
    return next((root / ".sys" / "vendor").glob("steering@*")) / "skills" / "pp-steering" / "pp-steering.py"


def player(script: Path, cwd: Path):
    """-> `play(*args, stdin="", cwd=None, env=None)`: the script in a subprocess, as the
    console runs it."""
    def play(*args: str, stdin: str = "", cwd_: Path | None = None,
             env: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(script), *args], input=stdin, capture_output=True,
                              text=True, cwd=str(cwd_ or cwd), env=env)
    return play


def one_open_thread(root: Path) -> list[str]:
    """-> the steps listed by two open threads or born in a thread nobody knows, at `root`."""
    final = record(root)
    known = set(final["threads"]) | {tomb["id"] for tomb in graves(root)}
    wrong = []
    for sid, step in final["steps"].items():
        if sum(sid in one["steps"] for one in final["threads"].values()) > 1:
            wrong.append(f"{sid} listed twice")
        if step["thread"] not in known or not step["name"]:
            wrong.append(f"{sid} born nowhere")
    return wrong


# --- the readers -------------------------------------------------------------------------
def _read(pattern: re.Pattern, text: str) -> re.Match:
    found = pattern.match(text)
    if found is None:
        raise ValueError(f"unread: {text!r}")
    return found


PIPE = re.compile(r"(?<!\\)\|")
PROGRESS = re.compile(r"^([▰▱]{5}) (\d+)/(\d+)(?: 🔄(\d+))?$")
ACTION = re.compile(r"^`([^`]+)`(\S*)$")
WAITING = re.compile(r"^(\S+) › `([^`]+)`(?: \((.*)\))?$")
FOLDED = re.compile(r"^(?:🔗 )?(\S+) `([^`]+)`\S* \((.+)\)$")
HEAD = re.compile(r"^~ (\S+) \[(\S+)\] \((\S+)\)(?: — (.*))?$")
STEP = re.compile(r"^ (.*?) ?(\S+\.s\.\d+) (\S+)(?: — (.*?))?(?:   \[(\S+)\])?$")
MOVED = re.compile(r"^pp-steering: moved -- (\S+) (\S+) : (\S+) -> (\S+) \[(\S+)\]$", re.M)


@dataclass
class Row:
    """One row of the front's table, cell by cell."""
    flag: str                          # `🔗` for a thread another member owns
    name: str
    note: str
    bar: str
    done: int
    total: int
    redo: int
    age: str
    actions: list[tuple[str, str]]     # (step name, mark), in the row's order
    more: bool                         # `…` past the cap


@dataclass
class Front:
    header: list[str] | None = None
    rows: list[Row] = field(default_factory=list)
    waiting: list[tuple[str, str, str | None]] = field(default_factory=list)   # (thread, step, reason)
    beyond: int = 0                    # the `+n` of the ⏸ line
    dormant: list[tuple[str, str, str]] = field(default_factory=list)          # (thread, step, age)

    def row(self, name: str) -> Row | None:
        return next((one for one in self.rows if one.name == name), None)


def cells(line: str) -> list[str]:
    """-> the cells of a table line, an escaped pipe kept inside its cell."""
    return [one.strip() for one in PIPE.split(line)[1:-1]]


def row_of(said: list[str]) -> Row:
    name, note, progress, age, actions = said
    flag, _, bare = name.rpartition(" ")
    bar, done, total, redo = _read(PROGRESS, progress).groups()
    more = actions.endswith(" …")
    listed = [_read(ACTION, one).groups() for one in actions.removesuffix(" …").split(" · ")]
    return Row(flag, bare, note, bar, int(done), int(total), int(redo or 0), age, listed, more)


def front(text: str) -> Front:
    """-> the front read back into its parts."""
    seen = Front()
    for line in text.splitlines():
        if line.startswith("|---"):
            continue
        if line.startswith("| "):
            if seen.header is None:
                seen.header = cells(line)
            else:
                seen.rows.append(row_of(cells(line)))
        elif line.startswith("⏸ "):
            parts = line.split(" ", 1)[1].split(" · ")
            if parts[-1].startswith("+"):
                seen.beyond = int(parts.pop()[1:])
            seen.waiting = [_read(WAITING, one).groups() for one in parts]
        elif line.startswith("💤 "):
            seen.dormant = [_read(FOLDED, one).groups() for one in line.split(" ", 1)[1].split(" · ")]
    return seen


@dataclass
class Line:
    """One step line of the ledger."""
    mark: str                          # `✓` `->` `🔄` `⛔` `🗑️` or empty
    name: str
    text: str | None
    key: str | None


@dataclass
class Block:
    """One thread of the ledger: its head and its step lines by id, in order."""
    id: str
    owner: str
    note: str | None
    steps: dict[str, Line]


def ledger(text: str) -> dict[str, Block]:
    """-> the ledger (`status --all`) read back, one block per thread name."""
    book = {}
    for chunk in text.split("\n\n"):
        lines = chunk.splitlines()
        if not lines or not lines[0].startswith("~ "):
            continue
        name, tid, owner, note = _read(HEAD, lines[0]).groups()
        steps = {}
        for one in lines[1:]:
            mark, sid, step, said, key = _read(STEP, one).groups()
            steps[sid] = Line(mark.strip(), step, said, key)
        book[name] = Block(tid, owner, note, steps)
    return book


def moved(text: str) -> tuple[str, ...] | None:
    """-> (step id, step name, source name, target name, target id) of the line `move` prints."""
    found = MOVED.search(text)
    return found.groups() if found else None
