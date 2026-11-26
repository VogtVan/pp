"""season -- the STATS of a team's seasons on the Teams tab, as `team stats --json` says them: the post draws them,
it computes no number -- sums, rates, medians and ratios are the face's; the post keeps the geometry of a drawing
alone, the length of a bar, the order of a table, the parts a width holds.

The three screens answer the same four questions in the same order: how much and how far (spent against the cap,
the pace, what is left), at what price (the cost per delegation, the cost of an hour of effort), with what load of
conduction (the launches per delegation, the root's share), what is at risk (the stopped tasks, the failures, the
context). A measure compared to the median of the seasons carries its ratio said without colour (`▲ ×1.50`) and the
look of the code the table of the judgments gives it (`model/looks.py`), a share judged on its thresholds its mark
(`!`, `!!`); the looks and the grounds are those of the vocabulary of the drawing (`palette.drawing_look`), read from
the theme.

The SUMMARY, the right half of the team's frame (`summary_text`): five lines, `spent`, `work`, `price`, `load`,
`watch`, each keeping its parts in order while the width holds them. The DASHBOARD (`SeasonBoard`), opened by the
glyph `palette.EXPAND` in the summary's title or by `z`, closed by `palette.COLLAPSE` in its own or by `escape`, takes
the whole centre of the tab beside the menu of the teams, which stays shown and played: another team chosen there shows
its dashboard. Both glyphs shine under the mouse, by the hover every tab shares (`panes.hover`). The dashboard draws one
season whole -- its head (`season_head`), its four tiles Spent, Price, Load, At risk, abreast or two by two, its tables
Tasks and Members, the dearest first, then Rhythm and Context and the principal (`season_zones`) --, or under `[all]`
every season played (`seasons_head`, `seasons_zones`): the table Seasons closed by its rows `all` and `median`, the empty
seasons named under it, and the table Dearest tasks. Each zone is drawn at its own width (`Zone`): a table leaves out
its columns from the last that the width does not hold, a line its parts -- a cell is never cut. The hours are local
(`moment`).

The BASE of the costs -- chosen in the settings (`panes.settings`), its word in both titles -- picks which of the
three bases the face gives is said, never converts one into another. The SEASON -- `[s.<n>] … [all]` in the
dashboard's title -- picks the season drawn; none chosen, the dashboard draws the season of the summary. The words of
a title are clicked (`title_word`), as the glyph of a frame that expands is."""
from __future__ import annotations

from rich.cells import cell_len
from rich.text import Text
from textual.containers import Grid, VerticalScroll
from textual.events import Resize
from textual.content import Content
from textual.markup import escape
from textual.widgets import Static

import palette
from palette import amount, lasted
from model import looks as judgments
from model.teams import SEASON_ALL

BASE_WORDS = {"usd": "USD", "launches": "launches", "tokens": "tokens"}   # a base as its title and its cells say it
SPARKS = "▁▂▃▄▅▆▇█"
GAP = "·"                      # a sparkline's cell for a measure the face says none of


# ---------- the words of a number ----------
def costed(cost: dict | None, base: str) -> str:
    """-> a cost said in its base, `41.20 USD`, `~1.2M tokens` when the face says the tokens estimated."""
    cost = cost or {}
    said = amount(cost.get(base), base)
    if said == palette.NONE:
        return said
    return f"{'~' if base == 'tokens' and cost.get('tokens_estimated') else ''}{said} {BASE_WORDS[base]}"


def share(value: object) -> str:
    return palette.percent(value)


def times(value: object) -> str:
    return f"×{value:.1f}" if isinstance(value, (int, float)) else palette.NONE


def moment(iso: object) -> str:
    """-> an instant of the face in local time (`palette.moment_of`, E6): its hour alone today, `DD/MM HH:MM` another
    day; `—` for none."""
    return palette.moment_of(str(iso)) if iso else palette.NONE


def axis(start: str, end: str, cells: int) -> str:
    """-> the axis of the hours under a sparkline of `cells` cells: its first hour, a line, its last, `18:00 ─── 08:58`."""
    return f"{start} {'─' * max(3, cells - len(start) - len(end) - 2)} {end}"


def spark(values: list) -> str:
    """-> a sparkline of the values in their order, each cell its value's height between the least and the most;
    `GAP` for a value that is no number."""
    found = [one for one in values if isinstance(one, (int, float))]
    if not found:
        return GAP * len(values)
    low, high = min(found), max(found)
    cells = []
    for one in values:
        if not isinstance(one, (int, float)):
            cells.append(GAP)
        else:
            cells.append(SPARKS[-1] if high == low else SPARKS[round((one - low) / (high - low) * (len(SPARKS) - 1))])
    return "".join(cells)


