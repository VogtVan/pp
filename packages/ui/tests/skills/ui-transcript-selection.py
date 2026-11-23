"""Scenario `ui-transcript-selection` -- a selection in the transcript, seen and copied (plan pp-fixes, batch
la-selection-du-transcript), `ui-transcript-cost`'s sibling (rule 10): on a `TranscriptView` alone in a Textual app of
60x14 played in a subprocess, no house:
- a selection over a row of the agent's words, on the themes `textual-dark` and `gruvbox`: each segment of the
  selected cells has a text colour other than its background, and a background other than the row's unselected cells
  -- the selection seen, its text kept
- a drag with the mouse from column 0 of a row (its margin, before its gutter) to the end of its text: the selection
  copied is the row's text whole, as `get_selection` reads it -- the cells before the text anchored at its start
- a selection held while the rows MOVE (batch la-selection-ancree), one case per movement, on a `TranscriptView` alone
  in a Textual app of 60x20 whose `ctrl+c` is the post's `action_copy`: (a) a call, a thought and a result alone placed
  above during a turn; (b) words added at the end, nothing moves; (c) a line above that takes another summary (`took`,
  a second thought) or unfolds (the steps' line at its first step, also once a layout has taken in a line whose
  summary changed); (d) `c` then `b`, each pressed twice, and the
  fallback -- a start whose line folds comes back to the next row shown, both ends folded clear the selection; (e) a
  resize, the scrollbar that comes, and a selection over a paragraph wrapped again; (f) another theme; (g) `rebuild`
  with a turn of history above, and with the selected words gone; (h) a drag under way while a line comes above it.
  Each case: the text `ctrl+c` copies after the movement is the text it copied before (for a fallback, that text
  without the rows folded; with a paragraph wrapped again, the same words), and the cells drawn in the selection's
  look carry that same text
- a selection in a view RAISED to an earlier message (batch la-selection-apres-defilement), on a `TranscriptView`
  above a message line in a Textual app of 60x20, the transcript running past the view: (i) the message line focused,
  a drag between two rows of words, then a click alone -- the view stays where it stands, the click selects nothing
  and opens nothing; `shift+tab` from the message line still puts the cursor on the last live line; (j) a press on
  the margin, then on the border of a framed transcript, and a pointer on its top border; (k) a pointer on the
  scrollbar, then below the view on the message line -- the selection ends with the rows in view; (l) a selection that
  ends on an empty last row, and the whole transcript selected; (m) a selection under a row that carries U+2028; (n) a
  drag released past the end of a row, then the terminal widened. Each case: the text `ctrl+c` copies is the text of
  the rows between the two places, read row by row in the rows the transcript holds, and the cells drawn in the
  selection's look carry that same text
The colours are read in the segments the row draws, the copy against the row the transcript holds or the copy before
the movement: no text of the test is compared (rule 2).
"""
from __future__ import annotations

import json
import subprocess

from tests.harness import SOURCE

