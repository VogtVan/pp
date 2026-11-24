"""render -- a pane of the post as TEXT, without a terminal: the app runs headless at the
asked size under Textual's test pilot, settles, and its screen is printed through a
recording console -- the same path `App.export_screenshot` takes to make its SVG, exported
as text instead -- under `--styles`, with the ANSI styles of what is drawn, the look of each line
the bench compares. What the bench and `--render` read is exactly what the compositor drew.
`rendered` is a coroutine: the entry awaits it on the loop the conversations were opened on."""
from __future__ import annotations

import asyncio
import io
import json
from pathlib import Path

from rich.console import Console
from textual import events
from textual.app import App
from textual.geometry import Offset
from textual.selection import Selection
from textual.widgets.markdown import MarkdownBlock

from model import FRAME, Size

LAYOUTS = "layouts"                  # a word of the keys: the count of the transcript's arrangements, noted there
SPINNING = "spinning"                # a word of the keys: whether the spinner's interval is alive, noted there
REST = "rest:"                       # a word of the keys: `rest:<seconds>` lets that time pass, the screen's timers playing
NODES = "nodes"                      # a word of the keys: the parts of the transcript's last block of the agent, noted there
CLICK = "click:"                     # a word of the keys: `click:<selector>:<x>:<y>` clicks a widget at that offset
DOUBLE = "double:"                   # a word of the keys: `double:<selector>:<x>:<y>` double-clicks a widget at that offset
HOVER = "hover:"                     # a word of the keys: `hover:<selector>:<x>:<y>` moves the mouse over a widget there
ROWS = "rows"                        # a word of the keys: the rows the Tasks tab's band drew of its thread before its history came
LIVE = "live"                        # a word of the keys: the activity of each member of the Tasks tab's band, noted there
LISTED = "list"                      # a word of the keys: the scroll of the Tasks tab's list and the task under its cursor
CRASH = "crash"                      # a word of the keys: an exception raised inside the application, as a defect would
BURST = "burst:"                     # a word of the keys: `burst:<key>:<key>…` sends those keys back to back, unsettled
SELECT = "select:"                   # a word of the keys: `select:<selector>:<x1>:<y1>:<x2>:<y2>` selects in a widget
CLIPBOARD = "clipboard"              # a word of the keys: what the application copied last, noted there
BOXES = "boxes"                      # a word of the keys: where the box of the overlay on top and its zones stand, noted there
BLOCKS = "blocks"                    # a word of the keys: the kinds of the blocks of the markdown on top, noted there
SVG = "svg:"                         # a word of the keys: `svg:<path>` saves the screen there as an SVG, Textual's own
BLUR, FOCUS = "blur", "focus"        # words of the keys: the application loses, or takes back, the focus of the terminal --
                                     # the widget focused then and the application's focus noted


def screen_text(app: App, styles: bool = False) -> str:
    """-> the screen of a RUNNING app, as text, line by line -- with its ANSI styles when asked."""
    width, height = app.size
    console = Console(width=width, height=height, file=io.StringIO(), force_terminal=True,
                      color_system="truecolor", record=True, legacy_windows=False, safe_box=False)
    console.print(app.screen._compositor.render_update(full=True,
                                                       screen_stack=app._background_screens))
    return console.export_text(styles=styles)


