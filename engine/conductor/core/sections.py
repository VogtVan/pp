"""core.sections -- the WRITER of a conducted document's front matter.

The engine has always PARSED a front matter; this is the other half. It is a
library: it raises `Refusal`, reads no stdin and writes no screen -- a console
(`pp-authoring`) or a package's own script (`pp-plan`) hands it the values and
says what to do with a refusal.

documentary: the edit is SURGICAL -- the document is split in lines and the
targeted key's span alone is replaced; untouched keys are never re-emitted, so
everything a writer does not own travels byte for byte.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

import yaml

from . import tokens
from .errors import Refusal

BUDGET = 500          # characters per value line -- a section is a contract, not a report
KEY = re.compile(r"^[a-z][a-z0-9_.-]*$")
CODE = re.compile(r"^\s\s([A-Z][A-Z0-9]*?[0-9]+)\s\s")     # `  KX1  text` -- a declared law
STOPWORDS = {"le", "la", "les", "l", "de", "des", "du", "et", "a", "au", "aux"}
SECTIONS = ("production", "behavior")   # the two sections of a document's laws

def bounded(value: list[str]) -> list[str]:
    """-> the piped value, trailing blanks dropped -- empty or over budget refuses."""
    lines = list(value)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines or not any(one.strip() for one in lines):
        raise Refusal("value-malformed", "an empty value writes nothing")
    for one in lines:
        if len(one) > BUDGET:
            raise Refusal("budget", f"{len(one)} chars on one line -- the budget is {BUDGET}")
    return lines


def front_span(lines: list[str]) -> tuple[int, int]:
    """-> (first, last) line indexes INSIDE the front matter -- the borders excluded."""
    if not lines or lines[0].strip() != "---":
        raise Refusal("frontmatter-missing", "the document opens on no `---` border")
    for at, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return 1, at
    raise Refusal("frontmatter-missing", "the front matter never closes")


def key_span(lines: list[str], start: int, end: int, key: str) -> tuple[int, int] | None:
    """-> the key's line span [first, last) inside the front matter -- the head line
    and every indented continuation of a block scalar; None when absent."""
    for at in range(start, end):
        if lines[at].startswith(f"{key}:"):
            stop = at + 1
            while stop < end and (lines[stop].startswith("  ") or not lines[stop].strip()):
                stop += 1
            return at, stop
    return None


def guard_key(key: str, lines: list[str], start: int, end: int) -> None:
    if not KEY.fullmatch(key):
        raise Refusal("key-invalid", f"`{key}` -- a key is lowercase, dots and dashes allowed")


def reads_back(text: str) -> bool:
    """-> whether `key: <text>` reads back, through the engine's YAML reader, as that very
    string -- a colon inside, a comment mark, an indicator in front or a word YAML types
    (`yes`, `3`, `null`) make it read otherwise, or not at all."""
    try:
        return yaml.safe_load(f"k: {text}") == {"k": text}
    except yaml.YAMLError:
        return False


def rendered(key: str, value: list[str]) -> list[str]:
    """-> the key's lines as the engine's reader parses them back: one line inline when it
    reads back as written, double-quoted otherwise (a JSON string is a YAML string); a block
    scalar for several lines."""
    if len(value) == 1:
        one = value[0].strip()
        return [f"{key}: {one if reads_back(one) else json.dumps(one, ensure_ascii=False)}"]
    return [f"{key}: |"] + [f"  {one}" for one in value]


def write(path: Path, lines: list[str]) -> None:
    handle, spot = tempfile.mkstemp(dir=path.parent, prefix=".section-")
    with os.fdopen(handle, "w", encoding="utf-8") as temp:
        temp.write("\n".join(lines) + "\n")
    os.replace(spot, path)


def get(path: Path, key: str) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = front_span(lines)
    span = key_span(lines, start, end, key)
    if span is None:
        raise Refusal("key-unknown", f"`{key}` is not in {path.name}'s front matter")
    try:
        read = yaml.safe_load("\n".join(lines[span[0]:span[1]]))
    except yaml.YAMLError:
        read = None
    value = read.get(key) if isinstance(read, dict) else None
    if isinstance(value, str):
        # what the reader reads: a quoted value unquoted, a folded or chomped block its text
        return value.rstrip("\n")
    head = lines[span[0]].split(":", 1)[1]
    if head.strip() and head.strip() != "|":
        return head.strip()
    return "\n".join(one[2:] if one.startswith("  ") else one
                     for one in lines[span[0] + 1:span[1]])


def edit(path: Path, key: str, value: list[str] | None, create: bool) -> None:
    """set/add/remove in ONE splice: the span replaced, nothing else touched."""
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = front_span(lines)
    guard_key(key, lines, start, end)
    span = key_span(lines, start, end, key)
    if create and span is not None:
        raise Refusal("key-taken", f"`{key}` already there -- `set` replaces it")
    if not create and span is None:
        raise Refusal("key-unknown", f"`{key}` is not in {path.name}'s front matter")
    if value is None:                                       # remove
        lines[span[0]:span[1]] = []
    elif span is None:                                      # add: before the closing border
        lines[end:end] = rendered(key, value)
    else:                                                   # set: the span alone moves
        lines[span[0]:span[1]] = rendered(key, value)
    write(path, lines)


def inventory(root: Path) -> set[str]:
    """-> every constraint code DECLARED across the instance -- vendored and local
    documents alike: the same universe the build's collision lint walks."""
    found = set()
    for doc in root.rglob("*.md"):
        if ".git" in doc.parts:
            continue
        try:
            text = doc.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            match = CODE.match(line)
            if match:
                found.add(match.group(1))
    return found


