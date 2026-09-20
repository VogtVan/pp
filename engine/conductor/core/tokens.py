"""core.tokens -- the GRAMMAR of a serve token, read without opening a file: a row cut
into its tokens, a token parsed into its name and its selector. The reader, the lint and
the writer read these functions and nothing else; a mount entry's selection reads
`selector` alone.

A token is a name, then an optional selector glued in brackets:
  `DOC`                 the whole document
  `DOC[start..end]`     from the first line that starts with `start` to the first line
                        after it that starts with `end`, that one excluded; either side
                        may stay empty -- `DOC[..end]`, `DOC[start..]`
  `DOC[x-y,...]`        line ranges: 1-based, ascending, disjoint
A tag is free text, blanks included; it carries neither `..` nor `]`."""
from __future__ import annotations

import re

from .errors import Refusal

TOKEN = re.compile(r"^([^\s\[\]]+)(?:\[([^\]]*)\])?$")
SEPARATOR = ".."


class Cut(tuple):
    """The selector of a token: a tuple of line ranges -- equal to the plain tuple it
    holds -- that carries its `span`, the couple of tags (an empty string for an open
    side), or None. It is true as soon as it selects something."""

    span: tuple[str, str] | None

    def __new__(cls, ranges=(), span: tuple[str, str] | None = None):
        cut = super().__new__(cls, ranges)
        cut.span = span
        return cut

    def __bool__(self) -> bool:
        return len(self) > 0 or self.span is not None


def split_row(line: str) -> tuple[str, ...]:
    """-> the tokens of one row: blanks separate them, except inside brackets -- a tag
    carries blanks. A bracket left open refuses."""
    tokens: list[str] = []
    current = ""
    inside = False
    for char in line:
        if char.isspace() and not inside:
            if current:
                tokens.append(current)
            current = ""
            continue
        if char == "[":
            inside = True
        elif char == "]":
            inside = False
        current += char
    if inside:
        raise Refusal("serve-range-malformed",
                      f"`{line.strip()}` -- a bracket is left open")
    if current:
        tokens.append(current)
    return tuple(tokens)


def parse(token: str, shape: str = "serve-range-malformed") -> tuple[str, Cut]:
    """-> (name, cut) of a token. What is badly written INSIDE the brackets refuses
    `serve-range-malformed`; a token that is not a name and its brackets refuses `shape`."""
    match = TOKEN.fullmatch(token)
    if not match:
        code = "serve-range-malformed" if "[" in token else shape
        raise Refusal(code, f"`{token}` -- a token is one name, then `[start..end]` "
                            "or `[x-y,...]` glued to it")
    name, inner = match.group(1), match.group(2)
    return name, selector(inner or "", token)


def selector(text: str, token: str = "") -> Cut:
    """-> the cut a SELECTOR says -- what a token carries between its brackets, read
    alone: two tags around `..`, line ranges, or nothing (the whole document). `token`
    names the whole in a refusal; a bare selector names itself."""
    whole = token or text
    if not text:
        return Cut()
    if SEPARATOR in text:
        tags = [tag.strip() for tag in text.split(SEPARATOR)]
        if len(tags) != 2 or not any(tags):
            raise Refusal("serve-range-malformed",
                          f"`{whole}` -- two tags at most, one at least: `[start..end]`, "
                          "`[..end]` or `[start..]`")
        return Cut(span=(tags[0], tags[1]))
    found: list[tuple[int, int]] = []
    last = 0
    for piece in text.split(","):
        pair = piece.split("-")
        if len(pair) != 2 or not pair[0].isdigit() or not pair[1].isdigit():
            raise Refusal("serve-range-malformed",
                          f"`{piece}` in `{whole}` -- a selector is `start..end` or `x-y`")
        low, high = int(pair[0]), int(pair[1])
        if low < 1 or high < low or low <= last:
            raise Refusal("serve-range-malformed",
                          f"`{piece}` in `{whole}` -- ranges are 1-based, "
                          "ascending, disjoint, ordered")
        found.append((low, high))
        last = high
    return Cut(tuple(found))
