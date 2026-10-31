"""reading.tokens -- the SERVING of a document: a token's lines -- by ranges or between
two tags --, a whole document's text, each with its hash. The grammar of a token is the
model's (core.tokens); this module reads bytes and proves them."""
from __future__ import annotations

import hashlib
from pathlib import Path

from ..core.errors import Refusal
from ..core.tokens import parse as ranged   # noqa: F401 -- the grammar is the model's


def sliced(path: Path, ranges: tuple[tuple[int, int], ...]) -> tuple[str, str]:
    """-> (the selected lines, a hash of the selection). A RANGED serve is partial
    by DESIGN: the selection is what is served and what is proven; a bound past
    the end serves what stands."""
    if not path.exists():
        raise Refusal("document-missing", f"{path} does not exist")
    lines = path.read_text(encoding="utf-8").splitlines()
    kept: list[str] = []
    for low, high in ranges:
        kept += lines[low - 1:high]
    text = "\n".join(kept) + "\n"
    return text, hashlib.sha256(text.encode()).hexdigest()[:6]


def spanned(path: Path, span: tuple[str, str]) -> tuple[str, str, str]:
    """-> (the lines between two tags, a hash of the selection, what is missing: `start`,
    `end` or nothing). The file is read RAW, line by line: a tag is matched at the start
    of a line, leading blanks ignored; the end tag is sought after the start's line and
    excluded; an empty tag leaves its side open. A start tag gone selects nothing; an end
    tag gone selects to the end of the document."""
    if not path.exists():
        raise Refusal("document-missing", f"{path} does not exist")
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = span

    def first(tag: str, since: int) -> int | None:
        return next((index for index in range(since, len(lines))
                     if lines[index].lstrip().startswith(tag)), None)

    low = first(start, 0) if start else 0
    if low is None:
        return "", hashlib.sha256(b"").hexdigest()[:6], "start"
    high = first(end, low + 1 if start else 0) if end else len(lines)
    missing = "end" if high is None else ""
    text = "\n".join(lines[low:high]) + "\n"
    return text, hashlib.sha256(text.encode()).hexdigest()[:6], missing


def served(path: Path) -> tuple[str, str]:
    """-> (the document's text, a hash of it). Any text file serves whole; the hash --
    computed HERE, never authored -- is what proves what was served and tells two
    readings apart."""
    if not path.exists():
        raise Refusal("document-missing", f"{path} does not exist")
    text = path.read_text(encoding="utf-8")
    return text, hashlib.sha256(text.encode()).hexdigest()[:6]
