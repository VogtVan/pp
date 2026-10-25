"""palette -- the ONE place a style or a glyph is written (the cockpit's palette, kept).

colour = a STATE, never decoration: green nominal (never bold), yellow, a frank red ·
bold = a PROBLEM · bold without colour = STRONG structure · dim = ignorance or to-come ·
default = neutral structure · cyan = a legitimate construction site · STALE = a line of the
transcript with nothing to open (the theme's disabled text, italic). The brand is `pp`
in bold and no colour: the post has no logo yet. Every datum shown carries the hour of
ITS reading, in dim -- the hour, never an age."""
from __future__ import annotations

from bisect import bisect_left
from datetime import datetime
from pathlib import Path

from rich import box
from rich.cells import cell_len
from rich.console import Console
from rich.markdown import Heading, HorizontalRule, Markdown, TableElement
from rich.rule import Rule
from rich.table import Table
from rich.text import Span, Text
from rich.theme import Theme
from textual.color import Color
from textual.content import Content

GREEN = "green"            # nominal -- never bold: bold is for problems
YELLOW = "yellow"
RED = "bold red3"          # red3: a frank red (the ansi bright-red renders pink)
RED_CONTENT = "bold #d70000"   # the same red3 in a Textual style, which knows no `red3`
DIM = "dim"
CYAN = "cyan"              # a construction site: a state, not a problem
BOLD = "bold"
STALE = "stale"            # the class of a line with nothing to open: its look is the theme's, never dim
TURNING = "bold $accent"   # the glyph of a turn under way: the theme's accent, a state to see at once

BRAND = "pp"               # bold, no colour: identity without a logo

# the frame's colours and weights, by widget id -- the theme's own tokens, never a literal
# colour; `app.py` composes this with its geometry and writes no style of its own. Every line the
# post draws is here: the THIN LINE that sets a zone apart -- `rule-top` above a band, `rule-left`
# beside a column, in the colour the theme gives a border out of focus --, the thin line of a field
# (its focus the accent), and the heavy line of an overlay's box
THEME_CSS = """
.rule-top { border-top: solid $border-blurred; }
.rule-left { border-left: solid $border-blurred; }
Screen.-narrow .centre.rule-left { border-left: none; }
#header { background: $surface; }
#brand { text-style: bold; }
#ctxbar, #keys, #status { color: $text-muted; }
#footer { background: $panel; }
#remedy { color: $warning; }
MessageArea.busy { color: $text-muted; }
TranscriptView .history { color: $text-muted; }
TranscriptView .line:focus { background: $boost; }
TranscriptView .line.stale { color: $text-disabled; text-style: italic; }
Overlay > #box { border: heavy $accent; background: $surface; }
#overlay-keys { color: $text-muted; }
.help { color: $text-disabled; }
.field { text-style: bold; }
Overlay Input, Overlay SelectCurrent { border: solid $border-blurred; background: $boost; }
Overlay Input:focus, Overlay Select:focus SelectCurrent { border: solid $accent; }
Overlay ListInput > .list-line { border: solid $border-blurred; background: $boost; }
Overlay ListInput Input, Overlay ListInput Input:focus { border: none; background: transparent; }
Overlay ListInput > .list-line:focus-within { border: solid $accent; }
Overlay PackagesLine { border: solid $border-blurred; background: $boost; }
Overlay PackagesLine:focus { border: solid $accent; }
ListInput .arrow { color: $foreground 50%; }
ListInput > ListOptions { border: solid $border-blurred; background: $surface; }
MessageArea { border: solid $border-blurred; }
MessageArea:focus { border: solid $accent; }
Tooltip { display: none; }
ConversationView > #paused { background: $warning 15%; color: $warning; text-style: bold; }
ConversationView > #bubble { background: $boost; }
ConversationView MessageArea.paused { border: solid $warning; }
"""

DARK = "textual-dark"     # the theme the post opens in when none was chosen
HOUSE = "."               # the house itself, addressed as an agent

# glyphs
LOGICAL, PHYSICAL = "◇", "●"
YES, NO, WARNING, EDIT, NONE = "✓", "✗", "⚠", "✎", "—"
PENDING = "…"              # never read once: the reading is on its way
SEP = " · "
SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"     # a turn under way: one glyph per frame, around
PAUSED = "⏸"               # a conversation whose exchanges are not conducted
STOP = "■ stop"            # the button that stops the turn under way
WAITS = "⧗"                # a switch of a package sent and not played yet
FULL, EMPTY = "▰", "▱"     # the cells of the budget's gauge
GAUGE_CELLS = 10
WARN_SHARE = 0.8           # the budget's gauge turns yellow past this share of its cap
CONTEXT_PP = "$accent"     # pp's part of a run's context, on its gauge
CONTEXT_REST = "$primary"  # the rest of the context the run uses


def spinner(frame: int) -> str:
    """-> the glyph of a turn under way at that frame."""
    return SPINNER[frame % len(SPINNER)]


def ok(s: object) -> Text: return Text(str(s), style=GREEN)
def warn(s: object) -> Text: return Text(str(s), style=f"bold {YELLOW}")
def bad(s: object) -> Text: return Text(str(s), style=RED)
def dim(s: object) -> Text: return Text(str(s), style=DIM)
def cyan(s: object) -> Text: return Text(str(s), style=CYAN)
def strong(s: object) -> Text: return Text(str(s), style=BOLD)


def seconds_since(iso: str) -> float | None:
    """-> the seconds since an instant the flow dated (ISO 8601), None when it does not parse."""
    try:
        moment = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        return None
    if moment.tzinfo is None:
        moment = moment.astimezone()
    return max(0.0, (datetime.now(moment.tzinfo) - moment).total_seconds())


def duration(seconds: object) -> str:
    """-> a duration read by a person: `12.3 s` under a minute, `5 min 03 s`, `1 h 02 min 05 s`; `—` for what is
    no number."""
    if not isinstance(seconds, (int, float)):
        return NONE
    if seconds < 60:
        return f"{float(seconds):.1f} s"
    whole = int(round(seconds))
    hours, rest = divmod(whole, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours} h {minutes:02d} min {secs:02d} s" if hours else f"{minutes} min {secs:02d} s"


def turn_time(seconds: float | None) -> str:
    """-> how long a turn has run: `12 s` under a minute, then as `duration` says it; '' when unknown."""
    if seconds is None:
        return ""
    return f"{int(seconds)} s" if seconds < 60 else duration(seconds)


def turning(frame: int, seconds: float | None) -> Content:
    """-> the glyph of a turn under way, bold in the theme's accent, then how long the turn has run."""
    elapsed = turn_time(seconds)
    return Content.assemble((spinner(frame), TURNING), (f" {elapsed}" if elapsed else "", TURNING))


READING = "reading"     # the word of the status while faces are read


def versions_of(engine: object, post: object) -> str:
    """-> what the header says of the versions, `engine 0.2.0 · ui 0.51.0`; '' when the face said neither."""
    said = [f"{name} {value}" for name, value in (("engine", engine), ("ui", post)) if value]
    return SEP.join(said)


def reading(frame: int, under_way: list[tuple[str, ...]]) -> Content:
    """-> the glyph of a reading under way, bold in the theme's accent, then what is read: each verb once, how many
    of it beside (`reading agent status ×4 · agent list`)."""
    counted: dict[str, int] = {}
    for one in under_way:
        counted[" ".join(one)] = counted.get(" ".join(one), 0) + 1
    said = SEP.join(f"{verb} ×{n}" if n > 1 else verb for verb, n in counted.items())
    return Content.assemble((spinner(frame), TURNING), (f" {READING} {said}", TURNING))


def budget_gauge(budget: object) -> Content | None:
    """-> the budget of a run as its status says it: `budget 0.42/2.00 USD` and a bar of ten cells, coloured by its
    state -- green, yellow past 80 % of the cap, bold red at the cap; None when the flow said no cap (`budget`
    null or absent: `—` stands in its place)."""
    if not isinstance(budget, dict) or not isinstance(budget.get("cap"), (int, float)) or budget["cap"] <= 0:
        return None
    cap, spent = float(budget["cap"]), float(budget.get("spent") or 0.0)
    share = spent / cap
    filled = min(GAUGE_CELLS, max(0, int(share * GAUGE_CELLS + 0.5)))
    style = RED_CONTENT if share >= 1 else YELLOW if share > WARN_SHARE else GREEN
    return Content.assemble((f"budget {spent:.2f}/{cap:.2f} USD {FULL * filled}{EMPTY * (GAUGE_CELLS - filled)}", style))


def percent(part: object) -> str:
    """A part of a whole as a percentage: `17%`, `0.7%` under ten; `—` for what is no number."""
    if not isinstance(part, (int, float)):
        return NONE
    value = part * 100
    return f"{value:.1f}%" if value < 10 else f"{value:.0f}%"


def context_gauge(context: object) -> Content:
    """The context of a run beside its message line, as `context` of `agent stats --json` says it: `ctx`, a bar of
    ten cells -- the part of the model's window the run uses, pp's share of it in the accent and the rest in the
    primary colour, the empty cells dim -- then `17% · pp 33%`; without a window, `ctx ~8.3k · pp ~33%` and no bar;
    without `context`, `ctx —`."""
    if not isinstance(context, dict):
        return Content(f"ctx {NONE}")
    pp = context.get("pp") if isinstance(context.get("pp"), dict) else {}
    share, used = pp.get("share"), context.get("used")
    if not isinstance(used, (int, float)):
        total = (context.get("flow") or {}).get("total") if isinstance(context.get("flow"), dict) else None
        return Content(f"ctx ~{tokens_of(total)}{SEP}pp {share_of(share)}")
    filled = min(GAUGE_CELLS, max(0, round(used * GAUGE_CELLS)))
    ours = min(filled, max(0, round(filled * share))) if isinstance(share, (int, float)) else 0
    return Content.assemble("ctx ", (FULL * ours, CONTEXT_PP), (FULL * (filled - ours), CONTEXT_REST),
                            (EMPTY * (GAUGE_CELLS - filled), DIM), f" {percent(used)}{SEP}pp {percent(share)}")


