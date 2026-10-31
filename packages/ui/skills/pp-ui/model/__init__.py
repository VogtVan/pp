"""model -- the typed state of the post: PURE dataclasses, shared by every layer above.
Data only: no I/O, no subprocess, no clock, no Textual, no import from any other module
of the post."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class House:
    """The house the post serves: its name (the directory's) and its root."""
    name: str
    root: str

    @staticmethod
    def at(root: Path) -> "House":
        return House(root.name or str(root), str(root))


@dataclass(frozen=True)
class Size:
    """A screen size in cells; `parse` reads `WxH` and refuses what no frame fits in: the
    header (1), the tabs (2), one line of body and the footer (3), with one to spare."""
    width: int
    height: int
    MIN_WIDTH = 40
    MIN_HEIGHT = 8

    @staticmethod
    def parse(text: str) -> "Size | None":
        found = re.fullmatch(r"(\d{1,4})x(\d{1,4})", text.strip())
        if not found:
            return None
        width, height = int(found.group(1)), int(found.group(2))
        if width < Size.MIN_WIDTH or height < Size.MIN_HEIGHT:
            return None
        return Size(width, height)


@dataclass(frozen=True)
class PaneSpec:
    """One pane of the post: its key (the tab's id and the `--render` word), its title, the
    digit that opens it."""
    key: str
    title: str
    digit: str


PANES: tuple[PaneSpec, ...] = (
    PaneSpec("dialogue", "Dialogue", "1"),
    PaneSpec("agents", "Agents", "2"),
    PaneSpec("teams", "Teams", "3"),
    PaneSpec("tasks", "Tasks", "4"),
)
FRAME = "frame"                                  # `--render frame`: the whole screen, first tab
PANE_KEYS: tuple[str, ...] = (FRAME, *(one.key for one in PANES))


def pane(key: str) -> PaneSpec:
    return next(one for one in PANES if one.key == key)