def regions_text(app: App, pane: str) -> str:
    """-> where the parts of a pane stand on the screen, one line each, `<part> <id> x=<x> y=<y> w=<w> h=<h>` --
    its menu, its folded line, and each band of its centre that is shown, then each part of that band that is shown
    and named (`inner`): what the bench measures to say that a centre is a pile of horizontal bands, that a menu folds
    on a narrow screen, and what a band holds; then each FRAMED zone of the pane that is shown (`framed`), its top row
    its frame's; then every fixed ZONE of the screen (class `zone`) that is laid out, shown or hidden -- what it
    measures to say that nothing moves a zone; then each part of the pane that shows a horizontal scroll bar (`hbar`) --
    what it measures to say that a menu holds its columns."""
    lines = []
    root = app.query_one(f"#pane-{pane}")
    for part, selector in (("menu", ".menu"), ("fold", ".fold")):
        for one in root.query(selector):
            region = one.region
            lines.append(f"{part} {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
    for centre in root.query(".centre"):
        for one in centre.children:
            region = one.region
            if one.display and region.width and region.height:
                lines.append(f"band {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
                for inner in one.children:
                    area = inner.region
                    if inner.id and inner.display and area.width and area.height:
                        lines.append(f"inner {inner.id} x={area.x} y={area.y} w={area.width} h={area.height}")
    for one in root.query(".framed"):
        region = one.region
        if one.display and region.width and region.height:
            lines.append(f"framed {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
    for one in app.screen.query(".zone"):
        region = one.region
        if region.width and region.height:
            lines.append(f"zone {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
    for one in root.walk_children():
        region = one.region
        if one.display and region.width and region.height and one.scrollbars_enabled[1]:
            lines.append(f"hbar {one.id} x={region.x} y={region.y} w={region.width} h={region.height}")
    return "\n".join(lines) + "\n"


def boxes_text(app: App) -> str:
    """-> where the overlay on top stands, `<id>=<x>,<y>,<w>,<h>` joined by `;`: its box (`#box`), then each ZONE of a
    file form (class `form-zone`) that is shown -- what the bench compares from one state of a form to the next;
    `none` without a box."""
    found = []
    for one in [*app.screen.query("#box"), *app.screen.query(".form-zone")]:
        region = one.region
        if one.display and region.width and region.height:
            found.append(f"{one.id}={region.x},{region.y},{region.width},{region.height}")
    return ";".join(found) or "none"


WAIT_SECONDS = 10.0                  # the default bound of `--wait`


async def rendered(app, pane: str, size: Size, keys: tuple[str, ...] = (), wait: str | None = None,
                   seconds: float = WAIT_SECONDS, styles: bool = False, regions: bool = False) -> str:
    """-> the pane `pane` (or the whole frame) at `size`, after the `keys` are pressed in
    order (Textual's key names: `2`, `tab`, `ctrl+left`) and, with `wait`, after one more
    event of that kind than before the LAST key pressed reached any conversation (within
    `seconds`), as text ending with a newline -- its ANSI styles kept under `styles`; under `regions`, where the
    parts of the pane stand instead (`regions_text`). The word `layouts` among the keys notes, at that point, how
    many arrangements the active conversation's transcript computed: the counts noted close the text on one line,
    `layouts <n> <n> …`; the word `spinning` notes whether the spinner's interval is alive (1, else 0), closing the
    text on `spinning <n> <n> …`; the word `rest:<seconds>` lets that time pass, the screen's timers playing; the word
    `nodes` notes how many parts (its head, its words) the last block of the agent's words in the active transcript holds, closing the text
    on `nodes <n> <n> …`; the words `blur` and `focus` make the application lose and take back the focus of the terminal,
    each noting the widget focused then (its id, `none` without one) and the application's focus (1, else 0), closing
    the text on `focused <id>:<n> <id>:<n> …`; the word `rows` notes how many rows the Tasks tab's band drew of its
    thread before the thread's history came -- those drawn so far while it is on its way --, closing the text on `rows <n> <n> …`; the word
    `live` notes the activity of each member of that band (`<member>=<what it does>`, joined by `;`), closing the
    text on `live <…> | <…> …`; the word `list` notes where the Tasks tab's list stands -- its scroll, the task under
    its cursor, the cursor's row in the view, its lines: `<scroll_y>:<team>/<task>:<row>:<lines>` --, closing the text
    on `list <…> <…> …`;
    the word `click:<selector>:<x>:<y>` clicks the widget the selector names at that
    offset, as the mouse would, and `double:<selector>:<x>:<y>` double-clicks it there; the word `hover:<selector>:<x>:<y>` moves the mouse there, as it would without a
    click -- what a look under the mouse is proven on; the word `select:<selector>:<x1>:<y1>:<x2>:<y2>` adds to the screen's selection the
    text of the widget the selector names between those offsets of its content, `-` for an open end, `h` for the
    row under its last, as a drag would; the word `clipboard` notes what the application copied last, closing the text on `clipboard <json> …`;
    the word `boxes` notes where the overlay on top and the zones of a file form stand (`boxes_text`), closing the
    text on `boxes <…> | <…> …`; the word `blocks` notes the kind of each block of the markdown the screen on top
    shows (`MarkdownH1`, `MarkdownTable`, `MarkdownFence` …), joined by `,`, closing the text on `blocks <…> | <…> …`;
    the word `svg:<path>` saves the screen at that point as an SVG at `path` (Textual's `save_screenshot`) -- what a
    capture for the eye is made of;
    the word `crash` raises an exception inside the application's loop, as a defect
    would -- what the trace of a crash is proven on; the word `burst:<key>:<key>…` sends those keys to the application
    back to back, none settled before the next, as fast typing does -- what a race between their events is proven on. A `wait:` counts from the last key pressed, or from the last
    `wait:` after it."""
    async with app.run_test(size=(size.width, size.height)) as pilot:
        await app.settled()                    # the conversations of the start in their tabs, the agents read
        await pilot.pause()
        if pane != FRAME:
            app.show_pane(pane)
        await app.pane_settled()               # the pane shown read what its showing asked
        seen = app.counts()
        counted: list[int] = []
        spun: list[int] = []
        nodes: list[int] = []
        focused: list[str] = []
        rows: list[int] = []
        lives: list[str] = []
        listed: list[str] = []
        clipped: list[str] = []
        boxed: list[str] = []
        blocked: list[str] = []
        for key in keys:
            if key == LAYOUTS:
                await pilot.pause()
                counted.append(app.layouts())
            elif key == SPINNING:
                await app.pane_settled()
                await pilot.pause()
                spun.append(app.spinning())
            elif key == NODES:
                await pilot.pause()
                nodes.append(app.nodes())
            elif key == ROWS:
                await pilot.pause()
                rows.append(app.rows())
            elif key == LISTED:
                await pilot.pause()
                await pilot.pause()                 # the scroll a reading asked, played after its refresh
                listed.append(app.listed())
            elif key == LIVE:
                lives.append(app.live_lines())      # noted at once: what the watch said is kept as it comes
            elif key.startswith(SVG):
                await pilot.pause()
                await pilot.pause()                 # the screen laid out once its fields are
                where = Path(key[len(SVG):])
                app.save_screenshot(where.name, str(where.parent))
            elif key == BOXES:
                await pilot.pause()
                await pilot.pause()                 # the box laid out once its fields are
                boxed.append(boxes_text(app))
            elif key == BLOCKS:
                await pilot.pause()
                await pilot.pause()                 # the markdown parsed and mounted
                blocked.append(",".join(type(one).__name__ for one in app.screen.query(MarkdownBlock)) or "none")
            elif key == CLIPBOARD:
                await pilot.pause()
                clipped.append(json.dumps(app.clipboard))
            elif key.startswith(SELECT):
                selector, x1, y1, x2, y2 = key[len(SELECT):].rsplit(":", 4)
                await _laid_out(app, pilot, selector, seconds)
                widget = app.query_one(selector)
                row = lambda y: widget.size.height if y == "h" else int(y)   # `h`: the row under its last
                start = None if "-" in (x1, y1) else Offset(int(x1), row(y1))
                end = None if "-" in (x2, y2) else Offset(int(x2), row(y2))
                app.screen.selections = {**app.screen.selections, widget: Selection(start, end)}
                await pilot.pause()
            elif key.startswith(BURST):
                for one in key[len(BURST):].split(":"):
                    pressed = events.Key(one, one if len(one) == 1 else None)
                    pressed.set_sender(app)
                    app._driver.send_message(pressed)
                await pilot.pause()
                await app.pane_settled()
            elif key == CRASH:
                app.call_later(_crash)
                await pilot.pause()
            elif key in (BLUR, FOCUS):
                app.post_message(events.AppBlur() if key == BLUR else events.AppFocus())
                await pilot.pause()
                widget = app.screen.focused
                focused.append(f"{(widget.id or type(widget).__name__) if widget is not None else 'none'}:"
                               f"{int(app.app_focus)}")
            elif key.startswith((CLICK, DOUBLE)):
                selector, x, y = key.split(":", 1)[1].rsplit(":", 2)
                await _laid_out(app, pilot, selector, seconds)   # the widget's region is where the mouse goes
                await pilot.click(selector, offset=(int(x), int(y)), times=2 if key.startswith(DOUBLE) else 1)
                await pilot.pause()
                await app.pane_settled()
            elif key.startswith(HOVER):
                selector, x, y = key[len(HOVER):].rsplit(":", 2)
                await _laid_out(app, pilot, selector, seconds)
                await pilot.hover(selector, offset=(int(x), int(y)))
                await pilot.pause()
            elif key.startswith(REST):
                await asyncio.sleep(float(key[len(REST):]))
                await pilot.pause()
                await app.pane_settled()
            elif key.startswith("wait:"):
                # a pause in the sequence: one more event of that kind than BEFORE the last key
                # pressed (the flow may have answered already, within the key's own settling)
                await _one_more(app, key[5:], seconds, seen.get(key[5:], 0))
                seen[key[5:]] = app.saw(key[5:])
                await pilot.pause()
            else:
                seen = app.counts()
                await pilot.press(key)
                if app.return_code is not None:   # the post left on a key (a verb asked of the console): nothing to show
                    return ""
                await app.pane_settled()
        if wait:
            await _one_more(app, wait, seconds, seen.get(wait, 0))
        await pilot.pause()
        await app.pane_settled(final=True)     # a thread whose cursor rests too
        await pilot.pause()                    # what the last reading changed, laid out before it is printed
        text = regions_text(app, pane) if regions else screen_text(app, styles)
    text = text if text.endswith("\n") else text + "\n"
    return (text + (f"{LAYOUTS} {' '.join(str(one) for one in counted)}\n" if counted else "")
            + (f"{SPINNING} {' '.join(str(one) for one in spun)}\n" if spun else "")
            + (f"{NODES} {' '.join(str(one) for one in nodes)}\n" if nodes else "")
            + (f"focused {' '.join(focused)}\n" if focused else "")
            + (f"{ROWS} {' '.join(str(one) for one in rows)}\n" if rows else "")
            + (f"{LIVE} {' | '.join(lives)}\n" if lives else "")
            + (f"{LISTED} {' '.join(listed)}\n" if listed else "")
            + (f"{CLIPBOARD} {' '.join(clipped)}\n" if clipped else "")
            + (f"{BOXES} {' | '.join(boxed)}\n" if boxed else "")
            + (f"{BLOCKS} {' | '.join(blocked)}\n" if blocked else ""))


def _crash() -> None:
    """The bench's crash: an exception out of a callback of the application's loop."""
    raise RuntimeError("the bench's crash -- an exception left the application")


async def _laid_out(app, pilot, selector: str, seconds: float) -> None:
    """Waits until the widget `selector` names has a region, the same at two pauses of the pilot in a row -- the
    screen laid out after what the last reading changed --, or `seconds` passed."""
    deadline = asyncio.get_event_loop().time() + seconds
    last = None
    while asyncio.get_event_loop().time() < deadline:
        await pilot.pause()
        region = app.query_one(selector).region
        if region.width and region.height and region == last:
            return
        last = region


async def _one_more(app, kind: str, seconds: float, before: int | None = None) -> None:
    """Waits until the conversations took ONE MORE event of `kind` than `before` (their count
    now, by default) -- or the flow ended, or `seconds` passed."""
    count = app.saw(kind) if before is None else before
    deadline = asyncio.get_event_loop().time() + seconds
    while app.saw(kind) <= count and not app.saw("ended"):
        if asyncio.get_event_loop().time() >= deadline:
            return
        await asyncio.sleep(0.05)


def text_of(app, pane: str, size: Size, keys: tuple[str, ...] = (), wait: str | None = None,
            seconds: float = WAIT_SECONDS) -> str:
    """The same, on a loop of its own -- for a post opened on no conversation."""
    return asyncio.run(rendered(app, pane, size, keys, wait, seconds))