def hhmmss(moment: datetime | None = None) -> str:
    """The HOUR of a reading, HH:MM:SS -- the post's one clock, on its status line."""
    return (moment or datetime.now()).strftime("%H:%M:%S")


FRESH = 5                  # under this many seconds an age says `now`


def age_of(iso: object) -> str:
    """The AGE of an instant a face gave, against the post's clock at the rendering, in coarse units: `now` under
    5 s, `12 s`, `3 min`, `2 h`, `3 d`; `—` for an instant absent or that does not parse. A freshness reads as a
    duration; the hour of an event stays `hour_of`."""
    seconds = seconds_since(str(iso)) if iso else None
    if seconds is None:
        return NONE
    if seconds < FRESH:
        return "now"
    if seconds < 60:
        return f"{int(seconds)} s"
    if seconds < 3600:
        return f"{int(seconds // 60)} min"
    if seconds < 86400:
        return f"{int(seconds // 3600)} h"
    return f"{int(seconds // 86400)} d"


def read_said(read: datetime | None) -> str:
    """How long ago a reading was made: `read now`, `read 12 s ago`; `…` before any."""
    if read is None:
        return PENDING
    age = age_of(read.isoformat())
    return "read now" if age == "now" else f"read {age} ago"


def stamped(cell: Text, at: str | None) -> Text:
    """A state and the hour of ITS reading, dim: the cell stays terse."""
    return Text.assemble(cell, (f" {at}", DIM)) if at else cell


def hour_of(iso: str) -> str:
    """The HOUR of an event the flow dated (ISO 8601 UTC), in local time; the raw text's
    own clock when it does not parse."""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone().strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return iso[11:19] if len(iso) >= 19 else ""


def moment_of(iso: str) -> str:
    """The MOMENT of a datum that may be of another day, in local time: its hour alone today
    (`18:17:28`), `DD/MM HH:MM` another day, `DD/MM/YYYY HH:MM` another year; the raw text's own
    clock when it does not parse."""
    try:
        moment = datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone()
    except (ValueError, TypeError):
        return iso[11:19] if len(iso) >= 19 else ""
    today = datetime.now().astimezone()
    if moment.date() == today.date():
        return moment.strftime("%H:%M:%S")
    return moment.strftime("%d/%m %H:%M" if moment.year == today.year else "%d/%m/%Y %H:%M")


# the voices of a conversation -- a glyph each, the hour of the event in dim, the voice's
# weight: the principal and the agent in clear, the conduction and the steps dim
PRINCIPAL, AGENT, TRACE, CONDUCTION = "▶", "◀", "·", LOGICAL
CALL, THOUGHT = "⚙", "∴"   # what the agent does during a launch: a call of a tool, its thought


def principal_head(at: str) -> Text:
    """The head of the principal's block: the glyph, the hour; the message renders under it."""
    return Text.assemble((f"{PRINCIPAL} ", BOLD), (hour_of(at), DIM))


def bubble_line(at: str, text: str, history: int | None = None) -> Text:
    """The bubble of a conversation's tab: the principal's glyph, bold, the hour of the turn -- `history #n` and its
    moment for a turn of history -- dim, then the first line of the message, cut at the width."""
    first = next((one.strip() for one in plain(text).splitlines() if one.strip()), "")
    when = f"history #{history}  {moment_of(at)}" if history is not None else hour_of(at)
    return one_line((f"{PRINCIPAL} ", BOLD), (when, DIM), (f"  {first}", ""))


def words_head(at: str, launch: object) -> Text:
    """The head of the agent's words at a launch: the glyph, the hour, the launch; the words render under it."""
    return Text.assemble((f"{AGENT} ", BOLD), (hour_of(at), DIM), (f"{SEP}launch {launch if launch is not None else '?'}", DIM))


def response_head(at: str) -> Text:
    """The head of a turn's answer: the glyph, the hour; the answer kept renders under it."""
    return Text.assemble((f"{AGENT} ", BOLD), (hour_of(at), DIM), (f"{SEP}the answer", DIM))


def size_of(chars: object) -> str:
    """A length in characters, short: `812 chars`, `12.3k chars`."""
    if not isinstance(chars, int):
        return ""
    return f"{chars} chars" if chars < 1000 else f"{chars / 1000:.1f}k chars"


def bytes_of(size: object) -> str:
    """A size in bytes, short: `812 B`, `12.3 kB`, `3.1 MB`, `1.2 GB`; `—` for what is no number."""
    if not isinstance(size, (int, float)):
        return NONE
    for bound, unit in ((1_000_000_000, "GB"), (1_000_000, "MB"), (1_000, "kB")):
        if size >= bound:
            return f"{size / bound:.1f} {unit}"
    return f"{int(size)} B"


def weight_cell(weight: object) -> str:
    """The `weight` cell of a run or an agent: the bytes the engine keeps of it and those of its flow, as one size;
    `—` without a weight."""
    if not isinstance(weight, dict):
        return NONE
    return bytes_of(int(weight.get("bytes") or 0) + int(weight.get("flow") or 0))


def purge_text(found: dict) -> Text:
    """What a purge would remove, as the verb said it without `--yes`: per run its lines by record, its files and
    their bytes, its flow, its clone; then the total."""
    said = Text()
    runs = [one for one in found.get("runs") or [] if isinstance(one, dict)]
    for one in runs:
        lines = ", ".join(f"{str(name).rsplit('.', 1)[0]} {n}" for name, n in (one.get("lines") or {}).items() if n)
        said.append(f"run {one.get('key')}", style=BOLD)
        said.append(f"{SEP}lines {lines or NONE}{SEP}{len(one.get('files') or [])} file(s), "
                    f"{bytes_of(int(one.get('bytes') or 0))}"
                    + (f"{SEP}flow {bytes_of(one['flow'])}" if isinstance(one.get("flow"), (int, float)) else "")
                    + (f"{SEP}material {one['workdir']}" if one.get("workdir") else "") + "\n")
    if not runs:
        said.append(f"{NONE}  no run to remove\n", style=DIM)
    said.append(f"total{SEP}{found.get('lines', 0)} line(s){SEP}{found.get('files', 0)} file(s){SEP}"
                f"{bytes_of(found.get('bytes') or 0)}", style=DIM)
    return said


BEFORE_HELP = "YYYY-MM-DD -- every run whose newest line and newest trace are older than the date"


def stale(summary: Text) -> Text:
    """-> a line with nothing to open: its words alone, on one line, the look left to the `STALE` class."""
    return one_line((summary.plain, ""))


def one_line(*parts: tuple[str, str]) -> Text:
    """A line of the transcript: never wrapped, cut at the width with an ellipsis."""
    said = Text.assemble(*parts)
    said.no_wrap, said.overflow = True, "ellipsis"
    return said


def conduction_line(at: str, fields: dict) -> Text:
    """A `conduction` on one dim line: its launch, the block it asks the agent to act on (the last
    the trace wrote, `+n` for the others, `parked` on a waiting one), its size, what is still to
    come of a cut output -- read from the flow's fields alone."""
    blocks = [one for one in fields.get("blocks") or [] if isinstance(one, dict)]
    said = f"{SEP}launch {fields.get('launch', '?')}"
    if blocks:
        said += f"{SEP}{blocks[-1].get('stack', '')}" + (f" +{len(blocks) - 1}" if len(blocks) > 1 else "")
        said += f"{SEP}parked" if blocks[-1].get("wait") else ""
    if size_of(fields.get("chars")):
        said += f"{SEP}{size_of(fields.get('chars'))}"
    if isinstance(fields.get("left"), int):
        said += f"{SEP}{fields['left']} chars left"
    return one_line((f"{CONDUCTION} ", DIM), (hour_of(at), DIM), (said, DIM))


SELECTOR = "\ufe0f"         # the emoji presentation selector: a terminal draws its emoji on one column, Rich counts two
PAUSED_BANNER = f"{PAUSED} pp OFF -- the exchanges are not conducted: the agent answers bare · [o] brings pp back"
PAUSED_LINE = "pp off -- the message goes to the agent bare"
READ_ONLY = "◉"            # a run of a member of a team, read: nothing is sent to it


def read_only_banner(member: str, team: str) -> str:
    """The head of a tab that reads the run of a member of a team."""
    return f"{READ_ONLY} read only -- the run of {member} in team {team}: its wake-ups are the team's"


def plain(text: str) -> str:
    """-> the text without `U+FE0F`: an emoji \"text by default\" keeps its text form, one column, as the
    terminal draws it -- the tables of a markdown answer stay aligned; nothing else is touched."""
    return text.replace(SELECTOR, "")


class _Rule(HorizontalRule):
    """The rule of a markdown text: one full line, as Textual's markdown draws it."""

    def __rich_console__(self, console, options):
        yield Rule(style="markdown.hr", characters="─")


class _Heading(Heading):
    """A heading of a markdown text on the left, as Textual's markdown draws it -- Rich centres it."""

    def __rich_console__(self, console, options):
        text = self.text.copy()
        text.justify = "left"
        if self.tag == "h2":
            yield Text("")
        yield Text.assemble(text, style=f"markdown.{self.tag}")


class _Table(TableElement):
    """A table of a markdown text: boxed and spread over the width, as Textual's markdown draws it."""

    def __rich_console__(self, console, options):
        table = Table(box=box.SQUARE, expand=True, border_style="markdown.table.border",
                      header_style="markdown.table.header", pad_edge=False)
        if self.header is not None and self.header.row is not None:
            for column in self.header.row.cells:
                table.add_column(column.content)
        if self.body is not None:
            for row in self.body.rows:
                table.add_row(*(cell.content for cell in row.cells))
        yield table


class _Markdown(Markdown):
    elements = {**Markdown.elements, "hr": _Rule, "heading_open": _Heading, "table_open": _Table}


def _tone(raw: object) -> str | None:
    """-> a colour of the theme as Rich spells it: `#rrggbb`, the name of an ANSI colour for an `ansi_*` theme, None
    for what draws nothing of its own (`transparent`) or does not parse (`auto 60%`)."""
    said = str(raw or "").split()
    if not said or said[0] == "transparent":
        return None
    if said[0].startswith("ansi_"):
        return said[0][len("ansi_"):]
    try:
        return Color.parse(said[0]).hex6
    except Exception:
        return None


