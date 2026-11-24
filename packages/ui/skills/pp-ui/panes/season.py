"""season -- the STATS of a team's seasons on the Teams tab, as `team stats --json` says them: the post draws them,
it computes no number.

Two places show them. The SUMMARY, the right half of the team's frame (`summary_text`): the season under way or the
last one -- its tasks, its cost and its cost per closed task, its three times, its context, its losses. The
DASHBOARD (`SeasonBoard`), opened by the glyph `palette.EXPAND` in the summary's title and closed by
`palette.COLLAPSE` in its own or by `escape`, takes the whole centre of the tab beside the menu of the teams, which
stays shown and played: another team chosen there shows its dashboard. Both glyphs shine under the mouse, by the hover
every tab shares (`panes.hover`). The dashboard draws one season whole -- its bounds (`season_head`), then one ZONE
framed and titled per block the face gives, in its order (`season_zones`): the yield against the median of the
seasons, the cost of a task, where the cost goes, the time, the principal in the loop, the context, the losses --, or
under `[all]` every season not empty (`seasons_head`, `seasons_zones`): a zone of one row each, the empty ones named
under them, then a zone of one sparkline per measure from season to season. The zones stand apart, two by two once
the dashboard is wide enough (`PAIRED`).

The BASE of the costs -- chosen in the settings (`panes.settings`), its word in both titles -- picks which of the
three bases the face gives is said, never converts one into another. The SEASON -- `[s.<n>] … [all]` in the
dashboard's title -- picks the season drawn; none chosen, the dashboard draws the season of the summary. The words of
a title are clicked (`title_word`), as the glyph of a frame that expands is."""
from __future__ import annotations

from rich.text import Text
from textual.containers import Grid, VerticalScroll
from textual.events import Resize
from textual.content import Content
from textual.markup import escape
from textual.widgets import Static

import palette
from palette import amount, lasted
from model.teams import SEASON_ALL

BASE_WORDS = {"usd": "USD", "launches": "launches", "tokens": "tokens"}   # a base as its title and its cells say it
SPARKS = "▁▂▃▄▅▆▇█"
BLOCKS = " ▏▎▍▌▋▊▉█"           # the eighths of a cell of a bar
BAR = 24                       # the cells of a bar at its whole
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


def day(iso: object) -> str:
    """-> the day and the hour of an instant, `20/11 18:00`; `—` for none."""
    text = str(iso or "")
    if len(text) < 16:
        return palette.NONE
    return f"{text[8:10]}/{text[5:7]} {text[11:16]}"


def hour(iso: object) -> str:
    """-> the hour of an instant, `18:00`; `—` for none."""
    text = str(iso or "")
    return text[11:16] if len(text) >= 16 else palette.NONE


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