SKILL = SOURCE / "packages" / "ui" / "skills" / "pp-ui"
TEXTUAL = ("uv", "run", "--quiet", "--no-project", "--with", "textual==8.2.8", "--with", "pyyaml>=6", "python3")
THEMES = ("textual-dark", "gruvbox")
PROBE = r'''
import asyncio, json, sys
sys.path.insert(0, sys.argv[1])
THEMES = sys.argv[2:]
from textual.app import App
from textual.binding import Binding
from textual.geometry import Offset
from textual.selection import Selection
from textual.widgets import TextArea
from app import PostApp
from model.dialogue import Event, Turn
from panes.transcript import Block, TranscriptView

AT = "2026-11-08T09:00:{:02d}+00:00"
WORDS = ("The first paragraph of the answer, wrapped on two rows here and on three rows once narrowed."
         "\n\nThe second paragraph, short.")


class Probe(App):
    BINDINGS = [Binding("ctrl+c", "copy", "copy", show=False, priority=True)]
    action_copy = PostApp.action_copy          # the post's copy: the focused field's selection, else the screen's
    _note = ""

    def compose(self):
        yield TranscriptView()

    def _tick(self):
        pass


async def built(app, pilot):
    view = app.query_one(TranscriptView)
    at = "2026-11-08T09:00:0{}+00:00"
    await view.add(Event("principal", at.format(0), "r00001", {"text": "a question"}))
    await view.add(Event("words", at.format(1), "r00001", {"text": "The first answer, one sentence.", "launch": 1}))
    await view.add(Event("words", at.format(2), "r00001", {"text": "The second answer, below it.", "launch": 1}))
    await pilot.pause()
    view._settle()
    rows = [(row[0].plain, row[1]) for item in view._items for row in view._rows_of(item)]
    return view, rows, max(n for n, (text, _) in enumerate(rows) if text.strip())


def hue(color):
    return None if color is None else color.get_truecolor().hex


async def seen(theme):
    app = Probe()
    async with app.run_test(size=(60, 14)) as pilot:
        app.theme = theme
        await pilot.pause()
        view, rows, row = await built(app, pilot)
        text, indent = rows[row]
        start, end = 4, min(len(text), 14)
        app.screen.selections = {view: Selection(Offset(start, row), Offset(end, row))}
        await pilot.pause()
        strip, x, cells = view.render_line(row - view.scroll_offset.y), 0, []
        for segment in strip:
            cells.append({"from": x, "to": x + segment.cell_length,
                          "fg": hue(segment.style.color if segment.style else None),
                          "bg": hue(segment.style.bgcolor if segment.style else None)})
            x += segment.cell_length
        chosen = [one for one in cells if one["from"] >= indent + start and one["to"] <= indent + end]
        others = {one["bg"] for one in cells if one["to"] <= indent + start or one["from"] >= indent + end}
        return {"theme": theme, "selected": chosen, "others": sorted(map(str, others))}


async def dragged():
    app = Probe()
    async with app.run_test(size=(60, 14)) as pilot:
        view, rows, row = await built(app, pilot)
        text, indent = rows[row]
        y, left = row - view.scroll_offset.y, view.content_region.x - view.region.x
        await pilot.mouse_down(view, offset=(left, y))
        await pilot.hover(view, offset=(left + indent + len(text), y))
        await pilot.mouse_up(view, offset=(left + indent + len(text), y))
        await pilot.pause()
        return {"row": text, "indent": indent, "copied": app.screen.get_selected_text(),
                "selection": str(app.screen.selections.get(view))}


def said(kind, n, **fields):
    return Event(kind, AT.format(n), "r00001", fields)


async def opened(app, pilot, words=WORDS, steps=True, above=()):
    """-> the transcript of one turn: the message, the conduction, its steps (or none yet), what came `above` the
    words, then the words of two paragraphs."""
    view = app.query_one(TranscriptView)
    await view.add(said("principal", 0, text="a question"))
    await view.add(said("conduction", 1, launch=1, blocks=[{"stack": "TURN{2/4}"}]))
    if steps:
        await view.add(said("step", 2, event="launch", launch=1))
    for event in above:
        await view.add(event)
    await view.add(said("words", 9, text=words, launch=1))
    await pilot.pause()
    view._settle()
    return view


def placed(view):
    """-> the first words' block as laid: its first row and its rows' text; None when no words are left."""
    view._settle()
    blocks = [one for one in view._items if isinstance(one, Block) and one.voice == "agent"]
    return (view._tops[blocks[0].index], [row[0].plain for row in view._rows_of(blocks[0])]) if blocks else None


def chosen(view, single=False):
    """-> a selection in the words: from the 5th character of their first row to the 11th of their last -- or, single,
    within their last row."""
    top, rows = placed(view)
    said_rows = [top + n for n, row in enumerate(rows) if n and row.strip()]
    last = said_rows[-1]
    if single:
        return Selection(Offset(4, last), Offset(min(len(rows[last - top].rstrip()), 20), last))
    return Selection(Offset(4, said_rows[0]), Offset(10, last))


async def copied(app, pilot):
    """-> what `ctrl+c` copies, read on the clipboard ("" when nothing is selected)."""
    app._clipboard = ""
    await pilot.press("ctrl+c")
    await pilot.pause()
    return app.clipboard


def cells(strip):
    """-> each character of a strip with its look, the offsets a selection reads left out."""
    return [(char, segment.style.clear_meta_and_links() if segment.style else None)
            for segment in strip for char in segment.text]


def lit(view):
    """-> the text the cells drawn in the selection's look carry: each row drawn with the selection and without it,
    the characters whose look differs kept, the rows from the first to the last that has one joined."""
    view._settle()
    rows = []
    for row in range(view._total):
        y = row - view.scroll_offset.y
        drawn = cells(view.render_line(y))
        TranscriptView.text_selection = property(lambda self: None)
        try:
            bare = cells(view.render_line(y))
        finally:
            del TranscriptView.text_selection
        rows.append("".join(char for (char, look), (_, under) in zip(drawn, bare) if look != under))
    marked = [n for n, row in enumerate(rows) if row]
    return "\n".join(rows[marked[0]:marked[-1] + 1]).rstrip("\n") if marked else ""


async def held(app, pilot, view, case, move, single=False, moves=True, expect=None, loose=False):
    """-> one case judged: a selection laid, its copy read, `move` played, the copy and the lit text read again."""
    app.screen.selections = {view: chosen(view, single)}
    await pilot.pause()
    before, place = await copied(app, pilot), placed(view)
    await move()
    await pilot.pause()
    after = await copied(app, pilot)
    return {"case": case, "before": before, "after": after, "lit": lit(view),
            "expected": before if expect is None else expect(before),
            "moved": placed(view) != place, "moves": moves, "loose": loose}


async def case(name, move, single=False, moves=True, size=(60, 20), above=(), steps=True, words=WORDS, **rest):
    app = Probe()
    async with app.run_test(size=size) as pilot:
        view = await opened(app, pilot, words, steps, above)
        return await held(app, pilot, view, name, lambda: move(app, pilot, view), single, moves, **rest)


TOOL = said("tool", 4, id="t1", name="Bash", input={"command": "ls"})
THOUGHT = said("thinking", 5, launch=1, text="a thought")


async def cases():
    out = []

    async def inserted(app, pilot, view):
        await view.add(TOOL)
        await view.add(THOUGHT)
        await view.add(said("tool-result", 6, id="t9", content="a result alone"))
    out.append(await case("a: a call, a thought, a result placed above", inserted))

    async def appended(app, pilot, view):
        await view.add(said("words", 10, text="More words at the end.", launch=1))
    out.append(await case("b: words added at the end", appended, moves=False))

    async def took(app, pilot, view):
        await view.add(said("tool-result", 6, id="t1", content="a.py\nb.py"))
        await view.add(said("thinking", 7, launch=1, text="a second thought"))
    out.append(await case("c: a call took its result, a thought another text", took, moves=False,
                          above=(TOOL, THOUGHT)))

    async def unfolded(app, pilot, view):
        await view.add(said("step", 8, event="launch", launch=1))
    out.append(await case("c: the steps' line unfolds at its first step", unfolded, steps=False))

    async def unfolded_later(app, pilot, view):
        await view.add(said("tool-result", 6, id="t1", content="a.py\nb.py"))   # a line changed, laid out
        await pilot.pause()
        await view.add(said("step", 8, event="launch", launch=1))
    out.append(await case("c: the steps' line unfolds after a layout took in a changed line", unfolded_later,
                          steps=False, above=(TOOL,)))

    for keys in ("c", "b", "cc", "bb"):
        async def toggled(app, pilot, view, keys=keys):
            for key in keys:
                (view.toggle_conduction if key == "c" else view.toggle_calls)()
                await pilot.pause()
        out.append(await case(f"d: {keys} pressed", toggled, moves=len(keys) == 1, above=(TOOL, THOUGHT)))

    out.extend(await folded())

    async def resized(app, pilot, view):
        await pilot.resize_terminal(40, 20)
    out.append(await case("e: the terminal resized", resized, single=True))
    out.append(await case("e: a paragraph wrapped again", resized,
                          expect=lambda before: " ".join(before.split()), loose=True))
    out.append(await scrolled())

    async def themed(app, pilot, view):
        app.theme = "gruvbox"
    out.append(await case("f: another theme", themed, moves=False))

    events = [said("principal", 0, text="a question"), said("conduction", 1, launch=1, blocks=[{"stack": "TURN{2/4}"}]),
              said("step", 2, event="launch", launch=1), said("words", 9, text=WORDS, launch=1)]

    async def rebuilt(app, pilot, view):
        kept = Turn(exchange=1, message="an earlier question", history=True, at=AT.format(0),
                    answer="An earlier answer, kept.")
        await view.rebuild(events, [kept])
    out.append(await case("g: rebuild with a turn of history above", rebuilt))

    async def gone(app, pilot, view):
        await view.rebuild(events[:2])
    out.append(await case("g: rebuild without the words selected", gone, moves=None,
                          expect=lambda before: ""))

    out.append(await dragging())
    return out


async def folded():
    """(d) the fallback: a selection from the conduction's line to the words, `c` -- its start comes back to the next
    row shown, the rows folded leave the copy --, `c` again -- the selection as it was; one from the conduction's line
    to the thought, `c` -- both ends folded: nothing selected."""
    out = []
    app = Probe()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await opened(app, pilot, above=(TOOL, THOUGHT))
        line = next(one for one in view._items if not isinstance(one, Block) and one.has_class("conduction"))
        start = Offset(3, view._tops[line.index])
        end = chosen(view).end
        app.screen.selections = {view: Selection(start, end)}
        await pilot.pause()
        before = await copied(app, pilot)
        kept = [not (hasattr(view._at(row)[0], "has_class") and view._at(row)[0].has_class("conduction"))
                for row in range(start.y, end.y + 1)]
        view.toggle_conduction()
        await pilot.pause()
        after = await copied(app, pilot)
        out.append({"case": "d: c folds the start's line", "before": before, "after": after, "lit": lit(view),
                    "expected": "\n".join(text for text, keep in zip(before.split("\n"), kept) if keep),
                    "moved": True, "moves": True, "loose": False})
        view.toggle_conduction()
        await pilot.pause()
        again = await copied(app, pilot)
        out.append({"case": "d: c again unfolds it", "before": before, "after": again, "lit": lit(view),
                    "expected": before, "moved": True, "moves": True, "loose": False})
        thought = next(one for one in view._items if not isinstance(one, Block) and one.has_class("conduction")
                       and view._items.index(one) > line.index + 1)
        app.screen.selections = {view: Selection(start, Offset(4, view._tops[thought.index]))}
        await pilot.pause()
        before = await copied(app, pilot)
        view.toggle_conduction()
        await pilot.pause()
        out.append({"case": "d: c folds both ends", "before": before, "after": await copied(app, pilot),
                    "lit": lit(view), "expected": "", "moved": True, "moves": True, "loose": False})
    return out


async def scrolled():
    """(e) the scrollbar that comes: a first paragraph that fills the row, lines added at the end until the transcript
    runs past the view -- the scrollbar takes its cells, the paragraph wraps on one row more."""
    app = Probe()
    async with app.run_test(size=(60, 20)) as pilot:
        view = app.query_one(TranscriptView)
        inner = view.scrollable_content_region.width - 2
        view = await opened(app, pilot, "a" * (inner - 6) + " bcdef\n\nThe second paragraph, short.")

        async def added():
            for n in range(24):
                await view.add(said("verdict", 20 + n, state="done", cost_usd=0.01, launches=1))
        return await held(app, pilot, view, "e: the scrollbar comes", added, single=True)


async def dragging():
    """(h) a drag under way: pressed in the words, moved to their last row, a call placed above, moved again over the
    same character -- its row one lower -- and released."""
    app = Probe()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await opened(app, pilot)
        top, rows = placed(view)
        said_rows = [top + n for n, row in enumerate(rows) if n and row.strip()]
        left, indent = view.content_region.x - view.region.x, view._rows_of(view._at(top)[0])[1][1]
        first, last = said_rows[0], said_rows[-1]
        await pilot.mouse_down(view, offset=(left + indent + 4, first - view.scroll_offset.y))
        await pilot.hover(view, offset=(left + indent + 10, last - view.scroll_offset.y))
        await pilot.pause()
        before = await copied(app, pilot)
        await view.add(TOOL)
        await pilot.pause()
        moved = placed(view)[0] - top
        await pilot.hover(view, offset=(left + indent + 10, last + moved - view.scroll_offset.y))
        await pilot.mouse_up(view, offset=(left + indent + 10, last + moved - view.scroll_offset.y))
        await pilot.pause()
        return {"case": "h: a drag under way, a line placed above", "before": before, "after": await copied(app, pilot),
                "lit": lit(view), "expected": before, "moved": moved != 0, "moves": True, "loose": False}


class Lined(Probe):
    """The transcript above a message line, as a conversation's tab lays them: the line stands below it in the
    focus chain."""
    CSS = "TextArea { dock: bottom; height: 3; }"

    def compose(self):
        yield TranscriptView()
        yield TextArea(id="message")


async def long(app, pilot, turns=8, framed=False):
    """-> a transcript that runs past the view: `turns` turns, each a message, a conduction, a call with its result
    and words of two paragraphs."""
    view = app.query_one(TranscriptView)
    if framed:
        view.styles.border = ("round", "white")
    for turn in range(turns):
        n = turn * 5
        for event in (said("principal", n, text=f"question {turn}"),
                      said("conduction", n + 1, launch=1, blocks=[{"stack": "TURN{2/4}"}]),
                      said("tool", n + 2, id=f"t{turn}", name="Bash", input={"command": f"ls {turn}"}),
                      said("tool-result", n + 3, id=f"t{turn}", content=f"file{turn}.py"),
                      said("words", n + 4, launch=1, text=f"Answer {turn}, its first paragraph of words."
                                                          f"\n\nAnswer {turn}, its second paragraph.")):
            await view.add(event)
    await pilot.pause()
    view._settle()
    return view


async def raised(app, pilot, line=False, framed=False):
    """-> the long transcript, its view raised to its 7th row, the focus on the message line or on the transcript."""
    view = await long(app, pilot, framed=framed)
    (app.query_one("#message") if line else view).focus()
    await pilot.pause()
    view.scroll_to(y=6, animate=False)
    await pilot.pause()
    return view


def texts(view):
    """-> the text of every row the transcript holds."""
    view._settle()
    return [row[0].plain for item in view._items for row in view._rows_of(item)]


def taken(rows, start, end):
    """-> the text between two places of the rows, read row by row: from the character `start` to the one before
    `end`."""
    (x1, y1), (x2, y2) = start, end
    if y1 == y2:
        return rows[y1][x1:x2]
    return "\n".join([rows[y1][x1:], *rows[y1 + 1:y2], rows[y2][:x2]])


def gutter(view):
    """-> the cells before the content of the view, and above it."""
    return view.content_region.x - view.region.x, view.content_region.y - view.region.y


def cell(view, row, char):
    """-> where the character `char` of the row `row` is drawn, as an offset in the view."""
    item, within = view._at(row)
    left, top = gutter(view)
    return left + view._rows_of(item)[within][1] + char, top + row - view.scroll_offset.y


def worded(view, least=12):
    """-> the rows in view that a block draws with `least` characters or more, top down."""
    rows, first = texts(view), view.scroll_offset.y
    return [row for row in range(first, min(first + view.scrollable_content_region.height, view._total))
            if isinstance(view._at(row)[0], Block) and len(rows[row]) >= least]


async def read(name, app, pilot, view, expected, stood, guard=True):
    """-> one raised case judged: what `ctrl+c` copies, what is lit, whether the view moved, the screens standing."""
    await pilot.pause()
    screens = len(app.screen_stack)
    return {"case": name, "copied": await copied(app, pilot), "expected": expected, "lit": lit(view),
            "moved": view.scroll_offset.y != stood, "screens": screens, "guard": bool(guard)}


async def drag(pilot, view, press, pointer, on=None):
    """A drag from an offset of the view to another -- or to an offset of the widget `on`."""
    await pilot.mouse_down(view, offset=press)
    await pilot.hover(view if on is None else on, offset=pointer)
    await pilot.mouse_up(view if on is None else on, offset=pointer)


async def raised_cases():
    out = []
    # (i) the message line focused: a drag, a click alone, `shift+tab`
    app = Lined()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await raised(app, pilot, line=True)
        rows, stood, rows_in = texts(view), view.scroll_offset.y, worded(view)
        first, last = rows_in[0], rows_in[-1]
        await drag(pilot, view, cell(view, first, 4), cell(view, last, 9))
        out.append(await read("i: a drag in a raised view, the message line focused", app, pilot, view,
                              taken(rows, (4, first), (10, last)), stood, last > first))
    app = Lined()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await raised(app, pilot, line=True)
        stood = view.scroll_offset.y
        await pilot.click(view, offset=cell(view, worded(view)[0], 4))
        out.append(await read("i: a click alone in a raised view, the message line focused", app, pilot, view, "",
                              stood))
    app = Lined()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await raised(app, pilot, line=True)
        await pilot.press("shift+tab")
        await pilot.pause()
        live = view._live()
        at = view._tops[live[-1].index] - view.scroll_offset.y
        keyed = {"focused": app.screen.focused is view, "cursor": bool(live) and view.cursor is live[-1],
                 "shown": 0 <= at < view.scrollable_content_region.height}

    # (j) a press on the margin; on the border of a framed transcript; a pointer on its top border
    app = Lined()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await raised(app, pilot)
        rows, stood, rows_in = texts(view), view.scroll_offset.y, worded(view)
        first, last = rows_in[0], rows_in[-1]
        left, top = gutter(view)
        await drag(pilot, view, (left - 1, top + first - stood), cell(view, last, 9))
        out.append(await read("j: a press on the margin of a raised view", app, pilot, view,
                              taken(rows, (0, first), (10, last)), stood, left >= 1 and last > first))
    app = Lined()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await raised(app, pilot, framed=True)
        rows, stood, rows_in = texts(view), view.scroll_offset.y, worded(view)
        first, last = rows_in[0], rows_in[-1]
        left, top = gutter(view)
        await drag(pilot, view, (0, top + first - stood), cell(view, last, 9))
        out.append(await read("j: a press on the border of a raised view", app, pilot, view,
                              taken(rows, (0, first), (10, last)), stood, left >= 2 and last > first))
        app.screen.clear_selection()
        await pilot.pause()
        await drag(pilot, view, cell(view, last, 4), (cell(view, last, 9)[0], 0))
        out.append(await read("j: a pointer on the top border of a raised view", app, pilot, view,
                              taken(rows, (0, stood), (5, last)), stood, top >= 1 and last > stood))

    # (k) a pointer on the scrollbar; below the view, on the message line
    app = Lined()
    async with app.run_test(size=(60, 20)) as pilot:
        view = await raised(app, pilot)
        rows, stood, rows_in = texts(view), view.scroll_offset.y, worded(view)
        first, last = rows_in[0], rows_in[-1]
        bar = view.scrollable_content_region.right - view.region.x
        await drag(pilot, view, cell(view, first, 4), (bar, cell(view, last, 0)[1]))
        out.append(await read("k: a pointer on the scrollbar of a raised view", app, pilot, view,
                              taken(rows, (4, first), (len(rows[last]), last)), stood,
                              view.show_vertical_scrollbar and last > first))
        app.screen.clear_selection()
        await pilot.pause()
        bottom = stood + view.scrollable_content_region.height - 1
        await drag(pilot, view, cell(view, first, 4), (5, 1), on="#message")
        out.append(await read("k: a pointer below a raised view, on the message line", app, pilot, view,
                              taken(rows, (4, first), (len(rows[bottom]), bottom)), stood, bottom < view._total - 1))

    # (l) a selection that ends on an empty last row; the whole transcript selected
    app = Probe()
    async with app.run_test(size=(60, 20)) as pilot:
        view = app.query_one(TranscriptView)
        await view.add(said("principal", 0, text="a question"))
        await view.add(said("words", 1, launch=1, text="A paragraph.\n\n```python\nprint(1)\n```\n"))
        await pilot.pause()
        rows = texts(view)
        end, empty = len(rows) - 1, len(rows) > 3 and rows[-1] == "" and rows[-2].strip() != ""
        app.screen.selections = {view: Selection(Offset(0, end - 3), Offset(0, end))}
        out.append(await read("l: a selection that ends on an empty last row", app, pilot, view,
                              taken(rows, (0, end - 3), (0, end)), 0, empty))
        view.text_select_all()
        out.append(await read("l: the whole transcript selected, its last row empty", app, pilot, view,
                              "\n".join(rows), 0, empty))

    # (m) a selection under a row that carries U+2028
    app = Probe()
    async with app.run_test(size=(60, 20)) as pilot:
        view = app.query_one(TranscriptView)
        await view.add(said("principal", 0, text="a question"))
        await view.add(said("words", 1, launch=1, text="before\u2028after the separator.\n\nA second paragraph."))
        await view.add(said("words", 2, launch=1, text="The last block, on one row."))
        await pilot.pause()
        rows = texts(view)
        last = max(n for n, row in enumerate(rows) if row.strip())
        carried = [n for n, row in enumerate(rows) if "\u2028" in row]
        app.screen.selections = {view: Selection(Offset(0, last), Offset(8, last))}
        out.append(await read("m: a selection under a row that carries U+2028", app, pilot, view,
                              taken(rows, (0, last), (8, last)), 0, carried and carried[0] < last))

    # (n) a drag released past the end of a row, then the terminal widened
    app = Probe()
    async with app.run_test(size=(50, 20)) as pilot:
        view = app.query_one(TranscriptView)
        await view.add(said("principal", 0, text="a question"))
        await view.add(said("words", 1, launch=1, text="Four short words here then-one-word-too-long-to-stay-on-it "
                                                       "and words that follow it, enough of them to wrap twice."))
        await pilot.pause()
        view.focus()
        rows, first = texts(view), placed(view)[0] + 1       # the first row of the words, under their head
        edge = view.scrollable_content_region.right - view.region.x - 1
        past = edge - cell(view, first, len(rows[first]))[0]
        await drag(pilot, view, cell(view, first, 0), (edge, cell(view, first, 0)[1]))
        await pilot.pause()
        before = await copied(app, pilot)
        await pilot.resize_terminal(110, 20)
        await pilot.pause()
        wider = texts(view)
        out.append(await read("n: a drag released past a row's end, the terminal widened", app, pilot, view, before, 0,
                              past >= 3 and before == rows[first] and len(wider[first]) > len(rows[first])))
    return out, keyed


async def main():
    out = {"seen": [await seen(theme) for theme in THEMES], "dragged": await dragged(), "cases": await cases()}
    out["raised"], out["keyed"] = await raised_cases()
    print(json.dumps(out))


asyncio.run(main())
'''