def per_unit(value: object, base: str) -> str:
    """-> a rate in a base -- a cost per delegation, per launch, per hour --: `4.23` USD, `2.10` launches, `11.5M`
    tokens; `—` for what is no number."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return palette.NONE
    return palette.tokens_of(value) if base == "tokens" else f"{value:.2f}"


def hours(value: object) -> str:
    """-> hours as the face counts them, `7.9 h`; `—` for none."""
    return f"{value:.1f} h" if isinstance(value, (int, float)) and not isinstance(value, bool) else palette.NONE


# ---------- the judgments: a measure against its median, a share on its thresholds (`model/looks.py`) ----------
def against(one: dict, group: str, key: str) -> dict:
    """-> what the face says of a measure against the median of the seasons, `against.<group>.<key>`: `{median,
    ratio, over}`; empty when it says none."""
    return (((one.get("against") or {}).get(group) or {}).get(key)) or {}


def judged(one: dict, group: str, key: str, text: str, look: dict, code: str | None = None) -> Text:
    """-> `text` compared to the median of the seasons as the face judged it: its ratio said without colour
    (`▲ ×1.50`), both in the look of the code the table of the judgments gives -- `code` when the measure is a share
    judged on its own thresholds."""
    said = against(one, group, key)
    found = code if code is not None else judgments.judged(f"{group}.{key}", said.get("ratio"), said.get("over"))
    return palette.compared(text, said.get("ratio"), found, look)


def marked(text: str, measure: str, value: object, look: dict) -> Text:
    """-> a share on the thresholds of the table of the judgments: `text`, its mark (`!`, `!!`) after it, in the look
    of its code."""
    code = judgments.shared(measure, value if isinstance(value, (int, float)) else None)
    mark = judgments.mark_of(code)
    return palette.coded(f"{text} {mark}" if mark else text, code, look)


def muted(text: str, look: dict) -> Text:
    return Text(text, style=look[judgments.MUTED])


def fitted(parts: list, width: int, priority: tuple[int, ...] | None = None, glued: frozenset = frozenset()) -> Text:
    """-> the parts of a line in their order, joined by `palette.SEP` -- by a blank for a part `glued` to the one
    before it --, as many of them as `width` holds: while the line is too wide, the part last in `priority` (the
    indices of `parts`, the most needed first; their order without one) leaves, whole -- never a part cut, the most
    needed always kept."""
    given = {at: (one if isinstance(one, Text) else Text(one)) for at, one in enumerate(parts) if one}
    order = [at for at in (priority if priority is not None else range(len(parts))) if at in given]
    kept = set(order)

    def line() -> Text:
        said, last = Text(), None
        for at in sorted(kept):
            if last is not None:
                said.append(" " if at in glued and last == at - 1 else palette.SEP)
            said.append_text(given[at])
            last = at
        return said
    said = line()
    while len(kept) > 1 and said.cell_len > width:
        kept.discard(next(at for at in reversed(order) if at in kept))
        said = line()
    return said


def flowed(parts: list, width: int, style: str = "") -> Text:
    """-> the parts joined by `palette.SEP` over as many lines of `width` as they need, a line breaking between two
    parts, never inside one."""
    lines: list[Text] = []
    for one in (part for part in parts if part):
        one = one if isinstance(one, Text) else Text(one)
        if lines and lines[-1].cell_len + len(palette.SEP) + one.cell_len <= width:
            lines[-1].append(palette.SEP)
            lines[-1].append_text(one)
        else:                                        # a line of its own, never the first part's: a
            lines.append(Text())                     # part's style stays on that part (`Text.style` would cover
            lines[-1].append_text(one)               # what the line appends after it)
    said = Text("\n").join(lines)
    if style:
        said.stylize(style)
    return said


# ---------- the summary: the right half of the team's frame ----------
def season_title(team: str, one: dict | None, number: object, state: object) -> str:
    """The LABEL of the team's frame: the team, then its season and the season's state, `pp-workers ── season 13 ·
    running`; the team alone for a team never started."""
    if one is not None:
        number, state = one.get("season"), one.get("state")
    if number is None:
        return palette.framed(team)
    return palette.framed(f"{team} ── season {number}" + (f"{palette.SEP}{state}" if state else ""))


def _tab(word: str, chosen: bool) -> str:
    """-> a word of a title between its brackets, `[s.3]`, in markup -- the one chosen in reverse."""
    said = f"\\[{escape(word)}]"
    return f"[bold reverse]{said}[/]" if chosen else said


def summary_title(base: str, hovered: bool = False) -> str:
    """The LABEL of the summary: its name, the base of its costs, the glyph that opens the dashboard last -- in the
    look `palette.HOVER` while the mouse is on it."""
    return palette.expandable(f"season stats ── {BASE_WORDS[base]}", False, hovered)


LABEL = 6                      # the cells of the word that heads a line of the summary
UNBOUND = 10_000               # a width no line reaches: the summary at its whole
GAUGE = 10                     # the cells of the gauge of the budget


SPENT_PRIORITY = (0, 2, 3, 4, 1)   # what `spent` keeps first: the spending, the share, the pace, what is left, the gauge
SPENT_GLUED = frozenset({2})       # the share follows its gauge


def spent_parts(one: dict, base: str, look: dict) -> list:
    """-> what the season spent, its parts in their order: against its cap, the gauge of the cap and its share, the
    pace per hour of active time, the hours left at that pace (`SPENT_PRIORITY` says which leave first); without a cap
    in the base, the cost alone."""
    budget = (one.get("budget") or {}).get(base) if base != "tokens" else None
    if not isinstance(budget, dict) or budget.get("cap") is None:
        return [costed(one.get("cost"), base)]
    return [f"{amount(budget.get('spent'), base)} / {amount(budget.get('cap'), base)}",
            palette.share_bar(budget.get("share"), GAUGE, look),
            marked(share(budget.get("share")), "budget.share", budget.get("share"), look),
            f"{per_unit(budget.get('per_active_hour'), base)} / active h",
            f"{hours(budget.get('hours_left'))} left" if budget.get("hours_left") is not None else ""]


def summary_lines(one: dict, base: str, look: dict) -> list[tuple[str, list]]:
    """-> the five lines of the summary, each its word and its parts, the most needed first: `spent`; `work`, the
    delegations and the tasks; `price`, the cost per delegation judged and its median; `load`, the launches per
    delegation judged and the root's share -- the root's share alone in `launches`, where the price says them --;
    `watch`, the cost per hour of effort judged, the failed wake-ups judged, the context's p90 judged as a share on
    its thresholds, its mark and no ratio (E14), the cost per launch said without judgment -- the two costs left out
    in `launches`. `spent` keeps its parts in the order of `SPENT_PRIORITY`, its gauge leaving first (E13)."""
    tasks, delegated = one.get("tasks") or {}, one.get("per_delegation") or {}
    root, context, losses = one.get("root") or {}, one.get("context") or {}, one.get("losses") or {}
    median = against(one, "per_delegation", base).get("median")
    rooted = f"root {share((root.get('share') or {}).get(base))}"
    p90 = context.get("p90")
    watch = [judged(one, "losses", "failed", f"{losses.get('failed', palette.NONE)} failed", look),
             marked(f"ctx p90 {share(p90)}", "context.p90", p90, look)]
    if base != "launches":
        watch.insert(0, judged(one, "per_effort_hour", base,
                               f"{per_unit((one.get('per_effort_hour') or {}).get(base), base)} / effort h", look))
        watch.append(f"{per_unit((one.get('per_launch') or {}).get(base), base)} / launch")
    return [("spent", spent_parts(one, base, look)),
            ("work", [f"{one.get('delegations', palette.NONE)} delegations",
                      f"{tasks.get('closed', palette.NONE)} closed", f"{tasks.get('stopped', palette.NONE)} stopped",
                      f"{tasks.get('open', palette.NONE)} open"]),
            ("price", [judged(one, "per_delegation", base, f"{per_unit(delegated.get(base), base)} / delegation", look),
                       muted(f"median {per_unit(median, base)}", look)]),
            ("load", [rooted] if base == "launches" else
             [judged(one, "per_delegation", "launches",
                     f"{per_unit(delegated.get('launches'), 'launches')} launches / delegation", look), rooted]),
            ("watch", watch)]


def summary_text(one: dict | None, base: str, look: dict, width: int = UNBOUND) -> Text:
    """The summary of a season, as the face says it, five lines -- the head's beside it --, each held to `width`
    cells: its word, then its parts, as many as the width holds, a part whole or left out (`summary_lines`)."""
    if one is None:
        return palette.dim(f"{palette.NONE}  no season stats")
    said = []
    for word, parts in summary_lines(one, base, look):
        line = Text(f"{word:<{LABEL}}", style=look[judgments.MUTED])
        spent = word == "spent" and len(parts) > 1
        line.append_text(fitted(parts, max(1, width - LABEL), SPENT_PRIORITY if spent else None,
                                SPENT_GLUED if spent else frozenset()))
        said.append(line)
    return Text("\n").join(said)


def summary_width(one: dict | None, base: str, look: dict) -> int:
    """-> the cells the summary takes at its whole: its longest line with every part."""
    return max((line.cell_len for line in summary_text(one, base, look).split("\n")), default=0)


# ---------- the dashboard ----------
def board_title(team: str, base: str, seasons: list[int], chosen: object, hovered: bool = False,
                room: int | None = None) -> str:
    """The LABEL of the dashboard: the team, the base of its costs, the tabs of the seasons, the latest first, then
    `[all]`, the one drawn bold; the glyph that closes it last -- in the look `palette.HOVER` while the mouse is on
    it. Held to `room` cells: the tabs of the oldest seasons leave whole, the one drawn, `[all]` and the glyph stay
    -- never a title cut."""
    shown = f"s.{chosen}" if chosen != SEASON_ALL else SEASON_ALL
    tabs = [f"s.{one}" for one in seasons]

    def label(kept: list[str]) -> str:
        said = " ".join(_tab(one, one == shown) for one in kept + [SEASON_ALL])
        return palette.expandable(f"{escape(team)}{palette.SEP}dashboard ── {BASE_WORDS[base]} ── {said}", True,
                                  hovered)
    while room is not None and cell_len(plain_of(label(tabs))) > room:
        older = [at for at, one in enumerate(tabs) if one != shown]
        if not older:
            break
        del tabs[older[-1]]
    return label(tabs)


TILES = (("spent", "Spent"), ("price", "Price"), ("load", "Load"), ("risk", "At risk"))   # a season's tiles, in order
ZONES = (("tasks", "Tasks ── dearest first"), ("members", "Members ── dearest first"))  # its tables, under the tiles
LOW = (("rhythm", "Rhythm"), ("context", "Context and the principal"))   # its two zones of the bottom, side by side
LAUNCHES = (("launches", "Launches"),)   # under them, the launches by model and by duration (D4)
EVERY_ZONES = (("seasons", "Seasons"), ("dearest", "Dearest tasks"))      # the zones of `[all]`, in order
TILE_LEAST = 30                # the cells a tile takes at least: the four tiles stand abreast once each has them


def season_head(one: dict | None):
    """-> the drawing of the head of a season's dashboard at a width, above its zones: its number, its bounds, its
    length, its state -- flowed over the lines the width asks."""
    def draw(width: int) -> Text:
        if one is None:
            return palette.dim(f"{palette.NONE}  no stats for this season")
        spent = one.get("time") or {}
        return flowed([f"SEASON {one.get('season')}",
                       f"{moment(one.get('started'))} → {moment(one.get('ended')) if one.get('ended') else 'now'}",
                       lasted(spent.get("elapsed")), str(one.get("state") or palette.NONE),
                       "empty" if one.get("empty") else ""], width, palette.BOLD)
    return draw


def _tile(title: str, head: str, lines: list, look: dict):
    """-> the drawing of a tile at a width: its title, its head figure in bold, then its lines, each held to the width
    (`fitted`) -- on the tile's ground (`palette.tile_text`)."""
    def draw(width: int) -> Text:
        room = max(1, width - 4)              # the frame and the padding of the tile
        return palette.tile_text(title, head, [fitted(one if isinstance(one, list) else [one], room) for one in lines],
                                 look, width)
    return draw