def markdown_look(variables: dict[str, str], dark: bool) -> tuple[Theme, str]:
    """-> the look of a markdown text in the theme whose CSS variables are given: the Rich styles of its elements,
    drawn in the theme's accent, primary, foreground and panel -- what is muted, the foreground half way to the
    background, else `dim` --, and the colouring of its code, light or dark as the theme is."""
    accent, primary = _tone(variables.get("accent")), _tone(variables.get("primary"))
    fore, panel = _tone(variables.get("foreground")), _tone(variables.get("panel"))
    back = _tone(variables.get("background"))
    muted = DIM
    if fore and back and fore.startswith("#") and back.startswith("#"):
        muted = Color.parse(fore).blend(Color.parse(back), 0.4).hex6

    def style(*parts: str | None) -> str:
        return " ".join(one for one in parts if one) or "none"
    on_panel = f"on {panel}" if panel else None
    styles = {"markdown.h1": style(BOLD, primary), "markdown.h2": style(BOLD, primary), "markdown.h3": style(BOLD, fore),
              "markdown.h4": style(BOLD, fore), "markdown.h5": style(BOLD, fore), "markdown.h6": style("italic", fore),
              "markdown.code": style(accent, on_panel), "markdown.code_block": style(on_panel),
              "markdown.hr": muted, "markdown.link": style(accent, "underline"), "markdown.link_url": muted,
              "markdown.item.bullet": style(BOLD, accent), "markdown.item.number": style(BOLD, accent),
              "markdown.block_quote": muted, "markdown.table.border": muted, "markdown.table.header": style(BOLD, fore)}
    return Theme(styles), ("monokai" if dark else "default")


def markdown_text(source: str, width: int, look: tuple[Theme, str]) -> Text:
    """-> a markdown text drawn by Rich at that width in that look, as ONE styled text: its rows joined, the spaces
    that pad a row taken off its end -- what a selection copies is the text; no `U+FE0F` (`plain`)."""
    width = max(width, 20)
    theme, code = look
    console = Console(width=width, color_system="truecolor", force_terminal=True, theme=theme)
    lines = console.render_lines(_Markdown(plain(source), code_theme=code), console.options.update_width(width),
                                 pad=False)
    drawn = Text()
    for at, line in enumerate(lines):
        row = Text()
        for segment in line:
            row.append(segment.text, segment.style)
        row.rstrip()
        drawn.append_text(row)
        if at < len(lines) - 1:
            drawn.append("\n")
    return drawn


def plain_text(text: Text) -> Text:
    """-> the `Text` without `U+FE0F`, as `plain` does, each style kept on the characters it covered."""
    cut = [at for at, char in enumerate(text.plain) if char == SELECTOR]
    if not cut:
        return text

    def shift(at: int) -> int:
        return at - bisect_left(cut, at)              # the selectors before `at` taken out
    said = text.copy()
    said.plain = plain(text.plain)
    said.spans = [Span(shift(span.start), shift(span.end), span.style) for span in text.spans
                  if shift(span.end) > shift(span.start)]
    return said


def agent_line(at: str, fields: dict) -> Text:
    """The end of a launch on one line: its launch and its cost -- the words it said are blocks of their own."""
    cost = fields.get("cost_usd")
    head = f"{SEP}launch {fields.get('launch', '?')}" + \
        (f"{SEP}{float(cost):.2f} USD" if isinstance(cost, (int, float)) else "")
    return one_line((f"{AGENT} ", BOLD), (hour_of(at), DIM), (head, DIM))


def tool_line(at: str, fields: dict, result: dict | None) -> Text:
    """A call of a tool on one line: its launch, `pp` when it calls the agent's console (else the tool's
    name), its title, then its issue once its result came -- `✓` (green) or `✗` and the size of the result,
    `…` before; the whole line red on an error. Read from the flow's fields alone."""
    name = "pp" if fields.get("pp") is True else str(fields.get("name") or "?")
    title = " ".join(plain(str(fields.get("title") or "")).split())
    head = f"{SEP}launch {fields.get('launch', '?')}{SEP}{name}" + (f"{SEP}{title}" if title else "") + SEP
    if result is None:
        return one_line((f"{CALL} ", DIM), (hour_of(at), DIM), (head, DIM), (PENDING, DIM))
    size = f"{SEP}{size_of(len(str(result.get('content') or '')))}"
    if result.get("error") is True:
        return one_line((f"{CALL} {hour_of(at)}{head}{NO}{size}", RED))
    return one_line((f"{CALL} ", DIM), (hour_of(at), DIM), (head, DIM), (YES, GREEN), (size, DIM))


def result_line(at: str, fields: dict) -> Text:
    """The result of a call the flow never announced, on its own line: its launch, its issue, its size."""
    size = f"{SEP}{size_of(len(str(fields.get('content') or '')))}"
    head = f"{SEP}launch {fields.get('launch', '?')}{SEP}result{SEP}"
    if fields.get("error") is True:
        return one_line((f"{CALL} {hour_of(at)}{head}{NO}{size}", RED))
    return one_line((f"{CALL} ", DIM), (hour_of(at), DIM), (head, DIM), (YES, GREEN), (size, DIM))


def call_whole(fields: dict, result: dict | None) -> Text:
    """A call opened whole: its input as indented JSON, then its result as the model read it -- red on an
    error, `…` while it has not come."""
    import json
    said = Text.assemble(("input\n", BOLD), (json.dumps(fields.get("input") or {}, indent=2, ensure_ascii=False), ""),
                         ("\n\nresult\n", BOLD))
    if result is None:
        said.append(PENDING, style=DIM)
    else:
        said.append(str(result.get("content") or ""), style=RED if result.get("error") is True else "")
    return said


def thinking_line(at: str, launch: object, tokens: object, text: str) -> Text:
    """The thought of a launch on one dim line: the last count the flow gave, else the start of its text."""
    said = f"{SEP}launch {launch if launch is not None else '?'}{SEP}thinking"
    if isinstance(tokens, int):
        said += f" ~{tokens} tokens"
    elif text:
        said += f"{SEP}{' '.join(plain(text).split())}"
    return one_line((f"{THOUGHT} ", DIM), (hour_of(at), DIM), (said, DIM))


def steps_line(steps: list) -> Text:
    """The steps of a launch on one line: their count and their kinds counted, in the order they
    first came; a refusal makes it a problem (bold yellow), a repair a state to watch (yellow)."""
    kinds: dict[str, int] = {}
    for one in steps:
        kind = str(one.fields.get("event", ""))
        kinds[kind] = kinds.get(kind, 0) + 1
    hour = hour_of(steps[-1].at) if steps else ""
    said = f"{TRACE} {hour}{SEP}{len(steps)} step(s)" + "".join(f"{SEP}{kind} ×{n}" for kind, n in kinds.items())
    style = f"bold {YELLOW}" if "refusal" in kinds else YELLOW if "repair" in kinds else DIM
    return one_line((said, style))


def step_line(at: str, event: str, fields: dict) -> Text:
    """A step of the run on one dim line; a refusal is a problem (bold yellow), a repair
    a state to watch (yellow)."""
    detail = " ".join(f"{key}={value}" for key, value in fields.items() if key not in ("event",))
    said = f"{TRACE} {hour_of(at)}  {event}" + (f"  {detail}" if detail else "")
    if event == "refusal":
        return Text(said, style=f"bold {YELLOW}")
    if event == "repair":
        return Text(said, style=YELLOW)
    return Text(said, style=DIM)


def verdict_line(at: str, state: str, cost: object, launches: object, reason: object) -> Text:
    """The verdict of an exchange: the state coloured as the palette says, the cost and the
    launches dim, the reason when the exchange did not end well."""
    tail = (f"  {float(cost):.2f} USD" if isinstance(cost, (int, float)) else "") + \
           (f" · {launches} launch(es)" if launches is not None else "")
    if state in ("parked", "unconducted"):
        head = (f"{YES} {state}", GREEN)
    elif state in ("interrupted", "standing"):
        head = (f"{WARNING} {state}", f"bold {YELLOW}")
    else:
        head = (f"{NO} {state or '?'}", RED)
    said = Text.assemble((f"{hour_of(at)}  ", DIM), head, (tail, DIM))
    if reason:
        said.append(f"  {reason}", style=RED if state not in ("interrupted",) else f"bold {YELLOW}")
    return said


def conduct_line(at: str, on: bool) -> Text:
    """What the house says after a `conduct`: whether the next exchanges are conducted, dim."""
    return Text(f"{TRACE} {hour_of(at)}  pp {'on' if on else 'off'}", style=DIM)


def package_line(at: str, name: str, on: bool) -> Text:
    """What the house says after a `package`: the package in or out of the run's play, dim."""
    return Text(f"{TRACE} {hour_of(at)}  {name} {'on' if on else 'off'}", style=DIM)


def house_line(at: str, kind: str, fields: dict) -> Text:
    """What the house itself says (opened, refused, a kind nobody knows): dim, the fields flat."""
    detail = " ".join(f"{key}={value}" for key, value in fields.items())
    return Text(f"{TRACE} {hour_of(at)}  {kind}" + (f"  {detail}" if detail else ""), style=DIM)


def tab_label(label: str, unread: int, busy: bool = False, frame: int = 0, paused: bool = False,
              waits: bool = False, seconds: float | None = None) -> Content:
    """The title of a conversation's tab: the glyph of the frame while a turn is under way and how long it has run,
    in the accent, its label, `⏸` while its exchanges are not conducted, `⧗` while a switch of a package waits, then
    -- on a tab of the background that spoke -- the count of what the operator has not read, bold (a thing to look
    at)."""
    return Content.assemble(*((turning(frame, seconds), " ") if busy else ()), label,
                            f" {PAUSED}" if paused else "", f" {WAITS}" if waits else "",
                            (f" {unread}", BOLD) if unread else "")


def state_word(on: bool) -> str:
    return "on" if on else "off"


