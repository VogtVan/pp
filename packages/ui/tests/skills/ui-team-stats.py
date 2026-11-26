"""Scenario `ui-team-stats` -- the frame of a team carries its season and is cut in two, the summary of the season's
stats beside the head, and the glyph in the summary's title opens the dashboard of the seasons (batch
le-cadre-de-la-saison, s.1891; the three screens of stats-d-equipe/les-trois-ecrans), on the bench's `pp-team`
witness answering `team stats --json [--all]` in the face of the socle -- figures that do not follow from one another
--, read by the structure of the render -- its frames, the looks of its rows and of the words of its titles, never a
text of the post:
- the frame cut in two: the head's frame, its title holding the number of the season the stats say under way, and the
  summary's frame beside it on the same row, five rows of stats, none cut at 130 and at 180 columns; the row of the
  price carries the ratio of the witness said without colour (`model/looks.py`, `ratio_said`) and, the ratio past
  the alert, the bold of the code `alert` the rows of the volumes do not have
- the glyph `⊞` of the summary under the mouse takes the look `palette.HOVER`, by the hover the Tasks tab shares
  (batch le-tableau-de-bord-range, s.1919)
- the glyph `⊞` of the summary opens the dashboard at 180 columns: the one frame beside the menu of the teams, its
  title closing on `⊟`, the tab of the season under way in reverse; inside it its nine ZONES framed, named by their
  widgets (`board-spent` … `board-launches`, `--regions`), apart, the four tiles on one row; no cell cut; the rows of
  Tasks and of Members in the order of the witness's costs, the dearest first, the root's row marked
  (`palette.ROOT_MARK`); the share of the stopped tasks past its alert carries its mark (`mark_of`); the context's
  p90 past its threshold, under its median, carries the mark of its code in the summary and in Context, and no
  ratio beside it (E14); the launches of the season (stats-d-equipe/le-detail-des-lancements): the zone Launches,
  its two tables -- one row per model of `by_model`, one per band of `by_duration` --, the table of Context, one row per
  band of `context.by_band`, the two sparklines of Rhythm -- the cost, then the effort, by slot -- on one axis, and in
  Members the model and the cost per hour of effort of each member, judged by the table of the judgments: its ratio
  said, in the bold of `alert` past it; in Context the cause of a failure after its count judged `alert` keeps its own
  look, neither that bold nor that ground; the cost per
  delegation of the witness is drawn as it is, the quotient of its cost by its delegations nowhere
- `[s.1]` draws season 1: its tab in reverse, its nine zones, other rows than the season under way's, the glyph `⊟`
  under the mouse in the look `palette.HOVER` -- found by the cells of its label measured as it is written --; the
  mouse gone to `[all]` gives `⊟` its look back, and `[all]` draws its two zones framed: the table of the seasons, one
  row per season played and its two closing rows (`all`, `median`) on the ground of its header, the empty seasons
  named under them; the dearest tasks, five rows
(the widths of the dashboard and its key: `ui-team-stats-widths`, cut out of this scenario past 22 s; the base kept, the dashboard of another team, the
race of two teams, the local hours and the themes: `ui-team-stats-teams`; the base chosen in the settings:
`ui-tasks-stats`)
"""
from __future__ import annotations

import re

from tests.harness import support

S = support(__file__, "team_stats")
J = S.judgments()
ROOT_MARK = S.D.palette_constant("ROOT_MARK")
TASK = re.compile(r"^(T\d+)\b")