def derived_prefix(path: Path) -> str:
    """-> the document's own prefix: K + the initials of its name's plain words -- the
    `slug:` its front matter declares when it declares one, the file's stem otherwise."""
    name = path.stem
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if line == "---":
            break
        if line.startswith("slug:"):
            name = line.split(":", 1)[1].strip()
            break
    words = [one for one in re.split(r"[-_.]", name)
             if one and one not in STOPWORDS and not one.isdigit()]
    return "K" + "".join(one[0].upper() for one in words)[:3]


def constrain(root: Path, path: Path, prefix: str | None, section: str,
              texts: list[str]) -> list[str]:
    """Writes law TEXTS under codes the script derives, in the section named: the
    numbering continues past every code the instance already declares -- a
    collision cannot happen -- and a law is written in `constraints.<section>`, never
    in a bare `constraints:` (the engine refuses that key)."""
    if section not in SECTIONS:
        raise Refusal("section-missing", "`--section production|behavior` names where the law lives")
    stem = prefix if prefix else derived_prefix(path)
    if not re.fullmatch(r"[A-Z][A-Z0-9]*", stem):
        raise Refusal("key-invalid", f"`{stem}` -- a prefix is uppercase letters")
    taken = inventory(root)
    rank = 0
    for code in taken:
        match = re.fullmatch(rf"{stem}(\d+)", code)
        if match:
            rank = max(rank, int(match.group(1)))
    posed = []
    for text in texts:
        rank += 1
        posed.append(f"{stem}{rank}  {text.strip()}")
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = front_span(lines)
    span = key_span(lines, start, end, f"constraints.{section}")
    if span is None:
        lines[end:end] = [f"constraints.{section}: |"] + [f"  {one}" for one in posed]
    else:
        lines[span[1]:span[1]] = [f"  {one}" for one in posed]
    write(path, lines)
    return [one.split("  ", 1)[0] for one in posed]


def valid_token(token: str) -> None:
    """The writer refuses exactly what the engine's reader will refuse: the grammar is
    the model's, one parser for both."""
    tokens.parse(token, shape="token-invalid")


DISCOURAGED = "a line range drifts when the file moves; prefer tags"


def serve(path: Path, rows: list[list[str]], whole: bool = False) -> str:
    """Appends ONE `serve:` line to the LAST section -- or replaces the whole block
    when the lines come piped (`-`), blank lines kept: a blank line separates two
    SECTIONS, and a bare SERVE plays one section whole. The grouping lines are the
    framing's voice, their order is the reading order. -> the count of lines written,
    then one line per token that selects by LINE RANGES: written as asked, and discouraged."""
    drifting: list[str] = []
    for row in rows:
        for token in row:
            name, cut = tokens.parse(token, shape="token-invalid")
            if len(cut):
                drifting.append(f"`{token}` -- {DISCOURAGED}: `{name}[<start>..<end>]`")
    lines = path.read_text(encoding="utf-8").splitlines()
    start, end = front_span(lines)
    span = key_span(lines, start, end, "serve")
    rendered_rows = [f"  {' '.join(row)}" if row else "" for row in rows]
    if whole or span is None:
        replacement = ["serve: |"] + rendered_rows
        if span is None:
            lines[end:end] = replacement
        else:
            lines[span[0]:span[1]] = replacement
    else:
        lines[span[1]:span[1]] = rendered_rows   # one more line of the last section
    write(path, lines)
    return "\n".join([f"{sum(1 for row in rows if row)} line(s)"] + drifting)