def waiting_line(pending: dict[str, bool]) -> str:
    """The switches waiting, as the status says them: `packages: steering off …`; '' when none."""
    return ("packages: " + ", ".join(f"{name} {state_word(on)}" for name, on in pending.items()) + f" {PENDING}"
            if pending else "")


def package_row(name: str, base: bool, staged: bool, waits: bool, required: bool = False) -> str:
    """A line of the overlay of the packages: the package and its state for the run -- `on → off` once
    toggled in the overlay, `off … pending` while a switch sent waits, `on · required` for a package the
    caller holds."""
    if required:
        return f"{name}  {state_word(base)} · required"
    if staged != base:
        return f"{name}  {state_word(base)} → {state_word(staged)}"
    return f"{name}  {state_word(base)}" + (f" {PENDING} pending" if waits else "")


PACKAGES_HELP = "for this run only -- a switch the run holds waits for the next launch"
REQUIRED_HELP = "a package marked required is held by what launches the run: it does not toggle"


def packages_help(required: bool) -> str:
    """The help under the packages of a run: what a switch does, and why a line marked required stays."""
    return PACKAGES_HELP + (f" · {REQUIRED_HELP}" if required else "")


def packages_line(base: dict[str, bool], staged: dict[str, bool], required: frozenset[str] = frozenset()) -> str:
    """The line `packages` of a profile: each package beyond the base with its state for the run, `on → off` for a
    line changed in their overlay, `(required)` for a package the caller holds."""
    if not base:
        return f"{NONE}  no package beyond the base"
    said = []
    for name, on in base.items():
        if name in required:
            said.append(f"{name} {state_word(on)} (required)")
        elif name in staged and staged[name] != on:
            said.append(f"{name} {state_word(on)} → {state_word(staged[name])}")
        else:
            said.append(f"{name} {state_word(on)}")
    return " · ".join(said)


PACKAGES_LINE_HELP = "the packages the run plays beyond its base -- enter opens them; a line changed goes with the profile"


def empty_dialogue() -> Text:
    """What the dialogue says with no conversation open: where to open one -- to come, so dim."""
    return Text.assemble((NONE, DIM), ("  no conversation open: `2` lists the agents -- `enter` shows the runs of "
                                       "one, `n` opens a conversation with it; or name an agent to talk to: "
                                       "./pp ui <agent path> [<agent path> …] [--run <key>]", DIM))


def agents_text(agents: int) -> Text:
    """What the Agents tab says under its table: the gestures of a line, or how an agent is born."""
    if agents:
        return Text("enter shows the agent's runs · n opens a conversation with it · u reads again", style=DIM)
    return Text.assemble((NONE, DIM), ("  no agent in this house yet: `./pp agent add <path>` gives birth to one",
                                       DIM))


def cap_note(agent: str, cap: object) -> str:
    """-> the remedy line's warning when the run's outputs are cut under more than the agent's
    `max_harness_tool_output` (`opened.cap`: the floor of a principal's cap raised it); '' otherwise."""
    if not isinstance(cap, dict):
        return ""
    found, served = cap.get("set"), cap.get("applied")
    if not isinstance(found, int) or not isinstance(served, int) or served <= found:
        return ""
    return f"{agent}: cap {found} lifted to {served} for this run"


def ended_line(rc: object, stderr: str) -> Text:
    """The end of a conversation's flow in its transcript: the exit code, what the verb said first."""
    said = next((one.strip() for one in str(stderr).splitlines() if one.strip()), "")
    return Text(f"{NO} ended rc {rc}" + (f" -- {said}" if said else ""), style=RED)


def cell_of(value: object, money: bool = False) -> str:
    """A cell of a table: `—` for what is absent, a cost with two decimals."""
    if value is None or value == "":
        return NONE
    if money and isinstance(value, (int, float)):
        return f"{float(value):.2f}"
    return str(value)


def history_head(turn, voice: str) -> Text:
    """A head of a turn of HISTORY (a past exchange `agent exchanges` gave), dim: the principal's
    carries the message on its line, the agent's the cost and the launches of the turn -- the answer
    kept renders under it; never a block of the live flow."""
    head = f"{TRACE} history #{turn.exchange}  {moment_of(turn.at)}  {voice}"
    if voice == PRINCIPAL:
        return Text(f"{head} {plain(turn.message)}", style=DIM)
    tail = (f"  {turn.cost_usd:.2f} USD" if isinstance(turn.cost_usd, (int, float)) else "") + \
           (f"{SEP}{turn.played} launch(es)" if turn.played is not None else "") + \
           (f"{SEP}{turn.error}" if turn.error else "")
    return Text(f"{head}{tail}", style=DIM)


def tokens_of(tokens: object) -> str:
    """A count of tokens at a glance: `850`, `6.8k`, `170k`, `3.6M`; `—` for what is absent."""
    if not isinstance(tokens, (int, float)):
        return NONE
    for bound, unit in ((1_000_000, "M"), (1_000, "k")):
        if tokens >= bound:
            return f"{tokens / bound:.1f}".removesuffix(".0") + unit
    return str(int(tokens))


def share_of(part: object) -> str:
    """A part of a whole as the post says it -- APPROACHED, the harness's own base left out: `~33%`,
    `~0.7%` under ten; `—` for what is absent."""
    if not isinstance(part, (int, float)):
        return NONE
    percent = part * 100
    return f"~{percent:.1f}%" if percent < 10 else f"~{percent:.0f}%"


def context_cell(context: dict | None) -> str:
    """The `ctx` cell of a run: the part of its model's window the flow fills, else its size in
    tokens; `—` without a flow."""
    if not context:
        return NONE
    return share_of(context.get("used")) if context.get("used") is not None else f"~{tokens_of(context.get('tokens'))}"


def stats_text(line, data: dict) -> Text:
    """The statistics of a run, as the overlay shows them, each section reading its one key of the
    face `agent stats` gives: `run` the sums, `pp` the detail of the conduction as the engine's
    `-stats` says it, `ctx` the context the flow approaches and pp's share of it -- a figure per line."""
    conduction = data.get("conduction") or {}
    said = Text()
    said.append(f"{line.label}\n", style=BOLD)
    said.append(f"run {line.run} · {line.state}" + (f" · session {line.session}" if line.session else "") + "\n", style=DIM)
    said.append("\nrun\n", style=BOLD)
    for label, value in (("exchanges", data.get("exchanges")), ("launches", data.get("launches")),
                         ("cost", cell_of(data.get("cost_usd"), money=True) + " USD")):
        said.append(f"{label:<12}{cell_of(value)}\n")
    said.append("\npp\n", style=BOLD)
    for key in ("exchanges", "blocks", "chunks", "proofs", "repairs", "refusals", "gestures", "mass", "tokens"):
        said.append(f"{key:<12}{cell_of(conduction.get(key))}\n")
    spent = conduction.get("spent") or {}
    if spent:
        said.append("spent       " + " · ".join(f"{part} {duration(value)}" for part, value in spent.items()) + "\n")
    said.append("\nctx\n", style=BOLD)
    context = data.get("context")
    if not isinstance(context, dict):
        said.append("no flow counted for this run\n", style=DIM)
    else:
        flow, pp = context.get("flow") or {}, context.get("pp") or {}
        window = context.get("window")
        said.append("context     " + (f"{share_of(context.get('used'))} of {tokens_of(window)} tokens" if window
                                      else f"~{tokens_of(flow.get('total'))} tokens") + "\n")
        said.append(f"pp          {share_of(pp.get('share'))} of the flow · ~{tokens_of(pp.get('tokens'))}"
                    f" · served ~{tokens_of(pp.get('served'))}\n")
        for voice, value in flow.items():
            if voice != "total":
                said.append(f"{voice:<12}~{tokens_of(value)}\n", style=DIM)
        for label, value in (("calls", cell_of(context.get("calls"))), ("reread", f"~{tokens_of(context.get('reread'))}"),
                             ("since", cell_of(context.get("since")))):
            said.append(f"{label:<12}{value}\n")
        said.append("approached from the flow, the harness's own base left out\n", style=DIM)
    said.append("\nescape closes", style=DIM)
    return said


def params_help(field: str, items: list[str], running: bool = False) -> str:
    """The help under a field of the run's parameters: what it takes, what the faces offer for it --
    the providers wired, the models the adapter names, what the provider spells -- and `[down]` where
    the field lists the names it knows."""
    if field == "provider":
        if running:
            return "fixed for the run: chosen at its opening"
        if not items:
            return "the house is wired with no provider: the flags after `--` name the harness"
        return f"the providers the house is wired with: {', '.join(items)}" + \
            (" -- left blank, the house's one provider, or provider-ambiguous" if len(items) > 1 else "")
    if field == "name":
        return "the run's name, one line of 1 to 60 printable characters -- played by `agent name` once the run is " \
            "opened; left blank, nothing is played"
    if field == "model":
        if items:
            return f"free; the adapter names {', '.join(items)} -- any other name goes as given · [down] lists them"
        return "free -- the adapter names no model verified yet; the name goes as given"
    spelled = "max_budget_usd" if field == "budget" else "effort"
    unspelled = items and spelled not in items
    said = "USD, above 0" if field == "budget" else "one of low, medium, high, xhigh, max · [down] lists them"
    return said + (" -- this provider does not spell it: policy-unsupported at the launch" if unspelled else "")


def agent_label(agent: str, house: str) -> str:
    """-> how the post names an agent: its path; the house itself (`.`) by its folder, `(house)`."""
    return f"{Path(house).name or house} (house)" if agent == HOUSE else agent


def permissions_help(value: object, spells: list[str]) -> Text:
    """The help under the permission regime: what each word lets the agent do -- `bypass` said as a
    warning, every check skipped; a provider that spells no regime says so."""
    if spells and "permissions" not in spells:
        return Text("this provider spells no regime: auto alone, any other refuses policy-unsupported")
    if value == "bypass":
        return bad("bypass: every check skipped -- the agent may do anything, `push --force` and `rm` included")
    return Text("auto: the harness's own judgment · strict: the house's settings alone, anything else denied · "
                "bypass: every check skipped")


MARKDOWN_KINDS = ("agent", "words")   # the events an overlay renders as markdown: what the agent wrote

