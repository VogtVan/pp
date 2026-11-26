"""looks -- the PLATE of the drawing: every code of the judgments, every ground, a table and a tile, drawn in the look
of the theme the post is in, as the pane `ui --render looks` prints it -- no tab, no key: a screen the render shows
alone, where the next theme is tried and the eye judges the vocabulary of `palette.py`. It draws only what the
vocabulary gives (`drawing_look`, `coded`, `table_text`, `tile_text`, `share_bar`) on figures of its own, which say
nothing of a team: each code comes from a ratio judged by the table of the judgments (`model/looks.py`), on the first
measure whose going up is the wrong side, and each code a share gives from shares on each side of the thresholds of
the first share of that table, its mark said without colour (`!`, `!!`). Drawn again when the width or the theme
changes."""
from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.events import Resize
from textual.screen import Screen
from textual.widgets import Static

import palette
from model import looks as judgments

LOOKS_KEY = "looks"                                  # the word of `--render`, and the title of the plate
LABEL = 12                                           # the width of a label of the plate
GROUND_WIDTH = 28                                    # the width a ground is shown on
BAR_CELLS = 20
STEP = 0.1                                           # how far off a threshold the plate's first and last ratios stand
# a ratio for each code a ratio gives -- good, nominal, watch, alert --, read from the thresholds: one moved, the plate
# moves with it
RATIOS = (judgments.RATIO_GOOD - STEP, (judgments.RATIO_GOOD + judgments.RATIO_WATCH) / 2,
          (judgments.RATIO_WATCH + judgments.RATIO_ALERT) / 2, judgments.RATIO_ALERT + STEP)
MEDIANS = (2.90, 29.00, 290.00, 2.90)                # the medians of the rows: a figure is its median x its ratio
FIGURES = tuple((round(median * ratio, 2), median) for median, ratio in zip(MEDIANS, RATIOS))
CLOSING = (("all", "415.57"), ("median", "4.64"))   # the table's closing rows, as a face would give them
SHARE = 0.53                                         # the share of the plate's bar

_LOOKS: dict[str, dict[str, str]] = {}               # the look of the drawing, by the theme it is drawn in


class LooksScreen(Screen):
    """The plate, the whole screen: its title says the theme it is drawn in."""

    DEFAULT_CSS = """
    LooksScreen #looks-plate { padding: 0 1; }
    """

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            yield Static(id="looks-plate")

    def on_mount(self) -> None:
        self.watch(self.app, "theme", self._themed, init=False)
        self._draw()

    def on_resize(self, event: Resize) -> None:
        self._draw()

    def _themed(self, theme: str) -> None:
        self._draw()

    def _draw(self) -> None:
        theme = self.app.theme
        if theme not in _LOOKS:
            _LOOKS[theme] = palette.drawing_look(self.app.get_css_variables())
        width = max(self.size.width - 2, 40)
        self.query_one("#looks-plate", Static).update(plate(_LOOKS[theme], theme, width))


def shares_of(measure: str) -> tuple[float, float, float]:
    """-> three shares of a measure of the table, one for each code a share gives -- under its first threshold,
    between its two, at its second --, read from its thresholds, never typed."""
    bounds = judgments.SHARES[measure]
    return bounds["watch"] / 2, (bounds["watch"] + bounds["alert"]) / 2, bounds["alert"]


def plate(look: dict[str, str], theme: str, width: int) -> Text:
    """-> the plate in a look: its title, the codes, the grounds, a table, a tile."""
    measure = next(name for name, sense in judgments.SENSE.items() if sense == judgments.UP_BAD)
    codes = [judgments.judged(measure, ratio, judgments.SEASONS_MIN) for ratio in RATIOS]
    drawn = Text()
    drawn.append(f"{LOOKS_KEY} · {theme}", style=palette.BOLD)
    drawn.append("\n\ncodes\n", style=palette.BOLD)
    for code, ratio in zip(codes, RATIOS):
        drawn.append_text(Text(f"  {code:<{LABEL}}{judgments.ratio_said(ratio)}", style=look[code]))
        drawn.append("\n")
    for share in shares_of(next(iter(judgments.SHARES))):
        code = judgments.shared(next(iter(judgments.SHARES)), share)
        mark = judgments.mark_of(code)
        drawn.append_text(Text(f"  {code:<{LABEL}}share {round(100 * share)}%" + (f" {mark}" if mark else ""),
                               style=look[code]))
        drawn.append("\n")
    drawn.append_text(Text(f"  {judgments.MUTED:<{LABEL}}median {FIGURES[0][1]:.2f}", style=look[judgments.MUTED]))
    drawn.append("\n\ngrounds\n", style=palette.BOLD)
    for ground in palette.GROUNDS:
        drawn.append("  ")
        drawn.append_text(Text(f" {ground}".ljust(GROUND_WIDTH), style=look[ground]))
        drawn.append("\n")
    drawn.append(f"  {'bar':<{LABEL}}")
    drawn.append_text(palette.share_bar(SHARE, BAR_CELLS, look))
    drawn.append(f" {round(100 * SHARE)}%\n\ntable\n", style=palette.BOLD)
    rows = [[f"row {at}", f"{figure:.2f}", f"{median:.2f}", palette.coded(judgments.ratio_said(ratio), code, look)]
            for at, ((figure, median), ratio, code) in enumerate(zip(FIGURES, RATIOS, codes), 1)]
    drawn.append_text(palette.table_text([("row", False), ("figure", True), ("median", True), ("ratio", True)], rows,
                                         look, width, closing=[[name, figure, "", ""] for name, figure in CLOSING]))
    drawn.append("\n\ntile\n", style=palette.BOLD)
    drawn.append_text(palette.tile_text("tile", "42.00 / 50", [
        palette.compared("32.31", RATIOS[2], codes[2], look),
        Text("median 24.85", style=look[judgments.MUTED])], look, 34))
    return drawn
