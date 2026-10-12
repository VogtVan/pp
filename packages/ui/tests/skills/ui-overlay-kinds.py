"""Scenario `ui-overlay-kinds` -- an event's overlay names its kind (plan ui, batch les-overlays-qui-tiennent; split
out of `ui-overlays`, rule 10), on the bench's `pp-chat` witness:
- each kind of line opened names its kind in the title: `conduction`, `tool call · Bash` (the call of pp, said `pp` on
  its line), `thinking`, `tool call · Read`, `words`, `steps`, `agent answer`
- an answer whose rows open on an emoji and its selector `U+FE0F` (🛠️) opens straight (batch les-retours-du-reel-0-18):
  no `U+FE0F` in the overlay, its right border on one column of the terminal (a selector counted as nothing, the
  terminal's way)
An answer opened as markdown is `ui-overlay-markdown`'s.
"""
from __future__ import annotations

import unicodedata

from tests.harness import support

P = support(__file__, "dialogue")
TURN = "h,i,enter,wait:waiting"


def columns_of(text: str) -> int:
    """-> the columns a terminal draws `text` on: a wide character on two, a selector or a combining mark on none."""
    return sum(0 if char == "\ufe0f" or unicodedata.combining(char) else
               2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures

    def title_of(text: str) -> list[str]:
        """-> the title of the overlay: its first rows of text inside the border, up to the first blank row."""
        rows = text.split("\n")
        top = next((n for n, row in enumerate(rows) if "┏" in row and "┓" in row), -1)
        if top < 0:
            return []
        left, right = rows[top].index("┏"), rows[top].index("┓")
        found: list[str] = []
        for row in rows[top + 1:]:
            inner = row[left + 1:right].strip() if len(row) > right else ""
            if not inner and not found:
                continue                              # the box's padding above the title
            if not inner or inner.startswith("━"):
                break
            found.append(inner)
        return found

    # --- each kind names itself in the title -------------------------------------------------------------
    tools = P.Post(bench, "ui-overlays-kinds", P.tools_script())
    wanted = {9: "conduction", 8: "tool call · Bash", 7: "thinking", 6: "tool call · Read", 5: "words", 4: "steps",
              3: "agent answer"}
    said = {}
    for up, label in wanted.items():
        shown = tools.render("ag1", "--render", "dialogue", "--size", "140x44", "--press",
                             f"{TURN},{','.join(['shift+tab'] * up)},enter")
        found = title_of(shown.stdout)
        said[label] = found[0] if found else ""
    if all(said[label].startswith(label) for label in wanted.values()):
        held("each kind names itself", "titles: " + "; ".join(f"{label}" for label in wanted.values()))
    else:
        failures.append(f"  ✗ kinds                       {said}")

    # --- an answer with emoji opens straight -------------------------------------------------------------
    emoji = P.Post(bench, "ui-overlays-emoji", P.emoji_answer_script())
    shown = emoji.render("ag1", "--render", "dialogue", "--size", "120x40", "--press",
                         f"{TURN},{','.join(['shift+tab'] * 3)},enter")
    rows = shown.stdout.split("\n")
    top = next((n for n, row in enumerate(rows) if "┏" in row), -1)
    bottom = next((n for n, row in enumerate(rows) if "┗" in row and n > top), -1)
    boxed = rows[top + 1:bottom] if 0 <= top < bottom else []
    columns = {columns_of(row[:row.rindex("┃")]) for row in boxed if "┃" in row}
    selectors = sum(row.count("\ufe0f") for row in boxed)
    if (shown.returncode == 0 and any("build" in row for row in boxed) and selectors == 0 and len(columns) == 1):
        held("an answer with emoji opens straight", f"no U+FE0F in the overlay's {len(boxed)} rows; its right border "
             f"on column {columns.pop()}")
    else:
        failures.append(f"  ✗ emoji                       rc={shown.returncode} U+FE0F={selectors} columns={sorted(columns)} "
                        f"{boxed[:12]!r} {shown.stderr[-300:]!r}")
    return 0