EVENT_KINDS = {"tool": "tool call", "tool-result": "tool result", "thinking": "thinking", "words": "words",
               "agent": "agent answer", "conduction": "conduction", "step": "steps"}   # the label of an event's kind


def event_label(kind: str, fields: dict | None = None) -> str:
    """-> the label of an event's kind, read from its `kind` alone: `tool call · <name>` for a call -- the
    `name` of the flow as it is, never translated --, the kind itself for a kind nobody knows."""
    label = EVENT_KINDS.get(kind, kind)
    name = (fields or {}).get("name")
    return f"{label} · {name}" if kind == "tool" and name else label


def event_title(label: str, summary: Text) -> Text:
    """-> the title of an event's overlay, on one line: the label in bold, then the line's summary."""
    return Text.assemble((label, BOLD), SEP, summary)


def typed_help(name: str) -> str:
    """The help of a gesture that destroys: the name its target must be typed with before it plays."""
    return f"this cannot be taken back -- type {name} to play it"


def keys_line(pairs: list[tuple[str, str]]) -> str:
    """The keys of an overlay on one line: `[key] label` joined -- keys and labels alone."""
    return SEP.join(f"[{key}] {label}" for key, label in pairs)


def keys_lines(pairs: list[tuple[str, str]], width: int) -> str:
    """The footer's keys, `[key] label` joined, on as many lines of `width` as they need: a line breaks between
    two keys, never inside one; a key wider than the line stands alone on its own. A key ending in `:` with no
    label names the group of the keys after it (`team:`, `member:`)."""
    lines: list[str] = []
    for one in (key if key.endswith(":") and not label else f"[{key}] {label}" for key, label in pairs):
        if lines and len(lines[-1]) + len(SEP) + len(one) <= width:
            lines[-1] += SEP + one
        else:
            lines.append(one)
    return "\n".join(lines)


# ---------- the Teams tab: what `team status --json` says, shown -- never a state computed here ----------
TASK_STYLES = {"open": GREEN, "stopped": f"bold {YELLOW}", "resolved": DIM}
HOW_STYLES = {"running": CYAN, "ended": GREEN, "dead": RED, "killed": RED, "reset": DIM}


def section_title(name: str, read: datetime | None = None, dated: bool = False) -> Text:
    """The title of a table of the two tabs: its name; the menu's says how long ago it was read, dim (`Teams · read
    12 s ago`), a band's says nothing of the hour -- the post's one clock is its status line."""
    return Text.assemble((name, BOLD), (f"{SEP}{read_said(read)}" if dated else "", DIM))


def count_cell(value: object) -> Text:
    """A count the face gives, as it is: `0` dim, another number plain, `—` when the face says none."""
    if not isinstance(value, int):
        return Text(NONE, style=DIM)
    return Text(str(value), style=DIM if value == 0 else "")


OWNER_GUARDS = ("owner", "budget", "launches", "suspected")   # what holds a waiting team that the owner alone lifts


def state_style(state: str | None, waiting_on: tuple = ()) -> str:
    """The look of a team's STATE, as the face says it: `working` a construction site (cyan), `waiting` yellow --
    bold, a problem, when a guard only the owner lifts holds it --, `paused` yellow, `idle` nominal (green),
    `never` dim; no state, no look."""
    if state == "waiting":
        return f"bold {YELLOW}" if any(one in OWNER_GUARDS for one in waiting_on) else YELLOW
    return {"working": CYAN, "paused": YELLOW, "idle": GREEN, "never": DIM}.get(state or "", "")


def team_cells(badge) -> tuple:
    """A line of the menu of the teams: the team's name in its state's look, `⏸` before it while paused; the
    wake-ups under way, the questions and the notices waiting for the owner, the tasks done the owner has not seen
    -- the counts of the face; `-` for a team never started."""
    name = Text(f"{PAUSED} {badge.team}" if badge.state == "paused" else badge.team,
                style=state_style(badge.state, badge.waiting_on))
    if badge.started is None:
        return (name, Text("-", style=DIM), Text("-", style=DIM), Text("-", style=DIM))
    return (name, count_cell(badge.running), count_cell(badge.for_owner), count_cell(badge.done))


def team_fold(team: str | None, badge) -> str:
    """The menu of the teams folded on one line: the team chosen and its state, `team: < test · waiting >`."""
    if team is None:
        return folded("team", NONE)
    return folded("team", f"{team}{SEP}{badge.state}" if badge is not None and badge.state else team)


def state_said(state) -> Text | None:
    """The state of the team chosen, in its look: the word -- `waiting` with the guards of `waiting_on` in the
    face's order, `paused` with who paused it and when --; None when the face says none."""
    if not state.state:
        return None
    said = state.state
    if state.state == "waiting" and state.waiting_on:
        said = f"waiting{SEP}{', '.join(state.waiting_on)}"
    elif state.state == "paused" and state.paused:
        said = f"paused since {age_of(state.paused.get('at'))} by {state.paused.get('by') or NONE}"
    return Text(said, style=state_style(state.state, state.waiting_on))


def stop_said(state) -> Text:
    """What `X` stops, counted on the face: the open tasks, and the wake-ups under way on them, which end on their
    own -- their answers routed nowhere."""
    tasks = [one for one in state.tasks if one.state == "open"]
    wakes = sum(len(one.running) for one in tasks)
    if not tasks:
        return Text("no open task: the verb says nothing to stop")
    said = f"stops {len(tasks)} open task{'' if len(tasks) == 1 else 's'}"
    if wakes == 1:
        said += "; 1 wake-up under way ends on its own, its answer routed nowhere"
    elif wakes:
        said += f"; {wakes} wake-ups under way end on their own, their answers routed nowhere"
    return Text(said)


def pause_head(paused: bool) -> Text:
    """What `P` does, above its field: a pause, or the resume of a team paused."""
    if paused:
        return Text("the team takes back its work: the next tick wakes each member due, in its own run; a ceremony "
                    "whose hour passed during the pause does not ring")
    return Text("nothing is killed: the wake-ups under way end on their own and their answers are routed; until "
                "the resume, no member is woken and no ceremony rings")


TASK_CUT = 30              # a task without a name is named by the start of its text, this long


def task_label(task) -> str:
    """-> how a task is named in a table: its name, else the start of its text, else `—` -- its id has its own
    column, and its own place in a title (`task_title`)."""
    if task.name:
        return task.name
    text = " ".join(plain(task.text or "").split())
    if text:
        return text if len(text) <= TASK_CUT else text[:TASK_CUT - 1] + PENDING
    return NONE


def task_title(task) -> str:
    """-> a task in the title of a gesture or of its thread: `T3 · review PR 88` -- its id, then its name; the id
    alone for a task without a name."""
    return f"{task.id}{SEP}{task.name}" if task.name else task.id


def progress_cell(task) -> Text:
    """The `do`s of a task between members answered over its `do`s -- counted on the face's list; `—` none."""
    from model.teams import progress
    found = progress(task)
    return Text(f"{found[0]}/{found[1]}") if found else Text(NONE, style=DIM)


def task_name_cell(task, frame: int = 0) -> Text | str:
    """The name of a task in its table -- the spinner before it while the face says a wake-up plays it."""
    if not task.running:
        return task_label(task)
    return Text.assemble((f"{spinner(frame)} ", CYAN), task_label(task))


def pane_label(digit: str, title: str, live: int = 0, frame: int = 0) -> str:
    """The title of a tab of the post: `4·Tasks`, and `4·Tasks ⠹ 2` while wake-ups play two of its tasks."""
    return f"{digit}·{title}" + (f" {spinner(frame)} {live}" if live else "")


def task_row_cells(row, frame: int = 0) -> tuple:
    """A line of the Tasks table: the task's id, its name (or the start of its text) -- the spinner before it while a
    wake-up plays it --, its team, its state, who holds it, its progress, its cost, the age of its last event -- every
    cell a field of the face."""
    task = row.task
    last = (task.last or {}).get("at")
    return (task.id, task_name_cell(task, frame), row.team, Text(task.state, style=TASK_STYLES.get(task.state, "")),
            ", ".join(task.holders) or Text(NONE, style=DIM), progress_cell(task),
            f"{task.cost:.2f}" if task.cost is not None else Text(NONE, style=DIM), Text(age_of(last), style=DIM))


def suspected(member) -> bool:
    """Whether the face says the member is not answering at the moment (`health.suspected`)."""
    return bool((member.health or {}).get("suspected"))


def tried_at(member) -> str:
    """The hour of the next try of a suspected member, as the face says it (`health.tried_at`, a local
    `YYYY-MM-DDTHH:MM`): its `HH:MM`; '' when the face says none."""
    said = str((member.health or {}).get("tried_at") or "")
    return said.partition("T")[2] if "T" in said else said


def owes_cell(member) -> Text:
    """The debts of a member, counted on the face's `owes`: `—` at none; the count, bold yellow once one of them was
    reminded already (a problem)."""
    if not member.owes:
        return Text(NONE, style=DIM)
    reminded = any(int(one.get("reminded") or 0) > 0 for one in member.owes)
    return Text(str(len(member.owes)), style=f"bold {YELLOW}" if reminded else "")


def member_cells(member, step=None, over: bool = False) -> tuple:
    """A line of the members: the member -- bold red while the face says it suspected --, the agent that plays it,
    its run, how its run stands (`suspected`, bold red, in place of the run's state for a member not answering),
    its tasks, its debts (`owes_cell`), then `live` -- the last step its team's watch said of it (cyan, dim once its
    wake-up ended), else `since 12 s` for a member the face says running, else `try HH:MM` for a suspected member,
    else `—`."""
    if step is not None:
        live = Text(f"{step_what(step, short=True)}{SEP}{age_of(step.at)}", style=DIM if over else CYAN)
    elif member.how == "running" and member.since:
        live = Text(f"since {age_of(member.since)}", style=CYAN)
    elif suspected(member) and tried_at(member):
        live = Text(f"try {tried_at(member)}", style=RED)
    else:
        live = Text(NONE, style=DIM)
    if suspected(member):
        name, how = Text(member.member, style=RED), Text("suspected", style=RED)
    else:
        name, how = Text(member.member), Text(member.how or NONE, style=HOW_STYLES.get(member.how or "", DIM))
    return (name, cell_of(member.path), cell_of(member.run), how, str(len(member.tasks)), owes_cell(member), live)