def bar(value: object, whole: object, cells: int = BAR) -> str:
    """-> a bar of `value` against `whole`, in eighths of a cell; empty for what is no number."""
    if not isinstance(value, (int, float)) or not isinstance(whole, (int, float)) or whole <= 0:
        return ""
    eighths = round(max(0.0, min(1.0, value / whole)) * cells * 8)
    return BLOCKS[-1] * (eighths // 8) + (BLOCKS[eighths % 8] if eighths % 8 else "")


def _per_closed(one: dict, base: str) -> object:
    return (one.get("yield") or {}).get(f"{base}_per_closed")


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


def summary_text(one: dict | None, base: str) -> Text:
    """The summary of a season, as the face says it, five lines -- the head's beside it: its tasks; its cost and its
    cost per closed task; its times elapsed, active, effort and their parallelism; the peak and the median of its
    context; its losses."""
    if one is None:
        return palette.dim(f"{palette.NONE}  no season stats")
    tasks, cost, spent = one.get("tasks") or {}, one.get("cost") or {}, one.get("time") or {}
    context, losses = one.get("context") or {}, one.get("losses") or {}
    said = Text()
    said.append(f"tasks    {tasks.get('closed', palette.NONE)} closed{palette.SEP}{tasks.get('open', palette.NONE)} "
                f"open{palette.SEP}{tasks.get('stopped', palette.NONE)} stopped\n")
    said.append(f"cost     {costed(cost, base)}"
                + (f"{palette.SEP}{cost.get('launches', palette.NONE)} launches" if base != "launches" else "")
                + f"{palette.SEP}{amount(_per_closed(one, base), base)} {BASE_WORDS[base]} / closed task\n")
    said.append(f"time     {lasted(spent.get('elapsed'))} elapsed{palette.SEP}{lasted(spent.get('active'))} active"
                f"{palette.SEP}{lasted(spent.get('effort'))} effort{palette.SEP}{times(spent.get('parallelism'))} "
                "parallel\n")
    said.append(f"context  peak {share(context.get('max'))}{palette.SEP}median {share(context.get('median'))}\n")
    failed = losses.get("failed")
    said.append(f"losses   {failed if failed is not None else palette.NONE} failed "
                f"({costed(losses.get('cost'), base)}){palette.SEP}{losses.get('do_extra', palette.NONE)} do again",
                style=palette.YELLOW if failed else "")
    return said


# ---------- the dashboard ----------
def board_title(team: str, base: str, seasons: list[int], chosen: object, hovered: bool = False) -> str:
    """The LABEL of the dashboard: the team, the base of its costs, the tabs of the seasons, the latest first, then
    `[all]`, the one drawn bold; the glyph that closes it last -- in the look `palette.HOVER` while the mouse is on
    it."""
    tabs = [f"s.{one}" for one in seasons] + [SEASON_ALL]
    shown = f"s.{chosen}" if chosen != SEASON_ALL else SEASON_ALL
    said = " ".join(_tab(one, one == shown) for one in tabs)
    return palette.expandable(f"{escape(team)}{palette.SEP}dashboard ── {BASE_WORDS[base]} ── {said}", True, hovered)


ZONES = (("yield", "Yield", "yield"), ("task-cost", "Cost of a task", "task_cost"),   # a season's zones, in order:
         ("roles", "Where the cost goes", "roles"), ("time", "Time", "time"),             # key, title, the field of the
         ("principal", "The principal in the loop", "principal"), ("context", "Context", "context"),   # face it draws
         ("losses", "Losses", "losses"))
EVERY_ZONES = (("seasons", "Seasons"), ("trends", "From season to season"))   # the zones of `[all]`, in order


def _against(value: object, median: object) -> str:
    """-> where a measure stands against the median of the seasons: the median, `▲` above it, `▼` under it."""
    if not isinstance(median, (int, float)):
        return palette.NONE
    mark = "" if not isinstance(value, (int, float)) or value == median else " ▲" if value > median else " ▼"
    return f"{median:g}{mark}" if isinstance(median, int) else f"{median:.2f}{mark}"


def season_head(one: dict | None) -> Text:
    """The head of a season's dashboard, above its zones: its number, its bounds, its length, its state."""
    if one is None:
        return palette.dim(f"{palette.NONE}  no stats for this season")
    spent = one.get("time") or {}
    return Text(f"SEASON {one.get('season')}{palette.SEP}{day(one.get('started'))} → "
                f"{day(one.get('ended')) if one.get('ended') else 'now'}{palette.SEP}{lasted(spent.get('elapsed'))}"
                f"{palette.SEP}{one.get('state') or palette.NONE}" + (f"{palette.SEP}empty" if one.get("empty") else ""),
                style=palette.BOLD)


def _yield(one: dict, median: dict, base: str) -> Text:
    tasks, yielded, central = one.get("tasks") or {}, one.get("yield") or {}, median.get("yield") or {}
    rows = [(f"{tasks.get('closed', palette.NONE)} closed tasks{palette.SEP}{tasks.get('stopped', palette.NONE)} stopped",
             _against(tasks.get("closed"), (median.get("tasks") or {}).get("closed"))),
            (f"{amount(yielded.get(f'{base}_per_closed'), base)} {BASE_WORDS[base]} / closed task",
             _against(yielded.get(f"{base}_per_closed"), central.get(f"{base}_per_closed")))]
    if base != "launches":
        rows.append((f"{amount(yielded.get('launches_per_closed'), 'launches')} launches / closed task",
                     _against(yielded.get("launches_per_closed"), central.get("launches_per_closed"))))
    rows.append((f"{amount(yielded.get('usd_per_launch'), 'usd')} USD / launch",
                 _against(yielded.get("usd_per_launch"), central.get("usd_per_launch"))))
    said = Text(f"{'':<40}{'median':>12}\n", style=palette.DIM)
    said.append("\n".join(f"{left:<40}{right:>12}" for left, right in rows))
    return said


def _task_cost(one: dict, base: str) -> Text:
    spread = (one.get("task_cost") or {}).get(base) or {}
    return Text(f"min {amount(spread.get('min'), base)}{palette.SEP}median {amount(spread.get('median'), base)}"
                f"{palette.SEP}max {amount(spread.get('max'), base)} {BASE_WORDS[base]}\n"
                f"{spark(spread.get('series') or [])}")


def _roles(one: dict, base: str) -> Text:
    return Text("\n".join(f"{str(role.get('role') or palette.NONE):<14}{share((role.get('share') or {}).get(base)):>6}  "
                          f"{bar((role.get('share') or {}).get(base), 1)}" for role in one.get("roles") or [])
                or palette.NONE)


def _time(one: dict) -> Text:
    spent, opening = one.get("time") or {}, one.get("opening") or {}
    slot = spent.get("slot")
    each = f"{slot // 3600} h" if isinstance(slot, int) and slot and slot % 3600 == 0 else lasted(slot)
    label, cells = f"effort by {each}   ", spark(spent.get("effort_by_slot") or [])
    said = Text(f"elapsed {lasted(spent.get('elapsed'))}{palette.SEP}active {lasted(spent.get('active'))} "
                f"({share(spent.get('active_share'))})\n"
                f"effort {lasted(spent.get('effort'))}{palette.SEP}parallelism {times(spent.get('parallelism'))}\n"
                f"{label}{cells}\n")
    said.append(" " * len(label) + axis(hour(one.get("started")), hour(one.get("ended")) if one.get("ended") else "now",
                                        len(cells)) + "\n", style=palette.DIM)
    said.append(f"opening of a wake-up   median {lasted(opening.get('median'))}{palette.SEP}"
                f"p90 {lasted(opening.get('p90'))}")
    return said


def _principal(one: dict) -> Text:
    asked = one.get("principal") or {}
    return Text(f"{asked.get('asked', palette.NONE)} questions{palette.SEP}{asked.get('answered', palette.NONE)} answered\n"
                f"median wait {lasted(asked.get('wait_median'))}{palette.SEP}max {lasted(asked.get('wait_max'))}")


def _context(one: dict) -> Text:
    context = one.get("context") or {}
    return Text(f"end of a wake-up: median {share(context.get('median'))}{palette.SEP}p90 {share(context.get('p90'))}\n"
                f"{context.get('renewals', palette.NONE)} renewals")


def _losses(one: dict, base: str) -> Text:
    losses = one.get("losses") or {}
    reasons = " · ".join(f"{reason} {count}" for reason, count in (losses.get("reasons") or {}).items())
    return Text(f"{losses.get('failed', palette.NONE)} wake-ups failed ({costed(losses.get('cost'), base)})"
                + (f": {reasons}" if reasons else "") + f"\n{losses.get('silences', palette.NONE)} silences\n"
                f"{losses.get('do_extra', palette.NONE)} do more on {losses.get('pairs_extra', palette.NONE)} pairs "
                f"task × member\n{amount(losses.get('do_per_pair'), 'launches')} do per delegation")


def season_zones(one: dict | None, median: dict | None, base: str) -> dict[str, Text]:
    """-> the zones of a season's dashboard, by key, in the order of `ZONES`: one per block whose field the face
    gives -- its YIELD against the median of the seasons; the cost of a task, its spread and its sparkline; where the
    cost goes, by role; its TIME and its effort by slot over the axis of its hours, the opening of a wake-up; the
    principal in the loop; its context; its losses. A field the face does not give draws no zone."""
    if one is None:
        return {}
    median = median or {}
    drawn = {"yield": lambda: _yield(one, median, base), "task-cost": lambda: _task_cost(one, base),
             "roles": lambda: _roles(one, base), "time": lambda: _time(one), "principal": lambda: _principal(one),
             "context": lambda: _context(one), "losses": lambda: _losses(one, base)}
    return {key: drawn[key]() for key, _, field in ZONES if field in one}


TRENDS = (("cost / closed task", lambda one, base: _per_closed(one, base)),       # the sparklines of `[all]`, in order
          ("launches / closed task", lambda one, base: (one.get("yield") or {}).get("launches_per_closed")),
          ("active", lambda one, base: (one.get("time") or {}).get("active_share")),
          ("parallelism", lambda one, base: (one.get("time") or {}).get("parallelism")),
          ("principal's wait", lambda one, base: (one.get("principal") or {}).get("wait_median")),
          ("do per delegation", lambda one, base: (one.get("losses") or {}).get("do_per_pair")))


def seasons_head(every: dict | None) -> Text:
    """The head of the dashboard under `[all]`: how many seasons are not empty, how many are."""
    if every is None:
        return palette.dim(f"{palette.NONE}  no season stats")
    return Text(f"ALL SEASONS{palette.SEP}{len(every.get('seasons') or [])} not empty{palette.SEP}"
                f"{len(every.get('empty') or [])} empty", style=palette.BOLD)


def seasons_zones(every: dict | None, base: str) -> dict[str, Text]:
    """-> the zones of `[all]`, as `team stats --all --json` says the seasons: `seasons`, one row each, the oldest
    first -- its number, its start, its cost as a bar against the dearest season, its tasks closed, its cost per closed
    task, its active share, its parallelism --, the empty seasons named under them; `trends`, one sparkline per measure
    from season to season."""
    if every is None:
        return {}
    seasons, empty = list(every.get("seasons") or []), list(every.get("empty") or [])
    word = BASE_WORDS[base]
    table = Text()
    dearest = max(((one.get("cost") or {}).get(base) for one in seasons
                   if isinstance((one.get("cost") or {}).get(base), (int, float))), default=None)
    table.append(f"{'s.':>4}  {'start':<11}  {word:>8} {'':<{BAR}}  {'closed':>6}  {'/ closed':>9}  {'active':>6}  "
                 f"{'parallel':>8}", style=palette.DIM)
    for one in seasons:
        value = (one.get("cost") or {}).get(base)
        table.append(f"\n{one.get('season'):>4}  {day(one.get('started')):<11}  {amount(value, base):>8} "
                     f"{bar(value, dearest):<{BAR}}  {(one.get('tasks') or {}).get('closed', palette.NONE):>6}  "
                     f"{amount(_per_closed(one, base), base):>9}  "
                     f"{share((one.get('time') or {}).get('active_share')):>6}  "
                     f"{times((one.get('time') or {}).get('parallelism')):>8}")
    if empty:
        table.append(f"\n      empty: {', '.join(str(one) for one in empty)}", style=palette.DIM)
    trends = Text("\n".join(f"{label:<24}{spark([measure(one, base) for one in seasons])}" for label, measure in TRENDS))
    return {"seasons": table, "trends": trends}


PAIRED = 100           # from this width, the dashboard sets its zones two by two


class SeasonBoard(VerticalScroll):
    """The dashboard of a team's seasons, framed: its head, then its ZONES, each framed and titled
    (`palette.framed`), apart from one another, two by two once the dashboard is `PAIRED` wide -- the whole scrolled
    when it goes beyond. A zone the dashboard does not draw is hidden; the zones of `[all]` take a row each."""

    DEFAULT_CSS = """
    SeasonBoard { height: 1fr; }
    SeasonBoard > #board-head { height: auto; padding: 0 1; margin-bottom: 1; }
    SeasonBoard > #board-zones { height: auto; grid-size: 1; grid-rows: auto; grid-gutter: 1 2; padding: 0 1; }
    SeasonBoard.paired > #board-zones { grid-size: 2; }
    SeasonBoard .board-zone { height: auto; padding: 0 1; }
    SeasonBoard.paired .board-zone.whole { column-span: 2; }
    SeasonBoard .board-zone.whole { text-wrap: nowrap; text-overflow: ellipsis; }   /* its height measured unwrapped */
    """

    def compose(self):
        yield Static("", id="board-head", markup=False)
        with Grid(id="board-zones"):
            for key, title, *_ in ZONES + EVERY_ZONES:
                zone = Static("", id=f"board-{key}", classes="framed board-zone", markup=False)
                zone.border_title = palette.framed(title)
                zone.set_class(any(key == one for one, _ in EVERY_ZONES), "whole")
                yield zone

    def on_resize(self, event: Resize) -> None:
        self.set_class(event.size.width >= PAIRED, "paired")

    def show(self, head: Text, zones: dict[str, Text]) -> None:
        """Draws `head` and the `zones` given by key; every other zone hidden."""
        self.query_one("#board-head", Static).update(head)
        for key, *_ in ZONES + EVERY_ZONES:
            zone = self.query_one(f"#board-{key}", Static)
            zone.display = key in zones
            if key in zones:
                zone.update(zones[key])


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
