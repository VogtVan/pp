"""Scenario `ui-tasks-band-filters` -- the filters beside the list of the tasks expanded (batch
la-liste-sous-les-filtres-et-le-survol, s.1459, cut out of `ui-tasks-band-list`), on the bench's `pp-team` witness:
expanded at 130x60, the list leaves the filters `SHOW` and `TEAM` shown beside it, neither over it, and a `SHOW`
changed from the keys reads its rows again, the list still expanded (`_tasks_band.filters_kept`).
"""
from __future__ import annotations

from tests.harness import support

B = support(__file__, "tasks_band")


def scenario(bench) -> int:
    return B.filters_kept(bench)
