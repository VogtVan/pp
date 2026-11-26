"""The data gestures of the migration 0.2.0-beta.33 -> 0.2.39, and what they share: the frozen data
of the starting version, the atomic rewrite of a file, the front of a document, the records of an
instance."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
RECORDS = Path(".sys") / "records"          # where an instance keeps its records, then and now


def replace(path: Path, text: str) -> None:
    """Writes `text` at `path` in one rename, the file's mode kept."""
    mode = path.stat().st_mode if path.exists() else 0o644
    handle, spot = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="") as out:
            out.write(text)
        os.chmod(spot, mode & 0o7777)
        os.replace(spot, path)
    finally:
        if os.path.exists(spot):          # the temporary file of this write, left by a failed rename:
            os.unlink(spot)               # never a file of the house -- the frame's cleanup removes those


def split(text: str) -> tuple[list[str] | None, str]:
    """-> (the lines of the front, the body after its closing `---`); (None, text) without a front."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 3)
    if end < 0:
        return None, text
    return text[4:end].split("\n"), text[end + 5:]


def joined(front: list[str], body: str) -> str:
    return "---\n" + "\n".join(front) + "\n---\n" + body


def every(kept, record: str) -> list:
    """-> every entry of a store record, in rank order, read in bounded pages."""
    found, cursor = [], None
    while True:
        page = kept.read(record, order="asc", **({} if cursor is None else {"after": cursor}))
        found += page.rows
        if page.next is None:
            return found
        cursor = page.next["after"]
