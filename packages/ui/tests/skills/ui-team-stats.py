"""Scenario `ui-team-stats` -- the frame of a team carries its season and is cut in two, the summary of the season's
stats beside the head, and the glyph in the summary's title opens the dashboard of the seasons (batch
le-cadre-de-la-saison, s.1891), on the bench's `pp-team` witness answering `team stats --json [--all]`, read by the
structure of the render -- its frames, the looks of its rows and of the words of its titles, never a text of the post:
- the frame cut in two: the head's frame, its title holding the number of the season the stats say under way, and the
  summary's frame beside it on the same row, five rows of stats
- the glyph `⊞` of the summary under the mouse takes the look `palette.HOVER`, by the hover the Tasks tab shares
  (batch le-tableau-de-bord-range, s.1919)
- the glyph `⊞` of the summary opens the dashboard: the one frame beside the menu of the teams, its title closing on
  `⊟`, the tab of the season under way in reverse; inside it its seven ZONES framed (s.1919), named by their widgets
  (`board-yield` … `board-losses`, `--regions`), each apart from the others by a blank cell at least
- `[s.1]` draws season 1: its tab in reverse, its seven zones, other rows than the season under way's, the glyph `⊟`
  under the mouse in the look `palette.HOVER` -- found by the cells of its label measured as it is written: the title
  holds `\\[s.3]`, which the markup Textual gives back no longer escapes, so a glyph measured on that markup, or not
  measured, never shines --; the mouse gone to `[all]` gives `⊟` its look back, and `[all]` draws
  its two zones framed, one row per season not empty in the first and one dim row under those rows -- the empty
  seasons --, a row per measure in the second
(the base kept from one opening to the next, the dashboard of another team, and the race of two teams:
`ui-team-stats-teams`; the base chosen in the settings: `ui-tasks-stats`)
"""
from __future__ import annotations

import re

from tests.harness import support