def spent_tile(one: dict, base: str, look: dict):
    """Spent: what the season spent against its cap, the gauge and the share of the cap, the pace and the hours left;
    without a cap in the base, the cost and the launches."""
    parts = spent_parts(one, base, look)
    if len(parts) == 1:
        return _tile("Spent", parts[0], [f"{(one.get('cost') or {}).get('launches', palette.NONE)} launches",
                                         muted(f"{palette.NONE} no cap", look)], look)
    gauge = parts[1].copy()
    gauge.append(" ")
    gauge.append_text(parts[2])
    return _tile("Spent", f"{parts[0]} {BASE_WORDS[base]}", [gauge, parts[3:]], look)


def price_tile(one: dict, base: str, look: dict):
    """Price: the cost per delegation, its median and its ratio judged; then the cost per hour of effort judged --
    none in `launches`."""
    median = against(one, "per_delegation", base).get("median")
    effort = (one.get("per_effort_hour") or {}).get(base)
    return _tile("Price", f"{per_unit((one.get('per_delegation') or {}).get(base), base)} {BASE_WORDS[base]} / deleg.",
                 [judged(one, "per_delegation", base, f"median {per_unit(median, base)}", look),
                  judged(one, "per_effort_hour", base, f"{per_unit(effort, base)} / effort h", look)
                  if base != "launches" else muted(palette.NONE, look)], look)


