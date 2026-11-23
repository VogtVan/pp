"""The head of a text, as a neighbour's line and a face read it."""
from __future__ import annotations


def first_line(text: str) -> str:
    """-> the first line of a text that says something, cut at 60 characters: the head a
    neighbour reads -- for a caller's wake-up, the head its message opens on."""
    return next((" ".join(one.split()) for one in text.splitlines() if one.strip()), "")[:60]