S = support(__file__, "team_stats")


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.T.Teams(bench, "ui-team-stats", S.T.script(stats=S.T.STATS))
    seasons = S.T.STATS["core-review"]["seasons"]
    now, first = seasons[-1], seasons[0]
    full = [one for one in seasons if not one["empty"]]

    def render(*keys: str, regions: bool = False):
        return house.render("--render", "teams", *S.SIZE, *(["--press", ",".join(keys)] if keys else []),
                            *(["--regions"] if regions else ["--styles"]))

    # --- the frame cut in two, the season in its title, five rows of stats ---------------------------------------
    plain = render()
    stats = S.framed(plain.stdout, "⊞")
    head = S.beside(plain.stdout, stats)
    summary = [one for one in S.inside(plain.stdout, stats) if one]
    if (plain.returncode == 0 and head and stats and re.search(rf"\b{now['season']}\b", S.title(plain.stdout, head))
            and len(summary) == 5):
        held("the frame cut in two, the season in its title", f"head x={head[1]} w={head[3]}, its title holding "
             f"{now['season']}; the summary x={stats[1]} w={stats[3]} on its row, {len(summary)} rows")
    else:
        failures.append(f"  ✗ cut in two                 rc={plain.returncode} {head} {stats} {summary} "
                        f"{S.rows(plain.stdout)[:10]} {plain.stderr[-300:]!r}")
        return 0
    expand = S.offset(plain.stdout, stats, "⊞")
    if expand is None:
        failures.append(f"  ✗ the glyph of the title      ⊞={expand} {S.rows(plain.stdout)[:8]}")
        return 0
    opening = f"click:#teams-stats:{expand}:0"
    hovering = f"hover:#teams-stats:{expand}:0"

    # --- the glyph of the summary under the mouse (a click moves no mouse: it stays there) ----------------------
    rest = S.look(plain.stdout, stats, "⊞")
    chosen = render(hovering)
    lit = S.look(chosen.stdout, stats, "⊞")
    if S.HOVERED and lit is not None and S.HOVERED <= lit and not S.HOVERED <= rest:
        held("⊞ shines under the mouse", f"{sorted(rest)} -> under the mouse {sorted(lit)}")
    else:
        failures.append(f"  ✗ ⊞ under the mouse           HOVER {sorted(S.HOVERED)}; {rest} -> {lit}")

    # --- the dashboard opened by the summary's glyph, beside the menu, in zones ------------------------------------
    drawn = render(opening)
    laid = S.laid(render(opening, regions=True).stdout)
    board, menu = S.framed(drawn.stdout, "⊟"), S.framed(drawn.stdout, "Teams")
    frames, zones = S.frames(drawn.stdout), S.zones_in(drawn.stdout, board)
    if (drawn.returncode == 0 and board and menu
            and all(one in (board, menu) or S.within(one, board) for one in frames)
            and board[1] >= menu[1] + menu[3] and S.in_reverse(drawn.stdout, board, f"[s.{now['season']}]")
            and len(zones) == len(S.SEASON_ZONES)
            and set(laid) == S.SEASON_ZONES and all(S.within(one, board) for one in laid.values())
            and S.apart(list(laid.values()))):
        held("⊞ opens the dashboard beside the menu, in zones", f"the dashboard x={board[1]} w={board[3]} the one frame beside the menu, ⊟ in "
             f"its title, [s.{now['season']}] in reverse; {len(zones)} zones framed inside it, apart: {sorted(laid)}")
    else:
        failures.append(f"  ✗ the dashboard               rc={drawn.returncode} {frames} {zones} "
                        f"{laid} {S.rows(drawn.stdout)[3:30]} {drawn.stderr[-300:]!r}")
        return 0

    # --- the seasons chosen: one season, then every season -----------------------------------------------------
    tab = S.offset(drawn.stdout, board, f"[s.{first['season']}]")
    every = S.offset(drawn.stdout, board, "[all]")
    closing = S.offset(drawn.stdout, board, "⊟")
    one = render(opening, f"click:#teams-board:{(tab or 0) + 1}:0", f"hover:#teams-board:{closing}:0")
    whole = render(opening, f"hover:#teams-board:{closing}:0", f"hover:#teams-board:{(every or 0) + 1}:0",
                   f"click:#teams-board:{(every or 0) + 1}:0")      # the mouse gone from ⊟ to [all]
    tables = S.zones_in(whole.stdout, board)
    seasons_zone, trends_zone = (tables + [None, None])[:2]
    rows = S.inside(whole.stdout, seasons_zone)
    plain_fg = S.plain_fg(whole.stdout, trends_zone) if trends_zone else None     # its rows all plain
    written = [at for at, row in enumerate(rows) if row]
    lines = [at for at in written if S.first(whole.stdout, seasons_zone, at)[1] == plain_fg]
    under = [at for at in written if S.first(whole.stdout, seasons_zone, at)[1] != plain_fg and lines and at > lines[-1]]
    measures = [row for row in S.inside(whole.stdout, trends_zone) if row]
    lit, out = S.look(one.stdout, board, "⊟"), S.look(whole.stdout, board, "⊟")
    if (tab is not None and every is not None and S.in_reverse(one.stdout, board, f"[s.{first['season']}]")
            and len(S.zones_in(one.stdout, board)) == len(S.SEASON_ZONES)
            and S.inside(one.stdout, board) != S.inside(drawn.stdout, board) and lit is not None and S.HOVERED <= lit
            and out == S.look(drawn.stdout, board, "⊟")
            and S.in_reverse(whole.stdout, board, "[all]") and len(tables) == 2 and len(lines) == len(full)
            and len(under) == 1 and measures):
        held("the tabs of the seasons", f"[s.{first['season']}] in reverse, {len(S.SEASON_ZONES)} zones, its own rows, "
             f"⊟ under the mouse {sorted(lit)}, gone to [all] {sorted(out)}; [all] in reverse, 2 zones, "
             f"{len(lines)} rows of seasons, "
             f"{len(under)} dim row under them, {len(measures)} measures")
    else:
        failures.append(f"  ✗ the seasons                 tab={tab} all={every} ⊟={lit}/{out} zones={tables} lines={lines} "
                        f"under={under} {rows}")

    return 0