def scenario(bench) -> int:
    held, failures = bench.held, bench.failures
    probe = bench.temp() / "transcript-selection-probe.py"
    probe.write_text(PROBE, encoding="utf-8")
    played = subprocess.run([*TEXTUAL, str(probe), str(SKILL), *THEMES],
                            capture_output=True, text=True, cwd=bench.temp(), timeout=180)
    try:
        out = json.loads(played.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        out = {}
    if played.returncode != 0 or not out:
        failures.append(f"  ✗ the probe of the selection    rc={played.returncode} {played.stderr[-600:]!r}")
        return 0

    # --- the selected cells seen: their text in a colour other than their background, on each theme --------------
    for one in out["seen"]:
        selected = one["selected"]
        kept = bool(selected) and all(cell["fg"] and cell["fg"] != cell["bg"] for cell in selected)
        marked = bool(selected) and all(cell["bg"] not in one["others"] for cell in selected)
        if kept and marked:
            held(f"the selection seen on {one['theme']}",
                 f"{len(selected)} segment(s) selected, text over background "
                 f"{sorted({(cell['fg'], cell['bg']) for cell in selected})}, the row's other backgrounds {one['others']}")
        else:
            failures.append(f"  ✗ the selection on {one['theme']:<14} text kept={kept} background marked={marked}: "
                            f"{[(cell['fg'], cell['bg']) for cell in selected]}, others {one['others']}")

    # --- a drag from the margin copies the row whole ----------------------------------------------------------------
    drag = out["dragged"]
    if drag["row"].strip() and drag["copied"] == drag["row"]:
        held("a drag from the margin copies the row",
             f"from column 0 over {drag['indent']} cell(s) before the text: {drag['selection']}, "
             f"{len(drag['copied'])} character(s) copied, the row's whole text")
    else:
        failures.append(f"  ✗ the drag from the margin      {drag['selection']}: copied {drag['copied']!r}, "
                        f"the row holds {drag['row']!r}")

    # --- a selection held while the rows move: the same text copied, the same text lit -----------------------------
    for one in out["cases"]:
        after = " ".join(one["after"].split()) if one["loose"] else one["after"]
        lit = " ".join(one["lit"].split()) if one["loose"] else one["lit"]
        copied = after == one["expected"] and (one["before"] or one["expected"] == "")
        seen = lit == after
        moved = one["moves"] is None or one["moved"] == one["moves"]
        if copied and seen and moved:
            held(one["case"], f"{len(one['after'])} character(s) copied as before the movement, the same lit; "
                              f"the rows moved: {one['moved']}")
        else:
            failures.append(f"  ✗ {one['case']}: copied={copied} lit={seen} moved={one['moved']} "
                            f"(expected {one['moves']}) -- before {one['before']!r}, after {one['after']!r}, "
                            f"lit {one['lit']!r}, expected {one['expected']!r}")

    # --- a selection in a raised view: the rows between its two places copied, the same lit, the view standing --------
    for one in out["raised"]:
        expected = one["expected"].rstrip("\n")               # the copy leaves the line ends that close it
        copied = one["copied"] == expected
        seen = one["lit"] == one["copied"].strip("\n")
        stood = not one["moved"] and one["screens"] == 1
        if one["guard"] and copied and seen and stood:
            held(one["case"], f"{len(one['copied'])} character(s) copied, the rows between the two places, the same "
                              f"lit; the view stood, {one['screens']} screen")
        else:
            failures.append(f"  ✗ {one['case']}: copied={copied} lit={seen} stood={stood} guard={one['guard']} -- "
                            f"copied {one['copied'][:90]!r} ({len(one['copied'])}), lit {one['lit'][:90]!r}, "
                            f"expected {expected[:90]!r} ({len(expected)}), screens {one['screens']}")
    keyed = out["keyed"]
    if all(keyed.values()):
        held("shift+tab from the message line, the view raised",
             "the focus on the transcript, the cursor on its last live line, that line in view")
    else:
        failures.append(f"  ✗ shift+tab from the message line    {keyed}")
    return 0
