"""Scenario `ui-team-stats-title` -- the title of the dashboard holds at any width (cut out of `ui-team-stats-widths`
past 22 s, stats-d-equipe/le-detail-des-lancements), on the bench's `pp-team` witness of 14 seasons, read by the
structure of the render, never a text of the post:
- at 100 columns, the tabs of the oldest seasons leave whole, the title keeps `[all]` and `⊟` and ends on no cut; a
  click on `[all]` draws it, its two zones
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "team_stats")


def scenario(bench) -> int:
    house = S.T.Teams(bench, "ui-team-stats-title", S.T.script(stats=S.T.many_seasons()))
    house.env["TZ"] = "UTC"

    def render(*keys: str, size=S.WIDE, regions: bool = False):
        return house.render("--render", "teams", *size, *(["--press", ",".join(keys)] if keys else []),
                            *(["--regions"] if regions else ["--styles"]))
    titled(bench, render)
    return 0


def titled(bench, render) -> None:
    """The title of a narrow dashboard of many seasons: `[all]` and `⊟` kept, nothing cut; `[all]` clicked, drawn."""
    held, failures = bench.held, bench.failures
    narrow = render("z", size=S.NARROW)
    board = S.framed(narrow.stdout, "⊟")
    title = S.title(narrow.stdout, board)
    every = S.offset(narrow.stdout, board, "[all]")
    whole = render("z", f"click:#teams-board:{(every or 0) + 1}:0", size=S.NARROW)
    if (narrow.returncode == 0 and board and every is not None and "⊟" in title and S.CUT not in title
            and S.in_reverse(whole.stdout, board, "[all]") and len(S.zones_in(whole.stdout, board)) == 2):
        held("the title of a narrow dashboard", f"14 seasons at 100 columns: {title.strip()!r}; [all] clicked, "
             "drawn in its two zones")
    else:
        failures.append(f"  ✗ the title at 100 columns    {title!r} all={every} {S.rows(whole.stdout)[3:6]}")