def load_tile(one: dict, base: str, look: dict):
    """Load: the launches per delegation, their median and their ratio judged, then the root and its share; in
    `launches`, where the price says them, the root and its share alone."""
    root = one.get("root") or {}
    rooted = f"root {root.get('member') or palette.NONE} {share((root.get('share') or {}).get(base))}"
    if base == "launches":
        return _tile("Load", rooted, [muted(palette.NONE, look), muted(palette.NONE, look)], look)
    median = against(one, "per_delegation", "launches").get("median")
    return _tile("Load", f"{per_unit((one.get('per_delegation') or {}).get('launches'), 'launches')} launches / deleg.",
                 [judged(one, "per_delegation", "launches", f"median {per_unit(median, 'launches')}", look), rooted],
                 look)


def risk_tile(one: dict, base: str, look: dict):
    """At risk: what the tasks stopped cost, their share of the season on its thresholds, the failed wake-ups
    judged."""
    stopped, losses = one.get("stopped_tasks") or {}, one.get("losses") or {}
    part = (stopped.get("share") or {}).get(base)
    return _tile("At risk", f"{amount((stopped.get('cost') or {}).get(base), base)} {BASE_WORDS[base]} stopped",
                 [marked(f"{share(part)} of the season", "stopped_tasks.share", part, look),
                  judged(one, "losses", "failed", f"{losses.get('failed', palette.NONE)} failed", look)], look)


SHARE_BAR = 8                  # the cells of the bar of a share in a table


def _cells(cell: object) -> int:
    return cell.cell_len if isinstance(cell, Text) else cell_len(str(cell))


def columned(columns: list[tuple[str, bool]], rows: list[list], look: dict, width: int, closing: list[list] = ()) -> Text:
    """-> a table drawn whole at `width` (`palette.table_text`): its columns given in the order of their priority,
    those the width does not hold left out from the last -- a column whole or gone, never a cell cut (E1)."""
    every = [*rows, *closing]

    def need(count: int) -> int:                     # the cells of the first `count` columns, their padding counted
        return sum(max([cell_len(title)] + [_cells(row[at]) for row in every]) + 2
                   for at, (title, _) in enumerate(columns[:count]))
    count = len(columns)
    while count > 1 and need(count) > width:
        count -= 1
    return palette.table_text(columns[:count], [row[:count] for row in rows], look, width,
                              closing=[row[:count] for row in closing])


def _share_cell(value: object, look: dict) -> Text:
    """-> a share in a table: its bar, then its figure -- the figure last, so that the column aligns it right."""
    said = palette.share_bar(value if isinstance(value, (int, float)) else None, SHARE_BAR, look)
    said.append(f" {share(value):>4}")
    return said


def _dearest(lines: list, base: str) -> list:
    """-> the lines of a table, the dearest first in the base -- the geometry of the drawing, no measure."""
    def cost(one: dict) -> float:
        found = (one.get("cost") or {}).get(base)
        return found if isinstance(found, (int, float)) else float("-inf")
    return sorted((one for one in lines if isinstance(one, dict)), key=cost, reverse=True)