def first_words(rows: list[str]) -> list[str]:
    """-> the first word of each row that starts with a name of the witness: a task or a member."""
    return [row.split()[0] for row in rows if row.split()]


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    house = S.T.Teams(bench, "ui-team-stats", S.T.script(stats=S.T.STATS))
    house.env["TZ"] = "UTC"
    seasons = S.T.STATS["core-review"]["seasons"]
    now, first = seasons[-1], seasons[0]
    full = [one for one in seasons if not one["empty"]]

    def render(*keys: str, size=S.WIDE, regions: bool = False):
        return house.render("--render", "teams", *size, *(["--press", ",".join(keys)] if keys else []),
                            *(["--regions"] if regions else ["--styles"]))

    # --- the frame cut in two, the season in its title, five rows of stats, none cut ------------------------------
    plain, wide = render(size=S.MID), render()
    stats = S.framed(plain.stdout, "⊞")
    head = S.beside(plain.stdout, stats)
    summary = [one for one in S.inside(plain.stdout, stats) if one]
    summaries = [[one for one in S.inside(done.stdout, S.framed(done.stdout, "⊞")) if one] for done in (plain, wide)]
    ratio = J.ratio_said(now["against"]["per_delegation"]["usd"]["ratio"])
    code = J.judged("per_delegation.usd", now["against"]["per_delegation"]["usd"]["ratio"],
                    now["against"]["per_delegation"]["usd"]["over"])
    priced = next((at for at, one in enumerate(S.inside(plain.stdout, stats)) if ratio in one), None)
    lit = None
    if priced is not None and stats:
        row = S.rows(plain.stdout)[stats[2] + 1 + priced]
        lit = S.looks(plain.stdout)[stats[2] + 1 + priced][row.find(ratio, stats[1])]
    volume = S.first(plain.stdout, stats, 1) if stats else None
    if (plain.returncode == 0 and head and stats and re.search(rf"\b{now['season']}\b", S.title(plain.stdout, head))
            and len(summary) == 5 and all(len(one) == 5 and not S.cut(one) for one in summaries)
            and code == J.ALERT and lit is not None and "1" in lit[0] and volume is not None and "1" not in volume[0]):
        held("the frame cut in two, the season in its title", f"head x={head[1]} w={head[3]}, its title holding "
             f"{now['season']}; the summary x={stats[1]} w={stats[3]} on its row, 5 rows at 130 and 180, none cut; "
             f"the price says {ratio}, bold ({code}) {sorted(lit[0])}, the work row {sorted(volume[0])}")
    else:
        failures.append(f"  ✗ cut in two                 rc={plain.returncode} {head} {stats} {summaries} "
                        f"ratio={ratio!r} at={priced} look={lit} {S.rows(plain.stdout)[:10]} {plain.stderr[-300:]!r}")
        return 0
    expand = S.offset(plain.stdout, stats, "⊞")
    wide_stats = S.framed(wide.stdout, "⊞")
    expand_wide = S.offset(wide.stdout, wide_stats, "⊞")
    if expand is None or expand_wide is None:
        failures.append(f"  ✗ the glyph of the title      ⊞={expand}/{expand_wide} {S.rows(plain.stdout)[:8]}")
        return 0
    opening = f"click:#teams-stats:{expand_wide}:0"

    # --- the glyph of the summary under the mouse (a click moves no mouse: it stays there) ----------------------
    rest = S.look(plain.stdout, stats, "⊞")
    chosen = render(f"hover:#teams-stats:{expand}:0", size=S.MID)
    shone = S.look(chosen.stdout, stats, "⊞")
    if S.HOVERED and shone is not None and S.HOVERED <= shone and not S.HOVERED <= rest:
        held("⊞ shines under the mouse", f"{sorted(rest)} -> under the mouse {sorted(shone)}")
    else:
        failures.append(f"  ✗ ⊞ under the mouse           HOVER {sorted(S.HOVERED)}; {rest} -> {shone}")

    # --- the dashboard opened by the summary's glyph, beside the menu, in nine zones ------------------------------
    drawn = render(opening)
    laid = S.laid(render(opening, regions=True).stdout)
    board, menu = S.framed(drawn.stdout, "⊟"), S.framed(drawn.stdout, "Teams")
    frames, zones = S.frames(drawn.stdout), S.zones_in(drawn.stdout, board)
    if (drawn.returncode == 0 and board and menu
            and all(one in (board, menu) or S.within(one, board) for one in frames)
            and board[1] >= menu[1] + menu[3] and S.in_reverse(drawn.stdout, board, f"[s.{now['season']}]")
            and len(zones) == len(S.SEASON_ZONES)
            and set(laid) == S.SEASON_ZONES and all(S.within(one, board) for one in laid.values())
            and S.apart(list(laid.values())) and len({laid[one][2] for one in S.TILES}) == 1
            and not S.cut(S.inside(drawn.stdout, board))):
        held("⊞ opens the dashboard beside the menu, in zones", f"the dashboard x={board[1]} w={board[3]} the one "
             f"frame beside the menu, [s.{now['season']}] in reverse; {len(zones)} zones framed inside it, apart: "
             f"{sorted(laid)}, the tiles on the row y={laid[S.TILES[0]][2]}; no cell cut")
    else:
        failures.append(f"  ✗ the dashboard               rc={drawn.returncode} {frames} {zones} "
                        f"{laid} {S.rows(drawn.stdout)[3:40]} {drawn.stderr[-300:]!r}")
        return 0

    # --- the tables in the order of the costs, the root marked; the figures of the face as they are ---------------
    def dearest(lines: list[dict]) -> list[str]:
        return [one.get("task") or one.get("member") for one in sorted(lines, key=lambda one: -one["cost"]["usd"])]
    tasks = [one for one in first_words(S.zone_rows(drawn.stdout, laid["board-tasks"]))
             if one in {line["task"] for line in now["by_task"]}]
    members = [row for row in S.zone_rows(drawn.stdout, laid["board-members"])
               if row.split() and row.split()[0] in {line["member"] for line in now["by_member"]}]
    root = now["root"]["member"]
    risk = S.zone_rows(drawn.stdout, laid["board-risk"])
    mark = J.mark_of(J.shared("stopped_tasks.share", now["stopped_tasks"]["share"]["usd"]))
    inner = "\n".join(S.inside(drawn.stdout, board))
    figure = f"{now['per_delegation']['usd']:.2f}"
    quotient = f"{now['cost']['usd'] / now['delegations']:.2f}"
    p90 = J.mark_of(J.shared("context.p90", now["context"]["p90"]))
    beside = J.ratio_said(now["against"]["context"]["p90"]["ratio"])
    spoken = ["\n".join(summaries[1]), "\n".join(S.zone_rows(drawn.stdout, laid["board-context"]))]
    if (tasks == dearest(now["by_task"]) and [one.split()[0] for one in members] == dearest(now["by_member"])
            and [ROOT_MARK in one for one in members] == [one.split()[0] == root for one in members]
            and mark and any(mark in one for one in risk) and figure in inner and quotient not in inner
            and p90 and all(p90 in one and beside not in one for one in spoken)):
        held("the tables by cost, the root marked, the face's figures", f"Tasks {tasks}, Members "
             f"{[one.split()[0] for one in members]}, {root} marked {ROOT_MARK}; At risk marked {mark!r}; "
             f"{figure} drawn, the quotient {quotient} nowhere; the p90 marked {p90!r} in the summary and Context, "
             f"{beside} nowhere")
    else:
        failures.append(f"  ✗ the tables                  tasks={tasks} members={members} risk={risk} mark={mark!r} "
                        f"{figure} in={figure in inner} {quotient} in={quotient in inner} p90={p90!r} {spoken}")

    # --- the launches: the zone Launches, the table of Context, the two lines of Rhythm, the columns of Members ---
    launches = S.headed(drawn.stdout, laid["board-launches"])
    bands = S.headed(drawn.stdout, laid["board-context"])
    rhythm = [S.sparked(one) for one in S.zone_rows(drawn.stdout, laid["board-rhythm"]) if S.sparked(one) is not None]
    reviewer = next((one for one in now["by_member"] if one["member"] == "reviewer"), {})
    hour = reviewer["against"]["per_effort_hour"]["usd"]
    said = J.ratio_said(hour["ratio"])
    judged = J.judged("per_effort_hour.usd", hour["ratio"], hour["over"])
    zone = laid["board-members"]
    at = next((zone[2] + 1 + n for n, one in enumerate(S.inside(drawn.stdout, zone)) if one.startswith("reviewer")), None)
    row = S.rows(drawn.stdout)[at] if at is not None else ""
    cell = S.looks(drawn.stdout)[at][row.find(said, zone[1])] if at is not None and said in row else None
    if ([len(one) for one in launches] == [len(now["by_model"]), len(now["by_duration"])]
            and [len(one) for one in bands] == [len(now["context"]["by_band"])]
            and len(rhythm) == 2 and len(set(rhythm)) == 1
            and all(model in row for model in reviewer["models"]) and judged == J.ALERT and cell is not None
            and "1" in cell[0]):
        held("the launches of the season", f"Launches {[len(one) for one in launches]} rows, Context "
             f"{[len(one) for one in bands]}, Rhythm two sparklines from column {rhythm[0]}; reviewer's models "
             f"{reviewer['models']} and its hour {said}, bold ({judged})")
    else:
        failures.append(f"  ✗ the launches                launches={launches} bands={bands} rhythm={rhythm} row={row!r} "
                        f"cell={cell}")

    # --- a cause of failure in Context keeps its own look: never the alert its count is judged ---------------------
    losses, versus = now["losses"], now["against"]["losses"]["failed"]
    code = J.judged("losses.failed", versus["ratio"], versus["over"])
    cause = next(iter(losses["reasons"]))
    zone = laid["board-context"]
    at = next((zone[2] + 1 + n for n, one in enumerate(S.inside(drawn.stdout, zone)) if cause in one), None)
    row = S.rows(drawn.stdout)[at] if at is not None else ""
    start = len(row) - len(row[zone[1] + 1:].lstrip()) if at is not None else 0
    count = (S.looks(drawn.stdout)[at][start], S.grounds(drawn.stdout)[at][start]) if at is not None else None
    reason = ((S.looks(drawn.stdout)[at][row.find(cause, start)], S.grounds(drawn.stdout)[at][row.find(cause, start)])
              if at is not None else None)
    if (code == J.ALERT and count and reason and "1" in count[0][0] and "1" not in reason[0][0]
            and reason[1] != count[1]):
        held("a cause of failure keeps its own look", f"{losses['failed']} failed judged {code}, bold on "
             f"{count[1]}; its cause {cause!r} {sorted(reason[0][0])} on {reason[1]}")
    else:
        failures.append(f"  ✗ the cause of a failure      code={code} row={row!r} count={count} cause={reason}")

    # --- the seasons chosen: one season, then every season -----------------------------------------------------
    tab = S.offset(drawn.stdout, board, f"[s.{first['season']}]")
    every = S.offset(drawn.stdout, board, "[all]")
    closing = S.offset(drawn.stdout, board, "⊟")
    one = render(opening, f"click:#teams-board:{(tab or 0) + 1}:0", f"hover:#teams-board:{closing}:0")
    whole = render(opening, f"hover:#teams-board:{closing}:0", f"hover:#teams-board:{(every or 0) + 1}:0",
                   f"click:#teams-board:{(every or 0) + 1}:0")      # the mouse gone from ⊟ to [all]
    tables = S.zones_in(whole.stdout, board)
    seasons_zone, dearest_zone = (tables + [None, None])[:2]
    rows = S.inside(whole.stdout, seasons_zone)
    written = [at for at, row in enumerate(rows) if row]
    ground = S.grounds(whole.stdout)
    on = [ground[seasons_zone[2] + 1 + at][seasons_zone[1] + 2] for at in written] if seasons_zone else []
    header = on[0] if on else None
    closings = [at for at, said in zip(written, on) if said == header and at != written[0]]
    under = [at for at in written if closings and at > closings[-1]]
    played = [at for at in written[1:] if at not in closings and at not in under]
    picked = [one for one in first_words(S.inside(whole.stdout, dearest_zone)) if TASK.match(one)]
    lit, out = S.look(one.stdout, board, "⊟"), S.look(whole.stdout, board, "⊟")
    if (tab is not None and every is not None and S.in_reverse(one.stdout, board, f"[s.{first['season']}]")
            and len(S.zones_in(one.stdout, board)) == len(S.SEASON_ZONES)
            and S.inside(one.stdout, board) != S.inside(drawn.stdout, board) and lit is not None and S.HOVERED <= lit
            and out == S.look(drawn.stdout, board, "⊟")
            and S.in_reverse(whole.stdout, board, "[all]") and len(tables) == 2 and header is not None
            and len(closings) == 2 and len(played) == len(full) and len(under) == 1 and len(picked) == 5
            and not S.cut(S.inside(whole.stdout, board))):
        held("the tabs of the seasons", f"[s.{first['season']}] in reverse, {len(S.SEASON_ZONES)} zones, its own rows, "
             f"⊟ under the mouse {sorted(lit)}, gone to [all] {sorted(out)}; [all] in reverse, 2 zones, "
             f"{len(played)} rows of seasons, 2 closing rows on the header's ground {header}, {len(under)} row of "
             f"empty seasons under them; {len(picked)} dearest tasks")
    else:
        failures.append(f"  ✗ the seasons                 tab={tab} all={every} ⊟={lit}/{out} zones={tables} "
                        f"on={on} closings={closings} played={played} under={under} picked={picked} {rows}")

    return 0

