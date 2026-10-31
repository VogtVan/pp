"""The SUPPORT module of the plan area's script scenarios (tests/README.md, rule 10): the
HOUSE a scenario installs -- a real instance carrying the plan package --, the vendored
`pp-plan` loaded from it, the gestures a case composes (a section, a framing, an item
prepared or born, a todo, a Delivery), the readers of a document (its front, its entries,
its title, its laws), the parsers of the lines the script prints (a status move, a next
move, a push, a section's answer, a material's answer) and the CASE that judges its checks
without hiding the cases after it. Loaded by `support(__file__, "plan")`; every scenario
installs its own houses.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
from pathlib import Path
from typing import NamedTuple

from tests.harness import load_script

GROUND = "The ground, measured on-piece."
TARGET = "What it becomes."
EXPECTED = "What is true when it closes -- the bench cited."
TESTS = "The scenario to run."


# --- the house and its script ----------------------------------------------------------

def house(bench, name: str, pin: bool = False):
    """-> a REAL environment carrying the plan package -- the script reads it as the
    operator's instance, never a fake."""
    return bench.env(name, ("plan",), pin=pin)


def vendor(root: Path) -> Path:
    """-> the plan package as the instance vendored it."""
    return next((root / ".sys" / "vendor").glob("plan@*"))


def script_path(root: Path) -> Path:
    return vendor(root) / "skills" / "pp-plan" / "pp-plan.py"


def script(root: Path):
    """-> the VENDORED `pp-plan`, not the source's: the script reaches the engine's write
    regime through its bootstrap, which finds one from inside an instance alone."""
    return load_script(script_path(root))


@contextlib.contextmanager
def fed(text: str):
    """stdin reads `text` for the span, restored after."""
    spot, sys.stdin = sys.stdin, io.StringIO(text)
    try:
        yield
    finally:
        sys.stdin = spot


def play(plans, argv: list[str], stdin: str = "") -> str:
    """-> what `pp-plan <argv>` prints, stdin fed -- the console's own entry."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out), fed(stdin):
        plans.main(argv)
    return out.getvalue()


# --- the case ----------------------------------------------------------------------------

class Case:
    """The checks of one case: each missed one is named, none stops the scenario."""

    def __init__(self) -> None:
        self.missed: list[str] = []

    def ok(self, condition, what: str = "a check") -> bool:
        if not condition:
            self.missed.append(what)
        return bool(condition)


@contextlib.contextmanager
def case(bench, label: str, detail: str = ""):
    """One case: ✓ under `label` when every check holds, its ✗ otherwise -- a raise inside
    the case is its failure, never the scenario's end."""
    one = Case()
    try:
        yield one
    except (Exception, SystemExit) as error:                              # noqa: BLE001
        one.missed.append(f"raised {type(error).__name__}: {str(error)[:160]}")
    if one.missed:
        bench.failures.append(f"  ✗ {label}  {'; '.join(one.missed)}")
    else:
        bench.held(label, detail)


# --- the gestures ------------------------------------------------------------------------

class Writer:
    """The gestures a case composes on the script's own functions, for any root."""

    def __init__(self, plans) -> None:
        self.plans = plans

    def section(self, base: Path, segments: list[str], name: str, prose: str,
                append: bool = False) -> tuple[Path, list[str]]:
        """-> (the document, what the write said then the moves it made)."""
        path, said, moves = self.plans.write_section(base, segments, name, prose, append)
        return path, said + moves

    def framed(self, base: Path, segments: list[str]) -> None:
        """The required sections up to Expected, a word each -- what makes a node `doing`;
        a prepared item is born by its Ground first."""
        plans = self.plans
        kind = plans.KINDS[len(segments) - 1]
        if not plans.doc_of(base, *segments).is_file():
            self.section(base, segments, "Ground", GROUND)
        _, body = plans.read(plans.doc_of(base, *segments))
        for name, prose in (("Ground", GROUND), ("Target", TARGET), ("Expected", EXPECTED), ("Tests", TESTS)):
            if name in plans.SECTIONS[kind] and not plans.is_written(kind, name, body):
                self.section(base, segments, name, prose)
                _, body = plans.read(plans.doc_of(base, *segments))

    frame = framed

    def deliver(self, base: Path, segments: list[str], log: str = "landed") -> list[str]:
        """The Delivery that closes a batch -- -> the closings it says."""
        return self.section(base, segments, "Delivery", log)[1]

    def items_of(self, base: Path, segments: list[str]) -> list[tuple[str, str]]:
        plans = self.plans
        kind = plans.KINDS[len(segments) - 1]
        _, body = plans.read(plans.doc_of(base, *segments))
        if not plans.is_written(kind, "Items", body):
            return []
        return plans.item_lines(plans.section_text(body, "Items") or "")

    def prepare(self, base: Path, segments: list[str], brief: str) -> None:
        """One more line in the parent's Items -- the child PREPARED, an entry, no document."""
        self.framed(base, segments[:-1])
        lines = self.items_of(base, segments[:-1]) + [(segments[-1], brief)]
        self.section(base, segments[:-1], "Items", "\n".join(f"- {s} -- {b}" for s, b in lines))

    def grow(self, base: Path, segments: list[str], brief: str) -> None:
        """Prepared, then BORN by its first section."""
        self.prepare(base, segments, brief)
        self.section(base, segments, "Ground", GROUND)

    def todo(self, base: Path, segments: list[str], name: str, text: str) -> None:
        self.prepare(base, segments + [name], text)

    def close_phase(self, base: Path, segments: list[str]) -> list[str]:
        """A phase closes by a delivered batch -- one prepared, framed and delivered under it."""
        self.grow(base, segments + ["closer"], "the batch that closes the phase")
        self.framed(base, segments + ["closer"])
        return self.deliver(base, segments + ["closer"])