def tasks_zone(one: dict, base: str, look: dict):
    """Tasks: one row per task of the season (`by_task`), the dearest first -- its state, its cost, its share, its
    delegations, its cost per delegation judged, its launches per delegation judged (none in `launches`, where the
    cost per delegation says them), its failed wake-ups, its largest context; the columns in that priority (E1)."""
    word = BASE_WORDS[base]
    columns = [("task", False), ("state", False), (word, True), ("share", True), ("deleg.", True),
               (f"{word}/deleg.", True)] + ([("launches/deleg.", True)] if base != "launches" else []) + \
        [("failed", True), ("ctx max", True)]
    rows = []
    for line in _dearest(one.get("by_task") or [], base):
        delegated = line.get("per_delegation") or {}
        row = [str(line.get("task") or palette.NONE),
               Text(str(line.get("state") or palette.NONE), style=palette.TASK_STYLES.get(line.get("state"), "")),
               amount((line.get("cost") or {}).get(base), base), _share_cell((line.get("share") or {}).get(base), look),
               str(line.get("do", palette.NONE)),
               judged(line, "per_delegation", base, per_unit(delegated.get(base), base), look)]
        if base != "launches":
            row.append(judged(line, "per_delegation", "launches", per_unit(delegated.get("launches"), "launches"),
                              look))
        rows.append(row + [str(line.get("failures", palette.NONE)), share(line.get("context_max"))])

    def draw(width: int) -> Text:
        return columned(columns, rows, look, width) if rows else muted(f"{palette.NONE}  no task", look)
    return draw


def members_zone(one: dict, base: str, look: dict):
    """Members: one row per member of the season (`by_member`), the dearest first, the root marked -- its cost, its
    share, its cost per launch, its cost per hour of effort judged against the median of the season
    (`against.per_effort_hour.<base>` of the line, D8), its role, its models, the most launched first, its launches,
    the delegations it received, the median wait of its answers, its failed wake-ups, its largest context; the costs
    per launch and per hour none in `launches`; the columns in that priority (E1)."""
    word, root, full = BASE_WORDS[base], (one.get("root") or {}).get("member"), base != "launches"
    columns = [("member", False), (word, True), ("share", True)] + \
        ([(f"{word}/launch", True), (f"{word}/effort h", True)] if full else []) + [("role", False), ("model", False)] + \
        ([("launches", True)] if full else []) + \
        [("deleg.", True), ("answers in", True), ("failed", True), ("ctx max", True)]
    rows = []
    for line in _dearest(one.get("by_member") or [], base):
        name = str(line.get("member") or palette.NONE)
        row = [f"{name} {palette.ROOT_MARK}" if root and name == root else name,
               amount((line.get("cost") or {}).get(base), base), _share_cell((line.get("share") or {}).get(base), look)]
        if full:
            row += [per_unit((line.get("per_launch") or {}).get(base), base),
                    judged(line, "per_effort_hour", base, per_unit((line.get("per_effort_hour") or {}).get(base), base),
                           look)]
        row += [", ".join(str(role) for role in line.get("roles") or []) or palette.NONE,
                ", ".join(str(model) for model in line.get("models") or [] if model) or palette.NONE]
        if full:
            row.append(str((line.get("cost") or {}).get("launches", palette.NONE)))
        rows.append(row + [str(line.get("do", palette.NONE)), lasted(line.get("do_re_median")),
                           str(line.get("failures", palette.NONE)), share(line.get("context_max"))])

    def draw(width: int) -> Text:
        return columned(columns, rows, look, width) if rows else muted(f"{palette.NONE}  no member", look)
    return draw


def rhythm_zone(one: dict, base: str, look: dict):
    """Rhythm: the cost by slot in the base of the settings (`time.cost_by_slot`, each launch's cost in the slot of its
    end, D3), above the effort by slot, both over ONE axis of the season's local hours; then the active share, the
    parallelism, the effort."""
    spent = one.get("time") or {}
    slot = spent.get("slot")
    each = f"{slot // 3600} h" if isinstance(slot, int) and slot and slot % 3600 == 0 else lasted(slot)
    costs = (spent.get("cost_by_slot") or {}).get(base)
    lines = ([(f"{BASE_WORDS[base]} by {each}", spark(costs))] if isinstance(costs, list) and costs else []) + \
        [(f"effort by {each}", spark(spent.get("effort_by_slot") or []))]
    head = max(len(label) for label, _ in lines) + 2
    cells = max(len(drawn) for _, drawn in lines)
    ruler = axis(moment(one.get("started")), moment(one.get("ended")) if one.get("ended") else "now", cells)

    def draw(width: int) -> Text:
        indent = head if head + max(cells, len(ruler)) <= width else 0
        said = Text()
        for label, drawn in lines:
            said.append(f"{label:<{head}}" if indent else f"{label}\n")
            said.append(drawn + "\n")
        said.append(" " * indent + ruler + "\n", style=look[judgments.MUTED])
        said.append_text(flowed([f"active {share(spent.get('active_share'))}",
                                 f"parallelism {times(spent.get('parallelism'))}",
                                 f"effort {lasted(spent.get('effort'))}"], width))
        return said
    return draw


def lasting(band: dict) -> str:
    """-> the bounds of a band of durations as the face gives them (`from`, `to` in seconds, `to` none for the last):
    `< 1 min`, `1 min–3 min`, `≥ 30 min` -- the post writes no bound of its own (DL1)."""
    start, end = band.get("from"), band.get("to")
    if end is None:
        return f"≥ {lasted(start)}"
    return f"< {lasted(end)}" if not start else f"{lasted(start)}–{lasted(end)}"


def banded(band: dict) -> str:
    """-> the bounds of a band of context as the face gives them (`from`, `to` shares of the window): `< 25%`,
    `25%–50%`, `≥ 90%`."""
    start, end = band.get("from"), band.get("to")
    if end is None:
        return f"≥ {share(start)}"
    return f"< {share(end)}" if not start else f"{share(start)}–{share(end)}"


