"""Scenario `ui-team-stats-widths` -- the dashboard of a season from 100 to 180 columns, and its key (cut out of
`ui-team-stats` past 22 s, stats-d-equipe/les-trois-ecrans), on the bench's `pp-team` witness in the face of the
socle, read by the structure of the render -- its frames, the widgets `--regions` names, the gaps between the cells of
a table, never a text of the post:
- at 100 columns, without the summary, `z` opens the dashboard: its nine zones named by their widgets, the tiles two
  by two, no cell cut, the table of the tasks with fewer columns than at 180 -- a column whole or gone (E1) --;
  `escape` closes it, the four bands of the centre back
- at 100 columns the two columns of Members the launches give -- the model, the cost per hour of effort -- are
  left out whole: the row of a member holds neither its model nor its ratio (stats-d-equipe/le-detail-des-lancements)
- at 130 columns, opened by `z` too: its nine zones and no cell cut
(the title of a narrow dashboard of many seasons: `ui-team-stats-title`, cut out of this scenario past 22 s)
"""
from __future__ import annotations

from tests.harness import support

S = support(__file__, "team_stats")


def scenario(bench) -> int:
    house = S.T.Teams(bench, "ui-team-stats-widths", S.T.script(stats=S.T.STATS))
    house.env["TZ"] = "UTC"

    def render(*keys: str, size=S.WIDE, regions: bool = False):
        return house.render("--render", "teams", *size, *(["--press", ",".join(keys)] if keys else []),
                            *(["--regions"] if regions else ["--styles"]))
    widths(bench, render, S.laid(render("z", regions=True).stdout), render("z"))
    return 0


def widths(bench, render, wide_laid: dict, wide) -> None:
    """The dashboard at 100 and 130 columns: at 100, without the summary, `z` opens it -- its nine zones named, the
    tiles two by two, no cell cut, the table of the tasks with fewer columns than at 180 -- and `escape` closes it;
    at 130, opened by `z` too, its nine zones and no cell cut."""
    held, failures = bench.held, bench.failures
    narrow, laid = render("z", size=S.NARROW), S.laid(render("z", size=S.NARROW, regions=True).stdout)
    closed = render("z", "escape", size=S.NARROW, regions=True)
    bands = [one[0] for one in S.regions(closed.stdout).get("band", [])]
    board = S.framed(narrow.stdout, "⊟")

    def header(text: str, zone) -> str:
        return next((one for one in S.zone_rows(text, zone) if one), "")
    reviewer = next(one for one in S.T.STATS["core-review"]["seasons"][-1]["by_member"] if one["member"] == "reviewer")
    said = S.judgments().ratio_said(reviewer["against"]["per_effort_hour"]["usd"]["ratio"])
    row = next((one for one in S.zone_rows(narrow.stdout, laid.get("board-members")) if one.startswith("reviewer")), "")
    few, many = S.columns(header(narrow.stdout, laid.get("board-tasks"))), S.columns(header(wide.stdout,
                                                                                          wide_laid["board-tasks"]))
    if (narrow.returncode == 0 and board and S.framed(narrow.stdout, "⊞") is None and set(laid) == S.SEASON_ZONES
            and len({laid[one][2] for one in S.TILES}) == 2 and not S.cut(S.inside(narrow.stdout, board))
            and 0 < few < many and "teams-board" not in bands and "teams-top" in bands
            and row and said not in row and not any(model in row for model in reviewer["models"])):
        held("the dashboard at 100 columns, by its key", f"z without the summary: {len(laid)} zones, the tiles on "
             f"{len({laid[one][2] for one in S.TILES})} rows, no cell cut, Tasks {few} columns against {many} at 180, "
             f"Members without the model and the hour; escape: the bands {bands} back")
    else:
        failures.append(f"  ✗ at 100 columns              rc={narrow.returncode} {laid} columns={few}/{many} {bands} {row!r} "
                        f"{S.rows(narrow.stdout)[3:40]} {narrow.stderr[-300:]!r}")
    middle, laid = render("z", size=S.MID), S.laid(render("z", size=S.MID, regions=True).stdout)
    board = S.framed(middle.stdout, "⊟")
    if middle.returncode == 0 and board and set(laid) == S.SEASON_ZONES and not S.cut(S.inside(middle.stdout, board)):
        held("the dashboard at 130 columns", f"{len(laid)} zones, no cell cut")
    else:
        failures.append(f"  ✗ at 130 columns              rc={middle.returncode} {laid} {S.rows(middle.stdout)[3:40]}")