def filter_cells(label: str, count: int | None = None) -> tuple:
    """A line of a menu of the Tasks tab: the filter, and the tasks it keeps when it counts them."""
    return (label,) if count is None else (label, count_cell(count))


def folded(label: str, value: str) -> str:
    """A menu folded on a narrow screen, on one line: `team: < test >`."""
    return f"{label}: < {value} >"


def tasks_bar(shown: int, total: int, show: str, team: str, at: str) -> str:
    """The Tasks tab on the status line: the tasks shown over every task, the filters, the hour of the reading."""
    return SEP.join([f"{shown}/{total} task(s)", f"show {show}", f"team {team}", f"read {at}"])


def rhythm_of(ceremony) -> str:
    """A ceremony's rhythm as its line declares it: `every weekday 09:30`, `after daily`."""
    if ceremony.mode == "after":
        return f"after {ceremony.after or NONE}"
    when = ceremony.when or {}
    return f"every {when.get('kind', '?')} {when.get('at', '')}".rstrip()


def progress_of(ceremony) -> str:
    """The progress of a ceremony's last ring: its participants that answered for good on all of them, counted
    on the face's `progress` -- `1/3`, ` any 2` under a quorum --; '' before any ring."""
    if not ceremony.progress:
        return ""
    answered = sum(1 for one in ceremony.progress if one.get("answered"))
    return f"{answered}/{len(ceremony.progress)}" + (f" any {ceremony.quorum}" if ceremony.quorum is not None else "")


def ceremony_cells(ceremony) -> tuple:
    """A line of the Ceremonies table: the name, the progress of its last ring, its next ring as `team` computed
    it (or what it follows), whether the next tick rings it, the state of its last ring."""
    after = ceremony.mode == "after"
    progress = progress_of(ceremony)
    nxt = Text(f"after {ceremony.after}" if after else (ceremony.next_due or NONE), style=DIM if after else "")
    due = Text("yes", style=f"bold {YELLOW}") if ceremony.due else Text(NONE, style=DIM)
    last = (ceremony.last or {}).get("state")
    return (ceremony.name, Text(progress) if progress else Text(NONE, style=DIM), nxt, due,
            Text(last, style=TASK_STYLES.get(last, "")) if last else Text(NONE, style=DIM))


def _lines(said: Text, label: str, items: list[str]) -> None:
    said.append(f"{label:<12}", style=DIM)
    said.append((", ".join(items) if items else NONE) + "\n")


def task_detail(task, team: str = "") -> Text:
    """A task whole, as the face says it: its name, its text whole, its cost, its team, who gave it to whom, its
    ceremony, its messages,
    who holds it, its `do`s between members (`✓` once answered), its waits (`open` or `met`)."""
    said = Text.assemble((f"{task.id}{SEP}", BOLD), (task.state, TASK_STYLES.get(task.state, "")),
                         (f"{SEP}{team}" if team else "", ""),
                         (f"{SEP}{task.sender or NONE} → {task.to or NONE}\n", ""))
    if task.name:
        said.append(f"{'task':<12}{task_label(task)}\n")
    if task.text:
        said.append(f"{'text':<12}{plain(task.text)}\n")
    if task.cost is not None:
        said.append(f"{'cost':<12}{task.cost:.2f} USD\n")
    if task.ceremony:
        said.append(f"{'ceremony':<12}{task.ceremony}{SEP}{task.period or NONE}\n")
    said.append(f"{'messages':<12}{cell_of(task.messages)}\n")
    if task.resumed is not None:
        said.append(f"{'resumed':<12}#{task.resumed}\n")
    _lines(said, "holders", list(task.holders))
    _lines(said, "dos", [f"{one.get('from')} → {one.get('to')} "
                         + (f"{YES} #{one.get('answered')}" if one.get("answered") is not None else PENDING)
                         for one in task.dos])
    _lines(said, "waits", [f"{one.get('member')} any {one.get('any') if one.get('any') is not None else NONE}"
                           + (f"{SEP}{one.get('answered')}/{one.get('of')}" if one.get("of") is not None else "")
                           + f"{SEP}{'open' if one.get('open') else 'met'}" for one in task.waits])
    return said


def member_detail(member) -> Text:
    """A member whole: the agent that plays it, its run and how it stands, its tasks, whom it waits for,
    the posts not delivered to it yet and the answers of the others it has not seen."""
    said = Text.assemble((f"{member.member}{SEP}", BOLD), (f"{member.path or NONE}\n", ""))
    said.append(f"{'run':<12}{member.run or NONE}{SEP}")
    said.append(member.how or NONE, style=HOW_STYLES.get(member.how or "", DIM))
    said.append((f" since {age_of(member.since)}" if member.since else "") + "\n")
    _lines(said, "tasks", list(member.tasks))
    _lines(said, "waits for", list(member.waits))
    _lines(said, "owes", [f"#{one.get('id')} {one.get('verb')} from {one.get('from')} on {one.get('task')}"
                          + (f"{SEP}reminded {one.get('reminded')}" if one.get("reminded") else "")
                          for one in member.owes])
    said.append(f"{'health':<12}", style=DIM)
    said.append_text(health_said(member.health))
    said.append("\n")
    _lines(said, "pending", [f"#{one.get('id')} {one.get('verb')} from {one.get('from')} on {one.get('task')}"
                             for one in member.pending])
    _lines(said, "unseen", [f"{one.get('member')} on {one.get('task')} (#{one.get('id')})" for one in member.unseen])
    return said


def health_said(health: dict | None) -> Text:
    """A member's health as the face says it: `suspected · falls 2 · tried again 10/10 09:30 · repents 1` (bold red
    while suspected), `ok · falls 0 · repents 1` for a member that answered again; `—` for a member never fallen."""
    if not isinstance(health, dict):
        return Text(NONE, style=DIM)
    parts = ["suspected" if health.get("suspected") else "ok", f"falls {health.get('falls', 0)}"]
    tried = str(health.get("tried_at") or "")
    if health.get("suspected") and "T" in tried:
        day, _, hour = tried.partition("T")
        parts.append(f"tried again {day[8:10]}/{day[5:7]} {hour}")
    parts.append(f"repents {health.get('repents', 0)}")
    return Text(SEP.join(parts), style=RED if health.get("suspected") else "")


def ceremony_detail(ceremony, ceremonies=(), tasks=()) -> Text:
    """A ceremony whole: its rhythm, its chain -- the ceremony it follows, those that follow it, as the face
    declares them --, who takes part and who facilitates, its quorum, its next ring and whether the next tick
    rings it -- `team`'s computation, shown --, its last ring, its progress and the participants still waited
    for, and the wait the task of that ring carries, as its `waits` say it."""
    said = Text.assemble((f"{ceremony.name}{SEP}", BOLD), (f"{rhythm_of(ceremony)}\n", ""))
    then = [one.name for one in ceremonies if one.mode == "after" and one.after == ceremony.name]
    chain = ([f"after {ceremony.after}"] if ceremony.mode == "after" and ceremony.after else []) + \
        ([f"then {', '.join(then)}"] if then else [])
    said.append(f"{'chain':<12}{SEP.join(chain) or NONE}\n")
    said.append(f"{'with':<12}{', '.join(ceremony.participants) or NONE} → {ceremony.facilitator or NONE}\n")
    if ceremony.quorum is not None:
        said.append(f"{'quorum':<12}any {ceremony.quorum}\n")
    said.append(f"{'next':<12}{ceremony.next_due or NONE}{SEP}due {'yes' if ceremony.due else 'no'}\n")
    last = ceremony.last or {}
    said.append(f"{'last':<12}" + (SEP.join(str(last.get(key)) for key in ("period", "task", "state") if last.get(key))
                                   + (f" by {last['by']}" if last.get("by") else "") if last else NONE) + "\n")
    waited = [str(one.get("member")) for one in ceremony.progress if not one.get("answered")]
    said.append(f"{'progress':<12}{progress_of(ceremony) or NONE}" + (f"{SEP}waits {', '.join(waited)}" if waited else "")
                + "\n")
    task = next((one for one in tasks if one.id == last.get("task")), None) if last.get("task") else None
    for one in task.waits if task is not None else ():
        said.append(f"{'wait':<12}{one.get('member')} any {one.get('any') if one.get('any') is not None else NONE}"
                    f"{SEP}{'open' if one.get('open') else 'met'}\n")
    return said


def budget_of(state) -> str:
    """The team's budget as its face says it: `budget 1.84/2.00 USD · reserved 0.10 · left 0.06`; without `budget:`,
    the cost spent alone."""
    budget = state.budget
    if isinstance(budget, dict) and isinstance(budget.get("cap"), (int, float)):
        return (f"budget {float(budget.get('spent') or 0):.2f}/{float(budget['cap']):.2f} USD"
                f"{SEP}reserved {float(budget.get('reserved') or 0):.2f}{SEP}left {float(budget.get('left') or 0):.2f}")
    return f"cost {cell_of(state.cost, money=True)} USD"


def for_you(waiting: dict) -> str:
    """What waits for the owner, counted on one line: `for you: 1 question · 1 notice · 1 task done`; `for you: nothing`."""
    parts = [(len(waiting.get("questions") or []), "question"), (len(waiting.get("notices") or []), "notice"),
             (len(waiting.get("done") or []), "task done"),
             (len(waiting.get("returned") or []), "post returned")]
    said = SEP.join(f"{count} {word}" + ("s" if count > 1 and word in ("question", "notice") else "")
                    for count, word in parts if count)
    return f"for you: {said or 'nothing'}"