def _launch_columns(first: str, base: str) -> list[tuple[str, bool]]:
    """-> the columns of a table of launches, in their priority (E1): its first, the launches, then the cost, the share,
    the cost per hour of effort and per launch -- in `launches` the launches are the cost, and no rate is."""
    word = BASE_WORDS[base]
    if base == "launches":
        return [(first, False), ("launches", True), ("share", True)]
    return [(first, False), ("launches", True), (word, True), ("share", True), (f"{word}/effort h", True),
            (f"{word}/launch", True)]


def _launch_row(label, line: dict, base: str, look: dict) -> list:
    """-> a row of a table of launches -- a model, a band --, nothing judged (D5): its figures as the face gives them."""
    row = [label, str(line.get("launches", palette.NONE))]
    if base != "launches":
        row.append(amount((line.get("cost") or {}).get(base), base))
    row.append(_share_cell((line.get("share") or {}).get(base), look))
    if base != "launches":
        row += [per_unit((line.get("per_effort_hour") or {}).get(base), base),
                per_unit((line.get("per_launch") or {}).get(base), base)]
    return row


def launches_zone(one: dict, base: str, look: dict):
    """Launches: two tables, nothing judged (D5) -- by model (`by_model`, the most launched first as the face gives
    them, the launches without a model written apart on their own row, DL3), then its effort and its provider; by
    duration of a launch (`by_duration`, its bands as the face gives them)."""
    models = []
    for line in one.get("by_model") or []:
        name = line.get("model")
        label = str(name) if name else muted(f"{palette.NONE} no model", look)
        models.append(_launch_row(label, line, base, look) + [lasted(line.get("effort")),
                                                              str(line.get("provider") or palette.NONE)])
    durations = [_launch_row(lasting(line), line, base, look) for line in one.get("by_duration") or []]

    def draw(width: int) -> Text:
        if not models and not durations:
            return muted(f"{palette.NONE}  no launch", look)
        said = muted("by model\n", look)
        said.append_text(columned(_launch_columns("model", base) + [("effort", True), ("provider", False)], models,
                                  look, width) if models else muted(palette.NONE, look))
        said.append("\n\n")
        said.append_text(muted("by duration\n", look))
        said.append_text(columned(_launch_columns("duration", base), durations, look, width) if durations
                         else muted(palette.NONE, look))
        return said
    return draw


def context_zone(one: dict, base: str, look: dict):
    """Context and the principal: the context a wake-up leaves at its end, its median and its p90 judged as a share on
    its thresholds, its mark and no ratio (E14); the runs renewed and the silences; the failed wake-ups judged and
    their causes; the questions to the principal and their wait (E4) -- each group flowed over the lines the width
    asks; then the table of the launches by their context at their end (`context.by_band`, nothing judged, D5)."""
    context, losses, asked = one.get("context") or {}, one.get("losses") or {}, one.get("principal") or {}
    p90 = context.get("p90")
    groups = [[f"end of a wake-up: median {share(context.get('median'))}",
               marked(f"p90 {share(p90)}", "context.p90", p90, look)],
              [f"{context.get('renewals', palette.NONE)} renewals", f"{losses.get('silences', palette.NONE)} silences"],
              [judged(one, "losses", "failed", f"{losses.get('failed', palette.NONE)} failed", look)]
              + [f"{reason} {count}" for reason, count in (losses.get("reasons") or {}).items()],
              [f"{asked.get('asked', palette.NONE)} questions", f"{asked.get('answered', palette.NONE)} answered",
               f"median wait {lasted(asked.get('wait_median'))}"]]

    bands = [_launch_row(banded(line), line, base, look) for line in context.get("by_band") or []]

    def draw(width: int) -> Text:
        said = Text("\n").join(flowed(group, width) for group in groups)
        if bands:                                    # under its lines, the launches by their context at their end
            said.append("\n\n")
            said.append_text(columned(_launch_columns("context", base), bands, look, width))
        return said
    return draw


def season_zones(one: dict | None, base: str, look: dict) -> dict:
    """-> the zones of a season's dashboard, by key, each the drawing of its zone at a width: its four tiles --
    Spent, Price, Load, At risk --, its tables, Tasks and Members, then its Rhythm and its Context, then its
    Launches."""
    if one is None:
        return {}
    return {"spent": spent_tile(one, base, look), "price": price_tile(one, base, look),
            "load": load_tile(one, base, look), "risk": risk_tile(one, base, look),
            "tasks": tasks_zone(one, base, look), "members": members_zone(one, base, look),
            "rhythm": rhythm_zone(one, base, look), "context": context_zone(one, base, look),
            "launches": launches_zone(one, base, look)}


DEAREST = 5                    # the dearest tasks `[all]` shows (E5); the others are read on the Tasks tab
CONCENTRATION = "80%"          # the share of the cost whose tasks the face counts in `task_cost.<base>.concentration`


def seasons_head(every: dict | None, base: str):
    """-> the drawing of the head of `[all]` at a width: the seasons played and those empty, then the totals of the
    face (`total`) -- the cost, the launches, the delegations, the cost per delegation."""
    def draw(width: int) -> Text:
        if every is None:
            return palette.dim(f"{palette.NONE}  no season stats")
        total = every.get("total") or {}
        cost = total.get("cost") or {}
        parts = ["ALL SEASONS", f"{total.get('seasons', palette.NONE)} played", f"{len(every.get('empty') or [])} empty",
                 costed(cost, base)] + ([f"{cost.get('launches', palette.NONE)} launches"] if base != "launches" else [])
        parts += [f"{total.get('delegations', palette.NONE)} delegations",
                  f"{per_unit((total.get('per_delegation') or {}).get(base), base)} {BASE_WORDS[base]} / delegation"]
        return flowed(parts, width, palette.BOLD)
    return draw


