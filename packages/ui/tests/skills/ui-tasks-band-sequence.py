"""Scenario `ui-tasks-band-sequence` -- the frame of the sequence in the band of the Tasks tab, on the bench's `pp-team`
witness:
- it expands over the whole centre, the menu of the filters kept beside it (batch les-cadres-depliables, cut out of
  `ui-tasks-band` by la-liste-qui-garde-sa-place): a click on the glyph in its title expands it, the other frames hidden,
  the glyph turned to the one that folds; the same click folds it back, the regions as they were (`_tasks_band.expands`)
"""
from __future__ import annotations

from tests.harness import support

B = support(__file__, "tasks_band")


def scenario(bench) -> int:
    return B.expands(bench, "sequence", "centre")