def team_head(state) -> Text:
    """The head of the chosen team, five lines at most: its owner and mandators; its
    state; its budget and its launches against their bound; its net and what is wrong -- `TEAM.md` changed and the budget
    spent are problems (bold); what waits for the owner, counted."""
    said = Text.assemble((state.team, BOLD), (f"{SEP}owner {state.owner or NONE}", ""),
                         (f"{SEP}principals {', '.join(state.principals) or NONE}\n", ""))
    line = state_said(state)
    if line is not None:
        said.append_text(line)
        said.append("\n")
    launches = f"launches {state.launches.get('launched', NONE)}/{state.launches.get('bound') or NONE}"
    said.append(f"{budget_of(state)}{SEP}{launches}\n")
    minutes, laid = state.schedule.get("minutes"), state.schedule.get("laid")
    said.append("schedule " + ("off" if minutes is None else f"every {minutes} min {'laid' if laid else 'absent'}"))
    if state.changed:
        said.append(f"{SEP}{WARNING} TEAM.md changed since the start", style=f"bold {YELLOW}")
    if state.budget_spent:
        said.append(f"{SEP}{WARNING} budget spent", style=RED)
    urgent = state.waiting.get("questions") or [one for one in state.waiting.get("notices") or [] if one.get("awaits")]
    said.append("\n" + for_you(state.waiting), style=f"bold {YELLOW}" if urgent else "")
    return said


def budget_head(state) -> Text:
    """What `B` raises, above its fields: the team's budget and its launches, as the face says them."""
    return Text(f"{budget_of(state)}{SEP}launches {state.launches.get('launched', NONE)}/{state.launches.get('bound') or NONE}")


def inbox_lines(found: dict | None) -> list[tuple[Text, tuple[str, object] | None]]:
    """The lines of the owner's inbox, as `team inbox <name> --json` says it, each with the post an answer cites --
    `(task, id)` -- or None: the questions waiting for the owner first (a problem: bold), then the team's notices (one
    that waits for the owner's answer bold, and answered like a question), then the tasks done, then the posts
    returned."""
    found = found or {}
    lines: list[tuple[Text, tuple[str, object] | None]] = []
    for one in found.get("questions") or []:
        lines.append((Text(f"#{one.get('id')} {one.get('verb')} from {one.get('from')} on {one.get('task')}"
                           f"  « {one.get('text', '')} »", style=f"bold {YELLOW}"), (str(one.get("task")), one.get("id"))))
    for one in found.get("notices") or []:
        lines.append((Text(f"#{one.get('id')} notice "
                           + (f"about {one.get('about')}" if one.get("about") else f"from {one.get('from')}")
                           + f" on {one.get('task')}  « {one.get('text', '')} »",
                           style=f"bold {YELLOW}" if one.get("awaits") else ""),
                      (str(one.get("task")), one.get("id")) if one.get("awaits") else None))
    for one in found.get("done") or []:
        lines.append((Text(f"{one.get('task')} done{SEP}#{one.get('id')}", style=GREEN), None))
    for one in found.get("returned") or []:
        lines.append((Text(f"#{one.get('id')} {one.get('verb')} from {one.get('from')} on {one.get('task')} returned"
                           f"  « {one.get('text', '')} »"), None))
    return lines


def declaration_text(found: dict) -> Text:
    """A team's declaration, as `team declaration <name> --json` says it: its path, the verdict of `start`'s judge
    (`ok`, or the refusal start would write: a problem), its start, the keys a new start would change, then
    `TEAM.md` whole, as the file says it."""
    import json
    verdict = found.get("verdict") or {}
    said = Text.assemble((f"{'path':<10}", ""), (f"{found.get('path', NONE)}\n", BOLD))
    if verdict.get("ok"):
        said.append_text(Text.assemble((f"{'verdict':<10}", ""), ("verdict ok\n", GREEN)))
    else:
        said.append_text(Text.assemble((f"{'verdict':<10}", ""), (f"verdict refused: {verdict.get('refusal')}\n", RED)))
    started = found.get("started")
    said.append(f"{'started':<10}" + (f"{started.get('at')} (#{started.get('id')})\n" if isinstance(started, dict)
                                      else "not started\n"))
    pending = found.get("pending")
    if pending is None:
        said.append(f"{'pending':<10}{NONE}  judged once the declaration reads\n", style=DIM)
    elif not pending:
        said.append(f"{'pending':<10}nothing pending\n")
    else:
        said.append(f"{'pending':<10}{len(pending)} key(s) wait a start\n", style=f"bold {YELLOW}")
        def value(one: object) -> str:
            return one if isinstance(one, str) else json.dumps(one, ensure_ascii=False)
        for one in pending:
            said.append(f"{'':<10}{one.get('key')} · {value(one.get('started'))} → {value(one.get('declared'))}\n")
    said.append("\n" + str(found.get("text") or ""))
    return said


def not_started(team: str) -> Text:
    """A team declared and never started: said, and the command that starts it -- to come, so dim."""
    return Text.assemble((f"{team}{SEP}not started\n", BOLD),
                         (f"./pp team start {team} --message …", DIM))


RESUME_HELP = "a message to the members it revives -- empty: `the task resumes`, team's own words"
TASK_HELP = "the message of the new task -- ctrl+enter goes to the line"
START_HELP = "the team's first message -- its task goes to the root of the team; ctrl+enter goes to the line"
TEXT_HELP = "what you post on the task -- ctrl+enter goes to the line"
TO_HELP = "who receives it -- left as it is, the members holding the task"
ROOT_HELP = "who receives the task -- left as it is, the root of the team"
AS_HELP = "the principal you post as -- the owner writes no --as"
REPLY_HELP = "a question waiting for you on this task, to answer -- left as it is, a plain note"
NAME_HELP = "the task's name, one line -- left empty, the tables say the start of its message"
TEAM_HELP = "the team that gets the task"
TEMPLATE_HELP = "the template the team is written from -- changing it sets the fields below to its own"
TEAM_NAME_HELP = "the team's name: its directory under teams/, one word of letters, digits and dashes"
MEMBERS_HELP = ("one member per line -- left as they are, team writes each under agents/<team>/<member>; changed, "
                "each line is `<name> <path>`; the intention team writes for them reads by `e` once the team stands")
FIRST_HELP = "who receives the team's tasks -- left as it is, the first member"
PRINCIPALS_HELP = "the mandators allowed to post, one name each, blanks between -- the owner needs none"
CEREMONY_HELP = "the template's ceremony, kept or left out"
LIMIT_HELP = "as the template sets it -- changed, written to TEAM.md"
SCHEDULE_HELP = "left empty, the template's (off); `off`, or the minutes between two ticks of the calendar"
BUDGET_HELP = "the team's budget, in dollars, above what it spent -- left as it is, unchanged"
LAUNCHES_HELP = "the launches the team may take since its start -- left as it is, unchanged"


AS_ALL = "·"                # a member's field left to `all`


# what a free field left empty shows in its place: an example of what it takes, in the weight of its help
BUDGET_EXAMPLE = "e.g. 2.5"
SEASON_BUDGET_EXAMPLE = "e.g. 10"
LAUNCHES_EXAMPLE = "e.g. 40"
EFFORT_EXAMPLE = "e.g. high"
NAME_EXAMPLE = "e.g. review PR 88"
PRINCIPALS_EXAMPLE = "e.g. alice bob"
SCHEDULE_EXAMPLE = "e.g. 15"
TIMEOUT_EXAMPLE = "e.g. 600"
RESUME_EXAMPLE = "e.g. the task resumes"


def model_example(models: list[str]) -> str:
    """The example of a model: the first name the provider's adapter declares, `opus` when it declares none."""
    return f"e.g. {models[0] if models else 'opus'}"


def field_title(label: str) -> str:
    """The title of a field: its label, its first letter in capital -- `budget` is `Budget`, `reply to` `Reply to`."""
    return label[:1].upper() + label[1:]


def as_all(value: object) -> str:
    """What a member's field left empty says in its profile: `all`'s, and the value it takes."""
    return f"{AS_ALL} as all ({value})" if value else f"{AS_ALL} as all"


def season_title(team: str, state) -> str:
    """The title of a season: the first of a team never started, or the next one of a team at work."""
    if state is None or state.started is None:
        return f"first season of {team}"
    n = int(state.season.get("n") or 1)
    return f"new season of {team} (season {n} -> {n + 1})"


def season_head(declared: dict) -> Text:
    """What the next start writes, above the fields of a season: the members, the root, the limits of TEAM.md."""
    limits = declared.get("limits") or {}
    members = len(declared.get("agents") or [])
    return Text(f"{members} member(s){SEP}root {declared.get('root') or NONE}{SEP}parallel "
                f"{limits.get('parallel', NONE)}{SEP}launches {limits.get('launches', NONE)} -- as TEAM.md declares them")


def season_limit_help(key: str, declared: object) -> str:
    """The help under the budget or the launches of a season: what TEAM.md says, and when the field is the season's."""
    said = NONE if declared is None else f"{declared:g}" if isinstance(declared, float) else str(declared)
    what = "the team's budget, in dollars" if key == "budget" else "the launches the team may take"
    return f"{what} for this season -- TEAM.md says {said}; another value is the season's own, empty keeps TEAM.md's value"


SEASON_LINES_HELP = ("enter edits a line in its profile -- all goes to every member, · is as all; packages: the "
                     "switches, -plan off, +plan on")


SEASON_MESSAGE_HELP = ("a first task's message, if any -- without it the season stands on its ceremonies and the posts "
                       "to come; a name goes with a message alone; ctrl+enter goes to the line")


def switches_text(switches: dict) -> str:
    """The switches of a line: `-plan +steering`."""
    return " ".join(f"{'+' if on else '-'}{name}" for name, on in switches.items())


def season_cells(line, whole) -> tuple[str, ...]:
    """A line of a season's table: `all` -- what it carries, `—` where nothing --, or a member -- what it changes of
    `all`, `·` the rest."""
    empty = NONE if line.member is None else AS_ALL
    own = line.profile if line.member is None else {key: value for key, value in line.profile.items()
                                                    if whole.profile.get(key) != value}
    return ((line.member or "all"), line.path or NONE,
            *(str(own.get(key) or empty) for key in ("provider", "model", "effort", "permissions")),
            switches_text(line.switches) or empty)


def question_option(question: dict) -> str:
    """A question of the task in the line's `reply` list: `#45 ask from reviewer`, `#52 notice about lead`."""
    if question.get("about"):
        return f"#{question.get('id')} notice about {question.get('about')}"
    return f"#{question.get('id')} {question.get('verb')} from {question.get('from')}"