def seasons_zone(every: dict, base: str, look: dict):
    """Seasons: one row per season played, the oldest first -- its start, its cost, its delegations, its cost per
    delegation and its launches per delegation judged, its cost per launch, the root's share, the share of its stopped
    tasks on its thresholds, its failed wake-ups judged --, closed by the face's `total` and `median`, on the ground of
    its header; the empty seasons named under it. The columns in that priority (E1)."""
    word, full = BASE_WORDS[base], base != "launches"
    total, median = every.get("total") or {}, every.get("median") or {}
    columns = [("s.", True), ("start", False), (word, True), ("deleg.", True), (f"{word}/deleg.", True)] + \
        ([("launches/deleg.", True), (f"{word}/launch", True)] if full else []) + \
        [("root", True), ("stopped", True), ("failed", True)]
    rows = []
    for one in every.get("seasons") or []:
        delegated, stopped = one.get("per_delegation") or {}, (one.get("stopped_tasks") or {}).get("share") or {}
        rows.append([str(one.get("season")), moment(one.get("started")), amount((one.get("cost") or {}).get(base), base),
                     str(one.get("delegations", palette.NONE)),
                     judged(one, "per_delegation", base, per_unit(delegated.get(base), base), look)]
                    + ([judged(one, "per_delegation", "launches", per_unit(delegated.get("launches"), "launches"), look),
                        per_unit((one.get("per_launch") or {}).get(base), base)] if full else [])
                    + [share(((one.get("root") or {}).get("share") or {}).get(base)),
                       marked(share(stopped.get(base)), "stopped_tasks.share", stopped.get(base), look),
                       judged(one, "losses", "failed", str((one.get("losses") or {}).get("failed", palette.NONE)), look)])
    every_delegated, central = total.get("per_delegation") or {}, median.get("per_delegation") or {}
    closing = [["all", f"{total.get('seasons', palette.NONE)} seasons", amount((total.get("cost") or {}).get(base), base),
                str(total.get("delegations", palette.NONE)), per_unit(every_delegated.get(base), base)]
               + ([per_unit(every_delegated.get("launches"), "launches"),
                   per_unit((total.get("per_launch") or {}).get(base), base)] if full else [])
               + ["", share(((total.get("stopped_tasks") or {}).get("share") or {}).get(base)),
                  str(total.get("failed", palette.NONE))],
               ["median", "", amount((median.get("cost") or {}).get(base), base), "", per_unit(central.get(base), base)]
               + ([per_unit(central.get("launches"), "launches"), ""] if full else [])
               + ["", "", str((median.get("losses") or {}).get("failed", palette.NONE))]]
    empty = every.get("empty") or []

    def draw(width: int) -> Text:
        said = columned(columns, rows, look, width, closing)
        if empty:
            said.append("\n")
            said.append_text(muted(f"empty: {', '.join(str(one) for one in empty)}", look))
        return said
    return draw


def _seasons_of(line: dict) -> str:
    found = sorted(one for one in line.get("seasons") or [] if isinstance(one, int))
    if not found:
        return palette.NONE
    return str(found[0]) if len(found) == 1 else f"{found[0]}-{found[-1]}"


def dearest_zone(every: dict, base: str, look: dict):
    """Dearest tasks: the `DEAREST` dearest tasks over every season (`by_task` of `--all`) -- their seasons, their
    state, their cost, their delegations, their cost per delegation, their name; the columns in that priority (E1)."""
    word = BASE_WORDS[base]
    columns = [("task", False), ("season", True), ("state", False), (word, True), ("deleg.", True),
               (f"{word}/deleg.", True), ("name", False)]
    rows = [[str(line.get("task") or palette.NONE), _seasons_of(line),
             Text(str(line.get("state") or palette.NONE), style=palette.TASK_STYLES.get(line.get("state"), "")),
             amount((line.get("cost") or {}).get(base), base), str(line.get("do", palette.NONE)),
             per_unit((line.get("per_delegation") or {}).get(base), base),
             " ".join(palette.plain(str(line.get("name") or palette.NONE)).split())]
            for line in _dearest(every.get("by_task") or [], base)[:DEAREST]]

    def draw(width: int) -> Text:
        return columned(columns, rows, look, width) if rows else muted(f"{palette.NONE}  no task", look)
    return draw


def seasons_zones(every: dict | None, base: str, look: dict) -> tuple[dict, dict[str, str]]:
    """-> the zones of `[all]`, as `team stats --all --json` says the seasons, each the drawing of its zone at a width
    -- Seasons, then Dearest tasks --, and their titles: the title of Dearest tasks says how the cost concentrates
    (`task_cost.<base>`: the tasks that carry `CONCENTRATION` of it, of how many, the median and the p90 of a task)."""
    if every is None:
        return {}, {}
    spread = (every.get("task_cost") or {}).get(base) or {}
    held = spread.get("concentration") or {}
    title = (f"Dearest tasks ── {CONCENTRATION} of the cost in {held.get('tasks', palette.NONE)} tasks of "
             f"{held.get('of', palette.NONE)}{palette.SEP}median {amount(spread.get('median'), base)}{palette.SEP}"
             f"p90 {amount(spread.get('p90'), base)} {BASE_WORDS[base]}") if spread else "Dearest tasks"
    return ({"seasons": seasons_zone(every, base, look), "dearest": dearest_zone(every, base, look)},
            {"dearest": title})


