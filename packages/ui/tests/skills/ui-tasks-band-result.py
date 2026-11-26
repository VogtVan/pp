"""Scenario `ui-tasks-band-result` -- the frame of the result expands over the whole place under the list as the text's
does (batch le-result-et-le-fil, s.1517; its own scenario beside `ui-tasks-band-text`, rule 10), on the bench's
`pp-team` witness, ops' T2 resolved: a click on the glyph in its title expands it, the other frames hidden, the glyph
turned to the one that folds; the same click folds it back, the regions as they were (`_tasks_band.expands`).
"""
from __future__ import annotations

from tests.harness import support

B = support(__file__, "tasks_band")


def scenario(bench) -> int:
    return B.expands(bench, "result", "below")
