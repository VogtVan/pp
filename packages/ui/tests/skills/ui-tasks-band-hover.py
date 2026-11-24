"""Scenario `ui-tasks-band-hover` -- the glyph of a frame that expands under the mouse (batch
la-liste-sous-les-filtres-et-le-survol, s.1460, cut out of `ui-tasks-band-list`), on the bench's `pp-team` witness:
the mouse on the cell of the list's glyph draws it with the look `palette.HOVER`, the mouse gone to another widget
gives its look back (`_tasks_band.glyph_hovered`).
"""
from __future__ import annotations

from tests.harness import support

B = support(__file__, "tasks_band")


def scenario(bench) -> int:
    return B.glyph_hovered(bench)