PAIRED = 100           # from this width, the dashboard sets its two zones of the bottom side by side


class Zone(Static):
    """A zone of the dashboard drawn at its own width: `draw(width)` gives its text, drawn again when the width
    changes -- a table leaves out the columns the width does not hold, a line the parts."""

    def __init__(self, **options) -> None:
        super().__init__("", markup=False, **options)
        self._draw = None
        self._width: int | None = None

    def draw(self, draw) -> None:
        self._draw, self._width = draw, None
        self._redraw()

    def on_resize(self, event: Resize) -> None:
        self._redraw()

    def _redraw(self) -> None:
        width = self.content_size.width
        if self._draw is None or width <= 0 or width == self._width:
            return
        self._width = width
        self.update(self._draw(width))


class SeasonBoard(VerticalScroll):
    """The dashboard of a team's seasons, framed: its head, then its four TILES -- abreast once each has
    `TILE_LEAST` cells, two by two below --, its tables one under the other, its two zones of the bottom side by side
    once the dashboard is `PAIRED` wide; or under `[all]` its two tables. Each zone is drawn at its own width
    (`Zone`), apart from the others; the whole scrolled when it goes beyond. A zone the dashboard does not draw is
    hidden."""

    DEFAULT_CSS = """
    SeasonBoard { height: 1fr; }
    SeasonBoard > #board-head { height: auto; padding: 0 1; }
    SeasonBoard > #board-tiles { height: auto; grid-size: 2; grid-rows: auto; grid-gutter: 1 1; padding: 0 1;
                                 margin-top: 1; }
    SeasonBoard.abreast > #board-tiles { grid-size: 4; }
    SeasonBoard > #board-low { height: auto; grid-size: 1; grid-rows: auto; grid-gutter: 1 2; padding: 0 1;
                               margin-top: 1; }
    SeasonBoard.paired > #board-low { grid-size: 2; }
    SeasonBoard .board-zone { height: auto; padding: 0 1; text-wrap: nowrap; text-overflow: ellipsis; }
    SeasonBoard > .board-zone { margin: 1 1 0 1; }
    SeasonBoard .board-tile { height: auto; text-wrap: nowrap; text-overflow: ellipsis; }
    """

    def compose(self):
        yield Zone(id="board-head")
        with Grid(id="board-tiles"):
            for key, _ in TILES:
                tile = Zone(id=f"board-{key}", classes="framed board-tile")
                tile.styles.border = ("none", "transparent")    # its frame is its text's (`palette.tile_text`): the
                tile.styles.padding = 0                         # house's frame of a zone, which wins over this CSS, off
                yield tile
        for key, title in ZONES:
            yield self._zone(key, title)
        with Grid(id="board-low"):
            for key, title in LOW:
                yield self._zone(key, title)
        for key, title in LAUNCHES + EVERY_ZONES:
            yield self._zone(key, title)

    @staticmethod
    def _zone(key: str, title: str) -> Zone:
        zone = Zone(id=f"board-{key}", classes="framed board-zone")
        zone.border_title = palette.framed(title)
        return zone

    def on_resize(self, event: Resize) -> None:
        width = event.size.width - 2
        self.set_class(width >= len(TILES) * TILE_LEAST + len(TILES) - 1, "abreast")
        self.set_class(event.size.width >= PAIRED, "paired")

    def show(self, head, zones: dict, titles: dict[str, str] | None = None) -> None:
        """Draws `head` and the `zones` given by key, each a drawing at a width -- a zone's title said again by
        `titles` --; every other zone hidden, a row of zones none of whose zones is drawn hidden with them."""
        self.query_one("#board-head", Zone).draw(head)
        for key, title in TILES + ZONES + LOW + LAUNCHES + EVERY_ZONES:
            zone = self.query_one(f"#board-{key}", Zone)
            zone.display = key in zones
            if key in zones:
                if (titles or {}).get(key):
                    zone.border_title = palette.framed(titles[key])
                elif (key, title) not in TILES:
                    zone.border_title = palette.framed(title)
                zone.draw(zones[key])
        self.query_one("#board-tiles").display = any(key in zones for key, _ in TILES)
        self.query_one("#board-low").display = any(key in zones for key, _ in LOW)


def plain_of(label: str) -> str:
    """-> the text a title's markup draws -- what `title_word` reads, the frame's `border_title` read back being
    markup written again, its brackets no longer escaped."""
    return Content.from_markup(label).plain


def title_word(frame, plain: str, x: int, y: int, words: list[str]) -> str | None:
    """-> the word of `words` the screen cell (x, y) stands on in the title of `frame`, drawn as `plain` -- its top
    edge, past the corner and the line and the blank a corner sets before the label --, each word found in the label's
    order; None elsewhere, on a frame not shown, or on a word the frame's width cuts."""
    region = frame.region
    if not frame.display or y != region.y or not plain:
        return None
    corner = frame.styles.border_left[0] not in ("", "none", "hidden")
    offset = x - (region.x + 1 + 2 * corner)
    room = region.width - 2 - 4 * corner
    at = 0
    for word in words:
        found = plain.find(word, at)
        if found < 0:
            continue
        at = found + len(word)
        if found <= offset < at and at <= room:
            return word
    return None