def preview_line(command: str) -> Text:
    """The command a gesture plays, under its fields -- the exact one; nothing while none can be made."""
    return Text(command, style=DIM) if command else Text("")


def no_team() -> Text:
    """A house without a team: how one is declared -- to come, so dim."""
    return Text.assemble((NONE, DIM), ("  no team declared: teams/<name>/TEAM.md declares one", DIM))


STATUS_DROP = ("last", "members", "tasks", "cost", "launches", "state")   # what a status line too wide loses, first first


def team_bar(team: str, badge, state, at: str) -> list[tuple[str, str]]:
    """The chosen team on the status line, as PARTS `(kind, text)`: its name, its state, `⚠` where a problem stands,
    its tasks by state and its members as the faces count them, its cost and its launches against their bound, its
    last event, the hour of its reading -- `fit_status` keeps what the width holds."""
    if state is None or state.started is None:
        return [("team", team), ("state", "not started"), ("read", f"read {at}")]
    tasks = (badge.tasks if badge is not None else {}) or {}
    counted = " ".join(f"{tasks[key]} {key}" for key in ("open", "stopped", "resolved") if key in tasks)
    launches = f"{state.launches.get('launched', NONE)}/{state.launches.get('bound') or NONE}"
    last = state.last or {}
    parts = [("team", team)] + ([("state", state.state)] if state.state else [])
    if state.changed:
        parts.append(("alert", f"{WARNING} TEAM.md changed"))
    if state.budget_spent:
        parts.append(("alert", f"{WARNING} budget spent"))
    return parts + [("tasks", f"tasks {counted or NONE}"), ("members", f"{len(state.members)} members"),
                    ("cost", f"cost {cell_of(state.cost, money=True)} USD"), ("launches", f"launches {launches}"),
                    ("last", f"last #{last.get('id', NONE)} {last.get('kind', '')}{SEP}{age_of(last.get('at'))}"),
                    ("read", f"read {at}")]


def fit_note(note: str, width: int) -> str:
    """-> the last note of the status line within `width` columns, its separator after it: cut by `…` when too long,
    nothing when no room is left -- the pane's state and the clock come first."""
    if not note or width <= len(SEP) + 1:
        return ""
    room = width - len(SEP)
    return (note if cell_len(note) <= room else note[:room - 1] + PENDING) + SEP


def fit_status(parts, width: int) -> str:
    """-> a pane's state on the status line within `width` columns: its parts joined, the parts of `STATUS_DROP`
    taken out in that order while the line is too wide -- never a team's name, a `⚠` nor the hour of a reading."""
    kept = list(parts)
    for kind in STATUS_DROP:
        if cell_len(SEP.join(text for _, text in kept)) <= width:
            break
        kept = [one for one in kept if one[0] != kind]
    return SEP.join(text for _, text in kept)


# ---------- the thread of a task: the journal's events as `log` and `watch` give them ----------
SPOKEN = ("task", "post")                 # what the members and the principals SAID: in clear; the rest dim
LIVE = "live:"


def thread_line(line, open_ids: set[int] = frozenset()) -> Text:
    """One event of a thread on one line: its id, its hour, then what it says -- a task or a post in
    clear (`from → to verb « text »`, `[open]` on a question the face counts as unanswered), any other
    event dim, its fields flat."""
    f = line.fields
    head = (f"#{line.id if line.id is not None else NONE} ", BOLD if line.kind in SPOKEN else DIM)
    hour = (f"{hour_of(line.at)}  ", DIM)
    if line.kind in SPOKEN:
        verb = str(f.get("verb") or line.kind)
        if verb == "re" and f.get("re") is not None:
            verb = f"re #{str(f.get('re')).lstrip('#')}"
        elif verb == "notice" and f.get("about"):
            verb = f"notice about {f.get('about')}"
        said = one_line(head, hour, (f"{f.get('from', NONE)} → {f.get('to', NONE)}  {verb}  ", ""),
                        (f"« {' '.join(plain(str(f.get('text') or '')).split())} »", ""))
        if f.get("by"):                               # the tick answered in a member's place
            said.append(f"  by {f.get('by')}", style=YELLOW)
        for word in ("preempted", "suspected"):       # a problem the tick settled, or says
            if f.get(word):
                said.append(f"{SEP}{word}", style=YELLOW)
        if f.get("was"):
            said.append(f"  (was {f.get('was')})", style=DIM)
        if line.id in open_ids:
            said.append(" [open]", style=f"bold {YELLOW}")
        return said
    if line.kind in ("wake-ended", "wake-failed", "wake-launched", "wake-intent", "wake-killed"):
        cost = f.get("cost")
        rest = SEP.join(one for one in (str(f.get("agent") or ""), f"run {f['run']}" if f.get("run") else "",
                                        f"relance {f['relance']}" if f.get("relance") else "",
                                        f"{float(cost):.2f} USD" if isinstance(cost, (int, float)) else "",
                                        str(f.get("reason") or "")) if one)
    else:
        rest = " ".join(f"{key}={value}" for key, value in f.items() if key not in ("task",))
    return one_line(head, hour, (f"{line.kind}  {rest}".rstrip(), DIM))


def step_what(step, short: bool = False) -> str:
    """What a step of a wake-up says: the block it served -- its last frame alone under `short` --, `parked` when
    it waits; else its kind and its code, its document or its name."""
    f = step.fields
    if step.kind == "block":
        stack = str(f.get("stack") or "")
        return (stack.split("▸")[-1].strip() if short else stack) + (f"{SEP}parked" if f.get("wait") else "")
    return " ".join([step.kind] + [str(f[key]) for key in ("code", "document", "name") if f.get(key)])


def call_text(call: dict | None) -> str:
    """The last call of a tool a wake-up made, as the kept flow says it: `⚙ WebSearch · "DDR4 spot"` -- `pp` for the
    agent's console; `` without one."""
    if call is None:
        return ""
    name = "pp" if call.get("pp") is True else str(call.get("name") or "?")
    title = " ".join(plain(str(call.get("title") or "")).split())
    return f"{CALL} {name}" + (f"{SEP}{title}" if title else "")


def relance_of(wake: dict | None) -> list[str]:
    """`relance owed` when the face says the wake-up is a reminder (`running[].relance`: `owed`, `cycle`, `tried`)."""
    return [f"relance {wake['relance']}"] if isinstance(wake, dict) and wake.get("relance") else []


def live_line(step, over: bool, label: str = LIVE, call: dict | None = None, wake: dict | None = None) -> Text:
    """The last step of a wake-up of the task: `live: reviewer · run a01389 · relance owed · TURN{4/4} · parked ·
    12 s`, then the last call of a tool of that wake-up when one is given -- dim once that wake-up ended; `—` before
    any step. `label` heads it."""
    if step is None:
        return Text(f"{label} {NONE}", style=DIM)
    f = step.fields
    said = SEP.join([str(f.get("agent") or NONE), f"run {f.get('run') or NONE}"] + relance_of(wake)
                    + [step_what(step), age_of(step.at)] + ([call_text(call)] if call is not None else []))
    return one_line((f"{label} ", BOLD if not over else DIM), (said, DIM if over else CYAN))


LAST = "last:"


def last_action(lives: list[tuple], last: dict | None) -> Text:
    """The LAST ACTION of a task, as the band says it: one `live:` line per member -- `(member, step, over, call,
    wake)`: the last step its wake-up said on the task and the last call of a tool of that wake-up, dim once it
    ended (`live_line`); or, for a member the face says running with no step seen yet, `wake` -- `live: sre · run
    b11111 · launched 12 s ago`; a task no wake-up was seen on says its last event (`last: #47 wake-ended ·
    3 min`), as the face says it."""
    if not lives:
        if not isinstance(last, dict):
            return Text(f"{LAST} {NONE}", style=DIM)
        return one_line((f"{LAST} ", BOLD), (f"#{last.get('id', NONE)} {last.get('kind', '')}{SEP}"
                                            f"{age_of(last.get('at'))}", DIM))
    said = Text(no_wrap=True, overflow="ellipsis")
    for index, (member, step, over, call, wake) in enumerate(lives):
        if index:
            said.append("\n")
        if step is not None:
            said.append_text(live_line(step, over, call=call, wake=wake))
        else:
            wake = wake or {}
            said.append_text(one_line((f"{LIVE} ", BOLD), (SEP.join([member, f"run {wake.get('run') or NONE}"]
                                                                   + relance_of(wake)
                                                                   + [f"launched {age_of(wake.get('since'))} ago"]),
                                                          CYAN)))
    return said


def thread_text(lines: list, open_ids: set[int] = frozenset()) -> Text:
    """Events one per line -- the thread of a task, or a team's whole journal in its overlay."""
    said = Text(no_wrap=True, overflow="ellipsis")       # one event, one line: cut at the width, never wrapped
    for index, line in enumerate(lines):
        if index:
            said.append("\n")
        said.append_text(thread_line(line, open_ids))
    return said if lines else Text(f"{NONE}  no event", style=DIM)


def responses_text(found: list[dict]) -> Text:
    """The responses of a member as `team responses --json` gives them: one block each -- its id, its task, its
    run, its hour, its cost --, then its text whole."""
    if not found:
        return Text(f"{NONE}  no response yet", style=DIM)
    said = Text()
    for index, one in enumerate(found):
        if index:
            said.append("\n\n")
        cost = one.get("cost_usd")
        said.append(f"#{one.get('id')}{SEP}{one.get('task') or NONE}{SEP}run {one.get('run') or NONE}{SEP}"
                    f"{hour_of(str(one.get('at') or ''))}" + (f"{SEP}{float(cost):.2f} USD" if isinstance(cost, (int, float)) else ""),
                    style=BOLD)
        said.append("\n" + (plain(str(one["response"])) if one.get("response") is not None else "(response missing)"))
    return said


def result_text(value: object) -> Text:
    """A task's result as `team result` gave it: its JSON, indented."""
    import json
    return Text(json.dumps(value, indent=2, ensure_ascii=False))