# --- the readers -------------------------------------------------------------------------

def front(plans, path: Path) -> dict:
    return plans.read(path)[0]


def kids(plans, path: Path) -> dict[str, str]:
    """-> the entries of a document: name -> status."""
    return dict(plans.children(front(plans, path)))


def title_line(plans, path: Path) -> str:
    return next(line for line in plans.read(path)[1].splitlines() if line.startswith("# "))


def untitled(plans, path: Path) -> str:
    """-> the body without its title line."""
    return "".join(line for line in plans.read(path)[1].splitlines(keepends=True)
                   if not line.startswith("# "))


def of(lines: list[str], slug: str) -> list[str]:
    """-> the findings (or mends) whose spot lies in the plan `slug`."""
    return [one for one in lines if one.split(":", 1)[0].split("/")[0] == slug]


def spots(lines: list[str]) -> set[str]:
    """-> the spots a list of findings or mends names."""
    return {one.split(":", 1)[0] for one in lines}


LAW = re.compile(r"^  ([A-Z][A-Z0-9]*?[0-9]+)  (.*)$")


def laws(path: Path) -> dict[str, dict[str, str]]:
    """-> the laws a document's front matter poses: `constraints.<section>` -> code -> text."""
    lines = path.read_text(encoding="utf-8").splitlines()
    found: dict[str, dict[str, str]] = {}
    key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line[:1] not in (" ", "\t") and ":" in line:
            key = line.split(":", 1)[0].strip()
            if key.startswith("constraints."):
                found[key] = {}
            continue
        hit = LAW.match(line)
        if key in found and hit:
            found[key][hit.group(1)] = hit.group(2)
    return found


# --- the parsers of what the script prints -----------------------------------------------

class Move(NamedTuple):
    status: str
    closes: tuple[str, ...]
    tail: str


MOVED = re.compile(r"^pp-plan: (\S+) -> (\w+)(?: -- (.*))?$")


def moves(said) -> dict[str, Move]:
    """-> the status moves a call says: address -> (new status, the nodes it closed, the
    tail after the dash)."""
    lines = said.splitlines() if isinstance(said, str) else said
    found = {}
    for line in lines:
        hit = MOVED.match(line)
        if hit:
            tail = hit.group(3) or ""
            closes = tuple(tail.removeprefix("closes ").split(", ")) if tail.startswith("closes ") else ()
            found[hit.group(1)] = Move(hit.group(2), closes, tail)
    return found


NEXT = re.compile(r"^the (plan|phase|batch) .*?(?:awaits its (framing|implementation|batches)"
                  r"|is (reopened)|has no (phase) yet).*\(([a-z-]+:\S+)\)$")


def move_of(line: str | None) -> tuple[str, str, str] | None:
    """-> a next move as (the node's kind, the word it awaits -- framing, implementation,
    batches, rework or phases --, its vector), None for no move."""
    hit = NEXT.match(line or "")
    if hit is None:
        return None
    word = hit.group(2) or ("rework" if hit.group(3) else "phases")
    return hit.group(1), word, hit.group(5)


def pushes(said: str) -> list[tuple[str, str, str, str]]:
    """-> the `::push` / `::clear` lines: (verb, signal, key, the action after the key)."""
    found = []
    for line in said.splitlines():
        if line.startswith(("::push ", "::clear ")):
            parts = line.split(" ", 3)
            found.append((parts[0], parts[1], parts[2], parts[3] if len(parts) > 3 else ""))
    return found


ANSWERED = re.compile(r"^pp-plan: (.+?) ((?:born|replaced|inserted|appended)(?: and \w+)*) on (\S+) -- (\S+)$")


def answers(said: str) -> list[tuple[str, tuple[str, ...], str, str]]:
    """-> what a section call answers: (the section, what it did, the address, the path)."""
    return [(hit.group(1), tuple(hit.group(2).split(" and ")), hit.group(3), hit.group(4))
            for hit in map(ANSWERED.match, said.splitlines()) if hit]


MATERIAL = re.compile(r"^pp-plan: material (?:`(\S+)` written on|taken out of) (\S+) -- (\d+) document\(s\): (.*)$")


def material_said(said: str) -> tuple[str | None, str, int, list[str]] | None:
    """-> what `material` answers: (the name written, None taken out; the plan; the count;
    the documents listed)."""
    hit = next(filter(None, map(MATERIAL.match, said.splitlines())), None)
    if hit is None:
        return None
    return hit.group(1), hit.group(2), int(hit.group(3)), hit.group(4).split(", ")
